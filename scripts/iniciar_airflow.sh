#!/usr/bin/env bash
set -euo pipefail
# Resolve o projeto mesmo se o comando for executado de outra pasta.
PROJETO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export PIZZARIA_PROJECT_DIR="$PROJETO_DIR"
export AIRFLOW_HOME="${AIRFLOW_HOME:-$HOME/airflow}"
AIRFLOW_BIN="$AIRFLOW_HOME/.venv/bin/airflow"
if [ ! -x "$AIRFLOW_BIN" ]; then
  echo "Airflow não encontrado em $AIRFLOW_BIN. Use a instalação feita no WSL."
  exit 1
fi
if [ ! -x "$PROJETO_DIR/.venv/bin/dbt" ]; then
  echo "Instale primeiro requirements.txt no .venv deste projeto."
  exit 1
fi
mkdir -p "$AIRFLOW_HOME/dags"
# Atualiza somente a DAG deste projeto; não altera as outras DAGs.
cp "$PROJETO_DIR/dags/pizzaria_pipeline.py" "$AIRFLOW_HOME/dags/pizzaria_pipeline.py"
export PATH="$AIRFLOW_HOME/.venv/bin:$PATH"
exec "$AIRFLOW_BIN" standalone

