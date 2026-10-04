"""Read the Concentriq image catalog without retrieving patient details."""

from sqlalchemy import text


CATALOG_QUERY = text("""
    SELECT c.id, btrim(c.accession_id::text) AS "accessionId",
           c.accession_date AS "accessionDate"
    FROM public.case_details c
    WHERE EXISTS (
        SELECT 1
        FROM public.slides s
        JOIN public.images i ON i.slide_id = s.id AND i.status = 'ready'
        WHERE s.case_detail_id = c.id
    )
    ORDER BY c.id
""")


def iter_catalog_batches(engine, batch_size):
    """Read one snapshot, including images added to older cases."""
    with engine.connect().execution_options(
        isolation_level="REPEATABLE READ"
    ) as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            connection.execute(text("SET LOCAL statement_timeout = '5min'"))
            result = connection.execution_options(stream_results=True).execute(
                CATALOG_QUERY
            ).mappings()
            try:
                while rows := result.fetchmany(batch_size):
                    items = []
                    for row in rows:
                        accession = row["accessionId"]
                        if not accession or len(accession) > 100:
                            raise ValueError("Invalid Concentriq accession identifier")
                        accession_date = row["accessionDate"]
                        items.append({
                            "id": row["id"],
                            "accessionId": accession,
                            "accessionDate": (
                                accession_date.isoformat() if accession_date else None
                            ),
                        })
                    yield items
            finally:
                result.close()
