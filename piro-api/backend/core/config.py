import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Get the directory where this config.py file is located
config_dir = Path(__file__).resolve().parent
# Look for .env in the backend directory (parent of core)
env_path = config_dir.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str | None = os.getenv("PROJECT_NAME")
    PROJECT_VERSION: str | None = os.getenv("PROJECT_VERSION")

    DATABASE: str | None = os.getenv("DATABASE")
    POSTGRES_USER: str | None = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str | None = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str | int = os.getenv(
        "POSTGRES_PORT", 5432
    )  # default postgres port is 5432
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tdd")
    POSTGRES_DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"  # noqa:E501

    MSSQL_USER: str | None = quote_plus(os.getenv("MSSQL_USER") or "")
    MSSQL_PASSWORD = quote_plus(os.getenv("MSSQL_PASSWORD", ""))
    MSSQL_SERVER: str = os.getenv("MSSQL_SERVER", "localhost")
    MSSQL_DB: str | None = os.getenv("MSSQL_DB")
    MSSQL_WINDOW_AUTH: str | None = os.getenv("MSSQL_WINDOW_AUTH")
    MSSQL_DRIVER: str | None = quote_plus(os.getenv("MSSQL_DRIVER") or "")
    MSSQL_DB_URL_SQL = f"mssql+pyodbc://{MSSQL_USER}:{MSSQL_PASSWORD}@{MSSQL_SERVER}/{MSSQL_DB}?driver={MSSQL_DRIVER}&TrustServerCertificate=yes"  # noqa:E501
    MSSQL_DB_URL_WIN = (
        f"mssql+pyodbc://{MSSQL_SERVER}/{MSSQL_DB}?driver={MSSQL_DRIVER}"
    )

    ACCESS_TOKEN_SECRET_KEY: str | None = os.getenv("ACCESS_TOKEN_SECRET_KEY")
    ACCESS_TOKEN_ALGORITHM: str | None = os.getenv("ACCESS_TOKEN_ALGORITHM")
    ACCESS_TOKEN_TEST_USER: str | None = os.getenv("ACCESS_TOKEN_TEST_USER")
    ACCESS_TOKEN_EXPIRE_MINUTES: float = float(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 300)
    )  # in mins
    SLIDEROOM_ACCESS_TOKEN_EXPIRE_MINUTES = float(
        os.getenv(
            "SLIDEROOM_ACCESS_TOKEN_EXPIRE_MINUTES",
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 300),
        )
    )

    TEST_USER_EMAIL = "test@example.com"
    API_CORS: str | None = os.getenv("API_CORS")
    SOLR_URL: str | None = os.getenv("SOLR_URL")
    SOLR_CORE: str | None = os.getenv("SOLR_CORE")
    SOLR_SUGGEST_COMMENT: str | None = os.getenv("SOLR_SUGGEST_COMMENT")
    SOLR_SUGGEST_STAFF: str | None = os.getenv("SOLR_SUGGEST_STAFF")
    SOLR_SUGGEST_CASE: str | None = os.getenv("SOLR_SUGGEST_CASE")
    SOLR_SUGGESTER_COMMENT: str = "commentSuggester"
    SOLR_SUGGESTER_STAFF: str = "staffSuggester"
    SOLR_SUGGESTER_CASE: str = "caseSuggester"
    SOLR_USER_NAME: str | None = os.getenv("SOLR_USER_NAME")
    SOLR_USER_PASSWORD: str | None = os.getenv("SOLR_USER_PASSWORD")
    AD_LDAP_PATH: str | None = os.getenv("AD_LDAP_PATH")
    AD_SECURITY_GROUP: str | None = os.getenv("AD_SECURITY_GROUP")
    AD_DOMAIN: str | None = os.getenv("AD_DOMAIN")

    # Authentication mode selector. Supported values: "LDAP" (default,
    # preserves the existing corporate-AD flow) or "OAUTH" (validates an
    # OIDC id_token supplied by the client and mints a PIRO JWT from its
    # claims). Case-insensitive; parsed once at import time.
    AUTH_MODE: str = os.getenv("AUTH_MODE", "LDAP").upper()

    # OIDC / OAuth settings. Only consulted when AUTH_MODE == "OAUTH".
    OIDC_ISSUER: str | None = os.getenv("OIDC_ISSUER")
    OIDC_AUDIENCE: str | None = os.getenv("OIDC_AUDIENCE")
    # If OIDC_JWKS_URL is empty, oauth_auth derives it from OIDC_ISSUER via
    # the standard /.well-known/openid-configuration discovery document.
    OIDC_JWKS_URL: str | None = os.getenv("OIDC_JWKS_URL")
    OIDC_ALGORITHMS: str = os.getenv("OIDC_ALGORITHMS", "RS256")
    # Comma-separated list of group names; user is authorized if their
    # `groups` claim intersects this list (OR semantics).
    OIDC_ALLOWED_GROUPS: str = os.getenv("OIDC_ALLOWED_GROUPS", "")
    # Claim-name mapping so we can point at different IdPs (Entra ID,
    # Ping, mock-oauth2-server, etc.) without code changes.
    OIDC_NUID_CLAIM: str = os.getenv("OIDC_NUID_CLAIM", "preferred_username")
    OIDC_GIVEN_NAME_CLAIM: str = os.getenv(
        "OIDC_GIVEN_NAME_CLAIM", "given_name"
    )
    OIDC_FAMILY_NAME_CLAIM: str = os.getenv(
        "OIDC_FAMILY_NAME_CLAIM", "family_name"
    )
    OIDC_GROUPS_CLAIM: str = os.getenv("OIDC_GROUPS_CLAIM", "groups")
    OIDC_CLOCK_SKEW_SECONDS: int = int(
        os.getenv("OIDC_CLOCK_SKEW_SECONDS", "60")
    )
    # Hardening default: do not auto-create PIRO users from OAuth claims
    # unless this is explicitly enabled.
    OAUTH_AUTO_PROVISION_USERS: bool = os.getenv(
        "OAUTH_AUTO_PROVISION_USERS", "false"
    ).lower() in {"1", "true", "yes", "on"}

    EXCEL_Template_DIRECTORY: str | None = os.getenv(
        "EXCEL_Template_DIRECTORY"
    )
    EXCEL_Output_DIRECTORY: str | None = os.getenv("EXCEL_Output_DIRECTORY")
    EXCEL_SEARCH_REQUEST_Template_FILE: str | None = os.getenv(
        "EXCEL_SearchRequest_Template_FILE",
        os.getenv("EXCEL_SearchRequst_Template_FILE"),
    )
    EXCEL_Output_DIRECTORY: str | None = os.getenv("EXCEL_Output_DIRECTORY")
    EXCEL_Cohort_MRN_Template_FILE: str | None = os.getenv(
        "EXCEL_Cohort_MRN_Template_FILE"
    )
    EXCEL_Cohort_CASE_Template_FILE: str | None = os.getenv(
        "EXCEL_Cohort_Case_Template_FILE"
    )
    EXCEL_Cohort_EID_Template_FILE: str | None = os.getenv(
        "EXCEL_Cohort_EID_Template_FILE"
    )
    RECORDS_PER_PAGE: int = 5
    EXCEL_Output_Records: int = 30000
    DATAREQUEST_EMAIL_Template_DIRECTORY: str | None = os.getenv(
        "DATAREQUEST_EMAIL_Template_DIRECTORY"
    )
    DATAREQUEST_EMAIL_Template_FILE: str | None = os.getenv(
        "DATAREQUEST_EMAIL_Template_FILE"
    )
    DATAREQUEST_EMAIL_SUBJECT: str | None = os.getenv(
        "DATAREQUEST_EMAIL_SUBJECT"
    )
    DATAREQUEST_EMAIL_TO: str | None = os.getenv("DATAREQUEST_EMAIL_TO")
    DATAREQUEST_EMAIL_CC: str | None = os.getenv("DATAREQUEST_EMAIL_CC")
    DATAREQUEST_EMAIL_ENABLE: str | None = os.getenv(
        "DATAREQUEST_EMAIL_ENABLE"
    )

    EMAIL_SMTP_SERVER: str | None = os.getenv("EMAIL_SMTP_SERVER")
    EMAIL_FROM: str | None = os.getenv("EMAIL_FROM")

    AIRFLOW_USERNAME: str | None = os.getenv("AIRFLOW_USERNAME")
    AIRFLOW_PASSWORD: str | None = os.getenv("AIRFLOW_PASSWORD")
    AIRFLOW_DAG_COHORT_LOADER_URL: str | None = os.getenv(
        "AIRFLOW_DAG_COHORT_LOADER_URL"
    )
    AIRFLOW_CERTIFICATE: str | None = os.getenv("AIRFLOW_CERTIFICATE")

    CONCENTRIQ_WEBHOOK_SECRET: str | None = os.getenv(
        "CONCENTRIQ_WEBHOOK_SECRET"
    )
    CONCENTRIQ_URL: str | None = os.getenv("CONCENTRIQ_URL")


settings = Settings()
