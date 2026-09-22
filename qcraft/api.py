"""Generated functions accepting and returning named-coordinate values."""

from __future__ import annotations

from . import data, model
from .data import (
    _CONSTANTS_0,
    _CONSTANTS_1,
    _CONSTANTS_2,
    _CONSTANTS_3,
    _CONSTANTS_4,
    _CONSTANTS_5,
    _CONSTANTS_6,
    _CONSTANTS_7,
    _CONSTANTS_8,
    _CONSTANTS_9,
    _CONSTANTS_10,
    _CONSTANTS_11,
    _CONSTANTS_12,
    _CONSTANTS_13,
    _CONSTANTS_14,
    _CONSTANTS_15,
    _CONSTANTS_16,
    _CONSTANTS_17,
    _CONSTANTS_18,
    _CONSTANTS_19,
    _CONSTANTS_20,
    _CONSTANTS_21,
    _CONSTANTS_22,
    _CONSTANTS_23,
    _CONSTANTS_24,
    _CONSTANTS_25,
)
from .model import (
    BaselinePrimaryExpenditurePctGdpInputs,
    BaselineInterestExpenditurePctGdpInputs,
    BaselineInterestRateInputs,
    BaselinePrimaryBalancePctGdpInputs,
    BaselineOverallBalancePctGdpInputs,
    BaselineDebtToGdpInputs,
    BaselineDebtStabilizingPrimaryBalanceInputs,
    BaselineFiscalConsolidationGapInputs,
    BaselineNominalGdpGrowthInputs,
    BaselineRealGdpGrowthInputs,
    BaselineRevenuePctGdpInputs,
    BaselineEmploymentGrowthInputs,
    BaselineLabourProductivityGrowthInputs,
    BaselineGdpDeflatorGrowthInputs,
    BaselinePopulationGrowthInputs,
    ScenarioPrimaryBalancePctGdpInputs,
    ScenarioOverallBalancePctGdpInputs,
    ScenarioDebtToGdpInputs,
    ScenarioDebtStabilizingPrimaryBalanceParisInputs,
    ScenarioDebtStabilizingPrimaryBalanceModerateInputs,
    ScenarioDebtStabilizingPrimaryBalanceHighInputs,
    ScenarioDebtStabilizingPrimaryBalanceHotInputs,
    ScenarioDebtStabilizingPrimaryBalanceHotAdaptedInputs,
    ScenarioDebtStabilizingPrimaryBalanceHotUnadaptedInputs,
    ScenarioNominalGdpGrowthParisInputs,
    ScenarioNominalGdpGrowthModerateInputs,
    ScenarioNominalGdpGrowthHighInputs,
    ScenarioNominalGdpGrowthHotInputs,
    ScenarioNominalGdpGrowthHotAdaptedInputs,
    ScenarioNominalGdpGrowthHotUnadaptedInputs,
    ScenarioPrimaryExpenditurePctGdpParisInputs,
    ScenarioPrimaryExpenditurePctGdpModerateInputs,
    ScenarioPrimaryExpenditurePctGdpHighInputs,
    ScenarioPrimaryExpenditurePctGdpHotInputs,
    ScenarioPrimaryExpenditurePctGdpHotAdaptedInputs,
    ScenarioPrimaryExpenditurePctGdpHotUnadaptedInputs,
    ScenarioInterestExpenditurePctGdpParisInputs,
    ScenarioInterestExpenditurePctGdpModerateInputs,
    ScenarioInterestExpenditurePctGdpHighInputs,
    ScenarioInterestExpenditurePctGdpHotInputs,
    ScenarioInterestExpenditurePctGdpHotAdaptedInputs,
    ScenarioInterestExpenditurePctGdpHotUnadaptedInputs,
    ScenarioRealGdpLevelIndexParisInputs,
    ScenarioRealGdpLevelIndexModerateInputs,
    ScenarioRealGdpLevelIndexHighInputs,
    ScenarioRealGdpLevelIndexHotInputs,
    ScenarioRealGdpLevelIndexHotAdaptedInputs,
    ScenarioRealGdpLevelIndexHotUnadaptedInputs,
    ScenarioFiscalConsolidationGapMilestones2050Inputs,
    ScenarioFiscalConsolidationGapMilestones2075Inputs,
    ScenarioFiscalConsolidationGapMilestones2099Inputs,
)
from .runtime import publish


