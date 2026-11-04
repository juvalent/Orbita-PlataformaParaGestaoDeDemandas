from marshmallow import Schema, fields, validate, pre_load, EXCLUDE

OBRIGATORIO = {
                "required": "Campo obrigatório.",
                "null": "Campo obrigatório."
                }

STATUS_DESAFIO = ("aberto", "em_triagem", "resolvido", "arquivado")


def _max(n):
    return validate.Length(max=n, error=f"Máximo de {n} caracteres.")


class DesafioSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(allow_none=True, validate=_max(100),
                         error_messages={"invalid": "E-mail inválido."})
    titulo = fields.Str(required=True, validate=_max(150),
                        error_messages=OBRIGATORIO)
    descricao_problema = fields.Str(required=True, error_messages=OBRIGATORIO)
    area_demandante = fields.Str(required=True, validate=_max(100),
                                 error_messages=OBRIGATORIO)
    quem_afeta = fields.Str(allow_none=True, validate=_max(200))
    impacto = fields.Str(allow_none=True, validate=_max(100))
    urgencia = fields.Str(allow_none=True, validate=_max(100))
    categoria = fields.Str(allow_none=True, validate=_max(100))
    status = fields.Str(
        load_default="aberto",
        validate=validate.OneOf(
            STATUS_DESAFIO,
            error="Status inválido. Use: " + ", ".join(STATUS_DESAFIO) + "."))

    @pre_load
    def normalizar_status(self, dados, **kwargs):
        if isinstance(dados, dict) and isinstance(dados.get("status"), str):
            dados = {**dados, "status": dados["status"].strip().lower()}
        return dados


class DesafioFiltroSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    page = fields.Int(load_default=1, validate=validate.Range(
        min=1, error="page deve ser maior ou igual a 1."))
    page_size = fields.Int(load_default=10, validate=validate.Range(
        min=1, max=100, error="page_size deve estar entre 1 e 100."))
    status = fields.Str(validate=validate.OneOf(
        STATUS_DESAFIO,
        error="Status inválido. Use: " + ", ".join(STATUS_DESAFIO) + "."))
    area = fields.Str(validate=_max(100))
    categoria = fields.Str(validate=_max(100))
    q = fields.Str(validate=_max(100))
