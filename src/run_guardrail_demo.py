import json
import os
import shutil
from collections import defaultdict
from typing import Dict, Any, List
from pathlib import Path

# --- Configuration and File Paths ---
DESKTOP_DIR = Path.home() / "Desktop"DATA_DIR = "data"
PROMPTS_DIR = "prompts"
DESKTOP_DIR = Path.home() / "Desktop"
PROMPTS_DIR = 'prompts'
DATA_DIR = "data"
#INPUT_IDEAS_FILE = "draft_portfolio_ideas2.md"  # or whatever exact name you use
LONG_PM_PROMPT_FILE = 'long_pm_system_prompt.md'
SHORT_PM_PROMPT_FILE = 'short_pm_system_prompt.md'
INPUT_IDEAS_FILE = 'draft_portfolio_ideas.md'

# Output Filenames
REPO_OUTPUT_JSON = 'guardrail_verdict.json'
REPO_OUTPUT_TXT = 'guardrail_verdict.txt'

# The directory to copy reports to on the user's desktop
DESKTOP_OUTPUT_DIR = Path.home() / 'Desktop' / 'guardrail_outputs'


# --- 1. Utility Functions ---

def load_file_content(filepath: str) -> str:
    """Loads the content of a file relative to the script location."""
    try:
        current_dir = os.path.dirname(__file__)
        # Navigate up one directory to the repo root
        repo_root = os.path.abspath(os.path.join(current_dir, '..'))
        full_path = os.path.join(repo_root, filepath)
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Required file not found at {full_path}")
        return ""


def parse_input_ideas(input_content: str) -> List[Dict[str, str]]:
    """
    Parses the structured Markdown input file into a list of dictionaries.
    """
    ideas: List[Dict[str, str]] = []
    current_idea: Dict[str, str] = {}
    
    for line in input_content.split('\n'):
        # Check for headers
        if (
            line.strip().startswith('## Idea 1: Long Proposal')
            or line.strip().startswith('## Idea 2: Short Proposal')
        ):
            if current_idea:
                ideas.append(current_idea)
            current_idea = {'proposal_header': line.strip()}
            
        # Check for key-value pairs (e.g. **Ticker:** ACME)
        elif current_idea and ':' in line:
            try:
                key_part, value_part = line.split(':', 1)
                key = (
                    key_part.strip()
                    .lower()
                    .replace('*', '')
                    .replace(' ', '_')
                    .replace('.', '')
                )
                current_idea[key] = value_part.strip()
            except Exception:
                continue
    
    if current_idea:
        ideas.append(current_idea)
    
    return ideas


def generate_text_report(verdicts: Dict[str, Dict[str, Any]]) -> str:
    """
    Formats the verdicts into a human-readable text memo.
    """
    lines = [
        "QUANT-GUARDRAIL VERDICT REPORT",
        "=" * 40,
        "",
    ]
    
    if not verdicts:
        lines.append("NO TRADES PROCESSED. (Check input data parsing)")
    
    for ticker, data in verdicts.items():
        direction = data.get('direction', 'UNKNOWN')
        guardrail = data.get('guardrail_check', {})
        status = guardrail.get('status', 'UNKNOWN')
        message = guardrail.get('message', 'No message')
        narrative = data.get('pm_narrative', '').strip()
        
        lines.append(f"TICKER: {ticker} ({direction})")
        lines.append(f"VERDICT: {status}")
        lines.append("-" * 40)
        lines.append(f"Guardrail Message: {message}")
        lines.append("")
        lines.append("PM AGENT NARRATIVE:")
        lines.append(narrative)
        lines.append("\n" + "=" * 40 + "\n")
        
    return "\n".join(lines)


# --- 2. LLM Simulation (Mock) ---

