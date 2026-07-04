#!/usr/bin/env python3
"""
Extração histórica completa do Digesto da IPB (sc.icalvinus.app).

Baixa TODOS os documentos da API pública que alimenta o app, ano a ano,
desde ANO_INICIAL até o ano atual, e monta:

  digesto_ipb_1951-2026/
    by_year/AAAA.jsonl          -> um arquivo por ano
    digesto_ipb_1951_2026.jsonl -> tudo consolidado (um doc por linha)
    stats_por_ano.csv           -> contagem de documentos por ano

Uso:
    python3 extrair_digesto_completo.py

Rodar de novo no futuro refaz a extração inteira do zero (sobrescreve
os arquivos). Para atualizar só os anos recentes sem reprocessar tudo,
use `atualizar_digesto.py` em vez deste script.
"""

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime

# --------------------------------------------------------------------------
# Configuração
# --------------------------------------------------------------------------
ANO_INICIAL = 1951
ANO_FINAL = datetime.now().year  # ano corrente, atualiza sozinho

API_URL = "https://se.icalvinus.app/consulta/digestoapi.php"

# Pasta onde os dados ficam. Este script mora em scripts/, os dados um
# nível acima em digesto_ipb_1951-2026/.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "digesto_ipb_1951-2026")
BY_YEAR_DIR = os.path.join(OUT_DIR, "by_year")
RAW_DIR = os.path.join(OUT_DIR, "_raw")  # cache do JSON bruto por ano

CONSOLIDADO_PATH = os.path.join(OUT_DIR, "digesto_ipb_1951_2026.jsonl")
STATS_PATH = os.path.join(OUT_DIR, "stats_por_ano.csv")

# "SC - 1951 - DOC. LIII: resto do texto..." -> tipo, ano, numero do doc
EMENTA_PATTERN = re.compile(r'^\s*([A-Z0-9\-]+)\s*-\s*(\d{4})\s*-\s*(DOC\.?\s*[^:]*)\s*:')


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------
def buscar_ano(ano, tentativas=3, timeout=20):
    """Busca todos os documentos de um ano na API pública do Digesto."""
    url = f"{API_URL}?palavra=&tipo=0&ano={ano}&resolucao="
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"  [aviso] ano {ano}, tentativa {tentativa + 1}: {e}", file=sys.stderr)
            time.sleep(2)
    return None


def montar_registro(ano, indice, item):
    """Converte um item bruto da API no registro estruturado usado no RAG."""
    ementa = (item.get("ementa") or "").strip()
    texto = (item.get("resolucao") or "").strip()
    m = EMENTA_PATTERN.match(ementa)
    if m:
        reuniao_tipo, _ano_str, doc_numero = m.group(1), m.group(2), m.group(3).strip()
    else:
        reuniao_tipo, doc_numero = None, None
    return {
        "id": f"{ano}-{indice:04d}",
        "ano": ano,
        "reuniao_tipo": reuniao_tipo,
        "doc_numero": doc_numero,
        "ementa": ementa,
        "texto": texto,
        "fonte": "Digesto da IPB (sc.icalvinus.app)",
    }


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    os.makedirs(BY_YEAR_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)

    todos_os_registros = []
    contagem_por_ano = []

    for ano in range(ANO_INICIAL, ANO_FINAL + 1):
        dados = buscar_ano(ano)
        if dados is None:
            print(f"{ano}: FALHOU (mantendo arquivo antigo, se existir)")
            continue

        # cache do bruto, útil para depuração
        with open(os.path.join(RAW_DIR, f"{ano}.json"), "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)

        registros_do_ano = [
            montar_registro(ano, i, item) for i, item in enumerate(dados, start=1)
        ]

        with open(os.path.join(BY_YEAR_DIR, f"{ano}.jsonl"), "w", encoding="utf-8") as f:
            for rec in registros_do_ano:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        todos_os_registros.extend(registros_do_ano)
        contagem_por_ano.append((ano, len(registros_do_ano)))
        print(f"{ano}: {len(registros_do_ano)} docs")

        time.sleep(0.3)  # não martelar a API

    with open(CONSOLIDADO_PATH, "w", encoding="utf-8") as f:
        for rec in todos_os_registros:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        f.write("ano,total_documentos\n")
        for ano, total in contagem_por_ano:
            f.write(f"{ano},{total}\n")

    print(f"\nTotal: {len(todos_os_registros)} documentos, {len(contagem_por_ano)} anos.")
    print(f"Consolidado salvo em: {CONSOLIDADO_PATH}")


if __name__ == "__main__":
    main()
