# llm-quant-guardrail

# **Institutional Portfolio Guardrails for LLM Outputs**

This repository aims to turn domain rules into machine-readable labels / filters
This repository implements an “online guardrail” layer for LLM-generated investment proposals. It demonstrates how a seasoned Portfolio Manager (PM) can embed institutional risk practices and quantitative logic directly into an AI workflow, so model outputs are checked for risk-efficiency and basic portfolio constraints before they are trusted or implemented.

The focus is on clear logic, transparent risk flags, and machine-readable structured output that bridges natural-language analysis and automated risk enforcement.

---

## How this repo is used for AI training

This repository shows how a PM guardrail layer can sit between raw LLM-generated investment ideas and a live portfolio by applying institutional checks before any trade is trusted. It takes free-text “Analyst LLM” proposals for long and short positions, runs them through PM-style prompts and rule-based checks, and produces both IC-style narratives and structured JSON verdicts with explicit risk flags and recommendations.

The resulting `(input text, structured verdict)` pairs serve as labeled examples for training or evaluating AI models on realistic portfolio-management decision logic.

---

## Building a training dataset

The script `src/build_guardrail_dataset.py` scans `data/` for files matching `draft_portfolio_ideas*.md` and pairs them with matching PM verdict JSON files (for example, `data/style_tilt_tariffs_guardrail_verdict_example.json`). It then writes a consolidated `data/guardrail_dataset.jsonl` where each line contains:

- The raw Analyst LLM idea text  
- The corresponding PM guardrail verdict  

This JSONL file is suitable as labeled training data for AI models.

---

## Model backends

The guardrail layer does not assume a specific model. In practice, the PM prompts and JSON verdict schema could sit on top of:

- A generic chat model (GPT-style, Anthropic-style, LLaMA-family).
- A finance-aware LLM tuned on filings, earnings calls, and research.
- Future “policy” or “risk” models that directly output structured decisions.
- The repository focuses on the institutional PM logic and machine-readable labels; any suitable LLM backend can be dropped in behind the prompts.
---

## What this demo does

This demo illustrates how a PM-style guardrail layer can sit between an LLM and a live portfolio.

### Input

- The script reads a raw markdown file from `data/`, chosen interactively from any `draft_portfolio_ideas*.md` scenario.  
- This represents unfiltered output from an “Analyst LLM” or junior PM: two proposals (one long, one short) with descriptors such as ticker, direction, size, implied volatility, crowding, and a draft thesis.

### Process

For each idea, the demo:

1. Parses the proposal into a simple structured format (ticker, direction, size, and risk/context fields).  
2. Applies role-specific system prompts (Long PM / Short PM) to simulate how a real PM would review the idea.  
3. Runs a set of guardrail checks that capture institutional concerns: crowding, risk usage, sizing sanity, and whether thesis and catalysts are coherent enough to justify putting risk on.

### Output

For each idea, the script produces:

- An IC-style narrative (written review) explaining how a PM would think about the proposal and where the risks or gaps are.  
- A machine-readable JSON verdict with a compact summary of the decision and guardrail flags (for example, crowding, aggressive sizing relative to volatility, or missing elements of a robust thesis).  
- Each verdict is a labeled training example: the input is the raw Analyst LLM text, and the output is the PM’s structured decision (flags + recommendation) that can be used as supervision for future models.

The goal of the demo is not to provide a production framework, but to show how PM judgment and institutional guardrails can be expressed in prompts, simple rules, and structured outputs that other systems (or other models) can consume.

---

## Core problem and solution

This repository encodes a simple but realistic pattern:

| Component                                          | Purpose                                                                                                         | Output format        |
|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------|
| Input contract (`data/draft_portfolio_ideas*.md`) | Raw, unconstrained investment ideas from an “Analyst LLM” or junior PM.                                        | Markdown / free text |
| PM agent prompts (`prompts/*.md`)                 | Encode a PM’s institutional risk logic (factor balance, sizing, conviction, implementation economics).         | System prompts       |
| LLM output (simulated in this demo)               | Narrative review for an investment committee plus a structured JSON verdict for risk systems.                  | Narrative + JSON     |
| Guardrail logic (`src/run_guardrail_demo.py`)     | Automated checks that read the JSON verdict and enforce hard/soft stop flags based on PM rules.                | Status + flags       |

---

## Repository structure

High-level layout:

