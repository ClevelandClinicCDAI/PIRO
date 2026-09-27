import pytest

from core.llm_client import _normalize_extraction_response


@pytest.mark.parametrize(
    "raw, schema",
    [
        ([], {"tumor_site": {"type": "string"}}),
        (
            {"tumor_site": ["bad", "payload"]},
            {"tumor_site": {"type": "string"}},
        ),
    ],
)
def test_normalize_extraction_response_rejects_malformed_payloads(raw, schema):
    with pytest.raises(ValueError, match="Malformed extraction response"):
        _normalize_extraction_response(raw, schema)


def test_normalize_extraction_response_accepts_scalar_bare_value():
    schema = {"tumor_site": {"type": "string"}}

    result = _normalize_extraction_response({"tumor_site": "colon"}, schema)

    assert result["tumor_site"].value == "colon"
    assert result["tumor_site"].confidence is None
    assert result["tumor_site"].provenance is None


def test_normalize_extraction_response_accepts_null_payload():
    schema = {"tumor_site": {"type": "string"}}

    result = _normalize_extraction_response(
        {
            "tumor_site": {
                "value": None,
                "confidence": None,
                "provenance": None,
            }
        },
        schema,
    )

    assert result["tumor_site"].value is None
    assert result["tumor_site"].confidence is None
    assert result["tumor_site"].provenance is None
