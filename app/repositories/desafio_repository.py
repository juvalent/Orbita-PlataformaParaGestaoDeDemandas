from sqlalchemy import func, or_, select

from app.extensions import db
from app.models import Desafio

def buscar_por_id(id_desafio):
    return db.session.get(Desafio, id_desafio)


def titulos_por_ids(ids):
    ids = set(ids)
    if not ids:
        return {}
    consulta = select(Desafio.id_desafio, Desafio.titulo).where(
        Desafio.id_desafio.in_(ids))
    return dict(db.session.execute(consulta).all())

def buscar_por_responsavel(id_responsavel):
    return db.session.scalar(select(Desafio).where(Desafio.id_responsavel == id_responsavel))

def buscar_todos():
    query = select(Desafio)
    return db.session.execute(query).scalars().all()

def listar(filtros, page, page_size):
    consulta = select(Desafio)

    if filtros.get("status"):
        consulta = consulta.where(Desafio.status == filtros["status"])
    if filtros.get("area"):
        consulta = consulta.where(Desafio.area_demandante == filtros["area"])
    if filtros.get("categoria"):
        consulta = consulta.where(Desafio.categoria == filtros["categoria"])
    if filtros.get("q"):
        termo = f"%{filtros['q'].strip()}%"
        consulta = consulta.where(or_(Desafio.titulo.ilike(termo),
                                      Desafio.descricao_problema.ilike(termo)))

    total = db.session.scalar(
        select(func.count()).select_from(consulta.subquery()))

    consulta = (consulta
                .order_by(Desafio.data_criacao.desc(), Desafio.id_desafio.desc())
                .limit(page_size)
                .offset((page - 1) * page_size))
    return list(db.session.scalars(consulta)), total

def cadastrar(desafio):
    db.session.add(desafio)
    db.session.flush()
    return desafio

def atualizar(desafio):
    db.session.add(desafio)
    db.session.flush()
    return desafio

def deletar(desafio):
    db.session.delete(desafio)
    db.session.flush()

def usuario_e_responsavel(id_desafio, id_usuario):
    consulta = select(Desafio.id_desafio).where(
        Desafio.id_desafio == id_desafio,
        Desafio.id_responsavel == id_usuario)
    return db.session.scalar(consulta) is not None
