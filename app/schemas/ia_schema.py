from marshmallow import EXCLUDE, Schema, fields, validate

OBRIGATORIO = {"required": "Campo obrigatório.", "null": "Campo obrigatório."}


class SugerirMatchSchema(Schema):
    """Payload de POST /api/v1/ia/matches/sugerir-ia."""

    class Meta:
        unknown = EXCLUDE

    id_desafio = fields.Int(required=True, strict=True,
                            error_messages=OBRIGATORIO,
                            validate=validate.Range(min=1, error="Informe um desafio válido."))
    top_n = fields.Int(load_default=5, strict=True,
                       validate=validate.Range(min=1, max=10,
                                               error="top_n deve estar entre 1 e 10."))