def mock_llm_call(
    system_prompt: str,
    user_query: str,
    ticker: str,
    direction: str,
) -> Dict[str, Any]:
    """
    Simulates the call to an LLM agent (e.g., Gemini).
    """
    ticker_for_log = ticker or "UNKNOWN"
    print(f"\n--- Simulating LLM Call: {ticker_for_log} ({direction}) ---")
    
    # --- MOCKING THE LLM RESPONSE (Actual output will vary) ---
    if direction.upper() == "LONG":
        narrative = """

### 3.2 Long Thesis, Mispricing, Margin of Safety, and Conviction
The core long thesis on ACME remains valid on a 3-year horizon driven by secular AI adoption. However, the current proposed sizing and high 1.4 Beta suggest the majority of the risk budget is being used for high-growth factor exposure rather than idiosyncratic alpha. The conviction is Medium-High (4.0), but fragile, as any shift in the momentum factor regime could lead to a sharp, factor-driven drawdown inconsistent with the idiosyncratic view. The proposal is currently under-budgeted for idiosyncratic risk and over-budgeted for factor risk.

### 3.4 Risk Units, Sizing, and Portfolio Fit
The proposed $5.0M notional size is inefficient. Given the high volatility (35%) and Beta (1.4), this concentration significantly worsens our existing Growth/Momentum factor exposure. We require a **40% reduction in notional** to de-risk the factor exposure and bring the position into alignment with a volatility-targeted 0.8% VaR contribution. The position *worsens_growth_concentration* and requires immediate adjustment.

### 3.7 One-Minute, 5-Bullet Executive Summary (Mandatory)
1. **Thesis & edge:** Strong secular growth, but high factor tilt masks true alpha.
2. **Conviction:** Medium-High (4.0), but *fragile* due to crowding. Upside 40%, Downside 15%.
3. **Risk size & portfolio impact:** Proposed size is too large. Worsens Growth factor concentration.
4. **Key catalysts:** Q4 Earnings (immediate check) and Analyst Day.
5. **Decision & immediate action:** **GUARDRAIL FAIL**. Approve at reduced size only.
"""
        json_verdict = {
            "ticker": ticker,
            "direction": "LONG",
            "conviction_score": 4.0,
            "conviction_label": "high",
            "decision": "GUARDRAIL_FAIL",
            "expected_upside_pct": 40.0,
            "expected_downside_pct": 15.0,
            "risk_target_bps": 80,
            "risk_target_vol_contribution_pct": 0.8,
            "portfolio_impact": "worsens_growth_concentration",
            "alpha_vs_factor_grade": "fail_factor_dominated",
            "factor_risk_share_pct": 55.0,
            "idiosyncratic_risk_share_pct": 45.0,
            "sizing_efficiency_loss_pct": 25.0,
            "factor_concentration_flag": True,
            "crowding_flag": True,
            "implementation_recommendation": "reduce_size_by_40_percent_to_mitigate_factor_risk",
        }
    else:  # SHORT
        narrative = """
### 3.2 Short Thesis, Mispricing, and Conviction
The Short thesis on BAUX is fundamentally sound, driven by cyclical peak and financial execution issues. However, the estimated idiosyncratic alpha is low, meaning the expected return is highly reliant on a macro factor (cyclicals/global growth). More critically, the **Borrow Cost (4% annualized)** represents a significant drag that could fully erode the thin alpha edge if the position is held longer than 9 months without the expected catalyst (legal judgment). The risk/reward asymmetry is poor on an implementation basis.

### 3.4 Risk Units, Sizing, and Portfolio Fit
The proposed size is reasonable on volatility, but the high **cost of carry** (4% borrow) makes this trade uneconomical relative to the expected edge. This short uses up precious borrow allocation for a factor-dominated trade, which is against the PM's rule to treat the short book as an *independent alpha engine*. The idiosyncratic alpha needs to be significantly higher to justify the cost/risk.

### 3.7 One-Minute, 5-Bullet Executive Summary (Mandatory)
1. **Thesis & edge:** Sound cyclical peak view, but edge is low and highly macro-dependent.
2. **Conviction & asymmetry:** Low (2.5), primarily due to poor implementation economics. Downside 30%, Upside (Loss) 10%.
3. **Risk size & portfolio impact:** Uses borrow budget for a factor-dominated, low-alpha trade.
4. **Key catalysts:** Q2 Legal Judgment (Too distant given high borrow cost).
5. **Decision & immediate action:** **PASS/REJECT**. Not economical for the short book.
"""
        json_verdict = {
            "ticker": ticker,
            "direction": "SHORT",
            "conviction_score": 2.5,
            "conviction_label": "low",
            "decision": "PASS/REJECT",
            "risk_target_bps": 50,
            "risk_target_vol_contribution_pct": 0.6,
            "portfolio_impact": "uses_expensive_borrow_for_low_alpha",
            "alpha_vs_factor_grade": "fail_factor_dominated",
            "factor_risk_share_pct": 70.0,
            "idiosyncratic_risk_share_pct": 30.0,
            "sizing_efficiency_loss_pct": 0.0,
            "factor_concentration_flag": False,
            "crowding_flag": False,
            "borrow_risk_flag": True,
            "implementation_recommendation": "pass_due_to_borrow_cost_vs_alpha",
        }
    
    return {
        "full_text_narrative": narrative,
        "json_verdict": json_verdict,
    }


