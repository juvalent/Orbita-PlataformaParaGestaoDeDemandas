import os
import sys
import time

from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault("AI_MODEL_NAME", "openai/gpt-oss-20b")
os.environ.setdefault("AI_EMBEDDING_PROVIDER", "local")

from app import create_app
from app.errors import AppError
from app.extensions import db
from app.models import Desafio, Ideia, Usuario
from app.services import ai_service_adapter, ia_match_service

if not os.getenv("AI_API_KEY"):
    sys.exit("Defina AI_API_KEY (a chave da Groq) antes de rodar.")

app = create_app()
with app.app_context():
    db.create_all()

    print("1/4 Preparando o modelo de embeddings local (1ª vez baixa ~220 MB)...")
    t0 = time.time()
    try:
        ai_service_adapter.aquecer_modelo_local()
    except Exception as erro:
        sys.exit(f"ERRO ao preparar o modelo local: {erro}\n"
                 "Causas comuns: sem internet/proxy bloqueando huggingface.co, "
                 "pouco espaço em disco, ou fastembed não instalado.")
    print(f"    ok em {time.time() - t0:.1f}s")

    print("2/4 Criando dados de exemplo...")
    u = db.session.query(Usuario).filter_by(email="teste-ia@orbita.local").first()
    if u is None:
        u = Usuario(nome="Teste IA", email="teste-ia@orbita.local",
                    senha_hash="x")
        db.session.add(u)
        db.session.flush()
    d = db.session.query(Desafio).filter_by(
        titulo="Automatizar a triagem de e-mails do atendimento").first()
    if d is None:
        d = Desafio(id_responsavel=u.id_usuario,
                    titulo="Automatizar a triagem de e-mails do atendimento",
                    descricao_problema="A equipe perde horas classificando e-mails "
                                       "manualmente no atendimento ao cliente.",
                    area_demandante="Atendimento")
        db.session.add(d)
        db.session.flush()
        for t, desc in [
            ("Classificador automático de e-mails",
             "Modelo que classifica e-mails do atendimento por assunto."),
            ("Horta comunitária no terraço",
             "Plantar hortaliças e flores para os colaboradores relaxarem."),
            ("Robô de resposta para e-mails de clientes",
             "Bot que faz triagem e responde e-mails de clientes."),
            ("Campanha de reciclagem de papel",
             "Reduzir o consumo de papel nos escritórios.")]:
            db.session.add(Ideia(id_autor=u.id_usuario, id_desafio=d.id_desafio,
                                 titulo=t, descricao=desc))
    db.session.commit()

    print("3/4 Chamando a IA (embeddings + Groq)...")
    t0 = time.time()
    try:
        r = ia_match_service.sugerir_matches(d.id_desafio, 3, u.id_usuario)
    except AppError as erro:
        sys.exit(f"ERRO {erro.status_code}: {erro}\n"
                 "(se for 503/504, veja a chave, o modelo e a internet)")
    print(f"    ok em {time.time() - t0:.1f}s")

    print("4/4 Resultado:")
    for s in r["sugestoes"]:
        print(f"  - {s['ideiaTitulo']}  |  score {s['scoreCompatibilidade']}"
              f"  |  {s['statusMatch']}\n      {s['justificativa']}")
    print("aiMetadata:", r["aiMetadata"])
