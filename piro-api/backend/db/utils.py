import sqlalchemy as sa
from db.session import SQLALCHEMY_DATABASE_URL
from logger import logger


async def check_db_connected():
    try:
        logger.info("check_db_connected")
        if not str(SQLALCHEMY_DATABASE_URL).__contains__("sqlite"):
            # Step 2: Create and configure engine with the connection string
            dbEngine = sa.create_engine(
                url=SQLALCHEMY_DATABASE_URL,
                # fast_executemany=True,
            )
            try:
                with dbEngine.connect() as con:
                    con.execute(sa.text("SELECT 1"))
                logger.info("Database is connected (^_^)")
            except Exception as e:
                logger.error(f"Database connection failed: {e}")

    except Exception as e:
        logger.error(
            "Looks like db is missing or is there is some problem creating the connection; see traceback below."  # noqa:E501
        )
        raise e


async def check_db_disconnected():
    try:
        logger.info("check_db_disconnected")
        if not str(SQLALCHEMY_DATABASE_URL).__contains__("sqlite"):
            dbEngine = sa.create_engine(
                url=SQLALCHEMY_DATABASE_URL,
                # fast_executemany=True,
            )
            conn = dbEngine.connect()
            conn.close()
        logger.info("Database is Disconnected (-_-) zZZ")
    except Exception as e:
        logger.error(
            f"There is an error with disconnecting from the database. Please see the error logs: {type(e), e, e.args}"  # noqa:E501
        )
        raise e
