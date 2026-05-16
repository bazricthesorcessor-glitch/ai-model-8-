from schemas import ArticleSummary
from web.schema_service import SchemaService


def test_schema_validation_round_trip():
    service = SchemaService()
    payload = {"title": "T", "summary": "S", "key_points": []}
    model = service.validate(ArticleSummary, payload)
    assert model.title == "T"