# --- 3. Guardrail Enforcement Logic ---

def enforce_guardrails(verdict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies simple institutional rules using the machine-readable JSON output.
    """
    
    ticker = verdict.get('ticker', 'N/A')
    direction = verdict.get('direction', 'N/A')
    
    # 1. Decision Guardrail
    if verdict.get('decision') not in ['LONG', 'SHORT']:
        return {
            "status": "HARD_FAIL",
            "message": f"PM Agent REJECTED/PASSED trade. Decision: {verdict.get('decision')}.",
            "reason": "PM agent explicitly vetoed the trade on qualitative/implementation grounds.",
        }
        
    # 2. Factor Concentration Guardrail
    if verdict.get('factor_concentration_flag'):
        if verdict.get('factor_risk_share_pct', 0) > 50:
            return {
                "status": "SOFT_FAIL_ADJUSTMENT_REQUIRED",
                "message": f"LONG-A: High factor risk share ({verdict['factor_risk_share_pct']}%) detected. Must adjust size.",
                "reason": verdict.get('implementation_recommendation', 'Reduce size or hedge factor exposure.'),
            }
             
    # 3. Borrow Cost Guardrail
    if direction == 'SHORT' and verdict.get('borrow_risk_flag'):
        return {
            "status": "HARD_FAIL",
            "message": "SHORT-B: Trade flagged for high borrow cost/risk. Implementation failure.",
            "reason": verdict.get('implementation_recommendation', 'Borrow cost too high relative to alpha edge.'),
        }

    return {
        "status": "PASS",
        "message": f"{direction} trade on {ticker} approved. Complies with all quantitative risk checks.",
        "reason": "All PM guardrails passed.",
    }

DATA_DIR = "data"

def choose_input_file() -> str:
    """
    Interactively choose which draft_portfolio_ideas* file to use from DATA_DIR.

    Returns the filename (not the full path).
    """
    candidates = [
        f for f in os.listdir(DATA_DIR)
        if f.startswith("draft_portfolio_ideas") and os.path.isfile(os.path.join(DATA_DIR, f))
    ]

    if not candidates:
        print(f"No draft_portfolio_ideas* files found in {DATA_DIR}/.")
        raise SystemExit(1)

    candidates.sort()

    print("Available idea files in data/:")
    for idx, name in enumerate(candidates, start=1):
        print(f"  [{idx}] {name}")

    while True:
        choice = input(f"Select an ideas file by number (1–{len(candidates)}): ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue

        idx = int(choice)
        if 1 <= idx <= len(candidates):
            selected = candidates[idx - 1]
            print(f"\nUsing ideas file: {selected}\n")
            return selected
        else:
            print(f"Please choose a number between 1 and {len(candidates)}.")

# --- 4. Main Execution Flow ---

def main():
    ideas_filename = choose_input_file()
    input_content = load_file_content(os.path.join(DATA_DIR, ideas_filename))

    long_pm_prompt = load_file_content(os.path.join(PROMPTS_DIR, LONG_PM_PROMPT_FILE))
    short_pm_prompt = load_file_content(os.path.join(PROMPTS_DIR, SHORT_PM_PROMPT_FILE))

    if not all([input_content, long_pm_prompt, short_pm_prompt]):
        print("Exiting due to missing input files.")
        return

    draft_ideas = parse_input_ideas(input_content)
    print(f"\n[INFO] Loaded {len(draft_ideas)} draft ideas from input file.")
    
    final_verdicts: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    # Execute LLM simulation
    for idea in draft_ideas:
        ticker = idea.get('ticker', 'UNKNOWN')
        direction = idea.get('direction', 'UNKNOWN')
        
        # Ensure proper PM selection
        if direction.upper() == 'LONG':
            system_prompt = long_pm_prompt
        elif direction.upper() == 'SHORT':
            system_prompt = short_pm_prompt
        else:
            print(f"[WARN] Skipping idea with unknown direction: {direction} (Ticker: {ticker})")
            continue
            
        user_query = f"""
Please apply the Quant-Guardrail review to the following investment proposal.

--- PM System Instruction Summary ---

You are the {direction} PM. Your task is to critique this proposal based on factor risk, sizing, and implementation economics, and output your final decision and JSON verdict.

--- Investment Proposal (Analyst Draft) ---

{idea.get('proposal_header', '')}

{json.dumps(idea, indent=2)}

--- End of Proposal ---
"""
        
        # 1. Simulate LLM Review
        llm_response = mock_llm_call(system_prompt, user_query, ticker, direction)
        
        # 2. Extract and Store Results
        final_verdicts[ticker]['direction'] = direction
        final_verdicts[ticker]['pm_narrative'] = llm_response['full_text_narrative']
        final_verdicts[ticker]['json_verdict'] = llm_response['json_verdict']
        
        # 3. Apply Automated Guardrail Check
        guardrail_result = enforce_guardrails(llm_response['json_verdict'])
        final_verdicts[ticker]['guardrail_check'] = guardrail_result
        
        print("\n\n--- PM Guardrail Verdict (Automated Check) ---")
        print(f"Status: {guardrail_result['status']}")
        print(f"Message: {guardrail_result['message']}")
        print("----------------------------------------------\n")

    # --- 5. Output Management ---
    
    # Generate Paths
    repo_json_path = os.path.join(DATA_DIR, REPO_OUTPUT_JSON)
    repo_txt_path = os.path.join(DATA_DIR, REPO_OUTPUT_TXT)
    
    # A. Write JSON Report
    print(f"--- Writing JSON Report to {repo_json_path} ---")
    with open(repo_json_path, 'w', encoding='utf-8') as f:
        json.dump(final_verdicts, f, indent=2)

    # B. Write Text Report
    text_report_content = generate_text_report(final_verdicts)
    print(f"--- Writing Text Report to {repo_txt_path} ---")
    with open(repo_txt_path, 'w', encoding='utf-8') as f:
        f.write(text_report_content)

    # C. Copy to Desktop
    DESKTOP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    desktop_json_path = DESKTOP_OUTPUT_DIR / REPO_OUTPUT_JSON
    desktop_txt_path = DESKTOP_OUTPUT_DIR / REPO_OUTPUT_TXT
    
    shutil.copyfile(repo_json_path, desktop_json_path)
    shutil.copyfile(repo_txt_path, desktop_txt_path)
    
    print(f"--- COPY SAVED to Desktop: {DESKTOP_OUTPUT_DIR} ---\n")
    print("Demo complete.")


if __name__ == "__main__":
    main()

