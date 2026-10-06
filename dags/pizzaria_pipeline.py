"""Orquestra executáveis do projeto sem instalar dbt no ambiente do Airflow."""
import os
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJETO = os.environ.get(
    "PIZZARIA_PROJECT_DIR",
    str(Path.home() / "projetos" / "pizzaria-data-pipeline"),
)

with DAG(
    dag_id="pizzaria_pipeline",
    description="CSV sintético -> Bronze PostgreSQL -> dbt Silver/Gold com testes",
    start_date=pendulum.datetime(2026, 9, 1, tz="America/Sao_Paulo"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(seconds=30)},
    tags=["portfolio", "dbt", "pizzaria"],
) as dag:
    def tarefa(task_id, comando):
        return BashOperator(
            task_id=task_id,
            bash_command='set -euo pipefail; "$PROJECT_DIR/.venv/bin/python" ' + comando,
            env={"PROJECT_DIR": PROJETO},
            append_env=True,
            cwd=PROJETO,
            do_xcom_push=False,
        )

    gerar = tarefa("gerar_dados", '"$PROJECT_DIR/scripts/gerar_dados.py"')
    carregar = tarefa("carregar_bronze", '"$PROJECT_DIR/scripts/carregar_bronze.py"')
    validar_origem = tarefa("validar_bronze", '"$PROJECT_DIR/scripts/dbt_local.py" test --select source:*')
    transformar = tarefa("transformar_e_testar", '"$PROJECT_DIR/scripts/dbt_local.py" build')
    gerar >> carregar >> validar_origem >> transformar

