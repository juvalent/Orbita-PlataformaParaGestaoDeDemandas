"""Testes HTTP de POST /api/v1/ia/matches/sugerir-ia (provedor de IA simulado)."""
import pytest
import requests
from flask_jwt_extended import create_access_token

from app.extensions import db, limiter
from app.models import AiSugestao, MatchIdeiaDesafio
from tests.test_ia_service import cenario, provedor  # noqa: F401  (fixtures)

URL_IA = "/api/v1/ia/matches/sugerir-ia"


def _cabecalho(app, id_usuario, perfis):
    with app.app_context():
        token = create_access_token(identity=str(id_usuario),
                                    additional_claims={"perfis": perfis})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def http(app, cenario):  # noqa: F811
    with app.app_context():
        limiter.reset()
    return app.test_client(), _cabecalho(app, cenario["usuario"], ["Analista/Hub"])


def test_200_contrato_e_tudo_pendente(http, cenario, provedor):  # noqa: F811
    client, auth = http
    r = client.post(URL_IA, headers=auth,
                    json={"id_desafio": cenario["desafio"], "top_n": 2})
    assert r.status_code == 200, r.get_json()
    corpo = r.get_json()
    assert len(corpo["sugestoes"]) == 2
    assert {s["statusMatch"] for s in corpo["sugestoes"]} == {"PENDENTE"}
    assert corpo["aiMetadata"]["humanInTheLoop"] is True


def test_sugestao_da_ia_e_validada_por_humano_na_rota_existente(
        http, app, cenario, provedor):  # noqa: F811
    client, auth = http
    r = client.post(URL_IA, headers=auth,
                    json={"id_desafio": cenario["desafio"], "top_n": 1})
    id_match = r.get_json()["sugestoes"][0]["matchId"]
    v = client.post(f"/api/v1/matches/{id_match}/validacao", headers=auth,
                    json={"decisao": "validar", "justificativa": "ok"})
    assert v.status_code == 200, v.get_json()
    assert v.get_json()["status_match"] == "VALIDADO"
    assert v.get_json()["origem_match"] == "ia"


def test_401_sem_token_403_colaborador_422_payload(http, app, cenario,
                                                   provedor):  # noqa: F811
    client, auth = http
    assert client.post(URL_IA, json={"id_desafio": 1}).status_code == 401
    colab = _cabecalho(app, cenario["usuario"], ["Colaborador"])
    assert client.post(URL_IA, headers=colab,
                       json={"id_desafio": cenario["desafio"]}).status_code == 403
    r = client.post(URL_IA, headers=auth, json={"top_n": 99})
    assert r.status_code == 422
    assert provedor.chamadas_chat == 0


def test_429_na_11a_requisicao_do_mesmo_usuario(http, cenario, provedor):  # noqa: F811
    client, auth = http
    for _ in range(10):
        assert client.post(URL_IA, headers=auth, json={
            "id_desafio": cenario["desafio"], "top_n": 1}).status_code == 200
    assert client.post(URL_IA, headers=auth, json={
        "id_desafio": cenario["desafio"], "top_n": 1}).status_code == 429


def test_504_timeout_nada_gravado_e_fluxo_manual_livre(http, app, cenario,
                                                       provedor):  # noqa: F811
    client, auth = http
    provedor.falhas_chat = [requests.Timeout()] * 5
    r = client.post(URL_IA, headers=auth,
                    json={"id_desafio": cenario["desafio"], "top_n": 2})
    assert r.status_code == 504
    with app.app_context():
        assert db.session.query(AiSugestao).count() == 0
        assert db.session.query(MatchIdeiaDesafio).count() == 0
    # o Match manual da equipe continua funcionando
    assert client.get("/api/v1/matches", headers=auth).status_code == 200
