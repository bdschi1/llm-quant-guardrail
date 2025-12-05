from typing import Dict, Any


def mock_llm_call(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Toy implementation that fabricates a response.

    It returns the same structure that run_guardrail_demo.py expects from a real LLM:
      {
        "full_text_narrative": "...",
        "json_verdict": { ... }
      }
    """
    fake_verdict = {
        "overall_ok": False,
        "guardrail_flags": ["mock_backend"],
        "pm_recommendation": "This is a placeholder PM recommendation from the mock backend."
    }

    return {
        "full_text_narrative": (
            "This is a placeholder PM narrative from the mock LLM backend. "
            "In a real setup this would summarize the idea, highlight risks, "
            "and explain the guardrail decision."
        ),
        "json_verdict": fake_verdict,
    }


def call_llm(model_name: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Unified entry point for all LLM backends.

    For now, all backends just use the same mock. Later you can swap in
    real implementations per model_name.
    """
    if model_name in {"mock", "finllama", "gpt4"}:
        # For now they all just call the same mock
        return mock_llm_call(system_prompt, user_prompt)
    else:
        raise ValueError(f"Unknown model backend: {model_name}")

