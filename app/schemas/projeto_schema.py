from datetime import date

from marshmallow import EXCLUDE, Schema, ValidationError, fields, pre_load, validate, validates_schema


ETAPAS_KANBAN = (
    "Aprovado",
    "Planejamento",
    "Em Desenvolvimento",
    "Em Teste",
    "Concluído",
)


class _ProjetoBaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    @pre_load
    def normalizar_textos(self, dados, **kwargs):
        if isinstance(dados, dict):
            return {chave: valor.strip() if isinstance(valor, str) else valor
                    for chave, valor in dados.items()}
        return dados


class ProjetoCriarSchema(_ProjetoBaseSchema):
    id_match = fields.Int(required=True, strict=True,
                          validate=validate.Range(min=1, error="Informe um match válido."))
    titulo = fields.Str(validate=validate.Length(min=3, max=150))
    descricao = fields.Str(allow_none=True, validate=validate.Length(max=5000))
    id_responsavel = fields.Int(strict=True, validate=validate.Range(min=1))
    data_prazo = fields.Date(allow_none=True)


class ProjetoAtualizarSchema(_ProjetoBaseSchema):
    titulo = fields.Str(validate=validate.Length(min=3, max=150))
    descricao = fields.Str(allow_none=True, validate=validate.Length(max=5000))
    id_responsavel = fields.Int(strict=True, validate=validate.Range(min=1))
    data_prazo = fields.Date(allow_none=True)

    @validates_schema
    def exigir_campo(self, dados, **kwargs):
        if not dados:
            raise ValidationError({"_schema": ["Informe ao menos um campo válido para atualizar."]})


class ProjetoKanbanSchema(_ProjetoBaseSchema):
    etapa = fields.Str(required=True, validate=validate.OneOf(
        ETAPAS_KANBAN, error="Etapa inválida. Use: " + ", ".join(ETAPAS_KANBAN) + "."))


class ProjetoFiltroSchema(_ProjetoBaseSchema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    page_size = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    status_kanban = fields.Str(validate=validate.OneOf(ETAPAS_KANBAN))
    id_responsavel = fields.Int(validate=validate.Range(min=1))
    id_ideia = fields.Int(validate=validate.Range(min=1))
    q = fields.Str(validate=validate.Length(max=100))
