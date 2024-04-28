from setuptools import find_packages, setup

setup(
    name="bi-airbyte-dbt-prefect-snowflake",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "dbt-postgres",
        "dbt-snowflake",
        "prefect",
        "prefect-airbyte",
        "prefect-dbt",
        "dbt-core>=1.4.0",
    ],
    extras_require={"dev": ["pytest"]},
)
