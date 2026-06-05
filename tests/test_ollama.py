from nutriplan.llm.client import resolve_llm_model
from nutriplan.llm.ollama_util import list_ollama_models, ollama_is_running, resolve_ollama_litellm_model


def test_ollama_list_on_dev_machine():
    if not ollama_is_running():
        return
    models = list_ollama_models()
    assert len(models) >= 1
    resolved = resolve_ollama_litellm_model()
    assert resolved and resolved.startswith("ollama/")
    assert resolve_llm_model() is not None