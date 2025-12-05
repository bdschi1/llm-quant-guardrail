import json
from typing import Tuple

from .client import LLMClient
from .prompt_loader import load_prompt
from .schemas import ScenarioInput, AnalystDraft, ShortPMOutput


def build_short_pm_user_message(
    scenario: ScenarioInput,
    draft: AnalystDraft,
) -> str:
    """
    Compose the user-facing part of the prompt: scenario + analyst draft.
    The system prompt (persona + instructions) is loaded separately.
    """
    return f"""
You are evaluating a SHORT idea for ticker {scenario.ticker}.

SCENARIO CONTEXT:
{scenario.scenario_narrative}

POSITIONING DATA (if any):
{scenario.positioning_data}

MARKET DATA (if any):
{scenario.market_data}

FACTOR DATA (if any):
{scenario.factor_data}

OPTIONS / DERIVATIVES DATA (if any):
{scenario.options_data}

UPSTREAM ANALYST DRAFT (LLM or human):
Direction: {draft.direction}
Naive size (bps): {draft.naive_size_bps}
Narrative:
{draft.narrative}

TASK:
Apply your Short PM system instructions to:
1) Assess and, if needed, correct the thesis and sizing.
2) Produce a full IC-ready narrative following the required structure.
3) End your answer with a single valid JSON object on the final line,
   matching the Short PM JSON schema described in your system instructions.
""".strip()


def run_short_pm(
    scenario: ScenarioInput,
    draft: AnalystDraft,
    client: LLMClient | None = None,
) -> Tuple[str, ShortPMOutput]:
    """
    Run the Short PM agent:
    - send system + user messages to the LLM
    - return (full_text_response, parsed ShortPMOutput)
    """
    if client is None:
        client = LLMClient()

    system_prompt = load_prompt("short_pm_system_prompt.md")
    user_content = build_short_pm_user_message(scenario, draft)

    raw = client.chat(
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )

    # Expect JSON on the final line
        # Try to find the JSON object near the end of the response.
    # We scan from the bottom up and look for a line that looks like JSON.
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    json_line = None

    for ln in reversed(lines):
        # Skip markdown fences or obviously non-JSON lines
        if ln.startswith("```") or ln.lower().startswith("json"):
            continue
        if ln.startswith("{") and ln.endswith("}"):
            json_line = ln
            break

    if json_line is None:
        raise ValueError(
            "Failed to locate JSON object in Short PM response. "
            "Ensure the model ends with a single-line JSON object."
        )

    try:
        data = json.loads(json_line)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON from Short PM response. "
            f"Candidate JSON line was:\n{json_line}"
        ) from e

    pm_output = ShortPMOutput(**data)
    return raw, pm_output

