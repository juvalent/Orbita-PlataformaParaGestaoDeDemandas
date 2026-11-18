# 🪐 Órbita — Documentação e Visão Geral do Backend

> **Documento gerado em:** 18 de Novembro de 2026  
> **Repositório:** `Orbita-PlataformaParaGestaoDeDemandas` (Squad 47 — Residência Tecnológica Porto Digital / Banco do Brasil)  
> **Objetivo:** Mapeamento arquitetural do backend, inventário completo de branches, descrição do que foi desenvolvido em cada uma e identificação da versão mais estável e atualizada.

---

## 1. Visão Geral da Arquitetura do Backend

O backend da plataforma **Órbita** foi concebido em Python utilizando o framework **Flask**, adotando um padrão arquitetural em camadas desacopladas (*Layered Architecture* / *Controller-Service-Repository*) com persistência relacional via **SQLAlchemy** e banco de dados **PostgreSQL**.

### 1.1. Stack Tecnológica
* **Linguagem & Runtime:** Python 3.12+
* **Framework Web:** Flask 3.1.3
* **ORM & Banco de Dados:** SQLAlchemy 2.0.50 / Flask-SQLAlchemy 3.1.1 + PostgreSQL (`psycopg2-binary`)
* **Autenticação & Segurança:** Flask-JWT-Extended 4.7.4 (tokens JWT com expiração de 2h) + Werkzeug Security (hashing de senhas com PBKDF2/SHA256)
* **Segurança Operacional:** Flask-Limiter (Rate limiting contra força bruta em rotas críticas) + Flask-CORS
* **Validação e Serialização:** Marshmallow 4.3.1 + marshmallow-sqlalchemy 1.5.0
* **Configuração:** `python-dotenv`

### 1.2. Organização de Diretórios e Camadas

```
app/
├── __init__.py             # Application Factory (create_app), inicialização de extensões e blueprints
├── errors.py               # Exceções customizadas de domínio
├── controllers/            # Controladores HTTP: extraem parâmetros, chamam services e gerenciam status HTTP
│   ├── auth_controller.py
│   ├── desafio_controller.py
│   ├── ideia_controller.py
│   ├── match_controller.py
│   └── triagem_controller.py
├── services/               # Regras de negócio, cálculos, validações de domínio e orquestração
│   ├── auth_service.py
│   ├── desafio_service.py
│   ├── ideia_service.py
│   ├── match_service.py
│   └── triagem_service.py
├── repositories/           # Abstração de acesso a dados (consultas SQLAlchemy e persistência)
│   ├── desafio_repository.py
│   ├── ideia_repository.py
│   ├── match_repository.py
│   ├── perfil_repository.py
│   ├── triagem_repository.py
│   └── usuario_repository.py
├── models/                 # Modelos relacionais ORM (entidades do banco de dados)
│   ├── auditoria.py
│   ├── desafio.py
│   ├── ideia.py
│   ├── match_ideia_desafio.py
│   ├── movimentacao_kanban.py
│   ├── mvp.py
│   ├── perfil.py
│   ├── projeto.py
│   ├── resultado.py
│   ├── triagem.py
│   ├── usuario.py
│   └── usuario_perfil.py
├── schemas/                # Schemas de validação e serialização JSON (Marshmallow)
│   ├── auth_schema.py
│   ├── desafio_schema.py
│   ├── ideia_schema.py
│   ├── match_schema.py
│   └── triagem_schema.py
├── routes/                 # Definição dos Blueprints REST, rotas e filtros de autenticação/rate-limit
│   ├── auth_route.py
│   ├── desafio_routes.py
│   ├── health_route.py
│   ├── ideia_route.py
│   ├── match_route.py
│   └── triagem_route.py
├── middlewares/            # Tratamento centralizado de erros e exceções HTTP
│   └── error_handler.py
└── extensions/             # Instâncias globais de extensões (db, jwt, limiter)
    └── __init__.py
```

### 1.3. Principais Módulos e Endpoints da API (`/api/v1`)

