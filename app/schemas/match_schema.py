"""Validação de entrada da API de Match (vínculo Ideia × Desafio)."""

from marshmallow import EXCLUDE, Schema, fields, pre_load, validate

OBRIGATORIO = {
    "required": "Campo obrigatório.",
    "null": "Campo obrigatório.",
}


class _SchemaMatchBase(Schema):
    """Ignora campos desconhecidos e remove espaços das strings."""

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def normalizar_textos(self, dados, **kwargs):
        if isinstance(dados, dict):
            return {
                chave: valor.strip() if isinstance(valor, str) else valor
                for chave, valor in dados.items()
            }
        return dados


class MatchCriarSchema(_SchemaMatchBase):
    """Corpo de POST /matches: o Analista escolhe a ideia e o desafio."""

    id_ideia = fields.Int(
        required=True,
        strict=True,
        error_messages=OBRIGATORIO,
        validate=validate.Range(min=1, error="Informe uma ideia válida."),
    )
    id_desafio = fields.Int(
        required=True,
        strict=True,
        error_messages=OBRIGATORIO,
        validate=validate.Range(min=1, error="Informe um desafio válido."),
    )
    justificativa = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=5000, error="Aceita até 5000 caracteres."),
    )


class MatchFiltroSchema(_SchemaMatchBase):
    """Paginação e filtros de GET /matches."""

    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1, error="page deve ser maior ou igual a 1."),
    )
    page_size = fields.Int(
        load_default=10,
        validate=validate.Range(
            min=1, max=100, error="page_size deve estar entre 1 e 100."),
    )
    id_desafio = fields.Int(
        validate=validate.Range(min=1, error="Informe um desafio válido."))
    id_ideia = fields.Int(
        validate=validate.Range(min=1, error="Informe uma ideia válida."))
    status_match = fields.Str(validate=validate.Length(max=20))
