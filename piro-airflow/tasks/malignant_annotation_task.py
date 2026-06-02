"""
Airflow task for generating 'malignant' annotations in the PIRO database.
Uses the Ollama API on the HPC to generate the annotations, then writes
them to the PIRO database.

Original version created on Tue Apr 16 10:50:21 2024
@author: roberts10
"""

from airflow.sdk import task, TriggerRule
from tasks.annotators.malignant_annotator import MalignantAnnotator


@task(trigger_rule=TriggerRule.ALL_DONE)
def malignant_annotation_task():
    annotator = MalignantAnnotator()
    return annotator.annotate()
