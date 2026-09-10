# 🪐 Órbita — Conectando ideias, pessoas e resultados (Backend)

> Sistema de Gestão de Demandas de Inovação

**Status: Em construção — MVP em desenvolvimento**

O **Órbita** é uma plataforma para gestão de demandas de inovação, criada para organizar e acompanhar iniciativas desde a identificação de uma necessidade até sua avaliação, desenvolvimento, validação e acompanhamento dos resultados.

O projeto está sendo desenvolvido no contexto da **Residência Tecnológica do Porto Digital**, pela **Squad 47**, em parceria com o **Banco do Brasil**, que atua como cliente e parceiro do projeto.

---

## Sobre o projeto

O Órbita tem como objetivo centralizar o processo de inovação em uma única plataforma, permitindo que demandas, ideias e iniciativas sejam registradas, avaliadas, priorizadas e acompanhadas de forma estruturada.

A plataforma busca facilitar a comunicação entre as pessoas envolvidas, dar visibilidade ao andamento das iniciativas e apoiar a tomada de decisões relacionadas à inovação.

---

## Problema

Processos de inovação podem envolver diferentes pessoas, áreas, etapas e decisões. Quando essas informações ficam distribuídas em diferentes ferramentas, documentos ou canais de comunicação, pode ser difícil acompanhar:

* quais demandas foram registradas;
* quais estão em avaliação;
* quais foram aprovadas ou rejeitadas;
* em que etapa cada iniciativa se encontra;
* quais iniciativas estão sendo desenvolvidas;
* quais resultados foram obtidos.

O Órbita busca solucionar esse problema centralizando essas informações e organizando o fluxo das demandas.

---

## Solução

A plataforma permite acompanhar o ciclo de vida de uma demanda de inovação, desde seu registro até sua evolução dentro do processo.

Entre as principais funcionalidades previstas estão:

* Cadastro de demandas de inovação;
* Edição e submissão de demandas;
* Avaliação e triagem;
* Aprovação ou rejeição;
* Acompanhamento do status;
* Organização das iniciativas em um funil de inovação;
* Gestão de MVPs;
* Acompanhamento de resultados;
* Dashboard e indicadores;
* Histórico das demandas;
* Notificações;
* Controle de acesso de acordo com o perfil do usuário.

---

## Perfis de usuários

O sistema possui diferentes perfis envolvidos no processo de inovação:

* **Gestor Demandante:** registra e acompanha demandas;
* **Membro do Grupo de Trabalho:** participa da análise e desenvolvimento das iniciativas;
* **Hub de Inovação:** realiza avaliação, acompanhamento e gestão das demandas;
* **PO da Iniciativa:** acompanha e conduz iniciativas;
* **Governança:** atua na priorização e tomada de decisões;
* **Diretoria:** acompanha e avalia iniciativas estratégicas;
* **Consultoria Lei do Bem:** atua nos processos relacionados à Lei do Bem;
* **Auditoria:** acompanha registros e informações para fins de auditoria;
* **Administrador:** responsável pela administração da plataforma.

---

## Fluxo da demanda

Uma demanda pode passar por diferentes etapas durante seu ciclo de vida:

```text
Rascunho
   ↓
Submetida
   ↓
Em Avaliação
   ↓
Aprovada / Rejeitada
   ↓
Em Funil
   ↓
MVP
   ↓
Produção
   ↓
Encerrada
```

O fluxo permite acompanhar a evolução da iniciativa e manter o histórico de suas etapas.

---

## Funil de inovação

As iniciativas podem avançar por diferentes etapas do processo de inovação:

```text
Entendimento do Problema
          ↓
Pesquisa
          ↓
Ideação
          ↓
Prototipação
          ↓
PoC
          ↓
MVP
          ↓
Validação
          ↓
Escala
```

Essa estrutura permite acompanhar a evolução de uma ideia desde a compreensão do problema até sua possível implementação em escala.

---

## MVP

O MVP do Órbita está sendo desenvolvido com foco nas funcionalidades essenciais para validar a solução.

Entre elas:

* Autenticação de usuários;
* Controle de acesso por perfil;
* Cadastro de demandas;
* Edição e submissão;
* Avaliação;
* Aprovação ou rejeição;
* Acompanhamento de status;
* Funil de inovação;
* Dashboard;
* Notificações;
* Histórico das demandas.

O objetivo é desenvolver primeiro uma versão funcional e validar a solução antes da implementação de funcionalidades mais avançadas.

---

## Interface

A plataforma será desenvolvida com uma abordagem **web responsiva**, permitindo sua utilização em diferentes tamanhos de tela.

Também está prevista a utilização de **PWA (Progressive Web App)**, proporcionando uma experiência mais próxima de uma aplicação instalada, sem a necessidade de desenvolver um aplicativo mobile nativo separado.

---

## Tecnologias

De acordo com os requisitos definidos para o projeto, a solução utiliza como base:

### Backend

* Python
* API REST
* PostgreSQL 16
  

### Frontend

* React
* PWA
* Interface responsiva

---

## Projeto em construção

O **Órbita está atualmente em desenvolvimento**.

O projeto está sendo construído de forma incremental, começando pelas funcionalidades essenciais do MVP e evoluindo posteriormente para recursos mais avançados de gestão, indicadores, governança e integração.

Funcionalidades e tecnologias podem ser aprimoradas ao longo do desenvolvimento conforme as necessidades do projeto e os resultados das validações.

---

## Contexto

O projeto está sendo desenvolvido pela **Squad 47** no contexto da **Residência Tecnológica do Porto Digital**, em parceria com o **Banco do Brasil**.

A iniciativa proporciona a aplicação prática de conhecimentos de desenvolvimento de software, arquitetura, banco de dados, metodologias ágeis e desenvolvimento de produtos digitais em um problema real de negócio.

---

## Visão do produto

O Órbita busca transformar a gestão de demandas de inovação em um processo mais organizado, transparente e orientado a resultados.

A proposta é conectar:

**Ideias → Pessoas → Processos → Resultados**

---

## Equipe

Projeto desenvolvido pela **Squad 47** da Residência Tecnológica do Porto Digital.

**Parcerias:**

* Porto Digital
* Banco do Brasil

---

