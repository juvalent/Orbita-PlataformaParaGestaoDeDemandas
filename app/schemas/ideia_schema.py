"""Schemas de validação e serialização para a entidade Ideia."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, pre_load, validate, validates_schema


OBRIGATORIO = {
    "required": "Campo obrigatório.",
    "null": "Campo obrigatório.",
}


class _SchemaIdeiaBase(Schema):
    """Configuração comum aos schemas de entrada: ignora campos desconhecidos."""

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def normalizar_textos(self, dados, **kwargs):
        """Remove espaços excedentes das extremidades dos textos enviados."""
        if isinstance(dados, dict):
            return {
                chave: valor.strip() if isinstance(valor, str) else valor
                for chave, valor in dados.items()
            }
        return dados


class IdeiaCriarSchema(_SchemaIdeiaBase):
    """Valida o payload necessário para cadastrar uma ideia."""

    id_desafio = fields.Int(
        required=True,
        strict=True,
        error_messages=OBRIGATORIO,
        validate=validate.Range(min=1, error="Informe um desafio válido."),
    )
    titulo = fields.Str(
        required=True,
        error_messages=OBRIGATORIO,
        validate=validate.Length(
            min=3,
            max=150,
            error="O título deve ter entre 3 e 150 caracteres.",
        ),
    )
    descricao = fields.Str(
        required=True,
        error_messages=OBRIGATORIO,
        validate=validate.Length(
            min=10,
            max=5000,
            error="A descrição deve ter entre 10 e 5000 caracteres.",
        ),
    )
    area = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=100, error="A área aceita até 100 caracteres."),
    )
    categoria = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=100, error="A categoria aceita até 100 caracteres."),
    )
    problema_resolvido = fields.Str(
        load_default=None, allow_none=True,
        validate=validate.Length(max=5000, error="Aceita até 5000 caracteres."))
    beneficio_esperado = fields.Str(
        load_default=None, allow_none=True,
        validate=validate.Length(max=5000, error="Aceita até 5000 caracteres."))


class IdeiaAtualizarSchema(_SchemaIdeiaBase):
    """Valida PATCH parcial sem permitir alterar código, autor ou status."""

    id_desafio = fields.Int(
        strict=True,
        allow_none=False,
        validate=validate.Range(min=1, error="Informe um desafio válido."),
    )
    titulo = fields.Str(
        validate=validate.Length(
            min=3,
            max=150,
            error="O título deve ter entre 3 e 150 caracteres.",
        ),
    )
    descricao = fields.Str(
        validate=validate.Length(
            min=10,
            max=5000,
            error="A descrição deve ter entre 10 e 5000 caracteres.",
        ),
    )
    area = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100, error="A área aceita até 100 caracteres."),
    )
    categoria = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100, error="A categoria aceita até 100 caracteres."),
    )
    problema_resolvido = fields.Str(
        allow_none=True,
        validate=validate.Length(max=5000, error="Aceita até 5000 caracteres."))
    beneficio_esperado = fields.Str(
        allow_none=True,
        validate=validate.Length(max=5000, error="Aceita até 5000 caracteres."))

    @validates_schema
    def exigir_campo_atualizavel(self, dados, **kwargs):
        """Impede PATCH vazio ou composto apenas por campos desconhecidos."""
        if not dados:
            raise ValidationError(
                {"_schema": ["Informe ao menos um campo válido para atualizar."]}
            )


class IdeiaFiltroSchema(_SchemaIdeiaBase):
    """Valida paginação, filtros e busca textual da listagem de ideias."""

    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1, error="page deve ser maior ou igual a 1."),
    )
    page_size = fields.Int(
        load_default=10,
        validate=validate.Range(
            min=1,
            max=100,
            error="page_size deve estar entre 1 e 100.",
        ),
    )
    status = fields.Str(validate=validate.Length(max=30))
    area = fields.Str(validate=validate.Length(max=100))
    categoria = fields.Str(validate=validate.Length(max=100))
    q = fields.Str(validate=validate.Length(max=100))
    id_desafio = fields.Int(
        validate=validate.Range(min=1, error="Informe um desafio válido."))
    # minhas=true: só as ideias de autoria do usuário logado ("Minhas Ideias")
    minhas = fields.Bool(load_default=False)


class IdeiaResponseSchema(Schema):
    """Define o formato público das respostas da API para uma ideia."""

    id_ideia = fields.Int(dump_only=True)
    codigo = fields.Str(dump_only=True, allow_none=True)
    id_autor = fields.Int(dump_only=True)
    id_desafio = fields.Int(dump_only=True)
    desafio_titulo = fields.Str(dump_only=True, allow_none=True)
    titulo = fields.Str(dump_only=True)
    descricao = fields.Str(dump_only=True)
    area = fields.Str(dump_only=True, allow_none=True)
    categoria = fields.Str(dump_only=True, allow_none=True)
    problema_resolvido = fields.Str(dump_only=True, allow_none=True)
    beneficio_esperado = fields.Str(dump_only=True, allow_none=True)
    status = fields.Str(dump_only=True)
    data_criacao = fields.DateTime(format="iso", dump_only=True, allow_none=True)
    data_atualizacao = fields.DateTime(format="iso", dump_only=True, allow_none=True)


# Nomes equivalentes do guia técnico, mantidos para facilitar integração futura.
IdeiaCreateSchema = IdeiaCriarSchema
IdeiaUpdateSchema = IdeiaAtualizarSchema
