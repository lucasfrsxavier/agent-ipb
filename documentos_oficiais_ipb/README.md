# Documentos Importantes da IPB

19 documentos oficiais em PDF (Constituição, Estatuto, Manual Presbiteriano,
Código de Disciplina, Regimentos Internos, modelos de estatuto/regimento
para igreja/presbitério/sínodo etc.), baixados de
`https://se.icalvinus.app/documentos_importantes.php`.

Diferente do Digesto (`digesto_ipb_1951-2026/`), aqui **só existe a versão em
PDF** na fonte — não há texto/JSON pronto. Por isso guardamos o PDF original
como está (fonte oficial, útil para citar página exata) e a extração de
texto para RAG deve ficar como uma etapa de `src/agent_ipb/ingestion/`.

## Conteúdo

- `pdfs/` — os 19 arquivos originais.
- `metadados.json` — título, arquivo local, URL de origem, tamanho e status
  de cada documento.

## Atualizar

```bash
python3 ../scripts/baixar_documentos_importantes.py
```

Script idempotente: só baixa o que ainda não existe em `pdfs/`, então pode
rodar de novo a qualquer momento pra pegar documentos novos que a IPB
adicionar à lista.
