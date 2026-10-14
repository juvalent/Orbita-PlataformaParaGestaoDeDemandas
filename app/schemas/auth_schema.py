from marshmallow import Schema, fields, validate, EXCLUDE

OBRIGATORIO = {"required": "Campo obrigatório.",
               "null": "Campo obrigatório."}


class RegistroSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # ignora campos que não existem no schema

    nome = fields.Str(
        required=True, error_messages=OBRIGATORIO,
        validate=validate.Length(min=2, max=100,
                                 error="Nome deve ter de 2 a 100 caracteres."))
    email = fields.Email(
        required=True, validate=validate.Length(max=100),
        error_messages={**OBRIGATORIO, "invalid": "E-mail inválido."})
    senha = fields.Str(
        required=True, load_only=True, error_messages=OBRIGATORIO,
        validate=validate.Length(min=6, max=72,
                                 error="Senha deve ter de 6 a 72 caracteres."))
    area = fields.Str(load_default=None, allow_none=True,
                      validate=validate.Length(max=100))
    perfil = fields.Str(
        load_default="colaborador",
        validate=validate.OneOf(
            ["colaborador", "gestor", "analista"],
            error="Perfil deve ser: colaborador, gestor ou analista."))


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(
        required=True,
        error_messages={**OBRIGATORIO, "invalid": "E-mail inválido."})
    senha = fields.Str(required=True, error_messages=OBRIGATORIO)