| Módulo | Prefixo | Endpoints Principais | Descrição e Regras |
| :--- | :--- | :--- | :--- |
| **Health** | `/api/v1/health` | `GET /` | Health check da aplicação para monitoramento. |
| **Autenticação** | `/api/v1/auth` | `POST /register`<br>`POST /login`<br>`GET /me` | Cadastro e login de usuários com JWT, proteção de taxa (Rate Limit de 5/min no register e 10/min no login) e consulta ao perfil autenticado. |
| **Desafios** | `/api/v1/desafios` | `GET /`<br>`POST /`<br>`GET /:id`<br>`PUT, PATCH /:id`<br>`DELETE /:id` | Gestão de demandas corporativas estratégicas (desafios). Exige autenticação e validação de permissões RBAC. |
| **Ideias** | `/api/v1/ideias` | `GET /`<br>`POST /`<br>`GET /:id`<br>`PUT, PATCH /:id`<br>`DELETE /:id`<br>`POST /:id/aprovar`<br>`POST /:id/arquivar` | Ciclo de vida de submissão de ideias/soluções, vinculação a desafios existentes e fluxos de aprovação/arquivamento. |
| **Match** | `/api/v1/matches` | `GET /`<br>`POST /`<br>`GET /:id`<br>`POST /sugerir-regra`<br>`POST /:id/validacao` | Conexão entre ideias submetidas e desafios corporativos por regras de negócio e validação por analistas. |
| **Triagem** | `/api/v1/triagens` | `GET /`<br>`POST /`<br>`GET /:id` | Avaliação, pontuação, classificação e movimentação da demanda no funil de inovação. |

---

## 2. Inventário e Análise Detalhada de Todas as Branches

Abaixo está o mapeamento de todas as branches presentes no repositório, incluindo data aproximada do último commit, o que foi desenvolvido e o status em relação à árvore principal (`main`), sem atribuições nominais individuais.

### 2.1. Tabela Resumo das Branches

