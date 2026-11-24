from math import ceil

from sqlalchemy.exc import IntegrityError

from app.errors import ConflitoError, NaoEncontradoError, ProibidoError
from app.extensions import db
from app.models import Auditoria, MovimentacaoKanban, Projeto
from app.repositories import projeto_repository, usuario_repository
from app.repositories import match_repository, ideia_repository
from app.schemas.projeto_schema import ETAPAS_KANBAN

_PERFIS_ANALISTA = {"analista/hub", "analista", "hub", "administrador", "admin"}


def _nomes(perfis):
    return {str(perfil).strip().casefold() for perfil in (perfis or [])}


def _e_analista(perfis):
    return bool(_nomes(perfis) & _PERFIS_ANALISTA)


def _exigir_analista(perfis):
    if not _e_analista(perfis):
        raise ProibidoError("Apenas o Analista/Hub pode realizar esta ação.")


def _buscar_ou_404(id_projeto):
    projeto = projeto_repository.buscar_por_id(id_projeto)
    if projeto is None:
        raise NaoEncontradoError("Projeto não encontrado.")
    return projeto


def _auditar(id_usuario, entidade, id_registro, acao, detalhes):
    db.session.add(Auditoria(id_usuario=id_usuario, entidade=entidade,
                             id_registro=id_registro, acao=acao, detalhes=detalhes))


def _serializar(projeto, incluir_historico=False):
    match = match_repository.buscar_por_id(projeto.id_match)
    ideia = ideia_repository.buscar_por_id(match.id_ideia) if match else None
    desafio_id = match.id_desafio if match else None
    responsavel = usuario_repository.buscar_por_id(projeto.id_responsavel)
    dados = {
        "id_projeto": projeto.id_projeto,
        "id_match": projeto.id_match,
        "id_ideia": ideia.id_ideia if ideia else None,
        "titulo_ideia": ideia.titulo if ideia else None,
        "id_desafio": desafio_id,
        "id_responsavel": projeto.id_responsavel,
        "responsavel_nome": responsavel.nome if responsavel else None,
        "titulo": projeto.titulo,
        "descricao": projeto.descricao,
        "status_kanban": projeto.status_kanban,
        "data_prazo": projeto.data_prazo.isoformat() if projeto.data_prazo else None,
        "data_criacao": projeto.data_criacao.isoformat() if projeto.data_criacao else None,
        "data_atualizacao": projeto.data_atualizacao.isoformat() if projeto.data_atualizacao else None,
    }
    if incluir_historico:
        dados["historico"] = [{
            "id_movimentacao": item.id_movimentacao,
            "id_usuario": item.id_usuario,
            "etapa_origem": item.etapa_origem,
            "etapa_destino": item.etapa_destino,
            "data_movimentacao": item.data_movimentacao.isoformat() if item.data_movimentacao else None,
        } for item in projeto_repository.listar_movimentacoes(projeto.id_projeto)]
    return dados


