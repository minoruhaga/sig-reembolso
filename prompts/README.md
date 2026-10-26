# Registro de Prompts e Análises Decisórias (Decision Analysis)

Esta pasta mantém os prompts estruturados e as análises decisórias de engenharia versionadas utilizadas pela equipe do **SIG-Reembolso** durante o ciclo de desenvolvimento da Fase 2.

## Organização de Subpastas

- `ambientes/` — análises e especificações do ecossistema de desenvolvimento (Nix, Docker, CI/CD, settings).
- `backend/` — análises arquiteturais, models, services, regras contábeis e APIs.
- `frontend/` — especificações de layout, componentes Bootstrap 5, wireframes e fluxos mobile.
- `requisitos/` — refinamentos de casos de uso e elicitação de novas demandas.
- `revisao/` — checklists de revisão arquitetural e auditoria de PRs.
- `testes/` — planos de testes automatizados e massa de teste com dados do AG VI / AG VII.
- `templates/` — modelos base para novas análises decisórias.

## Nomenclatura Padrão

Os arquivos de análise decisória gerados pela skill `$decision-analysis-v4` seguem a convenção:
`<YYYYMMDD>-<HHMMSS>-<slug>-v<NNN>.md` (ex: `20261026-105000-regras-estouro-teto-v001.md`).
