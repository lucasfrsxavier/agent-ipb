#!/usr/bin/env python3
"""
Baixa os "Documentos Importantes" do iCalvinus (Constituição, Estatuto,
Manuais, Regimentos Internos etc.) — arquivos oficiais em PDF, sem versão
em texto/JSON na fonte.

Fonte: https://se.icalvinus.app/documentos_importantes.php
(endpoint público, sem autenticação, achado no bundle do app Flutter).

Uso:
    python3 baixar_documentos_importantes.py

Idempotente: se um PDF já existe em documentos_oficiais_ipb/pdfs/, não
baixa de novo — então pode rodar de novo a qualquer momento para pegar
só os documentos novos que a IPB adicionar à lista.
"""

import json
import os
import urllib.request

API_URL = "https://se.icalvinus.app/documentos_importantes.php"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "documentos_oficiais_ipb")
PDFS_DIR = os.path.join(OUT_DIR, "pdfs")
METADADOS_PATH = os.path.join(OUT_DIR, "metadados.json")


def buscar_lista():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        # a API responde em latin-1, não em utf-8
        return json.loads(resp.read().decode("latin-1"))["documentos"]


def baixar_pdf(url, destino, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        with open(destino, "wb") as f:
            f.write(resp.read())


def main():
    os.makedirs(PDFS_DIR, exist_ok=True)
    docs = buscar_lista()

    metadados = []
    for d in docs:
        titulo = d["titulo"].strip()
        # alguns registros na fonte têm uma aspa sobrando no fim da URL
        url = d["url"].rstrip("'").strip()
        nome_arquivo = os.path.basename(url)
        destino = os.path.join(PDFS_DIR, nome_arquivo)
        caminho_relativo = os.path.join("pdfs", nome_arquivo)

        if os.path.exists(destino) and os.path.getsize(destino) > 0:
            tamanho_kb = round(os.path.getsize(destino) / 1024, 1)
            print(f"já existe {tamanho_kb:>8} KB  {titulo}")
            status = "ok (já existia)"
        else:
            try:
                baixar_pdf(url, destino)
                tamanho_kb = round(os.path.getsize(destino) / 1024, 1)
                print(f"baixado  {tamanho_kb:>8} KB  {titulo}")
                status = "ok"
            except Exception as e:
                print(f"ERRO               {titulo} :: {e}")
                tamanho_kb, status = None, f"erro: {e}"

        metadados.append({
            "titulo": titulo,
            "arquivo": caminho_relativo,
            "url_original": url,
            "tamanho_kb": tamanho_kb,
            "status": status,
        })

    with open(METADADOS_PATH, "w", encoding="utf-8") as f:
        json.dump(metadados, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {len(metadados)} documentos.")


if __name__ == "__main__":
    main()
