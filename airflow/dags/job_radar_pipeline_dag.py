from datetime import timedelta

import pendulum

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


LOCAL_TZ = pendulum.timezone("Europe/Podgorica")

DEFAULT_ARGS = {
    "owner": "job_radar",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="job_radar_pipeline",
    description="Run the complete Job Radar data pipeline",
    start_date=pendulum.datetime(2026, 7, 1, tz=LOCAL_TZ),
    schedule="0 8 * * *",
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

    run_pipeline = BashOperator(
        task_id="run_jobs_pipeline",
        bash_command=(
            "cd /opt/airflow/project && "
            "python -m src.pipelines.run_jobs_pipeline"
        ),
        execution_timeout=timedelta(minutes=20),
    )

    create_schema >> run_pipeline


job_radar_pipeline_dag()