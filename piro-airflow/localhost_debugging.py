import datetime
from tasks.converters.rtf_to_plain_text_epic_comment_converter import (
    RTFToPlainTextEpicCommentConverter,
)
from tasks.annotators.malignant_annotator import MalignantAnnotator
from tasks.loaders.solr_cohort_data_loader import SolrCohortDataLoader
from tasks.loaders.solr_case_data_loader import SolrCaseDataLoader
from tasks.loaders.solr_cohort_data_delete import SolrCohortDataDelete
from tasks.loaders.solr_case_suggest_loader import SolrCaseSuggestLoader
from tasks.loaders.solr_case_staff_loader import SolrCaseStaffLoader
from tasks.loaders.concentriq_case_loader import ConcentriqCaseLoader

runRTFToText: bool = False
runMalignant: bool = False
runCohort: bool = False
runCase: bool = False
runCohortDelete: bool = False
runCaseSuggest: bool = False
runCaseStaffSuggest: bool = False
runConcentriqCase: bool = False
runConcentriqCaseReload: bool = False

if runRTFToText:
    print("----------------------------------------------")
    print("Debug - Start")
    rtf_to_plain_text_converter = RTFToPlainTextEpicCommentConverter()
    print(rtf_to_plain_text_converter.convert(max_cases_to_process=1000))
    print("Debug - End")
    print("")

if runMalignant:
    print("----------------------------------------------")
    print("Debug - Start")
    malignant_annotator = MalignantAnnotator()
    print(malignant_annotator.annotate(max_records_to_process=200))
    print("Debug - End")
    print("")

if runCohort:
    print("----------------------------------------------")
    print("Debug - Start")
    cohort_loader = SolrCohortDataLoader()
    # print(case_loader._load_data(7))
    a = datetime.datetime.now()
    print(cohort_loader.upload_records_to_solr(49))
    b = datetime.datetime.now()
    print(f"Time elapsed: {b - a}")
    print(cohort_loader.reset_data_for_next_load(7))
    print(cohort_loader.close_db_connection())
    print("Debug - End")
    print("")

if runCase:
    print("----------------------------------------------")
    print("Debug - Start")
    case_loader = SolrCaseDataLoader()
    is_trigger = case_loader.are_there_records_to_load()
    print(f"is_trigger: {is_trigger}")
    if is_trigger:
        # print(case_loader._load_data())
        # print(case_loader._reset_case_data())
        a = datetime.datetime.now()
        print(case_loader.upload_records_to_solr())
        b = datetime.datetime.now()
        print(f"Time elapsed: {b - a}")
    print(case_loader.close_db_connection())
    print("Debug - End")
    print("")

if runCohortDelete:
    print("----------------------------------------------")
    print("Debug - Start")
    cohort_loader = SolrCohortDataDelete()
    print(cohort_loader.delete_data())
    print(cohort_loader.close_db_connection())
    print("Debug - End")
    print("")

if runCaseSuggest:
    print("----------------------------------------------")
    print("Debug - Start")
    case_loader = SolrCaseSuggestLoader()
    is_trigger = case_loader.are_there_records_to_load()
    print(f"is_trigger: {is_trigger}")
    if is_trigger:
        # print(case_loader._load_data())
        # print(case_loader._reset_case_data())
        a = datetime.datetime.now()
        print(case_loader.upload_records_to_solr())
        b = datetime.datetime.now()
        print(f"Time elapsed: {b - a}")
    print(case_loader.close_db_connection())
    print("Debug - End")
    print("")


if runCaseStaffSuggest:
    print("----------------------------------------------")
    print("Debug - Start")
    case_loader = SolrCaseStaffLoader()
    is_trigger = case_loader.are_there_records_to_load()
    print(f"is_trigger: {is_trigger}")
    if is_trigger:
        # print(case_loader._load_data())
        # print(case_loader._reset_case_data())
        a = datetime.datetime.now()
        print(case_loader.upload_records_to_solr())
        b = datetime.datetime.now()
        print(f"Time elapsed: {b - a}")
    print(case_loader.close_db_connection())
    print("Debug - End")
    print("")


if runConcentriqCase:
    print("----------------------------------------------")
    print("Debug - Start")
    case_loader = ConcentriqCaseLoader()
    is_trigger = case_loader.should_we_process_concentriq_data()
    print(f"is_trigger: {is_trigger}")
    if is_trigger:
        # print(case_loader._load_data())
        # print(case_loader._reset_case_data())
        a = datetime.datetime.now()
        print(case_loader.get_concentriq_data())
        b = datetime.datetime.now()
        print(f"Time elapsed: {b - a}")
    print(case_loader.close_db_connection())
    print("Debug - End")
    print("")


if runConcentriqCaseReload:
    print("----------------------------------------------")
    print("Debug - Start")
    case_loader = ConcentriqCaseLoader()
    result = case_loader.delete_concentriq_case_data()
    print(f"result: {result}")
    print(case_loader.close_db_connection())
    print("Debug - End")
    print("")
