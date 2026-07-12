from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


DEFAULT_ARGS = {
    "owner": "job_radar",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="job_radar_pipeline",
    description="Extract, load and aggregate job market data",
    start_date=datetime(2026, 6, 1),
    schedule=None,
    catchup=False,
    default_args=DEFAULT_ARGS,
    max_active_runs=1,
    tags=["job_radar"],
)
def job_radar_pipeline_dag():
    create_schema = BashOperator(
        task_id="create_clickhouse_schema",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m src.loaders.create_clickhouse_schema"
        ),
        execution_timeout=timedelta(minutes=5),
    )

    extract_jobs = BashOperator(
        task_id="extract_jobs",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m src.extractors.arbeitnow"
        ),
        execution_timeout=timedelta(minutes=10),
    )

    load_clickhouse = BashOperator(
        task_id="load_clickhouse",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m src.loaders.clickhouse_loader"
        ),
        execution_timeout=timedelta(minutes=10),
    )

    refresh_marts = BashOperator(
        task_id="refresh_marts",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m src.loaders.refresh_marts"
        ),
        execution_timeout=timedelta(minutes=10),
    )

    create_schema >> extract_jobs >> load_clickhouse >> refresh_marts


job_radar_pipeline_dag()