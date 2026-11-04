from marshmallow import Schema, fields, validate, pre_load, EXCLUDE

OBRIGATORIO = {
                "required": "Campo obrigatório.",
                "null": "Campo obrigatório."
                }

STATUS_MATCH = ("PENDENTE", "VALIDADO", "DESCARTADO")
ORIGENS_MATCH = ("manual", "regra", "ia")


class MatchCriarSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id_desafio = fields.Int(required=True, strict=True, error_messages=OBRIGATORIO,
                            validate=validate.Range(min=1, error="Informe um id válido."))
    id_ideia = fields.Int(required=True, strict=True, error_messages=OBRIGATORIO,
                          validate=validate.Range(min=1, error="Informe um id válido."))
    justificativa = fields.Str(allow_none=True, validate=validate.Length(
        max=5000, error="Máximo de 5000 caracteres."))


class MatchValidacaoSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    decisao = fields.Str(required=True, error_messages=OBRIGATORIO,
                         validate=validate.OneOf(
                             ("validar", "descartar"),
                             error="Decisão inválida. Use: validar ou descartar."))
    justificativa = fields.Str(allow_none=True, validate=validate.Length(
        max=5000, error="Máximo de 5000 caracteres."))

    @pre_load
    def normalizar_decisao(self, dados, **kwargs):
        if isinstance(dados, dict) and isinstance(dados.get("decisao"), str):
            dados = {**dados, "decisao": dados["decisao"].strip().lower()}
        return dados


class MatchSugestaoSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id_desafio = fields.Int(required=True, strict=True, error_messages=OBRIGATORIO,
                            validate=validate.Range(min=1, error="Informe um id válido."))
    limite = fields.Int(load_default=5, strict=True, validate=validate.Range(
        min=1, max=20, error="limite deve estar entre 1 e 20."))


class MatchFiltroSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    page = fields.Int(load_default=1, validate=validate.Range(
        min=1, error="page deve ser maior ou igual a 1."))
    page_size = fields.Int(load_default=10, validate=validate.Range(
        min=1, max=100, error="page_size deve estar entre 1 e 100."))
    id_desafio = fields.Int(validate=validate.Range(min=1, error="Informe um id válido."))
    id_ideia = fields.Int(validate=validate.Range(min=1, error="Informe um id válido."))
    status_match = fields.Str(validate=validate.OneOf(
        STATUS_MATCH, error="Status inválido. Use: " + ", ".join(STATUS_MATCH) + "."))
    origem_match = fields.Str(validate=validate.OneOf(
        ORIGENS_MATCH, error="Origem inválida. Use: " + ", ".join(ORIGENS_MATCH) + "."))