def criar(dados, id_usuario, perfis):
    _exigir_analista(perfis)
    match = match_repository.buscar_por_id(dados["id_match"])
    if match is None:
        raise NaoEncontradoError("Match não encontrado.")
    if match.status_match != "VALIDADO":
        raise ConflitoError("Só é possível criar um projeto a partir de um match validado.")
    ideia = ideia_repository.buscar_por_id(match.id_ideia)
    if ideia is None:
        raise NaoEncontradoError("Ideia não encontrada.")
    if (ideia.status or "").strip().casefold() != "aprovada":
        raise ConflitoError("Só é possível converter uma ideia aprovada em projeto.")
    if projeto_repository.ultima_triagem_aprovada(match.id_match) is None:
        raise ConflitoError("A ideia precisa possuir uma triagem com decisão aprovada.")
    if projeto_repository.buscar_por_match(match.id_match):
        raise ConflitoError("Esta ideia já foi convertida em projeto.")

    id_responsavel = dados.get("id_responsavel", id_usuario)
    if usuario_repository.buscar_por_id(id_responsavel) is None:
        raise NaoEncontradoError("Usuário responsável não encontrado.")
    projeto = Projeto(
        id_match=match.id_match,
        id_responsavel=id_responsavel,
        titulo=dados.get("titulo") or ideia.titulo,
        descricao=dados.get("descricao", ideia.descricao),
        status_kanban="Aprovado",
        data_prazo=dados.get("data_prazo"),
    )
    try:
        projeto_repository.adicionar(projeto)
        db.session.flush()
        _auditar(id_usuario, "projeto", projeto.id_projeto, "CRIACAO",
                 f"Projeto criado a partir da ideia {ideia.id_ideia} e do match {match.id_match}.")
        db.session.commit()
        db.session.refresh(projeto)
    except IntegrityError as erro:
        db.session.rollback()
        raise ConflitoError("Não foi possível converter a ideia em projeto.") from erro
    return _serializar(projeto, incluir_historico=True)


def listar(filtros, page, page_size, id_usuario, perfis):
    filtros = dict(filtros)
    if not _e_analista(perfis):
        filtros["id_responsavel"] = id_usuario
    projetos, total = projeto_repository.listar(filtros, page, page_size)
    return {"items": [_serializar(item) for item in projetos],
            "page": page, "page_size": page_size, "total": total,
            "pages": ceil(total / page_size) if total else 0}


def obter(id_projeto, id_usuario, perfis):
    projeto = _buscar_ou_404(id_projeto)
    if not _e_analista(perfis) and projeto.id_responsavel != id_usuario:
        raise ProibidoError("Você não tem permissão para acessar este projeto.")
    return _serializar(projeto, incluir_historico=True)


def atualizar(id_projeto, dados, id_usuario, perfis):
    projeto = _buscar_ou_404(id_projeto)
    if not _e_analista(perfis) and projeto.id_responsavel != id_usuario:
        raise ProibidoError("Você não tem permissão para editar este projeto.")
    if "id_responsavel" in dados and usuario_repository.buscar_por_id(dados["id_responsavel"]) is None:
        raise NaoEncontradoError("Usuário responsável não encontrado.")
    try:
        projeto_repository.atualizar(projeto, dados)
        _auditar(id_usuario, "projeto", projeto.id_projeto, "ATUALIZACAO",
                 "Dados do projeto atualizados: " + ", ".join(sorted(dados.keys())) + ".")
        db.session.commit()
        db.session.refresh(projeto)
    except IntegrityError as erro:
        db.session.rollback()
        raise ConflitoError("Não foi possível atualizar o projeto.") from erro
    return _serializar(projeto, incluir_historico=True)


def movimentar(id_projeto, etapa, id_usuario, perfis):
    _exigir_analista(perfis)
    projeto = _buscar_ou_404(id_projeto)
    if etapa not in ETAPAS_KANBAN:
        raise ConflitoError("Etapa Kanban inválida.")
    origem = projeto.status_kanban
    if origem == etapa:
        raise ConflitoError("O projeto já está nesta etapa.")
    if origem == "Concluído":
        raise ConflitoError("Um projeto concluído não pode ser movimentado.")
    try:
        projeto.status_kanban = etapa
        db.session.add(MovimentacaoKanban(
            id_projeto=projeto.id_projeto, id_usuario=id_usuario,
            etapa_origem=origem, etapa_destino=etapa))
        _auditar(id_usuario, "projeto", projeto.id_projeto, "MOVIMENTACAO_KANBAN",
                 f"Etapa alterada de '{origem}' para '{etapa}'.")
        db.session.flush()
        db.session.commit()
        db.session.refresh(projeto)
    except IntegrityError as erro:
        db.session.rollback()
        raise ConflitoError("Não foi possível movimentar o projeto no Kanban.") from erro
    return _serializar(projeto, incluir_historico=True)
