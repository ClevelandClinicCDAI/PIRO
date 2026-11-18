"""Read the Concentriq image catalog without retrieving patient details."""

from sqlalchemy import text


CATALOG_QUERY = text("""
    SELECT c.id, btrim(c.accession_id::text) AS "accessionId",
           c.accession_date AS "accessionDate"
    FROM public.case_details c
    WHERE (:after_case_id = 0 OR c.id > :after_case_id) AND EXISTS (
        SELECT 1
        FROM public.slides s
        JOIN public.images i ON i.slide_id = s.id AND i.status = 'ready'
        WHERE s.case_detail_id = c.id
    )
    ORDER BY c.id
    LIMIT :max_cases
""")


def iter_catalog_batches(engine, batch_size, max_cases_to_process=None,
                         after_case_id=0):
    """Read at most the limit in one snapshot, wrapping an exhausted cursor.

    A null limit reads the full catalog. If a saved cursor has no remaining
    cases, restart from the beginning within the same source snapshot.
    """
    fetch_size = min(batch_size, max_cases_to_process or batch_size)
    with engine.connect().execution_options(
        isolation_level="REPEATABLE READ"
    ) as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            connection.execute(text("SET LOCAL statement_timeout = '5min'"))
            cursors = (after_case_id, 0) if after_case_id else (0,)
            for cursor in cursors:
                result = connection.execution_options(stream_results=True).execute(
                    CATALOG_QUERY,
                    {"max_cases": max_cases_to_process, "after_case_id": cursor},
                ).mappings()
                found_cases = False
                try:
                    while rows := result.fetchmany(fetch_size):
                        found_cases = True
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
                if found_cases:
                    break
