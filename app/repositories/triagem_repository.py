from sqlalchemy import func, select

from app.extensions import db
from app.models import MatchIdeiaDesafio, Triagem

# soma dos critérios; o esforço entra invertido (6 - esforço), pois quanto maior o esforço, menor a prioridade
_SOMA = (Triagem.impacto + Triagem.urgencia + Triagem.viabilidade
         + Triagem.alinhamento + (6 - Triagem.esforco))

def _consulta():
    return (select(Triagem, MatchIdeiaDesafio.id_desafio, MatchIdeiaDesafio.id_ideia)
            .join(MatchIdeiaDesafio, MatchIdeiaDesafio.id_match == Triagem.id_match))

def buscar_por_id(id_triagem):
    return db.session.execute(
        _consulta().where(Triagem.id_triagem == id_triagem)).first()

def listar(filtros, page, page_size):
    consulta = _consulta()

    if filtros.get("id_match"):
        consulta = consulta.where(Triagem.id_match == filtros["id_match"])
    if filtros.get("id_desafio"):
        consulta = consulta.where(MatchIdeiaDesafio.id_desafio == filtros["id_desafio"])
    if filtros.get("decisao"):
        consulta = consulta.where(Triagem.decisao == filtros["decisao"])

    total = db.session.scalar(
        select(func.count()).select_from(consulta.subquery()))

    if filtros.get("ordenar") == "pontuacao":
        consulta = consulta.order_by(_SOMA.desc(), Triagem.data_avaliacao.desc(), Triagem.id_triagem.desc())
    else:
        consulta = consulta.order_by(Triagem.data_avaliacao.desc(), Triagem.id_triagem.desc())

    consulta = consulta.limit(page_size).offset((page - 1) * page_size)
    return db.session.execute(consulta).all(), total

def adicionar(triagem):
    db.session.add(triagem)
    db.session.flush()
    return triagem