| Branch | Última Atualização | Relação com `main` | Status do Desenvolvimento |
| :--- | :--- | :--- | :--- |
| **`main`** *(local & origin)* | ~18 horas atrás | **Base Oficial (Head)** | **Mais Estável e Consolidada** |
| **`remotes/origin/Triagem`** | ~18 horas atrás | Totalmente integrada (PR #9) | Concluída / Mergeada |
| **`remotes/origin/desafios/ludmilla`** | ~13 dias atrás | Totalmente integrada (PR #8) | Concluída / Mergeada |
| **`remotes/origin/correcoes-ideia`** | ~2 semanas atrás | Totalmente integrada (PR #7) | Concluída / Mergeada |
| **`remotes/origin/match`** | ~9 dias atrás | Totalmente integrada (via Triagem) | Concluída / Mergeada |
| **`remotes/origin/feat/crud-ideias`** | ~4 semanas atrás | Totalmente integrada (PR #6) | Concluída / Mergeada |
| **`remotes/origin/backendddd`** | ~5 semanas atrás | Totalmente integrada (via PR #5) | Histórica / Obsoleta |
| **`remotes/origin/models`** | ~5 semanas atrás | Totalmente integrada (PR #3/PR #4) | Concluída / Mergeada |
| **`remotes/origin/feat/health-test-endpoint`** | ~6 semanas atrás | Totalmente integrada (PR #2) | Concluída / Mergeada |
| **`remotes/origin/ratelimiter-auth`** | ~4 semanas atrás | Alterações aplicadas na `main` | Branch avulsa (obsoleta) |
| **`remotes/origin/feat/match-analista`** | ~7 horas atrás | 1 commit à frente da `main` | **Em Andamento (WIP)** |
| **`remotes/origin/feat/ia-match`** | ~30 minutos atrás | 1 commit à frente da `main` | **Em Andamento (WIP)** |

---

### 2.2. Detalhamento do que foi Desenvolvido em Cada Branch

#### 1. `main` (Branch Principal)
* **Objetivo:** Código-fonte oficial consolidado do backend.
* **O que contém:**
  * Integração completa de todos os Pull Requests (#2 ao #9).
  * Application Factory Flask, CORS, configuração de variáveis de ambiente.
  * Todas as entidades do banco em SQLAlchemy (`models/`).
  * Autenticação completa via JWT com hashing de senha e controle de rotas por perfis.
  * Proteção por Rate Limiting nas rotas públicas de autenticação.
  * CRUD completo de Ideias e Desafios.
  * Módulo completo de Triagem (avaliação, pontuação e movimentação).
  * Módulo inicial de Match (sugestão e validação).

#### 2. `remotes/origin/feat/health-test-endpoint`
* **O que foi desenvolvido:**
  * Criação da estrutura inicial da fábrica da aplicação Flask (`app/__init__.py`).
  * Configuração do `.gitignore` e `requirements.txt`.
  * Criação da rota `/api/v1/health` para testes de disponibilidade e conectividade.
  * Ajustes de CORS.
* **Status:** Mergeada na `main` através do PR #2.

#### 3. `remotes/origin/models`
* **O que foi desenvolvido:**
  * Criação da modelagem relacional de todas as entidades do banco de dados:
    * `Usuario`, `Perfil`, `UsuarioPerfil`, `Desafio`, `Ideia`, `MatchIdeiaDesafio`, `Triagem`, `MovimentacaoKanban`, `MVP`, `Projeto`, `Resultado`, `Auditoria`.
  * Configuração de chaves estrangeiras, relacionamentos e tipos de dados no SQLAlchemy.
* **Status:** Mergeada na `main` através dos PRs #3 e #4.

#### 4. `remotes/origin/backendddd`
* **O que foi desenvolvido:**
  * Branch intermediária de integração durante o desenvolvimento inicial do backend.
  * Integração da autenticação e registro de usuário com os modelos do banco.
  * Atualizações no arquivo de inicialização `run.py`.
* **Status:** Totalmente absorvida pelo histórico da `main`.

#### 5. `remotes/origin/ratelimiter-auth`
* **O que foi desenvolvido:**
  * Implementação de rate limiting com Flask-Limiter nas rotas de login e cadastro.
  * Tratamento de erro 429 (Too Many Requests) no middleware de erros.
* **Status:** O commit foi aplicado diretamente na linha do tempo principal (commit `8fa094b`), tornando essa branch específica obsoleta.

#### 6. `remotes/origin/feat/crud-ideias`
* **O que foi desenvolvido:**
  * Implementação da camada completa de Ideias: `ideia_controller.py`, `ideia_service.py`, `ideia_repository.py`, `ideia_schema.py` e `ideia_route.py`.
  * Adição do campo `id_desafio` ao modelo de ideias para permitir associação direta.
  * Integração das primeiras rotas da feature de desafios.
* **Status:** Mergeada na `main` através do PR #6.

#### 7. `remotes/origin/correcoes-ideia`
* **O que foi desenvolvido:**
  * Padronização de endpoints para o padrão RESTful (`/api/v1/...`).
  * Tratamento e refinamento de mensagens de erro e exceções.
  * Adição de verificações de segurança e controle de permissões por perfil nas rotas de desafio.
  * Adição da rota de atualização (`PUT`/`PATCH`) para desafios.
* **Status:** Mergeada na `main` através do PR #7.

#### 8. `remotes/origin/desafios/ludmilla`
* **O que foi desenvolvido:**
  * Refatoração arquitetural para eliminar arquivos legados: exclusão da pasta duplicada `controllers/` que residia fora de `app/`.
  * Sincronização e resolução de conflitos com a `main`.
* **Status:** Mergeada na `main` através do PR #8.

#### 9. `remotes/origin/match`
* **O que foi desenvolvido:**
  * Primeira implementação do CRUD de Match (`MatchIdeiaDesafio`).
  * Regras de negócio de compatibilidade entre ideias e desafios (`match_service.py`).
  * Schemas de validação de match (`match_schema.py`).
* **Status:** Incorporada à `main` durante a finalização da Triagem.

#### 10. `remotes/origin/Triagem`
* **O que foi desenvolvido:**
  * Estruturação completa do fluxo de Triagem:
    * Criação de `triagem_controller.py`, `triagem_service.py`, `triagem_repository.py` e `triagem_schema.py`.
    * Endpoints de registro de triagem, listagem e busca por ID.
    * Integração de regras de triagem com a entidade `MovimentacaoKanban`.
    * Inclusão do rate limiter consolidado nas rotas de autenticação.
* **Status:** Mergeada na `main` através do PR #9 há aproximadamente 18 horas.

#### 11. `remotes/origin/feat/match-analista`
* **Última modificação:** 18 de Novembro de 2026, 07:48 (há ~7 horas)
* **O que foi desenvolvido:**
  * Adição e refatoração dos endpoints de Match focados na visão e atuação do perfil Analista/Hub:
    * `GET /api/v1/matches` (listagem com filtros)
    * `POST /api/v1/matches` (criação de vínculo manual entre ideia e desafio)
    * `GET /api/v1/matches/<id>` (consulta detalhada do match)
  * Modificações substanciais em `match_controller.py`, `match_service.py`, `match_repository.py`, `match_route.py` e `match_schema.py`.
* **Status atual:** **Em desenvolvimento (WIP)**. Partiu da `main` atualizada (após PR #9), está 1 commit à frente e ainda não foi submetida/aprovada via Pull Request.

#### 12. `remotes/origin/feat/ia-match`
* **Última modificação:** 18 de Novembro de 2026, 14:01 (há ~30 minutos)
* **O que foi desenvolvido:**
  * Criação do ecossistema de Inteligência Artificial para match semântico automatizado:
    * **Novos modelos:** `AIEmbedding`, `AIFeedback`, `AISugestao` (em `app/models/`).
    * **Novo repositório:** `AIRepository` (em `app/repositories/ai_repository.py`) para persistência de vetores e sugestões.
    * **Novos serviços:** `AIServiceAdapter` e `IAMatchService` (em `app/services/`) para cálculo de similaridade semântica e integração com APIs de embeddings.
    * **Testes automatizados:** `tests/test_ia_service.py` e `tests/conftest.py`.
    * **Novas dependências:** Inclusão de bibliotecas de IA/embeddings no `requirements.txt`.
* **Status atual:** **Em desenvolvimento (WIP)**. Partiu da `main` atualizada (após PR #9), está 1 commit à frente e aguarda validação, testes integrados e Pull Request.

---

## 3. Qual Branch Contém a Versão Mais Estável e Atualizada?

### Conclusão: A branch `main` (ou `origin/main`)

A branch que contém a **versão mais estável e oficial do backend é a `main`**.

### Justificativas Técnicas:

1. **Estabilidade Comprovada:**
   * A branch `main` é o ponto de convergência de **todos os 9 Pull Requests concluídos**.
   * Não possui código órfão ou funcionalidades pela metade.
   * As dependências do `requirements.txt` estão consolidadas e sem bibliotecas experimentais de IA adicionadas recentemente.

2. **Abrangência de Funcionalidades Concluídas:**
   * Possui todos os módulos fundamentais do MVP em pleno funcionamento integrado:
     1. Autenticação e Autorização (JWT + RBAC);
     2. Proteção contra força bruta (Rate Limiting);
     3. Gestão completa de Desafios;
     4. Gestão completa de Ideias;
     5. Triagem e Priorização (incorporada há 18 horas via PR #9);
     6. Estrutura base de Matches.

3. **Situação das Branches com Código Mais Recente (`feat/ia-match` e `feat/match-analista`):**
   * Ambas foram criadas **hoje (18/11)** e partiram diretamente do último commit da `main`.
   * Embora contenham código mais recente em termos de horário:
     * A branch `feat/match-analista` refatora a camada de matches e precisa de homologação dos endpoints pelo time.
     * A branch `feat/ia-match` introduz novos modelos de dados, repositórios e serviços de IA que ainda precisam de migração de banco e testes em ambiente compartilhado.
   * **Nenhuma das duas foi mergeada ou revisada via Pull Request**, portanto representam *trabalhos em andamento (WIP)* e não a versão estável oficial.

---

## 4. Recomendações Técnicas para o Fluxo de Trabalho da Equipe

1. **Próximos Merges para a `main`:**
   * Abrir e revisar o Pull Request da branch `feat/match-analista` para consolidar os endpoints do perfil Analista.
   * Abrir o Pull Request da branch `feat/ia-match` após garantir que as tabelas de IA (`ai_embedding`, `ai_feedback`, `ai_sugestao`) foram integradas ao script de criação de tabelas (`create_tables.py` ou migrações Alembic).
2. **Higienização do Repositório (Housekeeping):**
   * As branches remotas `Triagem`, `desafios/ludmilla`, `correcoes-ideia`, `match`, `feat/crud-ideias`, `models`, `feat/health-test-endpoint`, `backendddd` e `ratelimiter-auth` já cumpriram seu propósito e estão 100% integradas à `main`. Podem ser deletadas no GitHub para manter a lista de branches limpa e organizada.
