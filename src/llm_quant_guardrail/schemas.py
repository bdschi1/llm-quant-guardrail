from typing import List, Optional, Literal
from pydantic import BaseModel, Field


Direction = Literal["LONG", "SHORT", "FLAT"]
Decision = Literal["LONG", "SHORT", "PASS", "WAIT"]


class ScenarioInput(BaseModel):
    """
    Minimal container for the scenario + data that will be passed into
    the Analyst and PM agents.
    """
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    region: Optional[str] = None

    scenario_narrative: str = Field(
        ...,
        description="Text description of the business, industry, and scenario setup."
    )

    positioning_data: Optional[dict] = None
    market_data: Optional[dict] = None
    factor_data: Optional[dict] = None
    options_data: Optional[dict] = None


class AnalystDraft(BaseModel):
    """
    Output of the upstream 'Analyst' LLM (or human): a naive trade idea
    that the PM agent will grade and correct.
    """
    ticker: str
    direction: Direction
    naive_size_bps: Optional[float] = Field(
        default=None,
        description="Naive position size in basis points of portfolio risk or capital."
    )
    narrative: str = Field(
        ...,
        description="Free-text thesis and rationale from the upstream analyst."
    )


class ShortPMOutput(BaseModel):
    """
    Parsed JSON object for the Short PM agent, matching the schema in
    short_pm_system_prompt.md.
    """
    ticker: str
    direction: Literal["SHORT", "FLAT"]
    conviction_score: float
    conviction_label: Literal["low", "medium", "high"]
    decision: Decision

    risk_target_bps: Optional[float] = None
    risk_target_vol_contribution_pct: Optional[float] = None

    portfolio_impact: Optional[
        Literal["improves_diversification", "worsens_concentration", "neutral"]
    ] = None

    alpha_vs_factor_grade: Optional[
        Literal[
            "pass_idiosyncratic_dominant",
            "fail_factor_dominated",
            "inconclusive",
        ]
    ] = None
    factor_risk_share_pct: Optional[float] = None
    idiosyncratic_risk_share_pct: Optional[float] = None
    sizing_efficiency_loss_pct: Optional[float] = None

    factor_concentration_flag: Optional[bool] = None
    options_liquidity_flag: Optional[bool] = None
    implied_move_vs_expected: Optional[
        Literal[
            "implied_greater_than_expected",
            "implied_less_than_expected",
            "implied_in_line",
            "unknown",
        ]
    ] = None

    key_catalysts: List[str] = []
    main_conviction_up_levers: List[str] = []
    main_conviction_down_levers: List[str] = []
    main_thesis_kill_switches: List[str] = []

    crowding_flag: Optional[bool] = None
    borrow_risk_flag: Optional[bool] = None

    implementation_recommendation: Optional[str] = None


class LongPMOutput(BaseModel):
    """
    Parsed JSON object for the Long PM agent, matching the schema in
    long_pm_system_prompt.md.
    """
    ticker: str
    direction: Literal["LONG", "FLAT"]
    conviction_score: float
    conviction_label: Literal["low", "medium", "high"]
    decision: Decision

    expected_upside_pct: Optional[float] = None
    expected_downside_pct: Optional[float] = None

    risk_target_bps: Optional[float] = None
    risk_target_vol_contribution_pct: Optional[float] = None

    portfolio_impact: Optional[str] = None  # e.g. "worsens_growth_concentration"

    alpha_vs_factor_grade: Optional[
        Literal[
            "pass_idiosyncratic_dominant",
            "fail_factor_dominated",
            "inconclusive",
        ]
    ] = None
    factor_risk_share_pct: Optional[float] = None
    idiosyncratic_risk_share_pct: Optional[float] = None
    sizing_efficiency_loss_pct: Optional[float] = None

    factor_concentration_flag: Optional[bool] = None
    liquidity_risk_flag: Optional[bool] = None
    options_liquidity_flag: Optional[bool] = None
    implied_move_vs_expected: Optional[
        Literal[
            "implied_greater_than_expected",
            "implied_less_than_expected",
            "implied_in_line",
            "unknown",
        ]
    ] = None

    key_catalysts: List[str] = []
    main_conviction_up_levers: List[str] = []
    main_conviction_down_levers: List[str] = []
    main_thesis_kill_switches: List[str] = []

    crowding_flag: Optional[bool] = None

    implementation_recommendation: Optional[str] = None
