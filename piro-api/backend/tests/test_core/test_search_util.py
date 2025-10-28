from core.search_util import filter_str_object

"""
Examples of Advanced Search JSON:
- {"condition":"and","rules":[{"field":"final","operator":"contains","value":"adenocarcinoma"}]}
- {"condition":"and","rules":[{"field":"final","operator":"contains","value":"adenocarcinoma"},{"field":"pathologist","operator":"contains","value":"Robertson"}]}
- {"condition":"or","rules":[{"condition":"and","rules":[{"field":"collectiondate","operator":">=","value":"2020-01-01"},{"field":"casepatientageyears","operator":"=<","value":75}]},{"condition":"and","rules":[{"field":"gender","operator":"!=","value":"Male"},{"field":"casetypecategory","operator":"not in","value":["Autopsy","Bone marrow"]}]}]}
"""  # NOQA


def test_filter_str_object_basic():
    str_input: str = '{"condition": "and", "rules": [{"field": "final", "operator": "contains", "value": "adenocarcinoma"}]}'

    result: str = filter_str_object(str_input)
    assert result == '(final: "adenocarcinoma")'


def test_filter_str_object_more_complex():
    str_input: str = '{"condition": "and", "rules": [{"field": "final", "operator": "not", "value": "Lymphoma"}, {"field": "gender", "operator": "in", "value": ["Male", "Female"]}]}'  # noqa: F401, F841

    result: str = filter_str_object(str_input)
    assert result == '(-final: "Lymphoma" AND gender:("Male", "Female"))'


def test_filter_str_object_even_more_complex():
    str_input: str = '{"condition":"or","rules":[{"condition":"and","rules":[{"field":"collectiondate","operator":">=","value":"2020-01-01"},{"field":"casepatientageyears","operator":"=<","value":75}]},{"condition":"and","rules":[{"field":"gender","operator":"!=","value":"Male"},{"field":"casetypecategory","operator":"not in","value":["Autopsy","Bone marrow"]}]}]}'  # noqa: F401, F841, E501

    result: str = filter_str_object(str_input)
    assert (
        result
        == '((collectiondate: [2020-01-01T00:00:00Z TO *] AND casepatientageyears: [* TO 75]) OR (-gender: "Male" AND -casetypecategory:("Autopsy", "Bone marrow")))'
    )  # NOQA:E501
