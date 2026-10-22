from marshmallow import Schema, fields, validate, EXCLUDE

OBRIGATORIO = {
                "required": "Campo obrigatório.",
                "null": "Campo obrigatório."
                }

class DesafioSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(
        required=True, validate=validate.Length(max=100),
        error_messages={**OBRIGATORIO, "invalid": "E-mail inválido."})
    titulo = fields.Str(required=True, validate=validate.Length(max=150),
                        error_messages=OBRIGATORIO)
    descricao_problema = fields.Str(required=True, error_messages=OBRIGATORIO)
    area_demandante = fields.Str(required=True, validate=validate.Length(max=100),
                        error_messages=OBRIGATORIO)
    quem_afeta = fields.Str(allow_none=True, validate=validate.Length(max=200))
    impacto = fields.Str(allow_none=True, validate=validate.Length(max=100))
    urgencia = fields.Str(allow_none=True, validate=validate.Length(max=100))
    categoria = fields.Str(allow_none=True, validate=validate.Length(max=100))
    status = fields.Str(required=True, validate=validate.Length(max=30)) # adicionar validação de status diferentes

