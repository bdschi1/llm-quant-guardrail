
import json
from pathlib import Path

# Resolve paths relative to this file:
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_FILE = DATA_DIR / "guardrail_dataset.jsonl"

# Optional mapping from scenario file -> custom label file name
# This lets us use your existing style-tilt/tariff label file.
LABEL_OVERRIDES = {
    "draft_portfolio_ideas_style_tilt_tariffs.md": "style_tilt_tariffs_guardrail_verdict_example.json",
}


def find_label_file(scenario_filename: str) -> Path | None:
    """
    Given a scenario filename (e.g., draft_portfolio_ideas_style_tilt_tariffs.md),
    try to find a matching label JSON file in DATA_DIR.

    Search order:
      1) LABEL_OVERRIDES mapping (if present)
      2) <stem>_labels.json
      3) <stem>_guardrail_verdict.json
    """
    # 1) explicit override
    override_name = LABEL_OVERRIDES.get(scenario_filename)
    if override_name:
        override_path = DATA_DIR / override_name
        if override_path.exists():
            return override_path

    # 2) convention-based names
    stem = scenario_filename.rsplit(".", 1)[0]
    candidates = [
        DATA_DIR / f"{stem}_labels.json",
        DATA_DIR / f"{stem}_guardrail_verdict.json",
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


def build_dataset() -> None:
    """
    Build a JSONL dataset from all scenario + label pairs we can find in DATA_DIR.

    Each line in OUTPUT_FILE is:
      {
        "scenario_file": "...",
        "label_file": "...",
        "raw_idea_text": "...",
        "pm_verdict": {...}
      }
    """
    scenario_files = sorted(DATA_DIR.glob("draft_portfolio_ideas*.md"))

    if not scenario_files:
        print(f"No scenario files matching 'draft_portfolio_ideas*.md' found in {DATA_DIR}")
        return

    print("Found scenario files:")
    for sf in scenario_files:
        print(f"  - {sf.name}")

    num_written = 0

    with OUTPUT_FILE.open("w", encoding="utf-8") as out_f:
        for scenario_path in scenario_files:
            scenario_name = scenario_path.name
            label_path = find_label_file(scenario_name)

            if not label_path:
                print(f"Skipping {scenario_name}: no matching label file found in {DATA_DIR}")
                continue

            raw_text = scenario_path.read_text(encoding="utf-8")
            pm_verdict = json.loads(label_path.read_text(encoding="utf-8"))

            record = {
                "scenario_file": scenario_name,
                "label_file": label_path.name,
                "raw_idea_text": raw_text,
                "pm_verdict": pm_verdict,
            }

            out_f.write(json.dumps(record))
            out_f.write("\n")
            num_written += 1
            print(f"Added record for {scenario_name} -> {label_path.name}")

    if num_written == 0:
        print("No scenario + label pairs were found; dataset file was created but is empty.")
    else:
        print(f"\nWrote {num_written} record(s) to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_dataset()

