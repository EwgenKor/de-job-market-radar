from datetime import datetime

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="job_radar_pipeline",
    start_date=datetime(2026, 6, 1),
    schedule=None,
    catchup=False,
    tags=["job_radar"],
)
def job_radar_pipeline_dag():
    create_schema = BashOperator(
        task_id="create_clickhouse_schema",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m src.loaders.create_clickhouse_schema"
        ),
    )

    extract_jobs = BashOperator(
        task_id="extract_jobs",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m src.extractors.arbeitnow"
        ),
    )

    load_clickhouse = BashOperator(
        task_id="load_clickhouse",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m src.loaders.clickhouse_loader"
        ),
    )

    refresh_marts = BashOperator(
        task_id="refresh_marts",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m src.loaders.refresh_marts"
        ),
    )

    create_schema >> extract_jobs >> load_clickhouse >> refresh_marts


job_radar_pipeline_dag()