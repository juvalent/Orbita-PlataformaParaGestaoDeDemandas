import hashlib
import json
import re

import pytest
import requests

from app.errors import IAIndisponivelError, IATimeoutError, NaoEncontradoError
from app.extensions import db
from app.models import (AiEmbedding, AiSugestao, Desafio, Ideia,
                        MatchIdeiaDesafio, Usuario)
from app.services import ia_match_service


class FakeResposta:
    def __init__(self, status=200, corpo=None):
        self.status_code, self._corpo = status, corpo or {}
        self.text = json.dumps(self._corpo)

    def json(self):
        return self._corpo


def _vetor(texto, dim=64):
    v = [0.0] * dim
    for palavra in re.findall(r"\w+", texto.lower()):
        v[int(hashlib.md5(palavra.encode()).hexdigest(), 16) % dim] += 1.0
    return v


class ProvedorFalso:
    def __init__(self):
        self.textos_embedding = 0
        self.chamadas_chat = 0
        self.falhas_chat = []
        self.conteudo_chat = None

    def __call__(self, url, json=None, headers=None, timeout=None):
        if url.endswith("/embeddings"):
            self.textos_embedding += len(json["input"])
            return FakeResposta(200, {"model": "emb-test", "data": [
                {"index": i, "embedding": _vetor(t)}
                for i, t in enumerate(json["input"])]})
        self.chamadas_chat += 1
        if self.falhas_chat:
            falha = self.falhas_chat.pop(0)
            if isinstance(falha, Exception):
                raise falha
            return FakeResposta(falha)
        conteudo = self.conteudo_chat or (
            '{"scoreCompatibilidade": 0.87, "justificativa": "Alinhado."}')
        return FakeResposta(200, {"model": "llama-test-2026", "choices": [
            {"message": {"content": conteudo}}]})


@pytest.fixture()
def provedor(monkeypatch):
    falso = ProvedorFalso()
    monkeypatch.setattr("app.services.ai_service_adapter.requests.post", falso)
    falso.esperas = []
    monkeypatch.setattr("app.services.ai_service_adapter.time.sleep",
                        falso.esperas.append)
    return falso


@pytest.fixture()
def cenario(app):
    with app.app_context():
        for t in (AiSugestao, MatchIdeiaDesafio, AiEmbedding, Ideia, Desafio,
                  Usuario):
            db.session.query(t).delete()
        u = Usuario(nome="Ana", email="ana@x.com", senha_hash="x")
        db.session.add(u)
        db.session.flush()
        d = Desafio(id_responsavel=u.id_usuario,
                    titulo="Automatizar a triagem de e-mails do atendimento",
                    descricao_problema="A equipe perde horas classificando "
                                       "e-mails manualmente no atendimento.",
                    area_demandante="Atendimento")
        db.session.add(d)
        db.session.flush()
        ids = {}
        for k, t, desc in [
            ("a", "Classificador automático de e-mails",
             "Classifica e-mails do atendimento automaticamente"),
            ("b", "Horta comunitária no terraço",
             "Plantar hortaliças e flores para relaxar"),
            ("c", "Robô de resposta para e-mails de clientes",
             "Bot que faz triagem e responde e-mails no atendimento")]:
            i = Ideia(id_autor=u.id_usuario, id_desafio=d.id_desafio,
                      titulo=t, descricao=desc)
            db.session.add(i)
            db.session.flush()
            ids[k] = i.id_ideia
        db.session.commit()
        yield {"usuario": u.id_usuario, "desafio": d.id_desafio, "ideias": ids}


def test_sugere_top_n_pendente_e_contrato(app, cenario, provedor):
    with app.app_context():
        r = ia_match_service.sugerir_matches(cenario["desafio"], 2,
                                             cenario["usuario"])
        assert len(r["sugestoes"]) == 2
        assert cenario["ideias"]["b"] not in {s["ideiaId"]
                                              for s in r["sugestoes"]}
        for chave in ("matchId", "ideiaId", "demandaId",
                      "scoreCompatibilidade", "justificativa", "statusMatch"):
            assert chave in r["sugestoes"][0]
        assert r["aiMetadata"]["humanInTheLoop"] is True
        assert r["aiMetadata"]["modeloVersao"] == "llama-test-2026"
        assert r["aiMetadata"]["grauConfianca"] == 87.0
        sug = db.session.query(AiSugestao).all()
        assert {s.status_revisao for s in sug} == {"PENDENTE"}


