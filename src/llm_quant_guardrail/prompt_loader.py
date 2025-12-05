from pathlib import Path


def load_prompt(name: str) -> str:
    """
    Load a prompt file from the prompts/ directory relative to the project root.
    """
    base = Path(__file__).resolve().parents[2]  # project root
    prompt_path = base / "prompts" / name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")
