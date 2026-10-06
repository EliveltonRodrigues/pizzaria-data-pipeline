"""Executa o dbt do ambiente do projeto, carregando a conexão do .env."""
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    load_dotenv(ROOT / ".env", override=False)
    executavel = Path(sys.executable).parent / "dbt"
    os.environ["DBT_PROFILES_DIR"] = str(ROOT / "dbt")
    resultado = subprocess.run(
        [str(executavel), *sys.argv[1:]],
        cwd=ROOT / "dbt",
        check=False,
    )
    sys.exit(resultado.returncode)