def test_dedupe_sha256_e_reindexacao_de_ideia_editada(app, cenario, provedor, monkeypatch):
    monkeypatch.setenv("AI_EMBEDDING_PROVIDER", "api")
    monkeypatch.setenv("AI_EMBEDDING_MODEL", "emb-test")
    with app.app_context():
        ia_match_service.sugerir_matches(cenario["desafio"], 1,
                                         cenario["usuario"])
        assert provedor.textos_embedding == 4    # desafio + 3 ideias
        ia_match_service.sugerir_matches(cenario["desafio"], 1,
                                         cenario["usuario"])
        assert provedor.textos_embedding == 4    # nada novo: hash igual

        ideia = db.session.get(Ideia, cenario["ideias"]["b"])
        ideia.descricao = "Agora classifica e-mails do atendimento com IA"
        db.session.commit()
        ia_match_service.sugerir_matches(cenario["desafio"], 1,
                                         cenario["usuario"])
        assert provedor.textos_embedding == 5    # só a editada


def test_timeout_504_nada_gravado(app, cenario, provedor):
    provedor.falhas_chat = [requests.Timeout()] * 5
    with app.app_context():
        with pytest.raises(IATimeoutError):
            ia_match_service.sugerir_matches(cenario["desafio"], 2,
                                             cenario["usuario"])
        assert db.session.query(AiSugestao).count() == 0
        assert db.session.query(MatchIdeiaDesafio).count() == 0


def test_retry_503_backoff_1s_2s_e_limite_de_2_retentativas(app, cenario,
                                                            provedor):
    with app.app_context():
        provedor.falhas_chat = [503, 503]
        ia_match_service.sugerir_matches(cenario["desafio"], 1,
                                         cenario["usuario"])
        assert provedor.esperas == [1, 2] and provedor.chamadas_chat == 3

        antes = provedor.chamadas_chat
        provedor.falhas_chat = [502, 503, 503]
        with pytest.raises(IAIndisponivelError):
            ia_match_service.sugerir_matches(cenario["desafio"], 1,
                                             cenario["usuario"])
        assert provedor.chamadas_chat == antes + 3

        antes = provedor.chamadas_chat
        provedor.falhas_chat = [401]             # 4xx não tem retry
        with pytest.raises(IAIndisponivelError):
            ia_match_service.sugerir_matches(cenario["desafio"], 1,
                                             cenario["usuario"])
        assert provedor.chamadas_chat == antes + 1


@pytest.mark.parametrize("conteudo", [
    "não é json",
    '{"scoreCompatibilidade": 1.7, "justificativa": "x"}',
    '{"scoreCompatibilidade": 0.5}',
])
def test_json_invalido_do_llm_e_descartado(app, cenario, provedor, conteudo):
    provedor.conteudo_chat = conteudo
    with app.app_context():
        with pytest.raises(IAIndisponivelError):
            ia_match_service.sugerir_matches(cenario["desafio"], 1,
                                             cenario["usuario"])
        assert db.session.query(AiSugestao).count() == 0


def test_match_manual_nao_e_sobrescrito(app, cenario, provedor):
    with app.app_context():
        m = MatchIdeiaDesafio(id_desafio=cenario["desafio"],
                              id_ideia=cenario["ideias"]["a"],
                              score_compatibilidade=0.1,
                              justificativa="humano", origem_match="manual",
                              status_match="PENDENTE")
        db.session.add(m)
        db.session.commit()
        id_match = m.id_match
        ia_match_service.sugerir_matches(cenario["desafio"], 3,
                                         cenario["usuario"])
        m = db.session.get(MatchIdeiaDesafio, id_match)
        assert (m.justificativa, m.score_compatibilidade) == ("humano", 0.1)


def test_desafio_inexistente(app, cenario, provedor):
    with app.app_context():
        with pytest.raises(NaoEncontradoError):
            ia_match_service.sugerir_matches(999999, 1, cenario["usuario"])


def test_embedding_local_sem_api_de_embeddings(app, cenario, provedor,
                                               monkeypatch):
    """Provedor local: vetores de 384 dims são completados até 1536."""
    from app.services import ai_service_adapter as mod

    class ModeloFalso:
        def embed(self, textos):
            for t in textos:
                yield _vetor(t, dim=384)

    monkeypatch.setenv("AI_EMBEDDING_PROVIDER", "local")
    monkeypatch.delenv("AI_EMBEDDING_MODEL", raising=False)
    monkeypatch.setattr(mod, "_carregar_modelo_local",
                        lambda nome: ModeloFalso())
    with app.app_context():
        r = ia_match_service.sugerir_matches(cenario["desafio"], 2,
                                             cenario["usuario"])
        assert len(r["sugestoes"]) == 2
        assert provedor.textos_embedding == 0     # nenhuma chamada de API
        emb = db.session.query(AiEmbedding).first()
        assert len(emb.vetor) == 1536
        assert emb.modelo_embedding == mod.MODELO_LOCAL_PADRAO