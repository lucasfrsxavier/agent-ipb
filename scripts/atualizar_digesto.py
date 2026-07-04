#!/usr/bin/env python3
"""
Atualização incremental do Digesto da IPB.

Use este script sempre que quiser puxar documentos novos de uma reunião
recente, ou quando o ano virar — SEM reprocessar os 70+ anos anteriores.

Ele:
  1. Rebusca na API só os anos pedidos (por padrão, o ano atual).
  2. Sobrescreve o by_year/AAAA.jsonl desses anos.
  3. Reconstrói o arquivo consolidado e o stats_por_ano.csv a partir de
     TODOS os arquivos em by_year/ (garante que tudo fique consistente).
  4. Mostra quantos documentos existiam antes e depois, para você ver
     na hora o que mudou.

Uso:
    # só o ano atual (uso mais comum: rodar depois de cada reunião)
    python3 atualizar_digesto.py

    # anos específicos
    python3 atualizar_digesto.py 2025 2026

    # quando o ano virar, garanta que o novo ano também está incluído
    python3 atualizar_digesto.py 2026 2027

    # refazer tudo do zero (equivalente a extrair_digesto_completo.py)
    python3 atualizar_digesto.py --full
"""

import glob
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime

ANO_INICIAL = 1951
API_URL = "https://se.icalvinus.app/consulta/digestoapi.php"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "digesto_ipb_1951-2026")
BY_YEAR_DIR = os.path.join(OUT_DIR, "by_year")
RAW_DIR = os.path.join(OUT_DIR, "_raw")

CONSOLIDADO_PATH = os.path.join(OUT_DIR, "digesto_ipb_1951_2026.jsonl")
STATS_PATH = os.path.join(OUT_DIR, "stats_por_ano.csv")

EMENTA_PATTERN = re.compile(r'^\s*([A-Z0-9\-]+)\s*-\s*(\d{4})\s*-\s*(DOC\.?\s*[^:]*)\s*:')


def buscar_ano(ano, tentativas=3, timeout=20):
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
    ementa = (item.get("ementa") or "").strip()
    texto = (item.get("resolucao") or "").strip()
    m = EMENTA_PATTERN.match(ementa)
    if m:
        reuniao_tipo, doc_numero = m.group(1), m.group(3).strip()
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


def contar_docs_existentes(ano):
    """Quantos documentos já estão salvos localmente para esse ano (0 se não existir)."""
    caminho = os.path.join(BY_YEAR_DIR, f"{ano}.jsonl")
    if not os.path.exists(caminho):
        return 0
    with open(caminho, encoding="utf-8") as f:
        return sum(1 for _ in f)


def atualizar_anos(anos):
    """Rebusca e sobrescreve by_year/{ano}.jsonl para os anos passados."""
    os.makedirs(BY_YEAR_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)

    for ano in anos:
        antes = contar_docs_existentes(ano)
        dados = buscar_ano(ano)
        if dados is None:
            print(f"{ano}: FALHOU ao buscar — arquivo local mantido como estava ({antes} docs)")
            continue

        with open(os.path.join(RAW_DIR, f"{ano}.json"), "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)

        registros = [montar_registro(ano, i, item) for i, item in enumerate(dados, start=1)]
        with open(os.path.join(BY_YEAR_DIR, f"{ano}.jsonl"), "w", encoding="utf-8") as f:
            for rec in registros:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        depois = len(registros)
        diff = depois - antes
        sinal = f"+{diff}" if diff > 0 else str(diff)
        print(f"{ano}: {antes} -> {depois} docs ({sinal})")
        time.sleep(0.3)


def reconstruir_consolidado_e_stats():
    """Recompila o JSONL consolidado e o CSV de estatísticas a partir de by_year/*.jsonl."""
    arquivos = sorted(
        glob.glob(os.path.join(BY_YEAR_DIR, "*.jsonl")),
        key=lambda p: int(os.path.basename(p).replace(".jsonl", "")),
    )

    total = 0
    with open(CONSOLIDADO_PATH, "w", encoding="utf-8") as saida, \
         open(STATS_PATH, "w", encoding="utf-8") as stats:
        stats.write("ano,total_documentos\n")
        for arquivo in arquivos:
            ano = os.path.basename(arquivo).replace(".jsonl", "")
            linhas = open(arquivo, encoding="utf-8").readlines()
            for linha in linhas:
                saida.write(linha)
            stats.write(f"{ano},{len(linhas)}\n")
            total += len(linhas)

    print(f"\nConsolidado reconstruído: {total} documentos em {len(arquivos)} anos.")


def main():
    args = sys.argv[1:]

    if args == ["--full"]:
        anos = list(range(ANO_INICIAL, datetime.now().year + 1))
        print(f"Modo --full: rebuscando TODOS os anos ({ANO_INICIAL}-{datetime.now().year})...")
    elif args:
        anos = sorted(set(int(a) for a in args))
    else:
        anos = [datetime.now().year]

    print(f"Atualizando ano(s): {anos}")
    atualizar_anos(anos)
    reconstruir_consolidado_e_stats()


if __name__ == "__main__":
    main()
