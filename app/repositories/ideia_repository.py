from sqlalchemy import func, or_, select

from app.extensions import db
from app.models import Desafio, Ideia


def _escapar_like(texto):
    """Escapa %, _ e \\ para que a busca trate o texto de forma literal."""
    return (texto.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_"))


def listar(filtros, page, page_size, escopo=None):
    """Devolve (ideias, total) aplicando filtros e paginação.

    filtros: dict com as chaves opcionais status, area, categoria,
             id_desafio e q.
    escopo:  quem pode ser visto. None = todas as ideias.
             {"id_autor": X}  = só as ideias do autor X;
             {"id_autor": X, "id_responsavel_desafio": X} = as do autor X
             mais as ligadas a desafios dos quais X é responsável.
    """
    consulta = select(Ideia)

    if escopo:
        condicoes = [Ideia.id_autor == escopo["id_autor"]]
        if escopo.get("id_responsavel_desafio"):
            desafios_do_gestor = select(Desafio.id_desafio).where(
                Desafio.id_responsavel == escopo["id_responsavel_desafio"])
            condicoes.append(Ideia.id_desafio.in_(desafios_do_gestor))
        consulta = consulta.where(or_(*condicoes))

    if filtros.get("id_desafio"):
        consulta = consulta.where(Ideia.id_desafio == filtros["id_desafio"])

    if filtros.get("status"):
        consulta = consulta.where(Ideia.status == filtros["status"])
    if filtros.get("area"):
        consulta = consulta.where(Ideia.area == filtros["area"])
    if filtros.get("categoria"):
        consulta = consulta.where(Ideia.categoria == filtros["categoria"])
    if filtros.get("q"):
        termo = f"%{_escapar_like(filtros['q'].strip())}%"
        consulta = consulta.where(or_(
            Ideia.codigo.ilike(termo, escape="\\"),
            Ideia.titulo.ilike(termo, escape="\\"),
            Ideia.descricao.ilike(termo, escape="\\"),
        ))

    total = db.session.scalar(
        select(func.count()).select_from(consulta.subquery()))

    consulta = (consulta
                .order_by(Ideia.data_criacao.desc(), Ideia.id_ideia.desc())
                .limit(page_size)
                .offset((page - 1) * page_size))
    return list(db.session.scalars(consulta)), total


def ultimo_codigo_do_ano(ano):
    """Maior código do ano (ex.: IDE-2026-0007) ou None se não houver."""
    consulta = (select(Ideia.codigo)
                .where(Ideia.codigo.like(f"IDE-{ano}-%"))
                .order_by(func.length(Ideia.codigo).desc(),
                          Ideia.codigo.desc())
                .limit(1))
    return db.session.scalar(consulta)


def buscar_por_id(id_ideia):
    return db.session.get(Ideia, id_ideia)


def adicionar(ideia):
    """Adiciona na sessão e gera o id (o commit é feito no service)."""
    db.session.add(ideia)
    db.session.flush()
    return ideia


def atualizar(ideia, campos):
    """Aplica os campos no objeto (o commit é feito no service)."""
    for nome, valor in campos.items():
        setattr(ideia, nome, valor)
    db.session.flush()
    return ideia


def alterar_status(ideia, novo_status):
    """Muda o status da ideia (o commit é feito no service)."""
    ideia.status = novo_status
    db.session.flush()
    return ideia
