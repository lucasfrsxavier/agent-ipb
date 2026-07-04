# Digesto da IPB — 1951 a 2026

Extração completa do Digesto da Igreja Presbiteriana do Brasil (site https://sc.icalvinus.app),
via a API pública que alimenta o app: `https://se.icalvinus.app/consulta/digestoapi.php`.

## Conteúdo

- `digesto_ipb_1951_2026.jsonl` — arquivo consolidado com **todos os 14.146 documentos**, um por linha (JSON Lines).
- `by_year/AAAA.jsonl` — mesmo conteúdo, separado por ano (1951.jsonl a 2026.jsonl), 76 arquivos.
- `stats_por_ano.csv` — contagem de documentos por ano.

## Estrutura de cada registro

```json
{
  "id": "1951-0001",
  "ano": 1951,
  "reuniao_tipo": "SC-E",
  "doc_numero": "DOC. LXIV",
  "ementa": "SC-E - 1951 - DOC. LXIV:",
  "texto": "Texto completo da resolução...",
  "fonte": "Digesto da IPB (sc.icalvinus.app)"
}
```

Campo `reuniao_tipo` (siglas encontradas): SC (Supremo Concílio), SC-E (Supremo Concílio –
sessão especial/extraordinária), CE (Comissão Executiva), CE-E / CE-E1 / CE-E2 / CE-E3
(Comissão Executiva – sessões especiais), SC-E1, CIP.

## Observações

- Nenhum ano de 1951 a 2026 ficou de fora (76/76 baixados).
- O ano de **2020** retornou 0 documentos na fonte (provável interrupção das reuniões
  presenciais durante a pandemia).
- Formato JSONL escolhido por ser o padrão mais direto para ingestão em pipelines de RAG
  (um chunk/documento por linha, metadata pronta para filtrar por ano ou tipo de reunião).
