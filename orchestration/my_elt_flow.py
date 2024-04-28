from dotenv import dotenv_values
from prefect import flow, task
from prefect_airbyte.server import AirbyteServer
from prefect_airbyte.connections import AirbyteConnection, AirbyteSyncResult
from prefect_airbyte.flows import run_connection_sync
from prefect_dbt.cli.commands import DbtCoreOperation

config = dotenv_values(".env");

remote_airbyte_server = AirbyteServer(
    username = config["AIRBYTE_USERNAME"],
    password = config["AIRBYTE_PASSWORD"],
    server_host = config["AIRBYTE_SERVER_HOST"],
    server_port = config["AIRBYTE_PORT"]
)

remote_airbyte_server.save("my-remote-airbyte-server", overwrite=True)

airbyte_connection = AirbyteConnection(
    airbyte_server=remote_airbyte_server,
    connection_id="d998b16c-24db-40e2-9d37-25fdaa8dcb76",
    status_updates=True,
)

@task(name="Extract, Load with Airbyte")
def run_airbyte_sync(connection: AirbyteConnection) -> AirbyteSyncResult:
    job_run = connection.trigger()
    job_run.wait_for_completion()
    return job_run.fetch_result()

def run_dbt_commands(commands, prev_task_result):
    dbt_task = DbtCoreOperation(
        commands=commands,
        project_dir="../dbt_project",
        profiles_dir="../dbt_project",
        wait_for=prev_task_result
    )
    return dbt_task

@flow(log_prints=True)
def my_elt_flow():

    # [Task] Run Airbyte sync
    # airbyte_sync_result: AirbyteSyncResult = run_connection_sync(
    #     airbyte_connection=airbyte_connection,
    # )
    airbyte_sync_result = run_airbyte_sync(airbyte_connection)

    # [Task] Run dbt precheck    
    dbt_init_task = task(name="dbt precheck")(run_dbt_commands)(
        commands=["pwd", "dbt debug", "dbt list"], 
        prev_task_result=airbyte_sync_result
        )
    dbt_init_task.run()

    # [Task] Run dbt example models to Snowflake DB
    dbt_run_task = task(name="Transform example models with dbt")(run_dbt_commands)(
        commands=["dbt run --target dev-snowflake --models example.*"], 
        prev_task_result=dbt_init_task
        )
    dbt_run_task.run()

    # [Task] Run transform data Postgres dim_discount_code
    dbt_run_task = task(name="Transform dim_discount_code with dbt")(run_dbt_commands)(
        commands=["dbt run --target dev-postgres-transform --select transform.dim_discount_code"], 
        prev_task_result=True
        )
    dbt_run_task.run()



if __name__ == "__main__":
    # my_elt_flow.visualize()
    my_elt_flow()
