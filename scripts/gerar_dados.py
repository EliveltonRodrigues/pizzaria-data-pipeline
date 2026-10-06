"""Gera um pequeno sistema de pedidos fictícios, repetível e sem dados pessoais."""
import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUTOS = [
    (1, "Mussarela", 4500), (2, "Calabresa", 4800),
    (3, "Frango com catupiry", 5500), (4, "Portuguesa", 5200),
    (5, "Quatro queijos", 5800), (6, "Chocolate", 5000),
]


def gerar(destino, quantidade=500, seed=42):
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser positiva.")
    rng = random.Random(seed)
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    clientes = [
        {"cliente_id": i, "cidade": rng.choice([" Sao Carlos ", "ARARAQUARA", " Ibate"])}
        for i in range(1, 61)
    ]
    produtos = [
        {"produto_id": i, "nome": nome, "preco_centavos": preco}
        for i, nome, preco in PRODUTOS
    ]
    pedidos, itens = [], []
    for pedido_id in range(1, quantidade + 1):
        pedidos.append({
            "pedido_id": pedido_id,
            "cliente_id": rng.randint(1, 60),
            "data_pedido": (date(2026, 9, 1) + timedelta(days=rng.randrange(30))).isoformat(),
            "status": rng.choices([" entregue ", "ENTREGUE", "cancelado"], [6, 3, 1])[0],
        })
        for produto_id, _, preco in rng.sample(PRODUTOS, k=rng.randint(1, 3)):
            itens.append({
                "item_id": len(itens) + 1,
                "pedido_id": pedido_id,
                "produto_id": produto_id,
                "quantidade": rng.randint(1, 2),
                "preco_unitario_centavos": preco,
            })
    tabelas = {"clientes": clientes, "produtos": produtos, "pedidos": pedidos, "itens": itens}
    for nome, linhas in tabelas.items():
        with (destino / f"{nome}.csv").open("w", newline="", encoding="utf-8") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
            writer.writeheader()
            writer.writerows(linhas)
        print(f"{nome}: {len(linhas)} registros")
    return tabelas


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pedidos", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--destino", type=Path, default=ROOT / "data" / "raw")
    args = parser.parse_args()
    gerar(args.destino, args.pedidos, args.seed)

