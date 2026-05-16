from web.ollama_client import OllamaClient


def test_list_models_uses_request_json():
    client = OllamaClient()
    client._request_json = lambda method, url, payload=None: (True, {"models": [{"name": "llama"}]}, None)
    result = client.list_models()
    assert result["success"] is True
    assert result["result"]["models"][0]["name"] == "llama"

