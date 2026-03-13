import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION")

    DATABASE: str = os.getenv("DATABASE")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv(
        "POSTGRES_PORT", 5432
    )  # default postgres port is 5432
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tdd")
    POSTGRES_DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    MSSQL_USER: str = os.getenv("MSSQL_USER")
    MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD")
    MSSQL_SERVER: str = os.getenv("MSSQL_SERVER", "localhost")
    MSSQL_DB: str = os.getenv("MSSQL_DB")
    MSSQL_WINDOW_AUTH: str = os.getenv("MSSQL_WINDOW_AUTH")
    MSSQL_DRIVER: str = os.getenv("MSSQL_DRIVER")
    MSSQL_DB_URL_SQL = f"mssql+pyodbc://{MSSQL_USER}:{MSSQL_PASSWORD}@{MSSQL_SERVER}/{MSSQL_DB}?driver={MSSQL_DRIVER}&TrustServerCertificate=yes"
    MSSQL_DB_URL_WIN = (
        f"mssql+pyodbc://{MSSQL_SERVER}/{MSSQL_DB}?driver={MSSQL_DRIVER}"
    )

    DATABASE: str = os.getenv("DATABASE")

    ACCESS_TOKEN_SECRET_KEY: str = os.getenv("ACCESS_TOKEN_SECRET_KEY")
    ACCESS_TOKEN_ALGORITHM = os.getenv("ACCESS_TOKEN_ALGORITHM")
    ACCESS_TOKEN_TEST_USER = os.getenv("ACCESS_TOKEN_TEST_USER")
    ACCESS_TOKEN_EXPIRE_MINUTES = float(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    )  # in mins
    SLIDEROOM_ACCESS_TOKEN_EXPIRE_MINUTES = float(
        os.getenv(
            "SLIDEROOM_ACCESS_TOKEN_EXPIRE_MINUTES",
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
        )
    )

    TEST_USER_EMAIL = "test@example.com"
    API_CORS: str = os.getenv("API_CORS")
    SOLR_URL: str = os.getenv("SOLR_URL")
    SOLR_CORE: str = os.getenv("SOLR_CORE")
    SOLR_SUGGEST_COMMENT: str = os.getenv("SOLR_SUGGEST_COMMENT")
    SOLR_SUGGEST_STAFF: str = os.getenv("SOLR_SUGGEST_STAFF")
    SOLR_SUGGEST_CASE: str = os.getenv("SOLR_SUGGEST_CASE")
    SOLR_SUGGESTER_COMMENT: str = "commentSuggester"
    SOLR_SUGGESTER_STAFF: str = "staffSuggester"
    SOLR_SUGGESTER_CASE: str = "caseSuggester"
    SOLR_USER_NAME: str = os.getenv("SOLR_USER_NAME")
    SOLR_USER_PASSWORD: str = os.getenv("SOLR_USER_PASSWORD")
    AD_LDAP_PATH: str = os.getenv("AD_LDAP_PATH")
    AD_SECURITY_GROUP: str = os.getenv("AD_SECURITY_GROUP")
    AD_DOMAIN: str = os.getenv("AD_DOMAIN")
    EXCEL_Template_DIRECTORY: str = os.getenv("EXCEL_Template_DIRECTORY")
    EXCEL_Output_DIRECTORY: str = os.getenv("EXCEL_Output_DIRECTORY")
    EXCEL_SEARCH_REQUEST_Template_FILE: str = os.getenv(
        "EXCEL_SearchRequest_Template_FILE",
        os.getenv("EXCEL_SearchRequst_Template_FILE"),
    )
    EXCEL_Cohort_MRN_Template_FILE: str = os.getenv(
        "EXCEL_Cohort_MRN_Template_FILE"
    )
    EXCEL_Cohort_CASE_Template_FILE: str = os.getenv(
        "EXCEL_Cohort_Case_Template_FILE"
    )
    EXCEL_Cohort_EID_Template_FILE: str = os.getenv(
        "EXCEL_Cohort_EID_Template_FILE"
    )
    RECORDS_PER_PAGE: int = 5
    EXCEL_Output_Records: int = 30000
    DATAREQUEST_EMAIL_Template_DIRECTORY: str = os.getenv(
        "DATAREQUEST_EMAIL_Template_DIRECTORY"
    )
    DATAREQUEST_EMAIL_Template_FILE: str = os.getenv(
        "DATAREQUEST_EMAIL_Template_FILE"
    )
    DATAREQUEST_EMAIL_SUBJECT: str = os.getenv("DATAREQUEST_EMAIL_SUBJECT")
    DATAREQUEST_EMAIL_TO: str = os.getenv("DATAREQUEST_EMAIL_TO")
    DATAREQUEST_EMAIL_CC: str = os.getenv("DATAREQUEST_EMAIL_CC")
    DATAREQUEST_EMAIL_ENABLE: str = os.getenv("DATAREQUEST_EMAIL_ENABLE")

    EMAIL_SMTP_SERVER: str = os.getenv("EMAIL_SMTP_SERVER")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM")

    AIRFLOW_HEADER_AUTH: str = os.getenv("AIRFLOW_HEADER_AUTH")
    AIRFLOW_DAG_COHORT_LOADER_URL: str = os.getenv(
        "AIRFLOW_DAG_COHORT_LOADER_URL"
    )
    AIRFLOW_CERTIFICATE: str = os.getenv("AIRFLOW_CERTIFICATE")

    CONCENTRIQ_WEBHOOK_SECRET: str = os.getenv("CONCENTRIQ_WEBHOOK_SECRET")
    CONCENTRIQ_URL: str = os.getenv("CONCENTRIQ_URL")


settings = Settings()