@publish(data.BASELINE_PRIMARY_EXPENDITURE_PCT_GDP.schema, constants=_CONSTANTS_0, cells=data.BASELINE_PRIMARY_EXPENDITURE_PCT_GDP.cells)
def compute_baseline_primary_expenditure_pct_gdp(inputs: BaselinePrimaryExpenditurePctGdpInputs) -> data.BaselinePrimaryExpenditurePctGdp:
    """Compute the baseline primary expenditure-to-GDP ratio.

    Derive the baseline scenario trajectory of primary expenditure as a share of nominal GDP, where primary expenditure grows with productivity, inflation, and total population, changing its ratio relative to GDP.

    Args:
        inputs: Baseline scenario inputs providing the macro-fiscal projections and assumptions (employment, productivity, inflation, demography, and fiscal aggregates) used to derive the baseline primary expenditure-to-GDP ratio.

    Returns:
        Baseline primary expenditure-to-GDP ratio series projected over the horizon, expressed as a share of nominal GDP.
    """
    if not isinstance(inputs, BaselinePrimaryExpenditurePctGdpInputs):
        raise TypeError(f"compute_baseline_primary_expenditure_pct_gdp() expected BaselinePrimaryExpenditurePctGdpInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_primary_expenditure_pct_gdp


@publish(data.BASELINE_INTEREST_EXPENDITURE_PCT_GDP.schema, constants=_CONSTANTS_0, cells=data.BASELINE_INTEREST_EXPENDITURE_PCT_GDP.cells)
def compute_baseline_interest_expenditure_pct_gdp(inputs: BaselineInterestExpenditurePctGdpInputs) -> data.BaselineInterestExpenditurePctGdp:
    """Compute baseline interest expenditure as a share of nominal GDP.

    Provides the baseline debt-service burden ratio used in the debt dynamics equation and overall balance calculations.

    Args:
        inputs: Baseline scenario assumptions and macro-fiscal projections, including the nominal interest rate on debt, the gross debt stock, and nominal GDP.

    Returns:
        Baseline interest expenditure-to-GDP ratio over the projection horizon.
    """
    if not isinstance(inputs, BaselineInterestExpenditurePctGdpInputs):
        raise TypeError(f"compute_baseline_interest_expenditure_pct_gdp() expected BaselineInterestExpenditurePctGdpInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_interest_expenditure_pct_gdp


@publish(data.BASELINE_INTEREST_RATE.schema, constants=_CONSTANTS_1, cells=data.BASELINE_INTEREST_RATE.cells)
def compute_baseline_interest_rate(inputs: BaselineInterestRateInputs) -> data.BaselineInterestRate:
    """Compute the baseline nominal interest rate profile for the projection horizon.

    Produces the baseline interest rate path used in the debt dynamics equation to project the debt-to-GDP ratio to 2099.

    Args:
        inputs: BaselineInterestRateInputs containing the Dashboard assumptions for the baseline scenario (including the interest rate assumption choice of constant nominal interest rate, constant nominal interest-growth differential, or constant real interest rate) together with the macro-fiscal data loaded from the IMF WEO and the productivity, inflation, and demography assumptions used to derive the nominal interest rate, interest-growth differential, and real interest rate profiles.

    Returns:
        The baseline interest rate projection, comprising the projected nominal interest rate, interest-growth differential, and real interest rate over the projection period from 2029 onwards.
    """
    if not isinstance(inputs, BaselineInterestRateInputs):
        raise TypeError(f"compute_baseline_interest_rate() expected BaselineInterestRateInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_interest_rate


@publish(data.BASELINE_PRIMARY_BALANCE_PCT_GDP.schema, constants=_CONSTANTS_0, cells=data.BASELINE_PRIMARY_BALANCE_PCT_GDP.cells)
def compute_baseline_primary_balance_pct_gdp(inputs: BaselinePrimaryBalancePctGdpInputs) -> data.BaselinePrimaryBalancePctGdp:
    """Compute the baseline primary balance as a share of nominal GDP.

    Derives the no-policy-change primary balance-to-GDP ratio that drives baseline debt dynamics.

    Args:
        inputs: Baseline scenario inputs supplying the projected revenue and primary expenditure aggregates, together with the nominal GDP decomposition used to express the resulting primary balance relative to GDP.

    Returns:
        The baseline primary balance expressed as a percent of nominal GDP, used in the debt dynamics equation to project the debt-to-GDP ratio.
    """
    if not isinstance(inputs, BaselinePrimaryBalancePctGdpInputs):
        raise TypeError(f"compute_baseline_primary_balance_pct_gdp() expected BaselinePrimaryBalancePctGdpInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_primary_balance_pct_gdp


@publish(data.BASELINE_OVERALL_BALANCE_PCT_GDP.schema, constants=_CONSTANTS_0, cells=data.BASELINE_OVERALL_BALANCE_PCT_GDP.cells)
def compute_baseline_overall_balance_pct_gdp(inputs: BaselineOverallBalancePctGdpInputs) -> data.BaselineOverallBalancePctGdp:
    """Compute the baseline overall balance as a percent of nominal GDP.

    Derive the baseline overall balance-to-GDP ratio from the projection's coordinate identities so the fiscal trajectory can be assessed against debt dynamics.

    Args:
        inputs: Baseline projection inputs supplying the revenue and primary expenditure coordinates used to derive the overall balance and the nominal GDP it is expressed against.

    Returns:
        The baseline overall balance expressed as a percent of nominal GDP.
    """
    if not isinstance(inputs, BaselineOverallBalancePctGdpInputs):
        raise TypeError(f"compute_baseline_overall_balance_pct_gdp() expected BaselineOverallBalancePctGdpInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_overall_balance_pct_gdp


@publish(data.BASELINE_DEBT_TO_GDP.schema, constants=_CONSTANTS_0, cells=data.BASELINE_DEBT_TO_GDP.cells)
def compute_baseline_debt_to_gdp(inputs: BaselineDebtToGdpInputs) -> data.BaselineDebtToGdp:
    """Project the baseline debt-to-GDP ratio.

    Derive the long-term baseline trajectory of the debt-to-GDP ratio from the debt dynamics equation using the projected primary balance, nominal interest rate, and nominal GDP growth.

    Args:
        inputs: Baseline debt-to-GDP inputs supplying the initial gross debt stock, the projected primary balance, and the interest rate and nominal GDP growth assumptions needed for the debt dynamics equation.

    Returns:
        The projected baseline debt-to-GDP ratio.
    """
    if not isinstance(inputs, BaselineDebtToGdpInputs):
        raise TypeError(f"compute_baseline_debt_to_gdp() expected BaselineDebtToGdpInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_debt_to_gdp


@publish(data.BASELINE_DEBT_STABILIZING_PRIMARY_BALANCE.schema, constants=_CONSTANTS_0, cells=data.BASELINE_DEBT_STABILIZING_PRIMARY_BALANCE.cells)
def compute_baseline_debt_stabilizing_primary_balance(inputs: BaselineDebtStabilizingPrimaryBalanceInputs) -> data.BaselineDebtStabilizingPrimaryBalance:
    """Compute the baseline debt-stabilizing primary balance for each projection year through 2099.

    Derives the primary balance, as a share of nominal GDP, needed to keep the debt-to-GDP ratio stable under the baseline debt dynamics equation.

    Args:
        inputs: Baseline inputs supplying the projected nominal GDP growth, the nominal interest rate, and the projected stock of gross debt used to evaluate the debt dynamics equation, with the binding range beginning at E37 and D37 retained as a fixed-leaf anchor.

    Returns:
        A BaselineDebtStabilizingPrimaryBalance holding the year-by-year baseline debt-stabilizing primary balance; comparing it with the projected primary balance indicates the fiscal task or the fiscal space available to the authorities.
    """
    if not isinstance(inputs, BaselineDebtStabilizingPrimaryBalanceInputs):
        raise TypeError(f"compute_baseline_debt_stabilizing_primary_balance() expected BaselineDebtStabilizingPrimaryBalanceInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_debt_stabilizing_primary_balance


@publish(data.BASELINE_FISCAL_CONSOLIDATION_GAP.schema, constants=_CONSTANTS_0, cells=data.BASELINE_FISCAL_CONSOLIDATION_GAP.cells)
def compute_baseline_fiscal_consolidation_gap(inputs: BaselineFiscalConsolidationGapInputs) -> data.BaselineFiscalConsolidationGap:
    """Compute the baseline fiscal consolidation gap from the debt-dynamics identity.

    Derive the annual gap between the projected primary balance and the debt-stabilizing primary balance needed to keep the debt-to-GDP ratio stable in the baseline scenario.

    Args:
        inputs: Baseline macro-fiscal inputs, including the primary balance, interest-growth differential, and debt-to-GDP ratio, used to evaluate the debt-dynamics identity for each projection year from 2026 onward.

    Returns:
        The baseline fiscal consolidation gap: the primary-balance adjustment per year required to stabilize the debt-to-GDP ratio, with padding leaves outside the binding range excluded.
    """
    if not isinstance(inputs, BaselineFiscalConsolidationGapInputs):
        raise TypeError(f"compute_baseline_fiscal_consolidation_gap() expected BaselineFiscalConsolidationGapInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_fiscal_consolidation_gap


@publish(data.BASELINE_NOMINAL_GDP_GROWTH.schema, constants=_CONSTANTS_2, cells=data.BASELINE_NOMINAL_GDP_GROWTH.cells)
def compute_baseline_nominal_gdp_growth(inputs: BaselineNominalGdpGrowthInputs) -> data.BaselineNominalGdpGrowth:
    """Compute baseline nominal GDP growth.

    Derive the baseline growth rate of nominal GDP from projected employment growth, labor productivity growth, and inflation.

    Args:
        inputs: Baseline component assumptions supplying employment, productivity, and inflation growth, which are summed to approximate nominal GDP growth.

    Returns:
        Baseline nominal GDP growth projections together with the component decompositions used to derive them.
    """
    if not isinstance(inputs, BaselineNominalGdpGrowthInputs):
        raise TypeError(f"compute_baseline_nominal_gdp_growth() expected BaselineNominalGdpGrowthInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_nominal_gdp_growth


@publish(data.BASELINE_REAL_GDP_GROWTH.schema, constants=_CONSTANTS_3, cells=data.BASELINE_REAL_GDP_GROWTH.cells)
def compute_baseline_real_gdp_growth(inputs: BaselineRealGdpGrowthInputs) -> data.BaselineRealGdpGrowth:
    """Compute the baseline real GDP growth path.

    Derive year-by-year real GDP growth for the baseline scenario from the production-function breakdown of nominal GDP into employment, productivity, and the GDP deflator.

    Args:
        inputs: Baseline scenario assumptions and pre-loaded macro-fiscal data used to derive employment growth (from working-age population projections), labor productivity growth, and inflation, which together determine baseline real GDP growth.

    Returns:
        The baseline real GDP growth projection for the horizon to 2099.
    """
    if not isinstance(inputs, BaselineRealGdpGrowthInputs):
        raise TypeError(f"compute_baseline_real_gdp_growth() expected BaselineRealGdpGrowthInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_real_gdp_growth


@publish(data.BASELINE_REVENUE_PCT_GDP.schema, constants=_CONSTANTS_4, cells=data.BASELINE_REVENUE_PCT_GDP.cells)
def compute_baseline_revenue_pct_gdp(inputs: BaselineRevenuePctGdpInputs) -> data.BaselineRevenuePctGdp:
    """Compute the baseline revenue-to-GDP ratio.

    Derive the baseline scenario's government revenue as a share of nominal GDP, assuming the revenue-to-GDP ratio remains constant after the WEO horizon.

    Args:
        inputs: Baseline revenue-to-GDP inputs supplying the macro-fiscal projections and assumptions from which the constant revenue-to-GDP ratio is derived.

    Returns:
        A BaselineRevenuePctGdp holding the projected baseline revenue-to-GDP ratio.
    """
    if not isinstance(inputs, BaselineRevenuePctGdpInputs):
        raise TypeError(f"compute_baseline_revenue_pct_gdp() expected BaselineRevenuePctGdpInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_revenue_pct_gdp


@publish(data.BASELINE_EMPLOYMENT_GROWTH.schema, constants=_CONSTANTS_3, cells=data.BASELINE_EMPLOYMENT_GROWTH.cells)
def compute_baseline_employment_growth(inputs: BaselineEmploymentGrowthInputs) -> data.BaselineEmploymentGrowth:
    """Compute baseline employment growth for the macro-fiscal baseline scenario.

    Derives the projected growth rate of employment from working-age (15-64) population growth, used to build the baseline nominal GDP projection.

    Args:
        inputs: Baseline employment growth inputs supplying the working-age population growth path and related baseline parameters from which the employment growth trajectory is derived.

    Returns:
        A BaselineEmploymentGrowth holding the projected employment growth series for the baseline scenario.
    """
    if not isinstance(inputs, BaselineEmploymentGrowthInputs):
        raise TypeError(f"compute_baseline_employment_growth() expected BaselineEmploymentGrowthInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_employment_growth


@publish(data.BASELINE_LABOUR_PRODUCTIVITY_GROWTH.schema, constants=_CONSTANTS_3, cells=data.BASELINE_LABOUR_PRODUCTIVITY_GROWTH.cells)
def compute_baseline_labour_productivity_growth(inputs: BaselineLabourProductivityGrowthInputs) -> data.BaselineLabourProductivityGrowth:
    """Compute the baseline labour productivity growth trajectory.

    Derives the baseline path of long-run labour productivity growth, defined as GDP per employed person, used to project nominal GDP in the Q-CRAFT baseline scenario.

    Args:
        inputs: Baseline labour productivity growth inputs, including the start-period and end-period structural productivity growth assumptions and the convergence parameters that shape the trajectory from the end of the WEO horizon through 2100.

    Returns:
        The baseline labour productivity growth trajectory, expressed as annual labour productivity growth over the projection horizon.
    """
    if not isinstance(inputs, BaselineLabourProductivityGrowthInputs):
        raise TypeError(f"compute_baseline_labour_productivity_growth() expected BaselineLabourProductivityGrowthInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_labour_productivity_growth


@publish(data.BASELINE_GDP_DEFLATOR_GROWTH.schema, constants=_CONSTANTS_5, cells=data.BASELINE_GDP_DEFLATOR_GROWTH.cells)
def compute_baseline_gdp_deflator_growth(inputs: BaselineGdpDeflatorGrowthInputs) -> data.BaselineGdpDeflatorGrowth:
    """Compute the baseline GDP deflator growth path.

    Derives the projected growth rate of the GDP deflator, which is used to translate real GDP growth into nominal GDP growth in the baseline scenario.

    Args:
        inputs: The parameter set defining the baseline scenario, including the GDP deflator path over the projection horizon.

    Returns:
        The baseline GDP deflator growth series used as an input to the nominal GDP decomposition.
    """
    if not isinstance(inputs, BaselineGdpDeflatorGrowthInputs):
        raise TypeError(f"compute_baseline_gdp_deflator_growth() expected BaselineGdpDeflatorGrowthInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_gdp_deflator_growth


@publish(data.BASELINE_POPULATION_GROWTH.schema, constants=_CONSTANTS_6, cells=data.BASELINE_POPULATION_GROWTH.cells)
def compute_baseline_population_growth(inputs: BaselinePopulationGrowthInputs) -> data.BaselinePopulationGrowth:
    """Compute the baseline population growth used in the baseline macro-fiscal scenario.

    Provide the population growth trajectory that drives long-run demographic and fiscal projections under a no-policy-change baseline.

    Args:
        inputs: Baseline population growth inputs containing the demographic assumptions needed to derive the baseline population growth.

    Returns:
        The computed baseline population growth.
    """
    if not isinstance(inputs, BaselinePopulationGrowthInputs):
        raise TypeError(f"compute_baseline_population_growth() expected BaselinePopulationGrowthInputs, got {type(inputs).__name__}")
    return model.Model(inputs).baseline_population_growth


@publish(data.SCENARIO_PRIMARY_BALANCE_PCT_GDP.schema, constants=_CONSTANTS_7, cells=data.SCENARIO_PRIMARY_BALANCE_PCT_GDP.cells)
def compute_scenario_primary_balance_pct_gdp(inputs: ScenarioPrimaryBalancePctGdpInputs) -> data.ScenarioPrimaryBalancePctGdp:
    """Compute the primary balance as a percent of GDP along each climate scenario path.

    Express the projected primary balance, in percent of nominal GDP, for the climate scenarios, excluding the baseline comparison row.

    Args:
        inputs: Scenario primary balance inputs supplying the scenario paths over which the primary balance is evaluated.

    Returns:
        Scenario primary balance as a percent of nominal GDP for each climate scenario path, excluding the baseline comparison row.
    """
    if not isinstance(inputs, ScenarioPrimaryBalancePctGdpInputs):
        raise TypeError(f"compute_scenario_primary_balance_pct_gdp() expected ScenarioPrimaryBalancePctGdpInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_primary_balance_pct_gdp


@publish(data.SCENARIO_OVERALL_BALANCE_PCT_GDP.schema, constants=_CONSTANTS_7, cells=data.SCENARIO_OVERALL_BALANCE_PCT_GDP.cells)
def compute_scenario_overall_balance_pct_gdp(inputs: ScenarioOverallBalancePctGdpInputs) -> data.ScenarioOverallBalancePctGdp:
    """Compute the overall balance as a percent of GDP for each climate scenario path.

    Projects the overall fiscal balance relative to nominal GDP along each climate change scenario through 2099, excluding the baseline comparison row.

    Args:
        inputs: Scenario computation inputs providing the macro-fiscal projections and climate scenario assumptions needed to derive overall balance as a share of GDP for each scenario path.

    Returns:
        A ScenarioOverallBalancePctGdp holding the overall-balance-to-GDP results for every climate scenario path, with no baseline comparison row.
    """
    if not isinstance(inputs, ScenarioOverallBalancePctGdpInputs):
        raise TypeError(f"compute_scenario_overall_balance_pct_gdp() expected ScenarioOverallBalancePctGdpInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_overall_balance_pct_gdp


@publish(data.SCENARIO_DEBT_TO_GDP.schema, constants=_CONSTANTS_7, cells=data.SCENARIO_DEBT_TO_GDP.cells)
def compute_scenario_debt_to_gdp(inputs: ScenarioDebtToGdpInputs) -> data.ScenarioDebtToGdp:
    """Compute the debt-to-GDP ratio for a climate scenario path.

    Projects the debt-to-GDP ratio under a climate scenario using cross-country empirical estimates of temperature impacts on GDP per capita applied to the baseline.

    Args:
        inputs: Climate scenario inputs containing the baseline macro-fiscal projections, the climate scenario path (excluding the baseline comparison row), and the associated temperature effects on real GDP per capita growth.

    Returns:
        A ScenarioDebtToGdp object holding the scenario's projected debt-to-GDP ratio.
    """
    if not isinstance(inputs, ScenarioDebtToGdpInputs):
        raise TypeError(f"compute_scenario_debt_to_gdp() expected ScenarioDebtToGdpInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_debt_to_gdp


@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_PARIS.schema, constants=_CONSTANTS_8, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_PARIS.cells)
def compute_scenario_debt_stabilizing_primary_balance_paris(inputs: ScenarioDebtStabilizingPrimaryBalanceParisInputs) -> data.ScenarioDebtStabilizingPrimaryBalanceParis:
    """Compute the debt-stabilizing primary balance under the Paris (SSP1-2.6) climate scenario.

    Derive the primary balance needed each year to 2099 to keep the debt-to-GDP ratio stable when the Paris scenario's slower productivity growth reduces nominal GDP and revenue while primary expenditure stays rigid.

    Args:
        inputs: Scenario input bundle for the Paris scenario, supplying the baseline nominal GDP path, the nominal interest rate and interest-growth differential assumptions, the WEO gross debt stock, and the Paris-scenario productivity-impact estimates used to evaluate the debt dynamics equation.

    Returns:
        The Paris-scenario debt-stabilizing primary balance series to 2099, indicating the fiscal task facing the authorities to stabilize debt relative to GDP.
    """
    if not isinstance(inputs, ScenarioDebtStabilizingPrimaryBalanceParisInputs):
        raise TypeError(f"compute_scenario_debt_stabilizing_primary_balance_paris() expected ScenarioDebtStabilizingPrimaryBalanceParisInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_debt_stabilizing_primary_balance_paris


@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_MODERATE.schema, constants=_CONSTANTS_9, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_MODERATE.cells)
def compute_scenario_debt_stabilizing_primary_balance_moderate(inputs: ScenarioDebtStabilizingPrimaryBalanceModerateInputs) -> data.ScenarioDebtStabilizingPrimaryBalanceModerate:
    """Compute the debt-stabilizing primary balance under the moderate climate scenario.

    Derive the primary balance needed to keep the debt-to-GDP ratio stable in each projection year under the moderate (SSP2-4.5) climate scenario.

    Args:
        inputs: Scenario inputs supplying the baseline macro-fiscal projections, climate-driven GDP adjustments, interest rate and nominal GDP growth assumptions, and the expenditure rigidity setting used to evaluate the debt-stabilizing primary balance.

    Returns:
        The moderate-scenario debt-stabilizing primary balance series, giving the primary balance required to hold the debt-to-GDP ratio stable in each year to 2099.
    """
    if not isinstance(inputs, ScenarioDebtStabilizingPrimaryBalanceModerateInputs):
        raise TypeError(f"compute_scenario_debt_stabilizing_primary_balance_moderate() expected ScenarioDebtStabilizingPrimaryBalanceModerateInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_debt_stabilizing_primary_balance_moderate


@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HIGH.schema, constants=_CONSTANTS_10, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HIGH.cells)
def compute_scenario_debt_stabilizing_primary_balance_high(inputs: ScenarioDebtStabilizingPrimaryBalanceHighInputs) -> data.ScenarioDebtStabilizingPrimaryBalanceHigh:
    """Compute the debt-stabilizing primary balance under the high climate scenario.

    Derive the yearly primary balance required to keep the debt-to-GDP ratio stable under the high-emissions climate scenario.

    Args:
        inputs: Scenario inputs supplying the high-scenario debt dynamics and fiscal projections used to solve for the debt-stabilizing primary balance.

    Returns:
        The projected debt-stabilizing primary balance for the high climate scenario.
    """
    if not isinstance(inputs, ScenarioDebtStabilizingPrimaryBalanceHighInputs):
        raise TypeError(f"compute_scenario_debt_stabilizing_primary_balance_high() expected ScenarioDebtStabilizingPrimaryBalanceHighInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_debt_stabilizing_primary_balance_high


@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT.schema, constants=_CONSTANTS_11, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT.cells)
def compute_scenario_debt_stabilizing_primary_balance_hot(inputs: ScenarioDebtStabilizingPrimaryBalanceHotInputs) -> data.ScenarioDebtStabilizingPrimaryBalanceHot:
    """Compute the debt-stabilizing primary balance under the Hot climate scenario.

    Derive the primary balance that holds the debt-to-GDP ratio stable each year to 2099 under the Hot scenario, where emissions follow SSP3-7.0 with 90th-percentile temperature increases.

    Args:
        inputs: Scenario inputs supplying the baseline macro-fiscal projections and Hot scenario climate effects, including the declining revenue and rigid primary expenditure paths used to derive the debt-stabilizing primary balance.

    Returns:
        A ScenarioDebtStabilizingPrimaryBalanceHot result containing the year-by-year debt-stabilizing primary balance for the Hot scenario.
    """
    if not isinstance(inputs, ScenarioDebtStabilizingPrimaryBalanceHotInputs):
        raise TypeError(f"compute_scenario_debt_stabilizing_primary_balance_hot() expected ScenarioDebtStabilizingPrimaryBalanceHotInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_debt_stabilizing_primary_balance_hot


@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_ADAPTED.schema, constants=_CONSTANTS_12, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_ADAPTED.cells)
def compute_scenario_debt_stabilizing_primary_balance_hot_adapted(inputs: ScenarioDebtStabilizingPrimaryBalanceHotAdaptedInputs) -> data.ScenarioDebtStabilizingPrimaryBalanceHotAdapted:
    """Compute the debt-stabilizing primary balance under the hot-adapted climate scenario.

    Derive the primary balance needed each year to hold the debt-to-GDP ratio stable when countries adapt quickly to the temperature increases of the hot scenario.

    Args:
        inputs: Scenario inputs supplying the macro-fiscal baseline, hot-scenario temperature effects on GDP per capita, and the faster adaptation setting used to project debt dynamics and the debt-stabilizing primary balance to 2099.

    Returns:
        A ScenarioDebtStabilizingPrimaryBalanceHotAdapted holding the projected debt-stabilizing primary balance trajectory for the hot-adapted climate scenario.
    """
    if not isinstance(inputs, ScenarioDebtStabilizingPrimaryBalanceHotAdaptedInputs):
        raise TypeError(f"compute_scenario_debt_stabilizing_primary_balance_hot_adapted() expected ScenarioDebtStabilizingPrimaryBalanceHotAdaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_debt_stabilizing_primary_balance_hot_adapted


@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_UNADAPTED.schema, constants=_CONSTANTS_13, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_UNADAPTED.cells)
def compute_scenario_debt_stabilizing_primary_balance_hot_unadapted(inputs: ScenarioDebtStabilizingPrimaryBalanceHotUnadaptedInputs) -> data.ScenarioDebtStabilizingPrimaryBalanceHotUnadapted:
    """Compute the debt-stabilizing primary balance under the hot un-adapted climate scenario.

    Project the primary balance needed to keep the debt-to-GDP ratio stable when temperatures rise as in the hot scenario and countries adapt only slowly, with the m adaptation parameter set to 50 years.

    Args:
        inputs: Scenario inputs supplying the hot un-adapted climate path and the baseline macro-fiscal projections, from which the debt dynamics equation and the debt-stabilizing primary balance series are derived.

    Returns:
        A ScenarioDebtStabilizingPrimaryBalanceHotUnadapted holding the annual debt-stabilizing primary balance to 2099 under the hot un-adapted climate scenario.
    """
    if not isinstance(inputs, ScenarioDebtStabilizingPrimaryBalanceHotUnadaptedInputs):
        raise TypeError(f"compute_scenario_debt_stabilizing_primary_balance_hot_unadapted() expected ScenarioDebtStabilizingPrimaryBalanceHotUnadaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_debt_stabilizing_primary_balance_hot_unadapted


@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_PARIS.schema, constants=_CONSTANTS_14, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_PARIS.cells)
def compute_scenario_nominal_gdp_growth_paris(inputs: ScenarioNominalGdpGrowthParisInputs) -> data.ScenarioNominalGdpGrowthParis:
    """Compute nominal GDP growth for the Paris climate scenario.

    Derives the Paris (SSP1-2.6) scenario path of nominal GDP growth in the engine sheet, where real GDP declines relative to the baseline as climate change slows productivity growth.

    Args:
        inputs: Scenario inputs supplying the preloaded macro-fiscal series and climate scenario parameters used to derive the Paris path of nominal GDP growth.

    Returns:
        The Paris scenario nominal GDP growth series, including the real GDP level from which index and deviation measures relative to the baseline can be derived.
    """
    if not isinstance(inputs, ScenarioNominalGdpGrowthParisInputs):
        raise TypeError(f"compute_scenario_nominal_gdp_growth_paris() expected ScenarioNominalGdpGrowthParisInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_nominal_gdp_growth_paris


@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_MODERATE.schema, constants=_CONSTANTS_15, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_MODERATE.cells)
def compute_scenario_nominal_gdp_growth_moderate(inputs: ScenarioNominalGdpGrowthModerateInputs) -> data.ScenarioNominalGdpGrowthModerate:
    """Compute long-term nominal GDP growth under the Moderate climate scenario.

    Derive nominal GDP growth for the Moderate (SSP2-4.5) scenario, where mitigation policies continue along observed trends and temperature rises roughly in line with the 1960-2014 trend.

    Args:
        inputs: Inputs used to derive nominal GDP under the Moderate climate scenario, including the baseline projections and climate-related slowdown in productivity growth that feed into nominal GDP growth.

    Returns:
        The Moderate scenario's nominal GDP projections, including the growth rate and level from which index and deviation measures can be derived.
    """
    if not isinstance(inputs, ScenarioNominalGdpGrowthModerateInputs):
        raise TypeError(f"compute_scenario_nominal_gdp_growth_moderate() expected ScenarioNominalGdpGrowthModerateInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_nominal_gdp_growth_moderate


@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_HIGH.schema, constants=_CONSTANTS_16, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_HIGH.cells)
def compute_scenario_nominal_gdp_growth_high(inputs: ScenarioNominalGdpGrowthHighInputs) -> data.ScenarioNominalGdpGrowthHigh:
    """Project nominal GDP growth under the High climate scenario.

    Provide the High (SSP3-7.0) climate-scenario shard of the nominal GDP growth engine sheet, capturing how contracting real GDP lowers employment, productivity, and price growth.

    Args:
        inputs: ScenarioNominalGdpGrowthHighInputs bundle holding the baseline nominal GDP decomposition (employment, productivity, and GDP deflator growth) together with the High-scenario temperature impact on GDP per capita growth used to derive the scenario trajectory.

    Returns:
        A ScenarioNominalGdpGrowthHigh record with the projected nominal GDP growth path under the High climate scenario, consistent with the baseline decomposition of employment, productivity, and inflation.
    """
    if not isinstance(inputs, ScenarioNominalGdpGrowthHighInputs):
        raise TypeError(f"compute_scenario_nominal_gdp_growth_high() expected ScenarioNominalGdpGrowthHighInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_nominal_gdp_growth_high


@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_HOT.schema, constants=_CONSTANTS_17, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_HOT.cells)
def compute_scenario_nominal_gdp_growth_hot(inputs: ScenarioNominalGdpGrowthHotInputs) -> data.ScenarioNominalGdpGrowthHot:
    """Compute nominal GDP growth under the hot climate scenario.

    Projects nominal GDP growth for the hot scenario, in which emissions follow the high pathway but temperature increases are taken at the 90th percentile of climate model projections, so that lower labor productivity reduces nominal GDP growth along the no-policy-change baseline.

    Args:
        inputs: Scenario inputs carrying the baseline nominal GDP decomposition and the hot-scenario climate impact on productivity growth used to derive nominal GDP growth.

    Returns:
        A `ScenarioNominalGdpGrowthHot` result containing the projected nominal GDP growth under the hot climate scenario.
    """
    if not isinstance(inputs, ScenarioNominalGdpGrowthHotInputs):
        raise TypeError(f"compute_scenario_nominal_gdp_growth_hot() expected ScenarioNominalGdpGrowthHotInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_nominal_gdp_growth_hot


@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_ADAPTED.schema, constants=_CONSTANTS_18, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_ADAPTED.cells)
def compute_scenario_nominal_gdp_growth_hot_adapted(inputs: ScenarioNominalGdpGrowthHotAdaptedInputs) -> data.ScenarioNominalGdpGrowthHotAdapted:
    """Compute nominal GDP growth for the hot adapted climate scenario.

    Derive the hot adapted scenario's nominal GDP growth path, where countries adapt more quickly to the same temperature increases as in the hot scenario.

    Args:
        inputs: Scenario nominal GDP growth hot adapted input parameters.

    Returns:
        A ScenarioNominalGdpGrowthHotAdapted holding the computed nominal GDP growth values for the hot adapted scenario.
    """
    if not isinstance(inputs, ScenarioNominalGdpGrowthHotAdaptedInputs):
        raise TypeError(f"compute_scenario_nominal_gdp_growth_hot_adapted() expected ScenarioNominalGdpGrowthHotAdaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_nominal_gdp_growth_hot_adapted


@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_UNADAPTED.schema, constants=_CONSTANTS_19, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_UNADAPTED.cells)
def compute_scenario_nominal_gdp_growth_hot_unadapted(inputs: ScenarioNominalGdpGrowthHotUnadaptedInputs) -> data.ScenarioNominalGdpGrowthHotUnadapted:
    """Compute nominal GDP growth for the hot un-adapted climate scenario.

    Provide the nominal GDP growth path under the hot un-adapted scenario, in which temperatures rise as in the hot scenario but countries adapt to climate change slowly, so that the drag on labor productivity and therefore on nominal GDP is more severe.

    Args:
        inputs: Scenario inputs for the hot un-adapted climate scenario, bundling the baseline nominal GDP decomposition (employment, productivity, and GDP deflator growth) with the scenario's temperature impact and slow adaptation assumptions.

    Returns:
        A scenario result containing the projected nominal GDP growth for the hot un-adapted climate scenario.
    """
    if not isinstance(inputs, ScenarioNominalGdpGrowthHotUnadaptedInputs):
        raise TypeError(f"compute_scenario_nominal_gdp_growth_hot_unadapted() expected ScenarioNominalGdpGrowthHotUnadaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_nominal_gdp_growth_hot_unadapted


@publish(data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_PARIS.schema, constants=_CONSTANTS_8, cells=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_PARIS.cells)
def compute_scenario_primary_expenditure_pct_gdp_paris(inputs: ScenarioPrimaryExpenditurePctGdpParisInputs) -> data.ScenarioPrimaryExpenditurePctGdpParis:
    """Compute the Paris scenario's primary expenditure as a share of GDP.

    Derive the primary-expenditure-to-GDP ratio under the Paris climate scenario from the imported inputs and their coordinate identities.

    Args:
        inputs: Input values for the Paris climate scenario used to derive the primary-expenditure-to-GDP ratio.

    Returns:
        The Paris scenario's primary expenditure as a percentage of GDP for each period.
    """
    if not isinstance(inputs, ScenarioPrimaryExpenditurePctGdpParisInputs):
        raise TypeError(f"compute_scenario_primary_expenditure_pct_gdp_paris() expected ScenarioPrimaryExpenditurePctGdpParisInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_primary_expenditure_pct_gdp_paris


@publish(data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_MODERATE.schema, constants=_CONSTANTS_9, cells=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_MODERATE.cells)
def compute_scenario_primary_expenditure_pct_gdp_moderate(inputs: ScenarioPrimaryExpenditurePctGdpModerateInputs) -> data.ScenarioPrimaryExpenditurePctGdpModerate:
    """Project primary expenditure as a share of GDP under the moderate climate scenario.

    Produce the moderate-scenario primary expenditure-to-GDP path implied by rigid primary expenditure and climate-driven nominal GDP losses.

    Args:
        inputs: Moderate-scenario projection inputs carrying the baseline primary expenditure level and the nominal GDP path under the moderate climate scenario, used to derive the primary expenditure-to-GDP ratio.

    Returns:
        A moderate-scenario projection holding the primary expenditure-to-GDP ratio over the projection horizon.
    """
    if not isinstance(inputs, ScenarioPrimaryExpenditurePctGdpModerateInputs):
        raise TypeError(f"compute_scenario_primary_expenditure_pct_gdp_moderate() expected ScenarioPrimaryExpenditurePctGdpModerateInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_primary_expenditure_pct_gdp_moderate


@publish(data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HIGH.schema, constants=_CONSTANTS_10, cells=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HIGH.cells)
def compute_scenario_primary_expenditure_pct_gdp_high(inputs: ScenarioPrimaryExpenditurePctGdpHighInputs) -> data.ScenarioPrimaryExpenditurePctGdpHigh:
    """Compute the high climate scenario's primary expenditure ratio to nominal GDP.

    Yield the high (SSP3-7.0) scenario's primary expenditure-to-GDP ratio, which rises above baseline as rigid expenditure meets a smaller climate-adjusted GDP.

    Args:
        inputs: Authored inputs for the high climate scenario engine sheet, supplying the baseline and scenario parameters needed to derive the primary expenditure ratio to nominal GDP.

    Returns:
        The high climate scenario's primary expenditure-to-GDP ratio under Q-CRAFT scenario assumptions.
    """
    if not isinstance(inputs, ScenarioPrimaryExpenditurePctGdpHighInputs):
        raise TypeError(f"compute_scenario_primary_expenditure_pct_gdp_high() expected ScenarioPrimaryExpenditurePctGdpHighInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_primary_expenditure_pct_gdp_high


@publish(data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT.schema, constants=_CONSTANTS_11, cells=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT.cells)
def compute_scenario_primary_expenditure_pct_gdp_hot(inputs: ScenarioPrimaryExpenditurePctGdpHotInputs) -> data.ScenarioPrimaryExpenditurePctGdpHot:
    """Compute the primary expenditure-to-GDP ratio under the hot climate scenario.

    Derive the engine-sheet primary expenditure share of nominal GDP for the hot scenario, where emissions follow the high path but temperature increase is taken at the 90th percentile of SSP3-7.0 projections.

    Args:
        inputs: Scenario primary expenditure inputs holding the baseline primary expenditure level in local currency and the hot-scenario nominal GDP path used to express expenditure as a share of GDP.

    Returns:
        The hot-scenario primary expenditure-to-GDP ratio, which rises above the baseline as rigid primary expenditure meets a lower nominal GDP.
    """
    if not isinstance(inputs, ScenarioPrimaryExpenditurePctGdpHotInputs):
        raise TypeError(f"compute_scenario_primary_expenditure_pct_gdp_hot() expected ScenarioPrimaryExpenditurePctGdpHotInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_primary_expenditure_pct_gdp_hot


@publish(data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_ADAPTED.schema, constants=_CONSTANTS_12, cells=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_ADAPTED.cells)
def compute_scenario_primary_expenditure_pct_gdp_hot_adapted(inputs: ScenarioPrimaryExpenditurePctGdpHotAdaptedInputs) -> data.ScenarioPrimaryExpenditurePctGdpHotAdapted:
    """Compute the primary expenditure-to-GDP ratio for the hot adapted climate scenario.

    Provide the engine-sheet primary expenditure ratio for the hot adapted scenario, where countries adapt more quickly to the same temperature increases as in the hot scenario.

    Args:
        inputs: Input bundle holding the coordinates required to derive the hot adapted scenario primary expenditure-to-GDP ratio.

    Returns:
        The hot adapted scenario primary expenditure-to-GDP ratio result.
    """
    if not isinstance(inputs, ScenarioPrimaryExpenditurePctGdpHotAdaptedInputs):
        raise TypeError(f"compute_scenario_primary_expenditure_pct_gdp_hot_adapted() expected ScenarioPrimaryExpenditurePctGdpHotAdaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_primary_expenditure_pct_gdp_hot_adapted


@publish(data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.schema, constants=_CONSTANTS_13, cells=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.cells)
def compute_scenario_primary_expenditure_pct_gdp_hot_unadapted(inputs: ScenarioPrimaryExpenditurePctGdpHotUnadaptedInputs) -> data.ScenarioPrimaryExpenditurePctGdpHotUnadapted:
    """Compute the primary expenditure-to-GDP ratio for the Hot Un-Adapted climate scenario.

    Produces the engine-sheet series for the Hot Un-Adapted scenario, in which temperature increases match the Hot scenario but countries adapt to climate change more slowly.

    Args:
        inputs: ScenarioPrimaryExpenditurePctGdpHotUnAdaptedInputs bundle providing the engine-sheet coordinates and scenario parameters from which the primary expenditure-to-GDP trajectory is derived.

    Returns:
        A ScenarioPrimaryExpenditurePctGdpHotUnAdapted result containing the projected primary expenditure-to-GDP ratio for the Hot Un-Adapted scenario.
    """
    if not isinstance(inputs, ScenarioPrimaryExpenditurePctGdpHotUnadaptedInputs):
        raise TypeError(f"compute_scenario_primary_expenditure_pct_gdp_hot_unadapted() expected ScenarioPrimaryExpenditurePctGdpHotUnadaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_primary_expenditure_pct_gdp_hot_unadapted


@publish(data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_PARIS.schema, constants=_CONSTANTS_8, cells=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_PARIS.cells)
def compute_scenario_interest_expenditure_pct_gdp_paris(inputs: ScenarioInterestExpenditurePctGdpParisInputs) -> data.ScenarioInterestExpenditurePctGdpParis:
    """Compute interest expenditure as a percent of GDP for the Paris climate scenario.

    Derives the ratio of government interest expenditure to nominal GDP along the Paris scenario path, where Paris assumes international commitments from the 2015 Paris summit are met and warming stays below 2°C.

    Args:
        inputs: Scenario interest-expenditure-to-GDP inputs for the Paris climate scenario, supplying the debt stock, interest rate assumptions, and nominal GDP projections needed to derive the ratio over the projection horizon.

    Returns:
        The Paris scenario interest expenditure as a percent of GDP path, aligned to the projection horizon of the engine sheet.
    """
    if not isinstance(inputs, ScenarioInterestExpenditurePctGdpParisInputs):
        raise TypeError(f"compute_scenario_interest_expenditure_pct_gdp_paris() expected ScenarioInterestExpenditurePctGdpParisInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_interest_expenditure_pct_gdp_paris


@publish(data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_MODERATE.schema, constants=_CONSTANTS_9, cells=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_MODERATE.cells)
def compute_scenario_interest_expenditure_pct_gdp_moderate(inputs: ScenarioInterestExpenditurePctGdpModerateInputs) -> data.ScenarioInterestExpenditurePctGdpModerate:
    """Return the moderate-scenario interest expenditure as a share of nominal GDP.

    Project the interest expenditure ratio under the Moderate climate scenario, where mitigation policies continue along observed trends.

    Args:
        inputs: Moderate-scenario inputs supplying the real GDP level and the fiscal variables used to derive interest expenditure as a percentage of nominal GDP.

    Returns:
        A ScenarioInterestExpenditurePctGdpModerate object holding the projected interest expenditure-to-GDP ratio for the Moderate climate scenario.
    """
    if not isinstance(inputs, ScenarioInterestExpenditurePctGdpModerateInputs):
        raise TypeError(f"compute_scenario_interest_expenditure_pct_gdp_moderate() expected ScenarioInterestExpenditurePctGdpModerateInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_interest_expenditure_pct_gdp_moderate


@publish(data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HIGH.schema, constants=_CONSTANTS_10, cells=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HIGH.cells)
def compute_scenario_interest_expenditure_pct_gdp_high(inputs: ScenarioInterestExpenditurePctGdpHighInputs) -> data.ScenarioInterestExpenditurePctGdpHigh:
    """Compute interest expenditure as a percent of GDP for the high-emissions climate scenario.

    Derives the high scenario's interest expenditure-to-GDP ratio from the scenario's debt dynamics, where climate-driven declines in nominal GDP raise primary deficits and debt, in turn raising interest expenditure.

    Args:
        inputs: Scenario inputs holding the high-emissions climate scenario's macro-fiscal projections, including real GDP level and the baseline fiscal and interest rate assumptions used to project debt and interest expenditure.

    Returns:
        A ScenarioInterestExpenditurePctGdpHigh object containing the high scenario's projected interest expenditure as a percent of GDP.
    """
    if not isinstance(inputs, ScenarioInterestExpenditurePctGdpHighInputs):
        raise TypeError(f"compute_scenario_interest_expenditure_pct_gdp_high() expected ScenarioInterestExpenditurePctGdpHighInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_interest_expenditure_pct_gdp_high


@publish(data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT.schema, constants=_CONSTANTS_11, cells=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT.cells)
def compute_scenario_interest_expenditure_pct_gdp_hot(inputs: ScenarioInterestExpenditurePctGdpHotInputs) -> data.ScenarioInterestExpenditurePctGdpHot:
    """Compute interest expenditure as a percent of GDP for the Hot climate scenario.

    Derive the Hot scenario's interest expenditure-to-GDP ratio from the scenario's macro-fiscal projections, in which emissions follow the high pathway but temperature increases are taken at the 90th percentile.

    Args:
        inputs: Scenario inputs for the Hot climate scenario, supplying the baseline and climate-affected macro-fiscal projections used to derive the interest expenditure-to-GDP ratio.

    Returns:
        An object containing the Hot scenario's interest expenditure as a percent of GDP over the projection horizon.
    """
    if not isinstance(inputs, ScenarioInterestExpenditurePctGdpHotInputs):
        raise TypeError(f"compute_scenario_interest_expenditure_pct_gdp_hot() expected ScenarioInterestExpenditurePctGdpHotInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_interest_expenditure_pct_gdp_hot


@publish(data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_ADAPTED.schema, constants=_CONSTANTS_12, cells=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_ADAPTED.cells)
def compute_scenario_interest_expenditure_pct_gdp_hot_adapted(inputs: ScenarioInterestExpenditurePctGdpHotAdaptedInputs) -> data.ScenarioInterestExpenditurePctGdpHotAdapted:
    """Compute interest expenditure as a percent of GDP under the Hot Adapted climate scenario.

    Project interest expenditure relative to nominal GDP for the Hot Adapted climate scenario, where countries adapt to higher temperatures more quickly.

    Args:
        inputs: Inputs for the Hot Adapted scenario, carrying the baseline fiscal settings and debt dynamics needed to derive interest expenditure as a share of GDP.

    Returns:
        Interest expenditure as a percentage of nominal GDP for the Hot Adapted climate scenario.
    """
    if not isinstance(inputs, ScenarioInterestExpenditurePctGdpHotAdaptedInputs):
        raise TypeError(f"compute_scenario_interest_expenditure_pct_gdp_hot_adapted() expected ScenarioInterestExpenditurePctGdpHotAdaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_interest_expenditure_pct_gdp_hot_adapted


@publish(data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.schema, constants=_CONSTANTS_13, cells=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.cells)
def compute_scenario_interest_expenditure_pct_gdp_hot_unadapted(inputs: ScenarioInterestExpenditurePctGdpHotUnadaptedInputs) -> data.ScenarioInterestExpenditurePctGdpHotUnadapted:
    """Compute interest expenditure as a share of GDP for the Hot Un-Adapted climate scenario.

    Derive the scenario's interest expenditure-to-GDP ratio to trace how slower GDP growth under hot un-adapted temperatures raises interest burdens relative to output.

    Args:
        inputs: Scenario inputs for the Hot Un-Adapted climate scenario, which shares the hot scenario's temperature increases while assuming countries adapt to climate change only slowly.

    Returns:
        The Hot Un-Adapted scenario's interest expenditure as a percentage of GDP.
    """
    if not isinstance(inputs, ScenarioInterestExpenditurePctGdpHotUnadaptedInputs):
        raise TypeError(f"compute_scenario_interest_expenditure_pct_gdp_hot_unadapted() expected ScenarioInterestExpenditurePctGdpHotUnadaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_interest_expenditure_pct_gdp_hot_unadapted


@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_PARIS.schema, constants=_CONSTANTS_20, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_PARIS.cells)
def compute_scenario_real_gdp_level_index_paris(inputs: ScenarioRealGdpLevelIndexParisInputs) -> data.ScenarioRealGdpLevelIndexParis:
    """Compute the Paris scenario real GDP level index.

    Project the real GDP level path under the Paris climate scenario so it can be used for index and deviation derivation.

    Args:
        inputs: Validated input bundle for the Paris scenario real GDP level index helper, supplying the scenario parameters and baseline projections used in the coordinate identities.

    Returns:
        A ScenarioRealGdpLevelIndexParis holding the projected real GDP level index under the Paris scenario.
    """
    if not isinstance(inputs, ScenarioRealGdpLevelIndexParisInputs):
        raise TypeError(f"compute_scenario_real_gdp_level_index_paris() expected ScenarioRealGdpLevelIndexParisInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_real_gdp_level_index_paris


@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_MODERATE.schema, constants=_CONSTANTS_21, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_MODERATE.cells)
def compute_scenario_real_gdp_level_index_moderate(inputs: ScenarioRealGdpLevelIndexModerateInputs) -> data.ScenarioRealGdpLevelIndexModerate:
    """Compute the real GDP level index for the moderate climate change scenario.

    Derive the real GDP level under the moderate (SSP2-4.5) scenario so it can be expressed as an index or deviation relative to the baseline.

    Args:
        inputs: Scenario inputs for the moderate climate change case, providing the baseline real GDP level and the moderate-scenario GDP-per-capita growth effects used to derive the indexed real GDP level.

    Returns:
        The moderate-scenario real GDP level index series, suitable for index or deviation derivation against the baseline.
    """
    if not isinstance(inputs, ScenarioRealGdpLevelIndexModerateInputs):
        raise TypeError(f"compute_scenario_real_gdp_level_index_moderate() expected ScenarioRealGdpLevelIndexModerateInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_real_gdp_level_index_moderate


@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_HIGH.schema, constants=_CONSTANTS_22, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_HIGH.cells)
def compute_scenario_real_gdp_level_index_high(inputs: ScenarioRealGdpLevelIndexHighInputs) -> data.ScenarioRealGdpLevelIndexHigh:
    """Compute the real GDP level index for the high-emissions climate scenario.

    Derive the high scenario's real GDP level index relative to the baseline, supporting index and deviation measures of climate change's macroeconomic impact.

    Args:
        inputs: Scenario inputs providing the high-emissions climate scenario's real GDP level path along which the index is derived.

    Returns:
        The high-emissions scenario's real GDP level index result.
    """
    if not isinstance(inputs, ScenarioRealGdpLevelIndexHighInputs):
        raise TypeError(f"compute_scenario_real_gdp_level_index_high() expected ScenarioRealGdpLevelIndexHighInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_real_gdp_level_index_high


@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT.schema, constants=_CONSTANTS_23, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT.cells)
def compute_scenario_real_gdp_level_index_hot(inputs: ScenarioRealGdpLevelIndexHotInputs) -> data.ScenarioRealGdpLevelIndexHot:
    """Compute the real GDP level index for the hot climate scenario.

    Derive the hot scenario's real GDP level index, supporting index and deviation-based analysis of climate-driven output losses relative to the baseline.

    Args:
        inputs: Scenario real GDP level index inputs for the hot climate scenario, carrying the baseline and scenario assumptions needed to derive the index.

    Returns:
        The hot climate scenario real GDP level index, expressed as a level index suitable for index or deviation derivation relative to the baseline.
    """
    if not isinstance(inputs, ScenarioRealGdpLevelIndexHotInputs):
        raise TypeError(f"compute_scenario_real_gdp_level_index_hot() expected ScenarioRealGdpLevelIndexHotInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_real_gdp_level_index_hot


@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_ADAPTED.schema, constants=_CONSTANTS_24, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_ADAPTED.cells)
def compute_scenario_real_gdp_level_index_hot_adapted(inputs: ScenarioRealGdpLevelIndexHotAdaptedInputs) -> data.ScenarioRealGdpLevelIndexHotAdapted:
    """Compute the real GDP level index for the hot-adapted climate scenario.

    Produces the real GDP level path for the hot-adapted climate scenario, where temperatures follow the hot scenario but countries adapt more quickly, so that the level index can support index and deviation derivations.

    Args:
        inputs: Engine-sheet shard inputs for one climate scenario carrying the coordinate identities from which the hot-adapted real GDP level index is derived.

    Returns:
        A ScenarioRealGdpLevelIndexHotAdapted holding the real GDP level index for the hot-adapted climate scenario.
    """
    if not isinstance(inputs, ScenarioRealGdpLevelIndexHotAdaptedInputs):
        raise TypeError(f"compute_scenario_real_gdp_level_index_hot_adapted() expected ScenarioRealGdpLevelIndexHotAdaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_real_gdp_level_index_hot_adapted


@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_UNADAPTED.schema, constants=_CONSTANTS_25, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_UNADAPTED.cells)
def compute_scenario_real_gdp_level_index_hot_unadapted(inputs: ScenarioRealGdpLevelIndexHotUnadaptedInputs) -> data.ScenarioRealGdpLevelIndexHotUnadapted:
    """Compute the real GDP level index for the hot un-adapted climate scenario.

    Produce a real GDP level series for the hot un-adapted scenario, supporting index or deviation derivation against the baseline.

    Args:
        inputs: Scenario inputs for the hot un-adapted climate scenario, providing the parameters and data needed to derive the real GDP level index.

    Returns:
        The real GDP level index for the hot un-adapted climate scenario, suitable for index or deviation derivation.
    """
    if not isinstance(inputs, ScenarioRealGdpLevelIndexHotUnadaptedInputs):
        raise TypeError(f"compute_scenario_real_gdp_level_index_hot_unadapted() expected ScenarioRealGdpLevelIndexHotUnadaptedInputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_real_gdp_level_index_hot_unadapted


@publish(data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2050.schema, constants=_CONSTANTS_7, cells=data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2050.cells)
def compute_scenario_fiscal_consolidation_gap_milestones_2050(inputs: ScenarioFiscalConsolidationGapMilestones2050Inputs) -> data.ScenarioFiscalConsolidationGapMilestones2050:
    """Compute the 2050 PB Gap milestone for climate output scenarios.

    Populate the 2050 primary-balance gap milestone column on the Output Scenarios worksheet for each climate scenario.

    Args:
        inputs: Scenario inputs supplying the climate-scenario projections and DSPB triplet start year needed to place the 2050 PB Gap milestone.

    Returns:
        The 2050 PB Gap milestone by climate scenario for the Output Scenarios worksheet.
    """
    if not isinstance(inputs, ScenarioFiscalConsolidationGapMilestones2050Inputs):
        raise TypeError(f"compute_scenario_fiscal_consolidation_gap_milestones_2050() expected ScenarioFiscalConsolidationGapMilestones2050Inputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_fiscal_consolidation_gap_milestones_2050


@publish(data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2075.schema, constants=_CONSTANTS_7, cells=data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2075.cells)
def compute_scenario_fiscal_consolidation_gap_milestones_2075(inputs: ScenarioFiscalConsolidationGapMilestones2075Inputs) -> data.ScenarioFiscalConsolidationGapMilestones2075:
    """Compute the 2075 PB gap milestone for the Output Scenarios climate rows.

    Report the 2075 primary balance fiscal consolidation gap milestone on Output Scenarios for the climate scenarios, with the Baseline row treated as internal and year headers filled from the DSPB triplet start.

    Args:
        inputs: Scenario fiscal consolidation gap milestone inputs supplying the PB gap milestone column for 2075, restricted to the climate scenarios, with the Baseline row internal and year headers filled from the DSPB triplet start.

    Returns:
        The 2075 PB gap milestone value for the climate scenarios on Output Scenarios, with the Baseline row internal.
    """
    if not isinstance(inputs, ScenarioFiscalConsolidationGapMilestones2075Inputs):
        raise TypeError(f"compute_scenario_fiscal_consolidation_gap_milestones_2075() expected ScenarioFiscalConsolidationGapMilestones2075Inputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_fiscal_consolidation_gap_milestones_2075


@publish(data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2099.schema, constants=_CONSTANTS_7, cells=data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2099.cells)
def compute_scenario_fiscal_consolidation_gap_milestones_2099(inputs: ScenarioFiscalConsolidationGapMilestones2099Inputs) -> data.ScenarioFiscalConsolidationGapMilestones2099:
    """Compute the 2099 primary balance gap milestones for the climate scenarios.

    Provide the 2099 PB gap milestone column shown on the Output Scenarios worksheet, filling year headers from the DSPB triplet start.

    Args:
        inputs: Scenario fiscal consolidation gap milestone inputs supplying the climate scenario selection and the DSPB triplet start used to fill the 2099 year header.

    Returns:
        The 2099 primary balance gap milestones for the climate scenarios (the Baseline row is internal).
    """
    if not isinstance(inputs, ScenarioFiscalConsolidationGapMilestones2099Inputs):
        raise TypeError(f"compute_scenario_fiscal_consolidation_gap_milestones_2099() expected ScenarioFiscalConsolidationGapMilestones2099Inputs, got {type(inputs).__name__}")
    return model.Model(inputs).scenario_fiscal_consolidation_gap_milestones_2099


__all__ = [
    "BaselinePrimaryExpenditurePctGdpInputs",
    "BaselineInterestExpenditurePctGdpInputs",
    "BaselineInterestRateInputs",
    "BaselinePrimaryBalancePctGdpInputs",
    "BaselineOverallBalancePctGdpInputs",
    "BaselineDebtToGdpInputs",
    "BaselineDebtStabilizingPrimaryBalanceInputs",
    "BaselineFiscalConsolidationGapInputs",
    "BaselineNominalGdpGrowthInputs",
    "BaselineRealGdpGrowthInputs",
    "BaselineRevenuePctGdpInputs",
    "BaselineEmploymentGrowthInputs",
    "BaselineLabourProductivityGrowthInputs",
    "BaselineGdpDeflatorGrowthInputs",
    "BaselinePopulationGrowthInputs",
    "ScenarioPrimaryBalancePctGdpInputs",
    "ScenarioOverallBalancePctGdpInputs",
    "ScenarioDebtToGdpInputs",
    "ScenarioDebtStabilizingPrimaryBalanceParisInputs",
    "ScenarioDebtStabilizingPrimaryBalanceModerateInputs",
    "ScenarioDebtStabilizingPrimaryBalanceHighInputs",
    "ScenarioDebtStabilizingPrimaryBalanceHotInputs",
    "ScenarioDebtStabilizingPrimaryBalanceHotAdaptedInputs",
    "ScenarioDebtStabilizingPrimaryBalanceHotUnadaptedInputs",
    "ScenarioNominalGdpGrowthParisInputs",
    "ScenarioNominalGdpGrowthModerateInputs",
    "ScenarioNominalGdpGrowthHighInputs",
    "ScenarioNominalGdpGrowthHotInputs",
    "ScenarioNominalGdpGrowthHotAdaptedInputs",
    "ScenarioNominalGdpGrowthHotUnadaptedInputs",
    "ScenarioPrimaryExpenditurePctGdpParisInputs",
    "ScenarioPrimaryExpenditurePctGdpModerateInputs",
    "ScenarioPrimaryExpenditurePctGdpHighInputs",
    "ScenarioPrimaryExpenditurePctGdpHotInputs",
    "ScenarioPrimaryExpenditurePctGdpHotAdaptedInputs",
    "ScenarioPrimaryExpenditurePctGdpHotUnadaptedInputs",
    "ScenarioInterestExpenditurePctGdpParisInputs",
    "ScenarioInterestExpenditurePctGdpModerateInputs",
    "ScenarioInterestExpenditurePctGdpHighInputs",
    "ScenarioInterestExpenditurePctGdpHotInputs",
    "ScenarioInterestExpenditurePctGdpHotAdaptedInputs",
    "ScenarioInterestExpenditurePctGdpHotUnadaptedInputs",
    "ScenarioRealGdpLevelIndexParisInputs",
    "ScenarioRealGdpLevelIndexModerateInputs",
    "ScenarioRealGdpLevelIndexHighInputs",
    "ScenarioRealGdpLevelIndexHotInputs",
    "ScenarioRealGdpLevelIndexHotAdaptedInputs",
    "ScenarioRealGdpLevelIndexHotUnadaptedInputs",
    "ScenarioFiscalConsolidationGapMilestones2050Inputs",
    "ScenarioFiscalConsolidationGapMilestones2075Inputs",
    "ScenarioFiscalConsolidationGapMilestones2099Inputs",
    "compute_baseline_primary_expenditure_pct_gdp",
    "compute_baseline_interest_expenditure_pct_gdp",
    "compute_baseline_interest_rate",
    "compute_baseline_primary_balance_pct_gdp",
    "compute_baseline_overall_balance_pct_gdp",
    "compute_baseline_debt_to_gdp",
    "compute_baseline_debt_stabilizing_primary_balance",
    "compute_baseline_fiscal_consolidation_gap",
    "compute_baseline_nominal_gdp_growth",
    "compute_baseline_real_gdp_growth",
    "compute_baseline_revenue_pct_gdp",
    "compute_baseline_employment_growth",
    "compute_baseline_labour_productivity_growth",
    "compute_baseline_gdp_deflator_growth",
    "compute_baseline_population_growth",
    "compute_scenario_primary_balance_pct_gdp",
    "compute_scenario_overall_balance_pct_gdp",
    "compute_scenario_debt_to_gdp",
    "compute_scenario_debt_stabilizing_primary_balance_paris",
    "compute_scenario_debt_stabilizing_primary_balance_moderate",
    "compute_scenario_debt_stabilizing_primary_balance_high",
    "compute_scenario_debt_stabilizing_primary_balance_hot",
    "compute_scenario_debt_stabilizing_primary_balance_hot_adapted",
    "compute_scenario_debt_stabilizing_primary_balance_hot_unadapted",
    "compute_scenario_nominal_gdp_growth_paris",
    "compute_scenario_nominal_gdp_growth_moderate",
    "compute_scenario_nominal_gdp_growth_high",
    "compute_scenario_nominal_gdp_growth_hot",
    "compute_scenario_nominal_gdp_growth_hot_adapted",
    "compute_scenario_nominal_gdp_growth_hot_unadapted",
    "compute_scenario_primary_expenditure_pct_gdp_paris",
    "compute_scenario_primary_expenditure_pct_gdp_moderate",
    "compute_scenario_primary_expenditure_pct_gdp_high",
    "compute_scenario_primary_expenditure_pct_gdp_hot",
    "compute_scenario_primary_expenditure_pct_gdp_hot_adapted",
    "compute_scenario_primary_expenditure_pct_gdp_hot_unadapted",
    "compute_scenario_interest_expenditure_pct_gdp_paris",
    "compute_scenario_interest_expenditure_pct_gdp_moderate",
    "compute_scenario_interest_expenditure_pct_gdp_high",
    "compute_scenario_interest_expenditure_pct_gdp_hot",
    "compute_scenario_interest_expenditure_pct_gdp_hot_adapted",
    "compute_scenario_interest_expenditure_pct_gdp_hot_unadapted",
    "compute_scenario_real_gdp_level_index_paris",
    "compute_scenario_real_gdp_level_index_moderate",
    "compute_scenario_real_gdp_level_index_high",
    "compute_scenario_real_gdp_level_index_hot",
    "compute_scenario_real_gdp_level_index_hot_adapted",
    "compute_scenario_real_gdp_level_index_hot_unadapted",
    "compute_scenario_fiscal_consolidation_gap_milestones_2050",
    "compute_scenario_fiscal_consolidation_gap_milestones_2075",
    "compute_scenario_fiscal_consolidation_gap_milestones_2099",
]
