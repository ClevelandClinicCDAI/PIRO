import re
import json
import requests
import traceback
import concurrent.futures
from typing import Any, Generator, Sequence
from datetime import datetime
from pathlib import Path
from sqlalchemy import text, Row
from sqlalchemy.engine.base import Engine
from airflow.sdk import Variable
from tasks.utils.database_setup import get_piro_db_engine
from tasks.utils.logging_setup import get_logger
from tasks.utils.certificate_setup import get_application_root_directory

logger = get_logger()


class MalignantAnnotator:
    """Class for generating 'Is_Malignant' annotations of case records in the
    PIRO database."""

    PREFIX: str = """
You are assisting a pathologist. You will read a pathology report and determine if the report asserts the presence of cancer-associated diagnoses.
You will respond in JSON format with one field "is_malignant", which will be either "POSITIVE" OR "NEGATIVE".

Specifically, return "POSITIVE" if the report asserts the presence of cancer, malignancy,  high-grade dysplasia, carcinoma, sarcoma, mesothelioma, lymphoma or leukemia.  Otherwise, report "NEGATIVE".

For cases in which the diagnosis is not clearly malignant or dysplastic, and contains the word "atypical",  report "NEGATIVE".

The pathology report may have many diagnoses. Analyze the most severate diagnosis.

Do not include any backslashes "\" in the JSON output.

##QUESTION##

Interpret this pathology report:

"""  # noqa

    def __init__(self):
        self._piro_db_engine: Engine = get_piro_db_engine()
        self._api_token: str = Variable.get("OLLAMA_API_BEARER_TOKEN")
        self._api_url: str = Variable.get("OLLAMA_API_URL")
        self._api_verify: str = self._get_api_verify()
        self._errors: list = []

    def _get_api_verify(self) -> str:
        """Return the path to the certificate used to verify calls to the
        LLM API."""
        # TODO: allow for usage of a boolean instead of a cert path, for cases
        # where certificate verification is not needed
        self._certificates_directory: Path = self._get_certificates_directory()
        self._api_verify: str = Variable.get("OLLAMA_API_VERIFY").strip()
        return str(self._certificates_directory / self._api_verify)

    def _get_certificates_directory(self) -> Path:
        application_root_directory: Path = get_application_root_directory()
        # TODO: make the certificates directory configurable via Airflow
        # Variable
        return application_root_directory / "certificates"

    def annotate(
        self,
        max_records_to_process: int | None = None,
        model: str | None = None,
    ) -> dict:
        """Primary method.  Run this to generate 'Malignant' annotations in
        the PIRO DB.

        We do a single query to retrieve the source records (for performance),
        and then process the records in batches of 100."""

        _max_records_to_process: int = self._get_max_records_to_process(
            max_records_to_process
        )

        _model: str = self._get_model(model)

        source_records: list[dict] = self._get_source_records(
            _max_records_to_process
        )

        source_data_batches = self._get_batches(source_records)

        counter: int = 0
        for source_data_batch in source_data_batches:

            try:
                batch_record_count: int = len(source_data_batch)

                logger.info("Generating annotations.")
                source_data_batch = self._get_annotation_values(
                    _model, source_data_batch
                )

                # eliminate rows with no AnnotationValues
                source_data_batch = self._eliminate_null_records(
                    _model, source_data_batch
                )

                logger.info("Formatting the resulting annotations.")
                results: list[dict] = self._format_results(
                    _model, source_data_batch
                )

                logger.info("Writing data to the PIRO database.")
                self._upload_to_piro(results)

                # capture any errors in the database
                self._write_errors_to_db()

                logger.info(
                    f"Batch completed ({batch_record_count} records processed)"
                )
                counter += batch_record_count
            except Exception as e:
                logger.error(f"Error processing a batch: {e}")
                logger.error(traceback.format_exc())
                if "Error in API call: 503" in str(e):
                    # if the LLM API is down abort
                    break

        return {"total_records_processed": counter}

    def _get_max_records_to_process(
        self, max_records_to_process: int | None
    ) -> int:
        """Determine how many records to process: using passed in value if
        available, or looking up via Airflow Variable."""

        if max_records_to_process:
            return max_records_to_process
        else:
            return int(
                Variable.get("MALIGNANT_ANNOTATION_MAX_RECORDS", default=50000)
            )

    def _get_model(self, model: str | None) -> str:
        """Determine model to be used: using passed in value if available,
        or looking up via Airflow Variable."""

        if model:
            return model
        else:
            return Variable.get(
                "MALIGNANT_ANNOTATION_MODEL",
                default="llama3.1:8b-instruct-fp16",
            )

    def _get_source_records(
        self, max_records_to_process: int = 50000
    ) -> list[dict]:
        """Query for PIRO records that haven't yet been annotated.

        For performance reasons we perform a single large query to get
        the records.
        """

        if not isinstance(max_records_to_process, int):
            raise ValueError("Invalid value for 'max_records_to_process'.")

        with self._piro_db_engine.connect() as connection:

            unannotated_records_query = text(f"""
                WITH main_query AS (
                    SELECT TOP {max_records_to_process}
                           C.CaseId,
                           CTMP.plain_Text,
                           row_number() OVER(PARTITION BY CTMP.CaseID ORDER BY CTMP.PlainTextId DESC) AS row_number
                      FROM CaseTextMasterPlain AS CTMP
                     INNER JOIN [Case] AS C ON C.CaseId = CTMP.CaseId
                     WHERE (RefLabCompName LIKE '%FINAL DIAGNOSIS%' OR RefLabCompName = '$final')
                       AND RefLabCompName <> 'CONVERTED PREVIOUS FINAL DIAGNOSIS'
                       AND C.CaseNumber LIKE 'S%'
                       AND C.CaseId NOT IN (SELECT CaseId from AnnotationData WHERE AnnotationKey = 'Is_Malignant')
                       AND C.CaseId NOT IN (SELECT CaseId from AnnotationDataError WHERE AnnotationKey = 'Is_Malignant')
                     ORDER BY C.AccessionDate DESC
                )
                SELECT CaseId, plain_Text
                  FROM main_query
                 WHERE row_number = 1
                ;
                """)  # noqa:E501

            source_records: Sequence[Row[Any]] = connection.execute(
                unannotated_records_query
            ).all()

            return self._format_source_records(source_records)

    def _format_source_records(
        self, source_records: Sequence[Row[Any]]
    ) -> list[dict]:
        """Format raw source records into dictionaries."""

        formatted_source_records: list = []
        for source_record in source_records:
            formatted_source_record = {
                "CaseId": source_record[0],
                "SourceText": source_record[1],
            }
            formatted_source_records.append(formatted_source_record)

        return formatted_source_records

    def _get_batches(self, source_records, batch_size=100) -> Generator:
        """Split the list of source_records into batches."""

        for i in range(0, len(source_records), batch_size):
            yield source_records[i : i + batch_size]  # noqa

    def _get_annotation_values(
        self, model: str, source_data_batch, max_workers=8
    ):
        """Call the LLM API to generate annotation values.

        Executes multiple calls to the LLM in parallel to improve performance.
        """

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers
        ) as executor:
            future_to_row = {
                executor.submit(
                    self._llm_call, model, row["CaseId"], row["SourceText"]
                ): row
                for row in source_data_batch
            }

            for future in concurrent.futures.as_completed(future_to_row):
                row = future_to_row[future]
                try:
                    row["AnnotationValue"] = future.result()
                except Exception as exc:
                    logger.error(f"Error generating an annotation: {exc}")

        return source_data_batch

    def _llm_call(self, model: str, case_id: int, prompt: str) -> str | None:
        """Executes a sequence of function calls to call the Ollama API
        and process the results."""

        raw_response: str = self._query_openai_endpoint(model, prompt)
        processed_response = self._process_response(raw_response)
        return self._parse_json(
            model, text=processed_response, case_id=case_id
        )

    def _query_openai_endpoint(self, model: str, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
        }

        prompt = f"{self.PREFIX}{prompt}"

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": 0,
            "top_p": 0.1,
        }

        response = requests.post(
            self._api_url,
            json=payload,
            headers=headers,
            timeout=3 * 60,
            verify=self._api_verify,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _process_response(self, raw_response: str) -> str:
        """Normalize model output into a JSON-like string.

        Handles plain JSON, markdown-fenced JSON, and escaped newline formats.
        """

        if not raw_response:
            return ""

        response_text: str = raw_response.strip()

        # Extract from markdown code fences when present (```json ... ```)
        fenced_json_match = re.search(
            r"```(?:json)?\s*([\s\S]*?)\s*```",
            response_text,
            re.IGNORECASE,
        )
        if fenced_json_match:
            response_text = fenced_json_match.group(1).strip()

        # Convert escaped newlines/tabs (e.g., "{\\n  ... \\n}")
        # into real text.
        if "\\n" in response_text or "\\t" in response_text:
            try:
                response_text = response_text.encode("utf-8").decode(
                    "unicode_escape"
                )
            except UnicodeDecodeError:
                pass

        # Return only the JSON object portion if extra text is present.
        json_str_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_str_match:
            return json_str_match.group(0).strip()

        return response_text

    def _parse_json(self, model: str, text: str, case_id: int) -> str | None:
        """This function finds the 'is_malignant' data element in the
        LLM-generated JSON, and extracts the value.

        Example:  {"is_malignant": "NEGATIVE"}    would extract 'NEGATIVE'
        """

        json_str_match = re.search(r"\{.*\}", text, re.DOTALL)

        try:
            if json_str_match:
                json_str: str = json_str_match.group(0)

                # Load the JSON string into a Python dictionary
                data: dict = json.loads(json_str)
                return data["is_malignant"]
            else:
                self._log_error_for_record(
                    case_id, model, error_text="NO JSON found in the output"
                )
                return None
        except Exception as e:
            self._log_error_for_record(
                case_id, model, error_text=f"ERROR in JSON_parser: {e}"
            )
            return None

    def _log_error_for_record(
        self, case_id: int, model: str, error_text: str
    ) -> None:
        """Log an error to file and capture it in the _errors attribute for
        writing to the database later."""
        logger.error(f"{case_id}: {error_text}")

        self._errors.append(
            {
                "CaseId": case_id,
                "ModelName": model,
                "AnnotationKey": "Is_Malignant",
                "ErrorMessage": error_text,
                "CreateDate": datetime.now(),
                "CreateBy": "airflow",
            }
        )

    def _eliminate_null_records(
        self, model: str, source_data_batch: list[dict]
    ) -> list[dict]:
        """Remove any records with no AnnotationValue, logging errors."""

        records_with_values: list = []

        for record in source_data_batch:
            if not record["AnnotationValue"]:
                self._log_error_for_record(
                    case_id=record["CaseId"],
                    model=model,
                    error_text="No annotation value generated for record.",
                )
            else:
                records_with_values.append(record)

        return records_with_values

    def _format_results(
        self, model: str, source_data_batch: list[dict]
    ) -> list[dict]:
        """Format the source data into a format that can be inserted into the
        database."""

        formatted_data_batch: list = []
        for record in source_data_batch:
            record["AnnotationKey"] = "Is_Malignant"
            record["ModelName"] = model
            record["CreateDate"] = datetime.now().date()
            record["CreateBy"] = "airflow"
            del record["SourceText"]
            formatted_data_batch.append(record)

        return formatted_data_batch

    def _upload_to_piro(self, results: list[dict]) -> None:
        """Write the resulting annotations to the PIRO database."""

        if results:
            insert_query = text("""
                INSERT INTO AnnotationData (CaseId, ModelName, AnnotationValue, AnnotationKey, CreateDate, CreateBy)
                VALUES (:CaseId, :ModelName, :AnnotationValue, :AnnotationKey, :CreateDate, :CreateBy)
                """)  # noqa:E501

            with self._piro_db_engine.connect() as connection:
                connection.execute(insert_query, results)
                connection.commit()

    def _write_errors_to_db(self) -> None:
        """If any errors were captured, write them to the PIRO database.

        Note that this is executed per-batch."""

        if self._errors:

            insert_query = text("""
                INSERT INTO AnnotationDataError (CaseId, ModelName, AnnotationKey, ErrorMessage, CreateDate, CreateBy)
                VALUES (:CaseId, :ModelName, :AnnotationKey, :ErrorMessage, :CreateDate, :CreateBy)
                """)  # noqa:E501

            with self._piro_db_engine.connect() as connection:
                connection.execute(insert_query, self._errors)
                connection.commit()

                self._errors = []
