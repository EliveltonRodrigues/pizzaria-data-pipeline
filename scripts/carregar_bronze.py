"""Carga FULL atômica de CSVs na Bronze; reexecução não acumula duplicatas."""
import csv
import os
from pathlib import Path

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
COLUNAS = {
    "clientes": ["cliente_id", "cidade"],
    "produtos": ["produto_id", "nome", "preco_centavos"],
    "pedidos": ["pedido_id", "cliente_id", "data_pedido", "status"],
    "itens": ["item_id", "pedido_id", "produto_id", "quantidade", "preco_unitario_centavos"],
}


def carregar():
    load_dotenv(ROOT / ".env", override=False)
    dados = {}
    # Valida arquivos antes de abrir a transação.
    for tabela, colunas in COLUNAS.items():
        with (ROOT / "data" / "raw" / f"{tabela}.csv").open(encoding="utf-8", newline="") as arquivo:
            reader = csv.DictReader(arquivo)
            if reader.fieldnames != colunas:
                raise ValueError(f"Cabeçalho inesperado em {tabela}.csv")
            dados[tabela] = [[linha[coluna] for coluna in colunas] for linha in reader]
            if not dados[tabela]:
                raise ValueError(f"Arquivo vazio: {tabela}.csv")

    conn = psycopg2.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"],
        dbname=os.environ["PGDATABASE"], user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"], connect_timeout=10,
    )
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CREATE SCHEMA IF NOT EXISTS bronze")
                for tabela, colunas in COLUNAS.items():
                    campos = sql.SQL(", ").join(
                        sql.SQL("{} TEXT").format(sql.Identifier(coluna)) for coluna in colunas
                    )
                    cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS bronze.{} ({})").format(
                        sql.Identifier(tabela), campos))
                    cur.execute(sql.SQL("TRUNCATE TABLE bronze.{}").format(sql.Identifier(tabela)))
                    query = sql.SQL("INSERT INTO bronze.{} ({}) VALUES ({})").format(
                        sql.Identifier(tabela),
                        sql.SQL(", ").join(map(sql.Identifier, colunas)),
                        sql.SQL(", ").join(sql.Placeholder() for _ in colunas),
                    )
                    cur.executemany(query, dados[tabela])
                    print(f"Bronze {tabela}: {len(dados[tabela])} registros")
        print("Transação confirmada.")
    finally:
        conn.close()


if __name__ == "__main__":
    carregar()

