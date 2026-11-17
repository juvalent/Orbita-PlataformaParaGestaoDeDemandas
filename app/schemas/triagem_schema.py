from marshmallow import Schema, fields, validate, pre_load, EXCLUDE

OBRIGATORIO = {
                "required": "Campo obrigatório.",
                "null": "Campo obrigatório."
                }

DECISOES_TRIAGEM = ("aprovada", "reprovada", "ajustes")
ORDENACOES_TRIAGEM = ("recentes", "pontuacao")


def _nota():
    return fields.Int(required=True, strict=True, error_messages=OBRIGATORIO,
                      validate=validate.Range(min=1, max=5, error="A nota deve ser de 1 a 5."))


class TriagemCriarSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id_match = fields.Int(required=True, strict=True, error_messages=OBRIGATORIO,
                          validate=validate.Range(min=1, error="Informe um id válido."))
    impacto = _nota()
    urgencia = _nota()
    viabilidade = _nota()
    alinhamento = _nota()
    esforco = _nota()
    parecer = fields.Str(required=True, error_messages=OBRIGATORIO,
                         validate=validate.Length(min=5, max=5000,
                                                  error="O parecer deve ter entre 5 e 5000 caracteres."))
    decisao = fields.Str(allow_none=True, validate=validate.OneOf(
        DECISOES_TRIAGEM, error="Decisão inválida. Use: " + ", ".join(DECISOES_TRIAGEM) + "."))

    @pre_load
    def normalizar_textos(self, dados, **kwargs):
        if isinstance(dados, dict):
            dados = {**dados}
            if isinstance(dados.get("parecer"), str):
                dados["parecer"] = dados["parecer"].strip()
            if isinstance(dados.get("decisao"), str):
                dados["decisao"] = dados["decisao"].strip().lower()
        return dados


class TriagemFiltroSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    page = fields.Int(load_default=1, validate=validate.Range(
        min=1, error="page deve ser maior ou igual a 1."))
    page_size = fields.Int(load_default=10, validate=validate.Range(
        min=1, max=100, error="page_size deve estar entre 1 e 100."))
    id_match = fields.Int(validate=validate.Range(min=1, error="Informe um id válido."))
    id_desafio = fields.Int(validate=validate.Range(min=1, error="Informe um id válido."))
    decisao = fields.Str(validate=validate.OneOf(
        DECISOES_TRIAGEM, error="Decisão inválida. Use: " + ", ".join(DECISOES_TRIAGEM) + "."))
    ordenar = fields.Str(load_default="recentes", validate=validate.OneOf(
        ORDENACOES_TRIAGEM, error="Ordenação inválida. Use: " + ", ".join(ORDENACOES_TRIAGEM) + "."))
