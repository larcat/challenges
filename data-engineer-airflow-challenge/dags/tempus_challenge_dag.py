from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

from tempus_challenge import get_sources, get_headlines
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 12, 6),
    'email': ['example@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG Object
dag = DAG(
    'tempus_challenge_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

get_sources_task = PythonOperator(
    task_id='getting_sources',
    provide_context=False,
    python_callable=get_sources,
    dag=dag
)

get_headlines_task = PythonOperator(
    task_id='getting_headlines',
    provide_context=True,
    # provide params and additional kwargs to python_callable
    python_callable=get_headlines,
    dag=dag
)

end = DummyOperator(
    task_id='end',
    dag=dag
)

get_sources_task >> get_headlines_task >> end
