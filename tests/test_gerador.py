import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from scripts.gerar_dados import gerar


class TestGerador(unittest.TestCase):
    def gerar_silencioso(self, pasta):
        with contextlib.redirect_stdout(io.StringIO()):
            return gerar(pasta)

    def test_reexecucao_produz_os_mesmos_arquivos(self):
        with tempfile.TemporaryDirectory() as pasta:
            self.gerar_silencioso(pasta)
            antes = {p.name: p.read_bytes() for p in Path(pasta).glob("*.csv")}
            self.gerar_silencioso(pasta)
            depois = {p.name: p.read_bytes() for p in Path(pasta).glob("*.csv")}
            self.assertEqual(antes, depois)

    def test_integridade_e_cenarios_de_negocio(self):
        with tempfile.TemporaryDirectory() as pasta:
            dados = self.gerar_silencioso(pasta)
        pedidos = {p["pedido_id"]: p for p in dados["pedidos"]}
        clientes = {c["cliente_id"] for c in dados["clientes"]}
        produtos = {p["produto_id"] for p in dados["produtos"]}
        self.assertEqual(len(pedidos), 500)
        self.assertEqual(len({i["item_id"] for i in dados["itens"]}), len(dados["itens"]))
        self.assertEqual({p["status"].strip().upper() for p in pedidos.values()}, {"ENTREGUE", "CANCELADO"})
        for p in pedidos.values():
            self.assertIn(p["cliente_id"], clientes)
        for item in dados["itens"]:
            self.assertIn(item["pedido_id"], pedidos)
            self.assertIn(item["produto_id"], produtos)
            self.assertGreater(item["quantidade"], 0)
            self.assertGreater(item["preco_unitario_centavos"], 0)


if __name__ == "__main__":
    unittest.main()

