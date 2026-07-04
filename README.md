# Agente de IA — Digesto da IPB

Agente de IA (RAG) para consultar o Digesto da Igreja Presbiteriana do Brasil:
atas e resoluções do Supremo Concílio e da Comissão Executiva, de 1951 até o
ano corrente.

## Estrutura do projeto

```
.
├── digesto_ipb_1951-2026/   # Dados extraídos (JSONL por ano + consolidado). Ver README próprio.
├── scripts/                 # Extração e atualização dos dados (fora do pacote principal)
│   ├── extrair_digesto_completo.py
│   └── atualizar_digesto.py
├── src/agent_ipb/           # Código do agente (pacote Python instalável)
│   ├── config/              # Configurações, variáveis de ambiente
│   ├── ingestion/           # Carregar/chunkar os documentos do Digesto
│   ├── retrieval/           # Embeddings, vector store, busca
│   ├── agent/               # Orquestração do agente (LLM, prompts, memória)
│   └── tools/                # Ferramentas que o agente pode chamar
├── tests/                   # Testes automatizados
├── notebooks/                # Notebooks de exploração/experimentação
├── pyproject.toml           # Definição do projeto e dependências (gerenciado via uv)
└── .env.example             # Modelo de variáveis de ambiente (chaves de API etc.)
```

Cada subpasta de `src/agent_ipb/` está vazia por enquanto (só com `__init__.py`)
— a lógica ainda não foi implementada, é só o esqueleto do projeto.

## Ambiente (uv)

Projeto gerenciado com [uv](https://docs.astral.sh/uv/).

```bash
# instalar dependências (quando houver alguma declarada no pyproject.toml)
uv sync

# rodar algo dentro do ambiente do projeto
uv run python -m agent_ipb

# adicionar uma nova dependência
uv add <pacote>
```

Copie `.env.example` para `.env` e preencha as chaves de API antes de rodar
qualquer coisa que dependa de LLM/embeddings.

## Dados

Os dados do Digesto já foram extraídos (14.146 documentos, 1951–2026) e estão
em `digesto_ipb_1951-2026/`. Para atualizar, veja `scripts/atualizar_digesto.py`.
