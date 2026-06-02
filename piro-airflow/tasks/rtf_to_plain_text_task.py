"""Airflow task for generating plain text versions of Epic comments for use
in LLM Annotations."""

from airflow.sdk import task
from tasks.converters.rtf_to_plain_text_epic_comment_converter import (
    RTFToPlainTextEpicCommentConverter,
)


@task
def rtf_to_plain_text_task(max_cases_to_process: int | None = None):
    converter = RTFToPlainTextEpicCommentConverter()
    return converter.convert(max_cases_to_process)
