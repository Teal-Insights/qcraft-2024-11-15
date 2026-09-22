"""Named calculation functions for every bound formula series."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Literal, cast
from . import data
from .tensor import Domain, Series
from .excel import XlError, as_measure, xl_add, xl_bool, xl_div, xl_eq, xl_exp, xl_ge, xl_gt, xl_index, xl_le, xl_lt, xl_match, xl_mul, xl_neg, xl_pow, xl_sub
from .runtime import CoordinateReader, RealBetween, evaluate, publish, span, view

@publish(data.BASELINE_ENGINE_WORKING_AGE_POPULATION.schema, cells=data.BASELINE_ENGINE_WORKING_AGE_POPULATION.cells)
def baseline_engine_working_age_population(*, demography_working_age_population: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the working-age population used to grow baseline employment.

    Supplies the baseline scenario's working-age (15-64 year old) population so employment can be assumed to grow in line with it beyond the WEO horizon.

    Args:
        demography_working_age_population: Working-age (15-64 year old) population by projection year, taken from the selected UN demographic scenario (medium, high, or low), used as the driver of baseline employment growth after the WEO horizon.

    Returns:
        Working-age population aligned to the baseline engine's projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(demography_working_age_population[time_period])

    return data.BASELINE_ENGINE_WORKING_AGE_POPULATION.collect(evaluate(formula, data.BASELINE_ENGINE_WORKING_AGE_POPULATION.required))

@publish(data.BASELINE_ENGINE_TOTAL_POPULATION.schema, cells=data.BASELINE_ENGINE_TOTAL_POPULATION.cells)
def baseline_engine_total_population(*, demography_total_population: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Align total population with the baseline engine timeline.

    Provides the baseline scenario's total population series so that per-capita and demographic aggregates can be projected over the long-term horizon.

    Args:
        demography_total_population: Projected total population by year from the Demography worksheet, covering all age groups as published in the UN population projections.

    Returns:
        Total population by year on the baseline engine timeline, in persons.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(demography_total_population[time_period])

    return data.BASELINE_ENGINE_TOTAL_POPULATION.collect(evaluate(formula, data.BASELINE_ENGINE_TOTAL_POPULATION.required))

@dataclass(frozen=True, slots=True)
class ScanBaselineEngineRealGdpLcuResult:
    """Complete named results of one recurrence group evaluation."""
    baseline_engine_real_gdp_lcu: data.Series[float | str | None]
    baseline_real_gdp_growth: data.BaselineRealGdpGrowth
    baseline_employment_growth: data.BaselineEmploymentGrowth
    baseline_labour_productivity_growth: data.BaselineLabourProductivityGrowth

def scan_baseline_engine_real_gdp_lcu(*, baseline_engine_working_age_population: data.Series[float | str | None], macrofiscal_real_gdp_lcu: data.Series[float | str | None], macrofiscal_real_gdp_growth: data.Series[float | str | None], productivity_growth: data.Series[float | str | None]) -> ScanBaselineEngineRealGdpLcuResult:
    """Scan the baseline real GDP in local currency units and its supporting recurrence group.

    Project baseline real GDP and the associated real GDP growth, employment growth, and labour productivity growth series, grounding the baseline scenario used for long-term fiscal analysis.

    Args:
        baseline_engine_working_age_population: Projected working-age (15-64 year old) population used to grow employment once the medium-term horizon ends.
        macrofiscal_real_gdp_lcu: Real GDP in billions of local currency units from the macro-fiscal data, used through the end of the medium-term horizon.
        macrofiscal_real_gdp_growth: Real GDP growth from the macro-fiscal data, used through the end of the medium-term horizon.
        productivity_growth: Labour productivity growth, defined as GDP per employed person.

    Returns:
        A result containing the projected baseline real GDP in local currency units and the aligned baseline real GDP growth, employment growth, and labour productivity growth series.
    """
    def baseline_engine_real_gdp_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_real_gdp_lcu[time_period])
        return as_measure(xl_mul(xl_mul(baseline_engine_real_gdp_lcu[time_period - 1], xl_add(1, xl_div(baseline_employment_growth[time_period], 100))), xl_add(1, xl_div(baseline_labour_productivity_growth[time_period], 100))))

    baseline_engine_real_gdp_lcu = CoordinateReader('baseline_engine_real_gdp_lcu', data.BASELINE_ENGINE_REAL_GDP_LCU.required, baseline_engine_real_gdp_lcu_formula)
    def baseline_real_gdp_growth_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_real_gdp_growth[time_period])
        return as_measure(xl_sub(xl_mul(xl_div(baseline_engine_real_gdp_lcu[time_period], baseline_engine_real_gdp_lcu[time_period - 1]), 100), 100))

    baseline_real_gdp_growth = CoordinateReader('baseline_real_gdp_growth', data.BASELINE_REAL_GDP_GROWTH.required, baseline_real_gdp_growth_formula)
    def baseline_employment_growth_formula(time_period: int) -> float | str | None:
        if time_period <= 2021:
            return as_measure(xl_mul(xl_div(xl_sub(xl_div(baseline_real_gdp_growth[time_period], 100), xl_div(baseline_labour_productivity_growth[time_period], 100)), xl_add(1, xl_div(baseline_labour_productivity_growth[time_period], 100))), 100))
        return as_measure(xl_sub(xl_mul(xl_div(baseline_engine_working_age_population[time_period], baseline_engine_working_age_population[time_period - 1]), 100), 100))

    baseline_employment_growth = CoordinateReader('baseline_employment_growth', data.BASELINE_EMPLOYMENT_GROWTH.required, baseline_employment_growth_formula)
    def baseline_labour_productivity_growth_formula(time_period: int) -> float | str | None:
        if 2023 <= time_period <= 2029:
            return as_measure(xl_mul(xl_div(xl_sub(xl_div(baseline_real_gdp_growth[time_period], 100), xl_div(baseline_employment_growth[time_period], 100)), xl_add(1, xl_div(baseline_employment_growth[time_period], 100))), 100))
        return as_measure(productivity_growth[time_period])

    baseline_labour_productivity_growth = CoordinateReader('baseline_labour_productivity_growth', data.BASELINE_LABOUR_PRODUCTIVITY_GROWTH.required, baseline_labour_productivity_growth_formula)
    return ScanBaselineEngineRealGdpLcuResult(
        baseline_engine_real_gdp_lcu=data.BASELINE_ENGINE_REAL_GDP_LCU.collect((coord, baseline_engine_real_gdp_lcu[coord]) for coord in data.BASELINE_ENGINE_REAL_GDP_LCU.required),
        baseline_real_gdp_growth=data.BASELINE_REAL_GDP_GROWTH.collect((coord, baseline_real_gdp_growth[coord]) for coord in data.BASELINE_REAL_GDP_GROWTH.required),
        baseline_employment_growth=data.BASELINE_EMPLOYMENT_GROWTH.collect((coord, baseline_employment_growth[coord]) for coord in data.BASELINE_EMPLOYMENT_GROWTH.required),
        baseline_labour_productivity_growth=data.BASELINE_LABOUR_PRODUCTIVITY_GROWTH.collect((coord, baseline_labour_productivity_growth[coord]) for coord in data.BASELINE_LABOUR_PRODUCTIVITY_GROWTH.required),
    )

@publish(data.BASELINE_ENGINE_NOMINAL_GDP_LCU.schema, cells=data.BASELINE_ENGINE_NOMINAL_GDP_LCU.cells)
def baseline_engine_nominal_gdp_lcu(*, macrofiscal_nominal_gdp_lcu: data.Series[float | str | None], baseline_real_gdp_growth: data.BaselineRealGdpGrowth, baseline_gdp_deflator_growth: data.BaselineGdpDeflatorGrowth) -> data.Series[float | str | None]:
    """Project nominal GDP in local currency units for the baseline scenario.

    Extend nominal GDP beyond the WEO horizon by compounding real GDP growth and GDP deflator growth onto the last macrofiscal nominal GDP level.

    Args:
        macrofiscal_nominal_gdp_lcu: Nominal GDP in billions of local currency units from the macrofiscal worksheet, used through the WEO horizon as the projection base.
        baseline_real_gdp_growth: Baseline real GDP growth rate (in percent), reflecting employment and productivity growth assumptions.
        baseline_gdp_deflator_growth: Baseline growth rate of the GDP deflator (in percent), reflecting the assumed inflation path.

    Returns:
        A series of nominal GDP in local currency units covering the baseline projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_nominal_gdp_lcu[time_period])
        return as_measure(xl_mul(xl_mul(baseline_engine_nominal_gdp_lcu[time_period - 1], xl_add(1, xl_div(baseline_real_gdp_growth[time_period], 100))), xl_add(1, xl_div(baseline_gdp_deflator_growth[time_period], 100))))

    baseline_engine_nominal_gdp_lcu = CoordinateReader('baseline_engine_nominal_gdp_lcu', data.BASELINE_ENGINE_NOMINAL_GDP_LCU.required, formula)
    return data.BASELINE_ENGINE_NOMINAL_GDP_LCU.collect((coord, baseline_engine_nominal_gdp_lcu[coord]) for coord in data.BASELINE_ENGINE_NOMINAL_GDP_LCU.required)

@publish(data.BASELINE_ENGINE_REVENUE_LCU.schema, cells=data.BASELINE_ENGINE_REVENUE_LCU.cells)
def baseline_engine_revenue_lcu(*, macrofiscal_revenue_lcu: data.Series[float | str | None], baseline_nominal_gdp_growth: data.BaselineNominalGdpGrowth) -> data.Series[float | str | None]:
    """Project baseline government revenue in local currency units through 2099.

    Extend the macro-fiscal revenue series beyond the WEO horizon by growing it in line with nominal GDP so the revenue-to-GDP ratio remains constant at its baseline setting.

    Args:
        macrofiscal_revenue_lcu: Historical and WEO-period general government revenue in billions of local currency units, used directly through 2029.
        baseline_nominal_gdp_growth: Baseline nominal GDP growth rate, in percent, used to carry revenue forward in line with the broadest measure of the tax base.

    Returns:
        Baseline general government revenue in local currency units for each projected year: the macro-fiscal value through 2029 and thereafter the prior year's revenue grown by baseline nominal GDP growth, in line with a constant revenue-to-GDP ratio.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_revenue_lcu[time_period])
        return as_measure(xl_mul(baseline_engine_revenue_lcu[time_period - 1], xl_add(1, xl_div(baseline_nominal_gdp_growth[time_period], 100))))

    baseline_engine_revenue_lcu = CoordinateReader('baseline_engine_revenue_lcu', data.BASELINE_ENGINE_REVENUE_LCU.required, formula)
    return data.BASELINE_ENGINE_REVENUE_LCU.collect((coord, baseline_engine_revenue_lcu[coord]) for coord in data.BASELINE_ENGINE_REVENUE_LCU.required)

@publish(data.BASELINE_ENGINE_PRIMARY_BALANCE_LCU.schema, cells=data.BASELINE_ENGINE_PRIMARY_BALANCE_LCU.cells)
def baseline_engine_primary_balance_lcu(*, baseline_engine_revenue_lcu: data.Series[float | str | None], baseline_engine_primary_expenditure_lcu: data.Series[float | str | None], macrofiscal_primary_balance_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the baseline primary balance in local currency units.

    Derive the baseline primary balance in local currency along the projection horizon, using WEO-based figures through 2029 and revenue less primary expenditure thereafter.

    Args:
        baseline_engine_revenue_lcu: Baseline engine government revenue in billions of local currency units; assumed to remain constant as a share of nominal GDP after the end of the WEO horizon (source indicator: baseline_engine_revenue_lcu).
        baseline_engine_primary_expenditure_lcu: Baseline engine primary expenditure in billions of local currency units, excluding government interest payments; assumed to grow by productivity, inflation, and total population after the end of the WEO horizon (source indicator: baseline_engine_primary_expenditure_lcu).
        macrofiscal_primary_balance_lcu: Macro-fiscal primary balance in billions of local currency units, loaded from the IMF WEO database for the period 2001–28 (source indicator: macrofiscal_primary_balance_lcu).

    Returns:
        A series of baseline primary balance values in billions of local currency units, indexed by time period.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_primary_balance_lcu[time_period])
        return as_measure(xl_sub(baseline_engine_revenue_lcu[time_period], baseline_engine_primary_expenditure_lcu[time_period]))

    return data.BASELINE_ENGINE_PRIMARY_BALANCE_LCU.collect(evaluate(formula, data.BASELINE_ENGINE_PRIMARY_BALANCE_LCU.required))

@publish(data.BASELINE_ENGINE_OVERALL_BALANCE_LCU.schema, cells=data.BASELINE_ENGINE_OVERALL_BALANCE_LCU.cells)
def baseline_engine_overall_balance_lcu(*, baseline_engine_revenue_lcu: data.Series[float | str | None], baseline_engine_total_expenditure_lcu: data.Series[float | str | None], macrofiscal_overall_balance_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the baseline overall balance in local currency units.

    Derives the overall balance as revenue less total expenditure once the projection period begins, while preserving the loaded macro-fiscal outturn up to 2029.

    Args:
        baseline_engine_revenue_lcu: Baseline government revenue in billions of local currency units; revenue is assumed to remain constant as a share of nominal GDP after the WEO horizon.
        baseline_engine_total_expenditure_lcu: Baseline total government expenditure in billions of local currency units, inclusive of interest payments.
        macrofiscal_overall_balance_lcu: Overall balance in billions of local currency units from the Macro-fiscal worksheet, covering historical data and the IMF WEO projections through 2029.

    Returns:
        Series of the baseline overall balance in billions of local currency units for each projected year, equal to the Macro-fiscal worksheet overall balance through 2029 and revenue less total expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_overall_balance_lcu[time_period])
        return as_measure(xl_sub(baseline_engine_revenue_lcu[time_period], baseline_engine_total_expenditure_lcu[time_period]))

    return data.BASELINE_ENGINE_OVERALL_BALANCE_LCU.collect(evaluate(formula, data.BASELINE_ENGINE_OVERALL_BALANCE_LCU.required))

@publish(data.BASELINE_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.schema, cells=data.BASELINE_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.cells)
def baseline_engine_interest_expenditure_pct_revenue(*, baseline_engine_revenue_lcu: data.Series[float | str | None], baseline_engine_interest_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Interest expenditure as a percentage of revenue in the baseline scenario.

    Expresses baseline interest expenditure relative to baseline revenue, scaled to percentage points.

    Args:
        baseline_engine_revenue_lcu: Baseline government revenue in billions of local currency units, used as the denominator.
        baseline_engine_interest_expenditure_lcu: Baseline government interest expenditure in billions of local currency units, used as the numerator.

    Returns:
        A series of interest expenditure as a percentage of revenue, in percentage points, per period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(baseline_engine_interest_expenditure_lcu[time_period], baseline_engine_revenue_lcu[time_period]), 100))

    return data.BASELINE_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.collect(evaluate(formula, data.BASELINE_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.required))

@dataclass(frozen=True, slots=True)
class ScanBaselineEngineTotalExpenditurePctGdpResult:
    """Complete named results of one recurrence group evaluation."""
    baseline_engine_total_expenditure_pct_gdp: data.Series[float | str | None]
    baseline_engine_total_expenditure_lcu: data.Series[float | str | None]
    baseline_engine_interest_expenditure_lcu: data.Series[float | str | None]
    baseline_engine_primary_expenditure_lcu: data.Series[float | str | None]
    baseline_engine_gross_debt_lcu: data.Series[float | str | None]
    baseline_engine_fiscal_rule_adjustment: data.Series[float | str | None]
    baseline_engine_debt_trajectory_direction: data.Series[float | str | None]
    baseline_engine_fiscal_gap_above_target: data.Series[float | str | None]
    baseline_engine_fiscal_gap_below_target: data.Series[float | str | None]
    baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp
    baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp
    baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp
    baseline_debt_to_gdp: data.BaselineDebtToGdp
    baseline_debt_stabilizing_primary_balance: data.BaselineDebtStabilizingPrimaryBalance
    baseline_fiscal_consolidation_gap: data.BaselineFiscalConsolidationGap

def scan_baseline_engine_total_expenditure_pct_gdp(*, baseline_debt_direction_above_sentinel: float | str, baseline_debt_direction_below_sentinel: float | str, baseline_engine_nominal_gdp_lcu: data.Series[float | str | None], baseline_fiscal_rule_flag: str | int | float | bool, baseline_debt_target_above: float | str, baseline_debt_target_below: float | str, macrofiscal_expenditure_lcu: data.Series[float | str | None], macrofiscal_debt_lcu: data.Series[float | str | None], macrofiscal_interest_expenditure_lcu: data.Series[float | str | None], macrofiscal_primary_expenditure_lcu: data.Series[float | str | None], macrofiscal_primary_expenditure_pct_gdp: data.Series[float | str | None], macrofiscal_debt_to_gdp: data.Series[float | str | None], macrofiscal_primary_balance_pct_gdp: data.Series[float | str | None], baseline_interest_rate: data.BaselineInterestRate, baseline_nominal_gdp_growth: data.BaselineNominalGdpGrowth, baseline_revenue_pct_gdp: data.BaselineRevenuePctGdp, baseline_labour_productivity_growth: data.BaselineLabourProductivityGrowth, baseline_gdp_deflator_growth: data.BaselineGdpDeflatorGrowth, baseline_population_growth: data.BaselinePopulationGrowth) -> ScanBaselineEngineTotalExpenditurePctGdpResult:
    """Evaluate the baseline engine total expenditure recurrence group and publish complete tensors.

    Project total expenditure as a share of nominal GDP, along with the linked expenditure, interest, primary expenditure, debt, fiscal rule, and debt sustainability series used in the baseline scenario.

    Args:
        baseline_debt_direction_above_sentinel: Sentinel value of the debt trajectory direction indicator denoting that the debt-to-GDP ratio is above its previous-period level.
        baseline_debt_direction_below_sentinel: Sentinel value of the debt trajectory direction indicator denoting that the debt-to-GDP ratio is below its previous-period level.
        baseline_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units, used as the denominator for expenditure and fiscal ratios.
        baseline_fiscal_rule_flag: Fiscal rule assumption; when set to 'No' no debt-target adjustment is applied, otherwise the appropriate debt ceiling or floor adjustment is activated.
        baseline_debt_target_above: Debt ceiling expressed as a debt-to-GDP ratio; a value of 0 means no ceiling is applied.
        baseline_debt_target_below: Debt floor expressed as a debt-to-GDP ratio; a value of 0 means no floor is applied.
        macrofiscal_expenditure_lcu: Total general government expenditure in local currency units over the WEO horizon, taken directly as the total expenditure path through 2029.
        macrofiscal_debt_lcu: Gross general government debt in local currency units over the WEO horizon, taken directly as the debt path through 2029.
        macrofiscal_interest_expenditure_lcu: General government interest expenditure in local currency units over the WEO horizon, taken directly through 2029.
        macrofiscal_primary_expenditure_lcu: General government primary expenditure, excluding interest payments, in local currency units over the WEO horizon and the base for the projected primary expenditure path.
        macrofiscal_primary_expenditure_pct_gdp: Primary expenditure as a share of nominal GDP over the WEO horizon, taken directly through 2029.
        macrofiscal_debt_to_gdp: Gross debt-to-GDP ratio over the WEO horizon, taken directly as the initial debt ratio through 2029.
        macrofiscal_primary_balance_pct_gdp: Primary balance as a share of nominal GDP over the WEO horizon, taken directly through 2029.
        baseline_interest_rate: Weighted average nominal interest rate on government debt, used to project interest expenditure and the automatic debt dynamics.
        baseline_nominal_gdp_growth: Nominal GDP growth rate, approximated as the sum of employment growth, labor productivity growth, and GDP deflator growth, used in the debt dynamics equation.
        baseline_revenue_pct_gdp: Government revenue as a share of nominal GDP, assumed constant over the long run in the baseline scenario.
        baseline_labour_productivity_growth: Labor productivity growth, defined as GDP per employed person, used to grow primary expenditure in the long run.
        baseline_gdp_deflator_growth: Growth in the GDP deflator, used as the inflation measure to project nominal primary expenditure and nominal GDP.
        baseline_population_growth: Total population growth, used together with productivity and deflator growth to grow primary expenditure in the long run.

    Returns:
        A result object containing the complete baseline engine tensors for total expenditure as a share of GDP, total expenditure, interest expenditure, primary expenditure, gross debt, the fiscal rule adjustment, the debt trajectory direction, the fiscal gaps above and below the debt targets, primary expenditure and interest expenditure as shares of GDP, the primary balance, the debt-to-GDP ratio, the debt-stabilizing primary balance, and the fiscal consolidation gap.
    """
    def baseline_engine_total_expenditure_pct_gdp_formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(baseline_engine_total_expenditure_lcu[time_period], baseline_engine_nominal_gdp_lcu[time_period]), 100))

    baseline_engine_total_expenditure_pct_gdp = CoordinateReader('baseline_engine_total_expenditure_pct_gdp', data.BASELINE_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required, baseline_engine_total_expenditure_pct_gdp_formula)
    def baseline_engine_total_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_expenditure_lcu[time_period])
        return as_measure(xl_add(baseline_engine_interest_expenditure_lcu[time_period], baseline_engine_primary_expenditure_lcu[time_period]))

    baseline_engine_total_expenditure_lcu = CoordinateReader('baseline_engine_total_expenditure_lcu', data.BASELINE_ENGINE_TOTAL_EXPENDITURE_LCU.required, baseline_engine_total_expenditure_lcu_formula)
    def baseline_engine_interest_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_interest_expenditure_lcu[time_period])
        return as_measure(xl_mul(xl_div(baseline_interest_rate[time_period], 100), baseline_engine_gross_debt_lcu[time_period - 1]))

    baseline_engine_interest_expenditure_lcu = CoordinateReader('baseline_engine_interest_expenditure_lcu', data.BASELINE_ENGINE_INTEREST_EXPENDITURE_LCU.required, baseline_engine_interest_expenditure_lcu_formula)
    def baseline_engine_primary_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_primary_expenditure_lcu[time_period])
        return as_measure(xl_add(xl_mul(xl_mul(xl_mul(baseline_engine_primary_expenditure_lcu[time_period - 1], xl_add(1, xl_div(baseline_gdp_deflator_growth[time_period], 100))), xl_add(1, xl_div(baseline_labour_productivity_growth[time_period], 100))), xl_add(1, xl_div(baseline_population_growth[time_period], 100))), baseline_engine_fiscal_rule_adjustment[time_period - 1]))

    baseline_engine_primary_expenditure_lcu = CoordinateReader('baseline_engine_primary_expenditure_lcu', data.BASELINE_ENGINE_PRIMARY_EXPENDITURE_LCU.required, baseline_engine_primary_expenditure_lcu_formula)
    def baseline_engine_gross_debt_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_debt_lcu[time_period])
        return as_measure(xl_mul(xl_div(baseline_debt_to_gdp[time_period], 100), baseline_engine_nominal_gdp_lcu[time_period]))

    baseline_engine_gross_debt_lcu = CoordinateReader('baseline_engine_gross_debt_lcu', data.BASELINE_ENGINE_GROSS_DEBT_LCU.required, baseline_engine_gross_debt_lcu_formula)
    def baseline_engine_fiscal_rule_adjustment_formula(time_period: int) -> float | str | None:
        return as_measure((0 if xl_bool(xl_eq(baseline_fiscal_rule_flag, 'No')) else (baseline_engine_fiscal_gap_above_target[time_period] if xl_bool(xl_eq(baseline_engine_debt_trajectory_direction[time_period], baseline_debt_direction_above_sentinel)) else (baseline_engine_fiscal_gap_below_target[time_period] if xl_bool(xl_eq(baseline_engine_debt_trajectory_direction[time_period], baseline_debt_direction_below_sentinel)) else 0))))

    baseline_engine_fiscal_rule_adjustment = CoordinateReader('baseline_engine_fiscal_rule_adjustment', data.BASELINE_ENGINE_FISCAL_RULE_ADJUSTMENT.required, baseline_engine_fiscal_rule_adjustment_formula)
    def baseline_engine_debt_trajectory_direction_formula(time_period: int) -> float | str | None:
        return as_measure((1 if xl_bool(xl_gt(baseline_debt_to_gdp[time_period], baseline_debt_to_gdp[time_period - 1])) else (2 if xl_bool(xl_lt(baseline_debt_to_gdp[time_period], baseline_debt_to_gdp[time_period - 1])) else 0)))

    baseline_engine_debt_trajectory_direction = CoordinateReader('baseline_engine_debt_trajectory_direction', data.BASELINE_ENGINE_DEBT_TRAJECTORY_DIRECTION.required, baseline_engine_debt_trajectory_direction_formula)
    def baseline_engine_fiscal_gap_above_target_formula(time_period: int) -> float | str | None:
        return as_measure((0 if xl_bool(xl_eq(baseline_debt_target_above, 0)) else (0 if xl_bool(xl_le(baseline_debt_to_gdp[time_period], baseline_debt_target_above)) else baseline_fiscal_consolidation_gap[time_period])))

    baseline_engine_fiscal_gap_above_target = CoordinateReader('baseline_engine_fiscal_gap_above_target', data.BASELINE_ENGINE_FISCAL_GAP_ABOVE_TARGET.required, baseline_engine_fiscal_gap_above_target_formula)
    def baseline_engine_fiscal_gap_below_target_formula(time_period: int) -> float | str | None:
        return as_measure((0 if xl_bool(xl_eq(baseline_debt_target_below, 0)) else (0 if xl_bool(xl_ge(baseline_debt_to_gdp[time_period], baseline_debt_target_below)) else baseline_fiscal_consolidation_gap[time_period])))

    baseline_engine_fiscal_gap_below_target = CoordinateReader('baseline_engine_fiscal_gap_below_target', data.BASELINE_ENGINE_FISCAL_GAP_BELOW_TARGET.required, baseline_engine_fiscal_gap_below_target_formula)
    def baseline_primary_expenditure_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_primary_expenditure_pct_gdp[time_period])
        return as_measure(xl_sub(baseline_engine_total_expenditure_pct_gdp[time_period], baseline_interest_expenditure_pct_gdp[time_period]))

    baseline_primary_expenditure_pct_gdp = CoordinateReader('baseline_primary_expenditure_pct_gdp', data.BASELINE_PRIMARY_EXPENDITURE_PCT_GDP.required, baseline_primary_expenditure_pct_gdp_formula)
    def baseline_interest_expenditure_pct_gdp_formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(baseline_engine_interest_expenditure_lcu[time_period], baseline_engine_nominal_gdp_lcu[time_period]), 100))

    baseline_interest_expenditure_pct_gdp = CoordinateReader('baseline_interest_expenditure_pct_gdp', data.BASELINE_INTEREST_EXPENDITURE_PCT_GDP.required, baseline_interest_expenditure_pct_gdp_formula)
    def baseline_primary_balance_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_primary_balance_pct_gdp[time_period])
        return as_measure(xl_sub(baseline_revenue_pct_gdp[time_period], baseline_primary_expenditure_pct_gdp[time_period]))

    baseline_primary_balance_pct_gdp = CoordinateReader('baseline_primary_balance_pct_gdp', data.BASELINE_PRIMARY_BALANCE_PCT_GDP.required, baseline_primary_balance_pct_gdp_formula)
    def baseline_debt_to_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_debt_to_gdp[time_period])
        return as_measure((0 if xl_bool(xl_lt(xl_sub(xl_div(xl_mul(baseline_debt_to_gdp[time_period - 1], xl_add(1, xl_div(baseline_interest_rate[time_period], 100))), xl_add(1, xl_div(baseline_nominal_gdp_growth[time_period], 100))), baseline_primary_balance_pct_gdp[time_period]), 0)) else xl_sub(xl_div(xl_mul(baseline_debt_to_gdp[time_period - 1], xl_add(1, xl_div(baseline_interest_rate[time_period], 100))), xl_add(1, xl_div(baseline_nominal_gdp_growth[time_period], 100))), baseline_primary_balance_pct_gdp[time_period])))

    baseline_debt_to_gdp = CoordinateReader('baseline_debt_to_gdp', data.BASELINE_DEBT_TO_GDP.required, baseline_debt_to_gdp_formula)
    def baseline_debt_stabilizing_primary_balance_formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(xl_div(xl_sub(baseline_interest_rate[time_period], baseline_nominal_gdp_growth[time_period]), 100), xl_add(1, xl_div(baseline_nominal_gdp_growth[time_period], 100))), baseline_debt_to_gdp[time_period - 1]))

    baseline_debt_stabilizing_primary_balance = CoordinateReader('baseline_debt_stabilizing_primary_balance', data.BASELINE_DEBT_STABILIZING_PRIMARY_BALANCE.required, baseline_debt_stabilizing_primary_balance_formula)
    def baseline_fiscal_consolidation_gap_formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(xl_sub(baseline_primary_balance_pct_gdp[time_period], baseline_debt_stabilizing_primary_balance[time_period]), 100), baseline_engine_nominal_gdp_lcu[time_period]))

    baseline_fiscal_consolidation_gap = CoordinateReader('baseline_fiscal_consolidation_gap', data.BASELINE_FISCAL_CONSOLIDATION_GAP.required, baseline_fiscal_consolidation_gap_formula)
    return ScanBaselineEngineTotalExpenditurePctGdpResult(
        baseline_engine_total_expenditure_pct_gdp=data.BASELINE_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.collect((coord, baseline_engine_total_expenditure_pct_gdp[coord]) for coord in data.BASELINE_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required),
        baseline_engine_total_expenditure_lcu=data.BASELINE_ENGINE_TOTAL_EXPENDITURE_LCU.collect((coord, baseline_engine_total_expenditure_lcu[coord]) for coord in data.BASELINE_ENGINE_TOTAL_EXPENDITURE_LCU.required),
        baseline_engine_interest_expenditure_lcu=data.BASELINE_ENGINE_INTEREST_EXPENDITURE_LCU.collect((coord, baseline_engine_interest_expenditure_lcu[coord]) for coord in data.BASELINE_ENGINE_INTEREST_EXPENDITURE_LCU.required),
        baseline_engine_primary_expenditure_lcu=data.BASELINE_ENGINE_PRIMARY_EXPENDITURE_LCU.collect((coord, baseline_engine_primary_expenditure_lcu[coord]) for coord in data.BASELINE_ENGINE_PRIMARY_EXPENDITURE_LCU.required),
        baseline_engine_gross_debt_lcu=data.BASELINE_ENGINE_GROSS_DEBT_LCU.collect((coord, baseline_engine_gross_debt_lcu[coord]) for coord in data.BASELINE_ENGINE_GROSS_DEBT_LCU.required),
        baseline_engine_fiscal_rule_adjustment=data.BASELINE_ENGINE_FISCAL_RULE_ADJUSTMENT.collect((coord, baseline_engine_fiscal_rule_adjustment[coord]) for coord in data.BASELINE_ENGINE_FISCAL_RULE_ADJUSTMENT.required),
        baseline_engine_debt_trajectory_direction=data.BASELINE_ENGINE_DEBT_TRAJECTORY_DIRECTION.collect((coord, baseline_engine_debt_trajectory_direction[coord]) for coord in data.BASELINE_ENGINE_DEBT_TRAJECTORY_DIRECTION.required),
        baseline_engine_fiscal_gap_above_target=data.BASELINE_ENGINE_FISCAL_GAP_ABOVE_TARGET.collect((coord, baseline_engine_fiscal_gap_above_target[coord]) for coord in data.BASELINE_ENGINE_FISCAL_GAP_ABOVE_TARGET.required),
        baseline_engine_fiscal_gap_below_target=data.BASELINE_ENGINE_FISCAL_GAP_BELOW_TARGET.collect((coord, baseline_engine_fiscal_gap_below_target[coord]) for coord in data.BASELINE_ENGINE_FISCAL_GAP_BELOW_TARGET.required),
        baseline_primary_expenditure_pct_gdp=data.BASELINE_PRIMARY_EXPENDITURE_PCT_GDP.collect((coord, baseline_primary_expenditure_pct_gdp[coord]) for coord in data.BASELINE_PRIMARY_EXPENDITURE_PCT_GDP.required),
        baseline_interest_expenditure_pct_gdp=data.BASELINE_INTEREST_EXPENDITURE_PCT_GDP.collect((coord, baseline_interest_expenditure_pct_gdp[coord]) for coord in data.BASELINE_INTEREST_EXPENDITURE_PCT_GDP.required),
        baseline_primary_balance_pct_gdp=data.BASELINE_PRIMARY_BALANCE_PCT_GDP.collect((coord, baseline_primary_balance_pct_gdp[coord]) for coord in data.BASELINE_PRIMARY_BALANCE_PCT_GDP.required),
        baseline_debt_to_gdp=data.BASELINE_DEBT_TO_GDP.collect((coord, baseline_debt_to_gdp[coord]) for coord in data.BASELINE_DEBT_TO_GDP.required),
        baseline_debt_stabilizing_primary_balance=data.BASELINE_DEBT_STABILIZING_PRIMARY_BALANCE.collect((coord, baseline_debt_stabilizing_primary_balance[coord]) for coord in data.BASELINE_DEBT_STABILIZING_PRIMARY_BALANCE.required),
        baseline_fiscal_consolidation_gap=data.BASELINE_FISCAL_CONSOLIDATION_GAP.collect((coord, baseline_fiscal_consolidation_gap[coord]) for coord in data.BASELINE_FISCAL_CONSOLIDATION_GAP.required),
    )

@publish(key=(), domain=None, cells=data.BASELINE_FISCAL_RULE_FLAG_CELLS)
def baseline_fiscal_rule_flag(*, fiscal_rule_enabled: Literal["No", "Yes"]) -> str | int | float | bool:
    """Read the baseline fiscal-rule flag from the Dashboard.

    Provides the fiscal-rule selection that Q-CRAFT mirrors into the engine fiscal-rule block for the baseline scenario.

    Args:
        fiscal_rule_enabled: The Dashboard fiscal-rule assumption, either "Yes" to apply a fiscal rule debt target or "No" to leave the debt-to-GDP ratio unconstrained.

    Returns:
        The fiscal-rule flag as a measure, or the error code if the value cannot be converted.
    """
    try:
        return as_measure(fiscal_rule_enabled, 'str')
    except XlError as error:
        return error.code

@publish(key=(), domain=None, cells=data.BASELINE_DEBT_TARGET_ABOVE_CELLS)
def baseline_debt_target_above(*, debt_target: Annotated[float, RealBetween(0.0, 300.0)]) -> float | str:
    """Return the baseline debt target for the debt-above-target branch.

    Mirrors the Dashboard debt-above-target calculation on the baseline scenario.

    Args:
        debt_target: Government debt-to-GDP target, expressed as a percentage of nominal GDP between 0 and 300.

    Returns:
        The baseline debt target as a numeric value, or an error code string if the target cannot be converted to a measure.
    """
    try:
        return as_measure(debt_target)
    except XlError as error:
        return error.code

@publish(key=(), domain=None, cells=data.BASELINE_DEBT_TARGET_BELOW_CELLS)
def baseline_debt_target_below(*, debt_target: Annotated[float, RealBetween(0.0, 300.0)]) -> float | str:
    """Return the baseline debt target for the debt-below-target branch.

    Mirrors Dashboard!C34 so the debt-below-target branch uses the same debt-to-GDP target as the baseline scenario.

    Args:
        debt_target: Debt-to-GDP target, in percent, applied under the debt-below-target branch of the baseline scenario.

    Returns:
        The baseline debt target as a number, or the error code string if the target is invalid.
    """
    try:
        return as_measure(debt_target)
    except XlError as error:
        return error.code

@publish(data.PARIS_ENGINE_EMPLOYMENT_GROWTH.schema, cells=data.PARIS_ENGINE_EMPLOYMENT_GROWTH.cells)
def paris_engine_employment_growth(*, baseline_employment_growth: data.BaselineEmploymentGrowth) -> data.Series[float | str | None]:
    """Return the Paris-scenario employment growth series passed through unchanged.

    Preserves the baseline employment growth path for the Paris (SSP1-2.6) climate scenario, where the 2015 Paris commitments are met and temperature increase stays below 2°C.

    Args:
        baseline_employment_growth: Baseline employment growth, projected after the WEO horizon to grow in line with the working-age (15-64) population; reused unchanged as the Paris scenario's employment growth path.

    Returns:
        Employment growth series for the Paris scenario, indexed by projection year, with values equal to the baseline employment growth in each period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_employment_growth[time_period])

    return data.PARIS_ENGINE_EMPLOYMENT_GROWTH.collect(evaluate(formula, data.PARIS_ENGINE_EMPLOYMENT_GROWTH.required))

@publish(data.PARIS_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.schema, cells=data.PARIS_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.cells)
def paris_engine_labour_productivity_growth(*, climate_data_labour_productivity_growth_variation_paris: data.Series[float | str | None], baseline_labour_productivity_growth: data.BaselineLabourProductivityGrowth) -> data.Series[float | str | None]:
    """Project labour productivity growth under the Paris climate scenario.

    Combine the baseline labour productivity growth trajectory with the Paris scenario's temperature-driven variation to obtain the climate-adjusted productivity growth path.

    Args:
        climate_data_labour_productivity_growth_variation_paris: Time series of the change in labour productivity growth (percentage points) attributable to the Paris (SSP1-2.6) climate scenario relative to the baseline, derived from estimates of temperature effects on GDP per capita.
        baseline_labour_productivity_growth: Baseline labour productivity growth trajectory, expressed as growth in GDP per employed person, prior to any climate change adjustment.

    Returns:
        Time series of labour productivity growth under the Paris climate scenario, obtained by adding the scenario variation to the baseline productivity growth in each period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(baseline_labour_productivity_growth[time_period], climate_data_labour_productivity_growth_variation_paris[time_period]))

    return data.PARIS_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.collect(evaluate(formula, data.PARIS_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.required))

@publish(data.PARIS_ENGINE_REAL_GDP_GROWTH.schema, cells=data.PARIS_ENGINE_REAL_GDP_GROWTH.cells)
def paris_engine_real_gdp_growth(*, paris_engine_employment_growth: data.Series[float | str | None], paris_engine_labour_productivity_growth: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute real GDP growth in the Paris climate scenario.

    Combines employment growth and labour productivity growth to derive real GDP growth for the Paris scenario.

    Args:
        paris_engine_employment_growth: Projected employment growth (percentage) under the Paris scenario.
        paris_engine_labour_productivity_growth: Projected labour productivity growth (percentage) under the Paris scenario.

    Returns:
        Real GDP growth (percentage) for the Paris scenario, consistent with Q-CRAFT's production-function decomposition.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(paris_engine_employment_growth[time_period], 100)), xl_add(1, xl_div(paris_engine_labour_productivity_growth[time_period], 100))), 100), 100))

    return data.PARIS_ENGINE_REAL_GDP_GROWTH.collect(evaluate(formula, data.PARIS_ENGINE_REAL_GDP_GROWTH.required))

@publish(data.PARIS_ENGINE_GDP_DEFLATOR_GROWTH.schema, cells=data.PARIS_ENGINE_GDP_DEFLATOR_GROWTH.cells)
def paris_engine_gdp_deflator_growth(*, baseline_gdp_deflator_growth: data.BaselineGdpDeflatorGrowth) -> data.Series[float | str | None]:
    """Return the Paris scenario GDP deflator growth series.

    Carries the baseline GDP deflator growth assumption into the Paris scenario (SSP1-2.6) so that inflation remains unchanged across climate scenarios.

    Args:
        baseline_gdp_deflator_growth: Baseline GDP deflator growth series, expressed as the growth rate of the GDP deflator used to convert real GDP into nominal GDP over the projection horizon.

    Returns:
        The GDP deflator growth series for the Paris climate scenario, indexed by time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_gdp_deflator_growth[time_period])

    return data.PARIS_ENGINE_GDP_DEFLATOR_GROWTH.collect(evaluate(formula, data.PARIS_ENGINE_GDP_DEFLATOR_GROWTH.required))

@publish(data.PARIS_ENGINE_NOMINAL_GDP_LCU.schema, cells=data.PARIS_ENGINE_NOMINAL_GDP_LCU.cells)
def paris_engine_nominal_gdp_lcu(*, baseline_engine_nominal_gdp_lcu: data.Series[float | str | None], scenario_nominal_gdp_growth_paris: data.ScenarioNominalGdpGrowthParis) -> data.Series[float | str | None]:
    """Project nominal GDP in local currency units under the Paris climate scenario.

    Extend the baseline nominal GDP level from 2030 onwards by compounding it with the Paris scenario's annual nominal GDP growth rate.

    Args:
        baseline_engine_nominal_gdp_lcu: Baseline nominal GDP in billions of local currency units, used as the starting level through 2029 before climate change effects are applied.
        scenario_nominal_gdp_growth_paris: Annual nominal GDP growth rate, in percent, under the Paris scenario based on SSP1-2.6, reflecting the macroeconomic effects of climate change from 2030 onwards.

    Returns:
        Nominal GDP in billions of local currency units under the Paris climate scenario for each projected year.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_nominal_gdp_lcu[time_period])
        return as_measure(xl_mul(paris_engine_nominal_gdp_lcu[time_period - 1], xl_add(1, xl_div(scenario_nominal_gdp_growth_paris[time_period], 100))))

    paris_engine_nominal_gdp_lcu = CoordinateReader('paris_engine_nominal_gdp_lcu', data.PARIS_ENGINE_NOMINAL_GDP_LCU.required, formula)
    return data.PARIS_ENGINE_NOMINAL_GDP_LCU.collect((coord, paris_engine_nominal_gdp_lcu[coord]) for coord in data.PARIS_ENGINE_NOMINAL_GDP_LCU.required)

@publish(data.PARIS_ENGINE_REVENUE_PCT_GDP.schema, cells=data.PARIS_ENGINE_REVENUE_PCT_GDP.cells)
def paris_engine_revenue_pct_gdp(*, paris_engine_discrete_risk_revenue_shock: data.Series[float | str | None], baseline_revenue_pct_gdp: data.BaselineRevenuePctGdp) -> data.Series[float | str | None]:
    """Compute the Paris scenario revenue-to-GDP ratio including registered discrete risk revenue shocks.

    Produces the Paris climate scenario path for government revenue as a share of nominal GDP by adding any user-registered discrete risk revenue shock to the baseline revenue-to-GDP ratio from 2030 onward.

    Args:
        paris_engine_discrete_risk_revenue_shock: Revenue loss (as a share of nominal GDP) from materialized discrete fiscal risks or natural disasters under the Paris scenario, entered in the Discrete Risks worksheet; used from 2030 onward.
        baseline_revenue_pct_gdp: Government revenue as a percentage of nominal GDP under the baseline scenario, assumed to remain constant in the face of slow-building climate change.

    Returns:
        Revenue-to-GDP ratio under the Paris scenario, equal to the baseline ratio through 2029 and to the baseline ratio plus the discrete risk revenue shock thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_revenue_pct_gdp[time_period])
        return as_measure(xl_add(baseline_revenue_pct_gdp[time_period], paris_engine_discrete_risk_revenue_shock[time_period]))

    return data.PARIS_ENGINE_REVENUE_PCT_GDP.collect(evaluate(formula, data.PARIS_ENGINE_REVENUE_PCT_GDP.required))

@publish(data.PARIS_ENGINE_OVERALL_BALANCE_PCT_GDP.schema, cells=data.PARIS_ENGINE_OVERALL_BALANCE_PCT_GDP.cells)
def paris_engine_overall_balance_pct_gdp(*, paris_engine_revenue_pct_gdp: data.Series[float | str | None], paris_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Project the overall fiscal balance under the Paris climate scenario.

    Derive the Paris-scenario overall balance as revenue minus total expenditure, while carrying over the baseline overall balance through 2029.

    Args:
        paris_engine_revenue_pct_gdp: Government revenue as a share of nominal GDP under the Paris scenario, held at the baseline revenue-to-GDP ratio.
        paris_engine_total_expenditure_pct_gdp: Government total expenditure as a share of nominal GDP under the Paris scenario, reflecting rigid primary expenditure against a smaller nominal GDP.
        baseline_overall_balance_pct_gdp: Baseline overall balance as a percentage of nominal GDP, used for years through 2029 before climate change effects begin.

    Returns:
        Overall balance as a percentage of nominal GDP under the Paris scenario, equal to the baseline balance through 2029 and to revenue minus total expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_overall_balance_pct_gdp[time_period])
        return as_measure(xl_sub(paris_engine_revenue_pct_gdp[time_period], paris_engine_total_expenditure_pct_gdp[time_period]))

    return data.PARIS_ENGINE_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.PARIS_ENGINE_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.PARIS_ENGINE_REVENUE_LCU.schema, cells=data.PARIS_ENGINE_REVENUE_LCU.cells)
def paris_engine_revenue_lcu(*, baseline_engine_revenue_lcu: data.Series[float | str | None], paris_engine_nominal_gdp_lcu: data.Series[float | str | None], paris_engine_revenue_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project government revenue in local currency units under the Paris climate scenario.

    Derives Paris-scenario revenue in local currency terms, carrying the baseline forward through 2029 and, from 2030 onward, scaling Paris-scenario nominal GDP by the constant revenue-to-GDP ratio.

    Args:
        baseline_engine_revenue_lcu: Baseline-scenario government revenue in billions of local currency units, used unchanged through the end of the WEO horizon (2029).
        paris_engine_nominal_gdp_lcu: Paris-scenario nominal GDP in billions of local currency units, reflecting the slowdown in productivity growth under the SSP1-2.6 pathway.
        paris_engine_revenue_pct_gdp: Paris-scenario government revenue as a share of nominal GDP, held constant at the baseline ratio on the assumption that tax policy is unchanged.

    Returns:
        Government revenue in billions of local currency units under the Paris climate scenario, equal to the baseline level through 2029 and to the revenue-to-GDP ratio applied to Paris-scenario nominal GDP thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_revenue_lcu[time_period])
        return as_measure(xl_mul(xl_div(paris_engine_revenue_pct_gdp[time_period], 100), paris_engine_nominal_gdp_lcu[time_period]))

    return data.PARIS_ENGINE_REVENUE_LCU.collect(evaluate(formula, data.PARIS_ENGINE_REVENUE_LCU.required))

@publish(data.PARIS_ENGINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.PARIS_ENGINE_PRIMARY_EXPENDITURE_LCU.cells)
def paris_engine_primary_expenditure_lcu(*, expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)], baseline_engine_primary_expenditure_lcu: data.Series[float | str | None], paris_engine_nominal_gdp_lcu: data.Series[float | str | None], paris_engine_discrete_risk_expenditure_shock: data.Series[float | str | None], paris_engine_recalibration_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project Paris-scenario primary expenditure in local currency units.

    Produces the annual Paris-scenario primary expenditure path by scaling the baseline for expenditure rigidity, recalibration, and discrete-risk shocks.

    Args:
        expenditure_rigidity: Degree to which primary expenditure stays fixed in nominal terms when climate change reduces GDP, ranging from 0 (fully flexible, so the primary expenditure-to-GDP ratio matches the baseline) to 1 (completely rigid).
        baseline_engine_primary_expenditure_lcu: Baseline primary expenditure, excluding interest payments, in billions of local currency units; used unchanged up to 2029 and as the starting point thereafter.
        paris_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units under the Paris scenario, declining with climate change and scaling the discrete-risk expenditure shock expressed as a share of GDP.
        paris_engine_discrete_risk_expenditure_shock: Fiscal cost of materialized discrete risks such as natural disasters in the Paris scenario, registered as a percentage of GDP and added to primary expenditure.
        paris_engine_recalibration_lcu: Amount of baseline primary expenditure that may be recalibrated as expenditure rigidity is relaxed, reducing primary expenditure in local currency units below the baseline.

    Returns:
        A series of Paris-scenario primary expenditure in billions of local currency units for each projected year, equal to the baseline through 2029 and thereafter adjusted for recalibration and discrete-risk shocks.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_expenditure_lcu[time_period])
        return as_measure(xl_add(xl_sub(baseline_engine_primary_expenditure_lcu[time_period], xl_mul(xl_sub(1, expenditure_rigidity), paris_engine_recalibration_lcu[time_period])), xl_mul(xl_div(paris_engine_discrete_risk_expenditure_shock[time_period], 100), paris_engine_nominal_gdp_lcu[time_period])))

    return data.PARIS_ENGINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.PARIS_ENGINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.PARIS_ENGINE_PRIMARY_BALANCE_LCU.schema, cells=data.PARIS_ENGINE_PRIMARY_BALANCE_LCU.cells)
def paris_engine_primary_balance_lcu(*, baseline_engine_primary_balance_lcu: data.Series[float | str | None], paris_engine_revenue_lcu: data.Series[float | str | None], paris_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the Paris scenario primary balance in local currency units.

    Derives the primary balance under the Paris scenario, where international commitments from the 2015 Paris summit are met, to assess fiscal risks from slow-building climate change.

    Args:
        baseline_engine_primary_balance_lcu: Primary balance in local currency units under the baseline scenario, used unchanged through the end of the IMF WEO horizon (2029).
        paris_engine_revenue_lcu: Government revenue in local currency units under the Paris scenario, assumed to decline in line with nominal GDP while the revenue-to-GDP ratio remains unchanged from the baseline.
        paris_engine_primary_expenditure_lcu: Primary expenditure in local currency units under the Paris scenario, assumed to remain rigid at the baseline level in local currency terms and thus rise as a share of GDP as nominal GDP declines.

    Returns:
        Primary balance in local currency units under the Paris scenario for each year through 2099: the baseline primary balance through 2029, and revenue less rigid primary expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_balance_lcu[time_period])
        return as_measure(xl_sub(paris_engine_revenue_lcu[time_period], paris_engine_primary_expenditure_lcu[time_period]))

    return data.PARIS_ENGINE_PRIMARY_BALANCE_LCU.collect(evaluate(formula, data.PARIS_ENGINE_PRIMARY_BALANCE_LCU.required))

@publish(data.PARIS_ENGINE_OVERALL_BALANCE_LCU.schema, cells=data.PARIS_ENGINE_OVERALL_BALANCE_LCU.cells)
def paris_engine_overall_balance_lcu(*, baseline_engine_overall_balance_lcu: data.Series[float | str | None], paris_engine_revenue_lcu: data.Series[float | str | None], paris_engine_total_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the overall balance in local currency units under the Paris climate scenario.

    Derive the overall fiscal balance for the Paris scenario from baseline values before the projection period and from the revenue-expenditure gap thereafter.

    Args:
        baseline_engine_overall_balance_lcu: Baseline overall balance in local currency units; used through 2029.
        paris_engine_revenue_lcu: Government revenue in local currency units under the Paris scenario, assumed to decline in line with nominal GDP while the revenue-to-GDP ratio remains unchanged from the baseline.
        paris_engine_total_expenditure_lcu: Government total expenditure in local currency units under the Paris scenario, reflecting rigid primary expenditure held at baseline levels in local currency terms.

    Returns:
        The overall balance in local currency units under the Paris scenario for each project year.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_overall_balance_lcu[time_period])
        return as_measure(xl_sub(paris_engine_revenue_lcu[time_period], paris_engine_total_expenditure_lcu[time_period]))

    return data.PARIS_ENGINE_OVERALL_BALANCE_LCU.collect(evaluate(formula, data.PARIS_ENGINE_OVERALL_BALANCE_LCU.required))

@publish(data.PARIS_ENGINE_WEIGHTED_INTEREST_RATE.schema, cells=data.PARIS_ENGINE_WEIGHTED_INTEREST_RATE.cells)
def paris_engine_weighted_interest_rate(*, baseline_interest_rate: data.BaselineInterestRate) -> data.Series[float | str | None]:
    """Project the weighted average nominal interest rate under the Paris climate scenario.

    Provides the Paris scenario's weighted average nominal interest rate path for use in the debt-dynamics equation.

    Args:
        baseline_interest_rate: Baseline nominal interest rate assumption, from which the Paris scenario's weighted average nominal interest rate is projected.

    Returns:
        Series of weighted average nominal interest rates for the Paris scenario, in percent.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_rate[time_period])

    return data.PARIS_ENGINE_WEIGHTED_INTEREST_RATE.collect(evaluate(formula, data.PARIS_ENGINE_WEIGHTED_INTEREST_RATE.required))

@publish(data.PARIS_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.schema, cells=data.PARIS_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.cells)
def paris_engine_interest_expenditure_pct_revenue(*, paris_engine_revenue_lcu: data.Series[float | str | None], paris_engine_interest_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute interest expenditure as a percentage of revenue under the Paris climate scenario.

    Express the Paris-scenario interest expenditure in local currency units relative to government revenue in the same units, so the interest burden on revenue is reported on a common percent basis.

    Args:
        paris_engine_revenue_lcu: Government revenue in billions of local currency units under the Paris scenario, used as the denominator of the ratio.
        paris_engine_interest_expenditure_lcu: Government interest expenditure in billions of local currency units under the Paris scenario, used as the numerator of the ratio.

    Returns:
        A series of interest expenditure as a percent of revenue under the Paris scenario, in percent, with the same time-period indexing as the inputs.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(paris_engine_interest_expenditure_lcu[time_period], paris_engine_revenue_lcu[time_period]), 100))

    return data.PARIS_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.collect(evaluate(formula, data.PARIS_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.required))

@publish(data.PARIS_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.schema, cells=data.PARIS_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.cells)
def paris_engine_discrete_risk_revenue_shock(*, discrete_revenue_shocks: data.DiscreteRevenueShocks) -> data.Series[float | str | None]:
    """Project the Paris-scenario discrete revenue shock series.

    Generates the year-by-year fiscal impact of registered discrete revenue shocks under the Paris climate scenario for use in the climate scenario projections.

    Args:
        discrete_revenue_shocks: Discrete revenue shocks registered as a percentage of GDP in the Discrete Risks worksheet, containing the revenue loss consequences of materialized fiscal risks under each climate change scenario.

    Returns:
        Series of discrete revenue shock values for each projected year under the Paris scenario, in percent of GDP.
    """
    data.DISCRETE_REVENUE_SHOCKS.schema.validate(discrete_revenue_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_revenue_shocks['Paris', time_period])

    return data.PARIS_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.collect(evaluate(formula, data.PARIS_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.required))

@publish(data.PARIS_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.schema, cells=data.PARIS_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.cells)
def paris_engine_discrete_risk_expenditure_shock(*, discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks) -> data.Series[float | str | None]:
    """Project the Paris-scenario discrete primary expenditure shock series.

    Supplies the discrete risk expenditure shock path used by the Paris climate scenario engine.

    Args:
        discrete_primary_expenditure_shocks: Discrete fiscal risk entries recording materialization of climate-related risks as increases in primary expenditure, expressed as a percent of GDP, under the Paris scenario based on SSP1-2.6 in which 2015 Paris Agreement commitments are met.

    Returns:
        A series of Paris-scenario discrete primary expenditure shocks indexed by projection year.
    """
    data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.schema.validate(discrete_primary_expenditure_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_primary_expenditure_shocks['Paris', time_period])

    return data.PARIS_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.collect(evaluate(formula, data.PARIS_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.required))

@publish(data.PARIS_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.schema, cells=data.PARIS_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.cells)
def paris_engine_memo_interest_expenditure_pct_gdp(*, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp) -> data.Series[float | str | None]:
    """Report interest expenditure as a share of GDP under the Paris climate scenario.

    Provide the Paris-scenario memo series for general government interest expenditure expressed as a percentage of nominal GDP, aligned to the baseline expenditure path.

    Args:
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure as a percent of nominal GDP, by time period, from which the Paris-scenario memo values are carried through.

    Returns:
        Series of interest expenditure-to-GDP ratios (in percent) for the Paris scenario, keyed by time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_expenditure_pct_gdp[time_period])

    return data.PARIS_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.PARIS_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.required))

@publish(data.PARIS_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.schema, cells=data.PARIS_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.cells)
def paris_engine_memo_primary_expenditure_pct_gdp(*, baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp) -> data.Series[float | str | None]:
    """Return the baseline primary expenditure ratio under the Paris scenario memo series.

    Provides the memo series that reports the baseline primary expenditure path as a share of GDP when the Paris climate scenario is being run.

    Args:
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure as a percentage of GDP, where primary expenditure excludes government interest payments and therefore evolves as a share of GDP when its growth is driven by productivity, inflation, and total population.

    Returns:
        A series containing the baseline primary expenditure-to-GDP ratio for each projection time period, reported as a float or a string (or None where the underlying value is unavailable).
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_expenditure_pct_gdp[time_period])

    return data.PARIS_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.PARIS_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.required))

@publish(data.PARIS_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.schema, cells=data.PARIS_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.cells)
def paris_engine_memo_primary_balance_pct_gdp(*, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Prepare the Paris scenario memo series for the primary balance as a share of GDP.

    Carries the baseline primary balance ratio into the Paris climate scenario unchanged, since the primary balance is memoed rather than adjusted.

    Args:
        baseline_primary_balance_pct_gdp: Baseline primary balance (revenue minus primary expenditure) expressed as a percentage of nominal GDP for each projection year.

    Returns:
        Series of the memoed primary balance as a percentage of nominal GDP.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_balance_pct_gdp[time_period])

    return data.PARIS_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.collect(evaluate(formula, data.PARIS_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.required))

@publish(data.PARIS_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.schema, cells=data.PARIS_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.cells)
def paris_engine_memo_overall_balance_pct_gdp(*, baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Return the Paris-scenario memo of the overall balance as a share of GDP.

    Expose a memo series that carries the baseline overall balance through the Paris climate scenario so it can be reported alongside climate-driven fiscal results.

    Args:
        baseline_overall_balance_pct_gdp: Baseline overall balance expressed as a percent of nominal GDP, provided per projection year and reused unchanged for the Paris memo series.

    Returns:
        A series of overall balance values as a percent of GDP, one value per projection year, retaining any missing entries as reported.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_overall_balance_pct_gdp[time_period])

    return data.PARIS_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.PARIS_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.PARIS_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.schema, cells=data.PARIS_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.cells)
def paris_engine_memo_gross_debt_pct_gdp(*, baseline_debt_to_gdp: data.BaselineDebtToGdp) -> data.Series[float | str | None]:
    """Report the Paris scenario memo gross debt-to-GDP ratio series.

    Provide the memo gross general government debt as a share of nominal GDP under the Paris climate change scenario (SSP1-2.6, with 2015 Paris Agreement commitments met) so it can be reported alongside the corresponding climate scenario projections.

    Args:
        baseline_debt_to_gdp: Baseline gross debt-to-GDP ratio series, indexed by time period, used as the source from which the Paris scenario memo values are taken.

    Returns:
        Series of gross debt-to-GDP ratio values under the Paris scenario, indexed by time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_to_gdp[time_period])

    return data.PARIS_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.collect(evaluate(formula, data.PARIS_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.required))

@publish(data.PARIS_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.PARIS_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.cells)
def paris_engine_baseline_primary_expenditure_lcu(*, baseline_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Return baseline primary expenditure in local currency units for the Paris climate scenario.

    Provides the baseline primary expenditure used when projecting fiscal outcomes under the Paris (SSP1-2.6) climate change scenario.

    Args:
        baseline_engine_primary_expenditure_lcu: Baseline primary expenditure in local currency units, excluding government interest payments, expressed over the projection horizon and measured as a float or string value.

    Returns:
        A series of baseline primary expenditure in local currency units aligned to the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_engine_primary_expenditure_lcu[time_period])

    return data.PARIS_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.PARIS_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.PARIS_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.schema, cells=data.PARIS_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.cells)
def paris_engine_primary_expenditure_baseline_share_lcu(*, paris_engine_nominal_gdp_lcu: data.Series[float | str | None], paris_engine_memo_primary_expenditure_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Convert the baseline primary expenditure ratio into local currency levels.

    Express baseline primary expenditure in billions of local currency units so climate scenario expenditure rigidity assumptions can be applied to the same baseline spending level.

    Args:
        paris_engine_nominal_gdp_lcu: Projected nominal GDP, in billions of local currency units, used as the scaling base for converting the primary expenditure ratio into a level.
        paris_engine_memo_primary_expenditure_pct_gdp: Baseline primary expenditure as a percentage of nominal GDP, which excludes government interest payments.

    Returns:
        A time series of baseline primary expenditure in billions of local currency units.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(paris_engine_memo_primary_expenditure_pct_gdp[time_period], 100), paris_engine_nominal_gdp_lcu[time_period]))

    return data.PARIS_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.collect(evaluate(formula, data.PARIS_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.required))

@publish(data.PARIS_ENGINE_RECALIBRATION_LCU.schema, cells=data.PARIS_ENGINE_RECALIBRATION_LCU.cells)
def paris_engine_recalibration_lcu(*, paris_engine_baseline_primary_expenditure_lcu: data.Series[float | str | None], paris_engine_primary_expenditure_baseline_share_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Recalibrate Paris-scenario primary expenditure in local currency units.

    Derives the recalculated Paris-scenario primary expenditure by removing the baseline primary expenditure share from the baseline primary expenditure level.

    Args:
        paris_engine_baseline_primary_expenditure_lcu: Baseline primary expenditure under the Paris scenario, expressed in billions of local currency units.
        paris_engine_primary_expenditure_baseline_share_lcu: Portion of baseline primary expenditure under the Paris scenario, in billions of local currency units, to be netted out during recalibration.

    Returns:
        Recalculated Paris-scenario primary expenditure in local currency units.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(paris_engine_baseline_primary_expenditure_lcu[time_period], paris_engine_primary_expenditure_baseline_share_lcu[time_period]))

    return data.PARIS_ENGINE_RECALIBRATION_LCU.collect(evaluate(formula, data.PARIS_ENGINE_RECALIBRATION_LCU.required))

@dataclass(frozen=True, slots=True)
class ScanParisEngineTotalExpenditurePctGdpResult:
    """Complete named results of one recurrence group evaluation."""
    paris_engine_total_expenditure_pct_gdp: data.Series[float | str | None]
    paris_engine_primary_balance_pct_gdp: data.Series[float | str | None]
    paris_engine_total_expenditure_lcu: data.Series[float | str | None]
    paris_engine_interest_expenditure_lcu: data.Series[float | str | None]
    paris_engine_gross_debt_lcu: data.Series[float | str | None]
    paris_engine_gross_debt_pct_gdp: data.Series[float | str | None]
    scenario_primary_expenditure_pct_gdp_paris: data.ScenarioPrimaryExpenditurePctGdpParis
    scenario_interest_expenditure_pct_gdp_paris: data.ScenarioInterestExpenditurePctGdpParis

def scan_paris_engine_total_expenditure_pct_gdp(*, baseline_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_engine_total_expenditure_lcu: data.Series[float | str | None], baseline_engine_interest_expenditure_lcu: data.Series[float | str | None], baseline_engine_gross_debt_lcu: data.Series[float | str | None], paris_engine_nominal_gdp_lcu: data.Series[float | str | None], paris_engine_revenue_pct_gdp: data.Series[float | str | None], paris_engine_primary_expenditure_lcu: data.Series[float | str | None], paris_engine_weighted_interest_rate: data.Series[float | str | None], baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp, baseline_debt_to_gdp: data.BaselineDebtToGdp, scenario_nominal_gdp_growth_paris: data.ScenarioNominalGdpGrowthParis) -> ScanParisEngineTotalExpenditurePctGdpResult:
    """Project total expenditure and the associated Paris-scenario fiscal aggregates.

    Derive the Paris scenario's total expenditure, primary balance, debt, and interest paths, using baseline values through 2029 and the expenditure-rigidity and debt-dynamics relationships thereafter.

    Args:
        baseline_engine_total_expenditure_pct_gdp: Baseline total expenditure as a share of nominal GDP, used for periods through 2029.
        baseline_engine_total_expenditure_lcu: Baseline total expenditure in local currency units, used for periods through 2029.
        baseline_engine_interest_expenditure_lcu: Baseline interest expenditure in local currency units, used for periods through 2029.
        baseline_engine_gross_debt_lcu: Baseline gross debt in local currency units, used for periods through 2029.
        paris_engine_nominal_gdp_lcu: Paris scenario nominal GDP in local currency units, the denominator for the expenditure and interest ratios.
        paris_engine_revenue_pct_gdp: Paris scenario revenue as a share of nominal GDP, which remains unchanged from the baseline.
        paris_engine_primary_expenditure_lcu: Paris scenario primary expenditure in local currency units, held rigid at the baseline level under climate change.
        paris_engine_weighted_interest_rate: Paris scenario weighted average nominal interest rate on government debt, in percent.
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure as a share of nominal GDP, used for periods through 2029.
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure as a share of nominal GDP, used for periods through 2029.
        baseline_primary_balance_pct_gdp: Baseline primary balance as a share of nominal GDP, used for periods through 2029.
        baseline_debt_to_gdp: Baseline gross debt-to-GDP ratio, used for periods through 2029.
        scenario_nominal_gdp_growth_paris: Paris scenario nominal GDP growth rate, in percent, used in the debt-dynamics equation.

    Returns:
        The collected Paris-scenario series for total expenditure (percent of GDP and local currency units), primary balance, interest expenditure (percent of GDP and local currency units), gross debt (percent of GDP and local currency units), and primary expenditure as a share of GDP.
    """
    def paris_engine_total_expenditure_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(paris_engine_total_expenditure_lcu[time_period], paris_engine_nominal_gdp_lcu[time_period]), 100))

    paris_engine_total_expenditure_pct_gdp = CoordinateReader('paris_engine_total_expenditure_pct_gdp', data.PARIS_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required, paris_engine_total_expenditure_pct_gdp_formula)
    def paris_engine_primary_balance_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_balance_pct_gdp[time_period])
        return as_measure(xl_sub(paris_engine_revenue_pct_gdp[time_period], scenario_primary_expenditure_pct_gdp_paris[time_period]))

    paris_engine_primary_balance_pct_gdp = CoordinateReader('paris_engine_primary_balance_pct_gdp', data.PARIS_ENGINE_PRIMARY_BALANCE_PCT_GDP.required, paris_engine_primary_balance_pct_gdp_formula)
    def paris_engine_total_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_lcu[time_period])
        return as_measure(xl_add(paris_engine_interest_expenditure_lcu[time_period], paris_engine_primary_expenditure_lcu[time_period]))

    paris_engine_total_expenditure_lcu = CoordinateReader('paris_engine_total_expenditure_lcu', data.PARIS_ENGINE_TOTAL_EXPENDITURE_LCU.required, paris_engine_total_expenditure_lcu_formula)
    def paris_engine_interest_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_interest_expenditure_lcu[time_period])
        return as_measure(xl_mul(xl_div(paris_engine_weighted_interest_rate[time_period], 100), paris_engine_gross_debt_lcu[time_period - 1]))

    paris_engine_interest_expenditure_lcu = CoordinateReader('paris_engine_interest_expenditure_lcu', data.PARIS_ENGINE_INTEREST_EXPENDITURE_LCU.required, paris_engine_interest_expenditure_lcu_formula)
    def paris_engine_gross_debt_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_gross_debt_lcu[time_period])
        return as_measure(xl_mul(xl_div(paris_engine_gross_debt_pct_gdp[time_period], 100), paris_engine_nominal_gdp_lcu[time_period]))

    paris_engine_gross_debt_lcu = CoordinateReader('paris_engine_gross_debt_lcu', data.PARIS_ENGINE_GROSS_DEBT_LCU.required, paris_engine_gross_debt_lcu_formula)
    def paris_engine_gross_debt_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_debt_to_gdp[time_period])
        return as_measure(xl_sub(xl_div(xl_mul(paris_engine_gross_debt_pct_gdp[time_period - 1], xl_add(1, xl_div(paris_engine_weighted_interest_rate[time_period], 100))), xl_add(1, xl_div(scenario_nominal_gdp_growth_paris[time_period], 100))), paris_engine_primary_balance_pct_gdp[time_period]))

    paris_engine_gross_debt_pct_gdp = CoordinateReader('paris_engine_gross_debt_pct_gdp', data.PARIS_ENGINE_GROSS_DEBT_PCT_GDP.required, paris_engine_gross_debt_pct_gdp_formula)
    def scenario_primary_expenditure_pct_gdp_paris_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_expenditure_pct_gdp[time_period])
        return as_measure(xl_sub(paris_engine_total_expenditure_pct_gdp[time_period], scenario_interest_expenditure_pct_gdp_paris[time_period]))

    scenario_primary_expenditure_pct_gdp_paris = CoordinateReader('scenario_primary_expenditure_pct_gdp_paris', data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_PARIS.required, scenario_primary_expenditure_pct_gdp_paris_formula)
    def scenario_interest_expenditure_pct_gdp_paris_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_interest_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(paris_engine_interest_expenditure_lcu[time_period], paris_engine_nominal_gdp_lcu[time_period]), 100))

    scenario_interest_expenditure_pct_gdp_paris = CoordinateReader('scenario_interest_expenditure_pct_gdp_paris', data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_PARIS.required, scenario_interest_expenditure_pct_gdp_paris_formula)
    return ScanParisEngineTotalExpenditurePctGdpResult(
        paris_engine_total_expenditure_pct_gdp=data.PARIS_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.collect((coord, paris_engine_total_expenditure_pct_gdp[coord]) for coord in data.PARIS_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required),
        paris_engine_primary_balance_pct_gdp=data.PARIS_ENGINE_PRIMARY_BALANCE_PCT_GDP.collect((coord, paris_engine_primary_balance_pct_gdp[coord]) for coord in data.PARIS_ENGINE_PRIMARY_BALANCE_PCT_GDP.required),
        paris_engine_total_expenditure_lcu=data.PARIS_ENGINE_TOTAL_EXPENDITURE_LCU.collect((coord, paris_engine_total_expenditure_lcu[coord]) for coord in data.PARIS_ENGINE_TOTAL_EXPENDITURE_LCU.required),
        paris_engine_interest_expenditure_lcu=data.PARIS_ENGINE_INTEREST_EXPENDITURE_LCU.collect((coord, paris_engine_interest_expenditure_lcu[coord]) for coord in data.PARIS_ENGINE_INTEREST_EXPENDITURE_LCU.required),
        paris_engine_gross_debt_lcu=data.PARIS_ENGINE_GROSS_DEBT_LCU.collect((coord, paris_engine_gross_debt_lcu[coord]) for coord in data.PARIS_ENGINE_GROSS_DEBT_LCU.required),
        paris_engine_gross_debt_pct_gdp=data.PARIS_ENGINE_GROSS_DEBT_PCT_GDP.collect((coord, paris_engine_gross_debt_pct_gdp[coord]) for coord in data.PARIS_ENGINE_GROSS_DEBT_PCT_GDP.required),
        scenario_primary_expenditure_pct_gdp_paris=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_PARIS.collect((coord, scenario_primary_expenditure_pct_gdp_paris[coord]) for coord in data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_PARIS.required),
        scenario_interest_expenditure_pct_gdp_paris=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_PARIS.collect((coord, scenario_interest_expenditure_pct_gdp_paris[coord]) for coord in data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_PARIS.required),
    )

@publish(data.MODERATE_ENGINE_EMPLOYMENT_GROWTH.schema, cells=data.MODERATE_ENGINE_EMPLOYMENT_GROWTH.cells)
def moderate_engine_employment_growth(*, baseline_employment_growth: data.BaselineEmploymentGrowth) -> data.Series[float | str | None]:
    """Return employment growth for the Moderate climate scenario.

    Supplies the Moderate (SSP2-4.5) scenario employment growth path used to project nominal GDP and fiscal aggregates.

    Args:
        baseline_employment_growth: Baseline-scenario employment growth series, taken as the scenario value under the assumption that employment growth beyond the WEO horizon follows projected growth in the working-age (15-64) population.

    Returns:
        Time series of per-period employment growth for the Moderate scenario through the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_employment_growth[time_period])

    return data.MODERATE_ENGINE_EMPLOYMENT_GROWTH.collect(evaluate(formula, data.MODERATE_ENGINE_EMPLOYMENT_GROWTH.required))

@publish(data.MODERATE_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.schema, cells=data.MODERATE_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.cells)
def moderate_engine_labour_productivity_growth(*, climate_data_labour_productivity_growth_variation_moderate: data.Series[float | str | None], baseline_labour_productivity_growth: data.BaselineLabourProductivityGrowth) -> data.Series[float | str | None]:
    """Combine the baseline labour productivity growth with the moderate-scenario climate variation to yield the moderate-scenario labour productivity growth trajectory.

    Produces the moderate climate scenario's labour productivity growth path by adding the climate-driven variation to the baseline productivity growth for each projection year.

    Args:
        climate_data_labour_productivity_growth_variation_moderate: Year-by-year change in labour productivity growth attributed to climate change under the moderate (SSP2-4.5) scenario, expressed relative to the baseline growth path.
        baseline_labour_productivity_growth: Baseline labour productivity growth path, defined as growth in GDP per employed person, derived before climate change effects are applied.

    Returns:
        Labour productivity growth path under the moderate climate change scenario, obtained by adding the climate-driven variation to the baseline productivity growth in each time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(baseline_labour_productivity_growth[time_period], climate_data_labour_productivity_growth_variation_moderate[time_period]))

    return data.MODERATE_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.collect(evaluate(formula, data.MODERATE_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.required))

@publish(data.MODERATE_ENGINE_REAL_GDP_GROWTH.schema, cells=data.MODERATE_ENGINE_REAL_GDP_GROWTH.cells)
def moderate_engine_real_gdp_growth(*, moderate_engine_employment_growth: data.Series[float | str | None], moderate_engine_labour_productivity_growth: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project real GDP growth under the moderate climate scenario.

    Combines employment growth and labour productivity growth to yield the moderate-scenario real GDP growth rate for each period.

    Args:
        moderate_engine_employment_growth: Employment growth rate (percent) under the moderate climate scenario, driven by projected growth in the working-age (15-64) population from 2029 onward.
        moderate_engine_labour_productivity_growth: Labour productivity growth rate (percent) under the moderate climate scenario, where climate change slows productivity via its effect on real GDP per capita.

    Returns:
        Real GDP growth rate (percent) for each period under the moderate climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(moderate_engine_employment_growth[time_period], 100)), xl_add(1, xl_div(moderate_engine_labour_productivity_growth[time_period], 100))), 100), 100))

    return data.MODERATE_ENGINE_REAL_GDP_GROWTH.collect(evaluate(formula, data.MODERATE_ENGINE_REAL_GDP_GROWTH.required))

@publish(data.MODERATE_ENGINE_GDP_DEFLATOR_GROWTH.schema, cells=data.MODERATE_ENGINE_GDP_DEFLATOR_GROWTH.cells)
def moderate_engine_gdp_deflator_growth(*, baseline_gdp_deflator_growth: data.BaselineGdpDeflatorGrowth) -> data.Series[float | str | None]:
    """Build the GDP deflator growth series for the Moderate climate scenario.

    Provide the Moderate (SSP2-4.5) climate scenario with the same GDP deflator growth path as the baseline, since inflation is assumed unchanged across climate scenarios.

    Args:
        baseline_gdp_deflator_growth: Baseline GDP deflator growth (inflation) projection, indexed by time period; the Moderate scenario reuses these values unchanged.

    Returns:
        A series of GDP deflator growth values for the Moderate climate scenario, aligned with the baseline projection over the Q-CRAFT horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_gdp_deflator_growth[time_period])

    return data.MODERATE_ENGINE_GDP_DEFLATOR_GROWTH.collect(evaluate(formula, data.MODERATE_ENGINE_GDP_DEFLATOR_GROWTH.required))

@publish(data.MODERATE_ENGINE_NOMINAL_GDP_LCU.schema, cells=data.MODERATE_ENGINE_NOMINAL_GDP_LCU.cells)
def moderate_engine_nominal_gdp_lcu(*, baseline_engine_nominal_gdp_lcu: data.Series[float | str | None], scenario_nominal_gdp_growth_moderate: data.ScenarioNominalGdpGrowthModerate) -> data.Series[float | str | None]:
    """Project nominal GDP in local currency units under the Moderate climate scenario.

    Extends the baseline nominal GDP path with the Moderate (SSP2-4.5) scenario's GDP growth rates to trace the macro-fiscal effect of climate change on the tax base.

    Args:
        baseline_engine_nominal_gdp_lcu: Baseline nominal GDP level in billions of local currency units, used through 2029.
        scenario_nominal_gdp_growth_moderate: percentage-point nominal GDP growth rates under the Moderate climate scenario, applied from 2030 onward.

    Returns:
        Nominal GDP in local currency units under the Moderate climate scenario, holding the baseline level through 2029 and compounding the scenario growth rates thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_nominal_gdp_lcu[time_period])
        return as_measure(xl_mul(moderate_engine_nominal_gdp_lcu[time_period - 1], xl_add(1, xl_div(scenario_nominal_gdp_growth_moderate[time_period], 100))))

    moderate_engine_nominal_gdp_lcu = CoordinateReader('moderate_engine_nominal_gdp_lcu', data.MODERATE_ENGINE_NOMINAL_GDP_LCU.required, formula)
    return data.MODERATE_ENGINE_NOMINAL_GDP_LCU.collect((coord, moderate_engine_nominal_gdp_lcu[coord]) for coord in data.MODERATE_ENGINE_NOMINAL_GDP_LCU.required)

@publish(data.MODERATE_ENGINE_REVENUE_PCT_GDP.schema, cells=data.MODERATE_ENGINE_REVENUE_PCT_GDP.cells)
def moderate_engine_revenue_pct_gdp(*, moderate_engine_discrete_risk_revenue_shock: data.Series[float | str | None], baseline_revenue_pct_gdp: data.BaselineRevenuePctGdp) -> data.Series[float | str | None]:
    """Project the revenue-to-GDP ratio under the Moderate climate scenario with discrete risk shocks.

    Combines the baseline revenue-to-GDP ratio with manually registered discrete risk revenue shocks to produce the Moderate scenario revenue path, holding the baseline ratio before the climate projection horizon.

    Args:
        moderate_engine_discrete_risk_revenue_shock: Revenue shock (as a share of GDP) from materialized discrete fiscal risks or natural disasters under the Moderate climate scenario, added to the baseline ratio from 2030 onward.
        baseline_revenue_pct_gdp: Baseline government revenue as a percentage of nominal GDP, assumed to grow in line with nominal GDP with no change in tax policy settings.

    Returns:
        Time series of government revenue as a percentage of nominal GDP under the Moderate climate scenario, equal to the baseline ratio through 2029 and the baseline ratio plus the discrete risk revenue shock thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_revenue_pct_gdp[time_period])
        return as_measure(xl_add(baseline_revenue_pct_gdp[time_period], moderate_engine_discrete_risk_revenue_shock[time_period]))

    return data.MODERATE_ENGINE_REVENUE_PCT_GDP.collect(evaluate(formula, data.MODERATE_ENGINE_REVENUE_PCT_GDP.required))

@publish(data.MODERATE_ENGINE_OVERALL_BALANCE_PCT_GDP.schema, cells=data.MODERATE_ENGINE_OVERALL_BALANCE_PCT_GDP.cells)
def moderate_engine_overall_balance_pct_gdp(*, moderate_engine_revenue_pct_gdp: data.Series[float | str | None], moderate_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Compute the overall balance under the moderate climate scenario as a share of GDP.

    Derive overall balance in percent of GDP for the moderate scenario from revenue and total expenditure, while preserving baseline overall balance through the WEO horizon.

    Args:
        moderate_engine_revenue_pct_gdp: Moderate scenario government revenue expressed as a share of nominal GDP; assumed to decline in line with nominal GDP, leaving the revenue-to-GDP ratio unchanged from the baseline.
        moderate_engine_total_expenditure_pct_gdp: Moderate scenario total expenditure expressed as a share of nominal GDP, combining primary expenditure (held rigid in local currency terms, so the ratio rises as GDP declines) and interest expenditure.
        baseline_overall_balance_pct_gdp: Baseline overall balance as a share of GDP, used to populate the moderate scenario up to the end of the WEO horizon (2029).

    Returns:
        Moderate scenario overall balance as a share of GDP for each projected year, equal to the baseline overall balance through 2029 and to the difference between revenue and total expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_overall_balance_pct_gdp[time_period])
        return as_measure(xl_sub(moderate_engine_revenue_pct_gdp[time_period], moderate_engine_total_expenditure_pct_gdp[time_period]))

    return data.MODERATE_ENGINE_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.MODERATE_ENGINE_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.MODERATE_ENGINE_REVENUE_LCU.schema, cells=data.MODERATE_ENGINE_REVENUE_LCU.cells)
def moderate_engine_revenue_lcu(*, baseline_engine_revenue_lcu: data.Series[float | str | None], moderate_engine_nominal_gdp_lcu: data.Series[float | str | None], moderate_engine_revenue_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project moderate-scenario government revenue in local currency units.

    Under the moderate climate scenario, revenue is assumed to decline in line with nominal GDP, so the revenue-to-GDP ratio stays at its baseline value and revenue is re-derived from that ratio and the scenario's nominal GDP.

    Args:
        baseline_engine_revenue_lcu: Baseline government revenue in billions of local currency units; used through 2029, before the climate scenarios begin affecting fiscal projections.
        moderate_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units under the moderate climate scenario (SSP2-4.5), which declines relative to the baseline as climate change slows productivity growth.
        moderate_engine_revenue_pct_gdp: Revenue-to-GDP ratio in percent under the moderate climate scenario, assumed unchanged from the baseline.

    Returns:
        Time series of government revenue in local currency units under the moderate climate scenario, with baseline values through 2029 and the ratio-implied values thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_revenue_lcu[time_period])
        return as_measure(xl_mul(xl_div(moderate_engine_revenue_pct_gdp[time_period], 100), moderate_engine_nominal_gdp_lcu[time_period]))

    return data.MODERATE_ENGINE_REVENUE_LCU.collect(evaluate(formula, data.MODERATE_ENGINE_REVENUE_LCU.required))

@publish(data.MODERATE_ENGINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.MODERATE_ENGINE_PRIMARY_EXPENDITURE_LCU.cells)
def moderate_engine_primary_expenditure_lcu(*, expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)], baseline_engine_primary_expenditure_lcu: data.Series[float | str | None], moderate_engine_nominal_gdp_lcu: data.Series[float | str | None], moderate_engine_discrete_risk_expenditure_shock: data.Series[float | str | None], moderate_engine_recalibration_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project primary expenditure in local currency units under the Moderate climate change scenario.

    Computes the Moderate scenario's primary expenditure path by holding baseline expenditure rigid and applying recalibration and discrete risk expenditure shocks.

    Args:
        expenditure_rigidity: Degree to which primary expenditure remains rigid in the face of lower GDP, between 0 (fully flexible) and 1 (completely rigid).
        baseline_engine_primary_expenditure_lcu: Baseline scenario primary expenditure (excluding interest payments) in billions of local currency units.
        moderate_engine_nominal_gdp_lcu: Moderate scenario nominal GDP in billions of local currency units, used to convert discrete risk shocks from percent of GDP into local currency amounts.
        moderate_engine_discrete_risk_expenditure_shock: Moderate scenario fiscal cost of materialized discrete risks and natural disasters, expressed as a percentage of nominal GDP.
        moderate_engine_recalibration_lcu: Moderate scenario primary expenditure recalibration in billions of local currency units, scaled by the degree of expenditure flexibility.

    Returns:
        Moderate scenario primary expenditure in billions of local currency units for each projection year.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_expenditure_lcu[time_period])
        return as_measure(xl_add(xl_sub(baseline_engine_primary_expenditure_lcu[time_period], xl_mul(xl_sub(1, expenditure_rigidity), moderate_engine_recalibration_lcu[time_period])), xl_mul(xl_div(moderate_engine_discrete_risk_expenditure_shock[time_period], 100), moderate_engine_nominal_gdp_lcu[time_period])))

    return data.MODERATE_ENGINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.MODERATE_ENGINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.MODERATE_ENGINE_PRIMARY_BALANCE_LCU.schema, cells=data.MODERATE_ENGINE_PRIMARY_BALANCE_LCU.cells)
def moderate_engine_primary_balance_lcu(*, baseline_engine_primary_balance_lcu: data.Series[float | str | None], moderate_engine_revenue_lcu: data.Series[float | str | None], moderate_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the primary balance in local currency units under the moderate climate scenario.

    Derive the moderate-scenario primary balance as revenue less primary expenditure from 2030 onward, carrying over the baseline primary balance through 2029.

    Args:
        baseline_engine_primary_balance_lcu: Baseline-scenario primary balance in local currency units, used unchanged through 2029 before climate change effects begin in 2030.
        moderate_engine_revenue_lcu: Government revenue in local currency units under the moderate climate scenario, declining in line with nominal GDP while the revenue-to-GDP ratio stays at its baseline level.
        moderate_engine_primary_expenditure_lcu: Primary expenditure in local currency units under the moderate climate scenario, held rigid at the baseline level so that its ratio to GDP rises as nominal GDP falls.

    Returns:
        A series of the moderate-scenario primary balance in local currency units: the baseline primary balance for time periods through 2029, and revenue minus primary expenditure from 2030 onward, with the resulting widening deficits reflecting lower revenue against unchanged primary expenditure.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_balance_lcu[time_period])
        return as_measure(xl_sub(moderate_engine_revenue_lcu[time_period], moderate_engine_primary_expenditure_lcu[time_period]))

    return data.MODERATE_ENGINE_PRIMARY_BALANCE_LCU.collect(evaluate(formula, data.MODERATE_ENGINE_PRIMARY_BALANCE_LCU.required))

@publish(data.MODERATE_ENGINE_OVERALL_BALANCE_LCU.schema, cells=data.MODERATE_ENGINE_OVERALL_BALANCE_LCU.cells)
def moderate_engine_overall_balance_lcu(*, baseline_engine_overall_balance_lcu: data.Series[float | str | None], moderate_engine_revenue_lcu: data.Series[float | str | None], moderate_engine_total_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the moderate-scenario overall balance in local currency units.

    Provide the overall fiscal balance under the moderate (SSP2-4.5) climate change scenario, expressed in billions of local currency units.

    Args:
        baseline_engine_overall_balance_lcu: Baseline overall balance in local currency units, used through 2029 (the end of the IMF WEO horizon) since climate change effects are assumed to begin only in 2030.
        moderate_engine_revenue_lcu: Government revenue in local currency units under the moderate climate scenario, which declines in line with nominal GDP while the revenue-to-GDP ratio remains unchanged from the baseline.
        moderate_engine_total_expenditure_lcu: Total government expenditure in local currency units under the moderate climate scenario, reflecting the expenditure rigidity assumption (held at baseline levels when the rigidity parameter equals 1).

    Returns:
        A series of the overall balance in local currency units under the moderate climate scenario: the baseline overall balance through 2029, and revenue minus total expenditure from 2030 onward.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_overall_balance_lcu[time_period])
        return as_measure(xl_sub(moderate_engine_revenue_lcu[time_period], moderate_engine_total_expenditure_lcu[time_period]))

    return data.MODERATE_ENGINE_OVERALL_BALANCE_LCU.collect(evaluate(formula, data.MODERATE_ENGINE_OVERALL_BALANCE_LCU.required))

@publish(data.MODERATE_ENGINE_WEIGHTED_INTEREST_RATE.schema, cells=data.MODERATE_ENGINE_WEIGHTED_INTEREST_RATE.cells)
def moderate_engine_weighted_interest_rate(*, baseline_interest_rate: data.BaselineInterestRate) -> data.Series[float | str | None]:
    """Project the weighted average nominal interest rate on government debt under the Moderate climate change scenario.

    Provide the interest rate path used in the debt dynamics equation when quantifying fiscal risks under the Moderate (SSP2-4.5) scenario, in which emissions stabilise at the end of the century along observed trends.

    Args:
        baseline_interest_rate: Baseline scenario profile of the weighted average nominal interest rate on government debt, reflecting the sovereign debt profile and the user's chosen interest rate assumption (constant nominal interest rate, constant interest-growth differential, or constant real interest rate).

    Returns:
        Series of the Moderate-scenario weighted average nominal interest rate by projection year, expressed in percent and used to derive debt dynamics.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_rate[time_period])

    return data.MODERATE_ENGINE_WEIGHTED_INTEREST_RATE.collect(evaluate(formula, data.MODERATE_ENGINE_WEIGHTED_INTEREST_RATE.required))

@publish(data.MODERATE_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.schema, cells=data.MODERATE_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.cells)
def moderate_engine_interest_expenditure_pct_revenue(*, moderate_engine_revenue_lcu: data.Series[float | str | None], moderate_engine_interest_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Interest expenditure as a share of revenue under the moderate scenario.

    Expresses interest expenditure as a percent of revenue under the moderate scenario so it can be compared with the baseline interest burden as a share of the revenue base.

    Args:
        moderate_engine_revenue_lcu: Government revenue in local currency units for each projection year, used as the denominator of the interest expenditure ratio.
        moderate_engine_interest_expenditure_lcu: Government interest expenditure in local currency units for each projection year, used as the numerator of the interest expenditure ratio.

    Returns:
        A time series of interest expenditure as a percent of revenue for each projection year, in local currency unit terms.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(moderate_engine_interest_expenditure_lcu[time_period], moderate_engine_revenue_lcu[time_period]), 100))

    return data.MODERATE_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.collect(evaluate(formula, data.MODERATE_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.required))

@publish(data.MODERATE_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.schema, cells=data.MODERATE_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.cells)
def moderate_engine_discrete_risk_revenue_shock(*, discrete_revenue_shocks: data.DiscreteRevenueShocks) -> data.Series[float | str | None]:
    """Extract the moderate-scenario discrete revenue shock series.

    Provide the projected revenue loss from materialized discrete fiscal risks under the moderate climate change scenario as a share of GDP, for use in the fiscal projections.

    Args:
        discrete_revenue_shocks: Discrete revenue shock entries, expressed as a percent of GDP, keyed by climate change scenario and projection year; the 'Moderate' scenario row is selected here.

    Returns:
        A series of discrete revenue shocks, as a percent of GDP, for the moderate climate change scenario across the projection horizon.
    """
    data.DISCRETE_REVENUE_SHOCKS.schema.validate(discrete_revenue_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_revenue_shocks['Moderate', time_period])

    return data.MODERATE_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.collect(evaluate(formula, data.MODERATE_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.required))

@publish(data.MODERATE_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.schema, cells=data.MODERATE_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.cells)
def moderate_engine_discrete_risk_expenditure_shock(*, discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks) -> data.Series[float | str | None]:
    """Return the moderate-scenario discrete risk primary expenditure shocks.

    Extracts the moderate climate scenario's discrete primary expenditure shock path so it can be applied as a one-off rise in primary expenditure.

    Args:
        discrete_primary_expenditure_shocks: Discrete primary expenditure shocks by climate change scenario and projection year, expressed as a percent of GDP, from which the moderate scenario path is selected.

    Returns:
        The moderate scenario's discrete primary expenditure shock for each projection year, as a percent of GDP.
    """
    data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.schema.validate(discrete_primary_expenditure_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_primary_expenditure_shocks['Moderate', time_period])

    return data.MODERATE_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.collect(evaluate(formula, data.MODERATE_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.required))

@publish(data.MODERATE_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.schema, cells=data.MODERATE_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.cells)
def moderate_engine_memo_interest_expenditure_pct_gdp(*, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp) -> data.Series[float | str | None]:
    """Compute the moderate-scenario memo of interest expenditure as a share of GDP.

    Carries the baseline interest-expenditure-to-GDP path through the moderate climate scenario unchanged, since monetary and external sectors are exogenous and inflation is assumed to remain unchanged across climate scenarios.

    Args:
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure expressed as a percentage of nominal GDP, indexed by projection year.

    Returns:
        A series of interest expenditure as a percentage of GDP under the moderate climate scenario, with the same values as the baseline memo.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_expenditure_pct_gdp[time_period])

    return data.MODERATE_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.MODERATE_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.required))

@publish(data.MODERATE_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.schema, cells=data.MODERATE_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.cells)
def moderate_engine_memo_primary_expenditure_pct_gdp(*, baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp) -> data.Series[float | str | None]:
    """Pass through baseline primary expenditure as a share of GDP to the moderate climate scenario.

    Provide a memo series showing the primary expenditure-to-GDP ratio carried over from the baseline into the moderate scenario, where primary expenditure is held rigid in local currency terms while nominal GDP declines.

    Args:
        baseline_primary_expenditure_pct_gdp: Baseline-scenario primary expenditure as a percent of nominal GDP, expressed per time period; it is passed through unchanged to the moderate scenario.

    Returns:
        A series of the primary expenditure-to-GDP ratio for the moderate scenario, with one value per time period, or None where the baseline value is missing.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_expenditure_pct_gdp[time_period])

    return data.MODERATE_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.MODERATE_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.required))

@publish(data.MODERATE_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.schema, cells=data.MODERATE_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.cells)
def moderate_engine_memo_primary_balance_pct_gdp(*, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Return the primary balance (in percent of GDP) carried over into the moderate climate scenario as a memo series.

    Under the moderate scenario (SSP2-4.5), the revenue-to-GDP ratio is held at its baseline level, so the memo primary balance simply mirrors the baseline primary balance path.

    Args:
        baseline_primary_balance_pct_gdp: Baseline primary balance expressed as a percentage of nominal GDP, aligned to the projection time periods, used as the memo value for the moderate climate scenario.

    Returns:
        A Series of the primary balance as a percentage of GDP for the moderate climate scenario, matching the baseline primary balance for each projected time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_balance_pct_gdp[time_period])

    return data.MODERATE_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.collect(evaluate(formula, data.MODERATE_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.required))

@publish(data.MODERATE_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.schema, cells=data.MODERATE_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.cells)
def moderate_engine_memo_overall_balance_pct_gdp(*, baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Return the overall balance as a percent of GDP memo series under the Moderate climate scenario.

    Memoizes the baseline overall balance-to-GDP ratio so it can be reused across Moderate climate scenario fiscal projections.

    Args:
        baseline_overall_balance_pct_gdp: Baseline overall balance expressed as a percent of nominal GDP; used unchanged as the memo series for the Moderate scenario.

    Returns:
        A per-period series of the baseline overall balance-to-GDP ratio, in percent, for the Moderate climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_overall_balance_pct_gdp[time_period])

    return data.MODERATE_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.MODERATE_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.MODERATE_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.schema, cells=data.MODERATE_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.cells)
def moderate_engine_memo_gross_debt_pct_gdp(*, baseline_debt_to_gdp: data.BaselineDebtToGdp) -> data.Series[float | str | None]:
    """Report gross debt as a share of GDP under the Moderate climate scenario.

    Provides the Moderate (SSP2-4.5) climate scenario's memo series for the gross debt-to-GDP ratio, in which emissions continue along present trends and mitigation policies are not strengthened beyond observed trends.

    Args:
        baseline_debt_to_gdp: Baseline gross debt-to-GDP ratio series, used as the projection basis from which the Moderate climate scenario memo values are derived.

    Returns:
        A series of gross debt-to-GDP ratio values for the Moderate climate scenario, keyed by projection year, with None marking years for which no value is available.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_to_gdp[time_period])

    return data.MODERATE_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.collect(evaluate(formula, data.MODERATE_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.required))

@publish(data.MODERATE_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.MODERATE_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.cells)
def moderate_engine_baseline_primary_expenditure_lcu(*, baseline_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project baseline primary expenditure in local currency units under the moderate climate scenario.

    Converts the baseline primary expenditure path into the moderate climate scenario's primary expenditure series in local currency units, which Q-CRAFT holds rigid from the baseline so that the primary expenditure-to-GDP ratio rises as nominal GDP declines under climate change.

    Args:
        baseline_engine_primary_expenditure_lcu: Baseline scenario primary expenditure, in billions of local currency units, excluding government interest payments; used unchanged as the rigid primary expenditure level for the moderate climate scenario.

    Returns:
        A series of moderate-scenario primary expenditure values in local currency units, aligned to the projection horizon, equal to the corresponding baseline primary expenditure values.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_engine_primary_expenditure_lcu[time_period])

    return data.MODERATE_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.MODERATE_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.MODERATE_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.schema, cells=data.MODERATE_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.cells)
def moderate_engine_primary_expenditure_baseline_share_lcu(*, moderate_engine_nominal_gdp_lcu: data.Series[float | str | None], moderate_engine_memo_primary_expenditure_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the baseline primary expenditure level in local currency units.

    Translate the baseline primary expenditure ratio into local currency units using nominal GDP, consistent with the 'no policy change' baseline assumption.

    Args:
        moderate_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units for the moderate climate change scenario.
        moderate_engine_memo_primary_expenditure_pct_gdp: Primary expenditure as a percent of nominal GDP for the moderate climate change scenario.

    Returns:
        A time series of baseline primary expenditure in local currency units.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(moderate_engine_memo_primary_expenditure_pct_gdp[time_period], 100), moderate_engine_nominal_gdp_lcu[time_period]))

    return data.MODERATE_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.collect(evaluate(formula, data.MODERATE_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.required))

@publish(data.MODERATE_ENGINE_RECALIBRATION_LCU.schema, cells=data.MODERATE_ENGINE_RECALIBRATION_LCU.cells)
def moderate_engine_recalibration_lcu(*, moderate_engine_baseline_primary_expenditure_lcu: data.Series[float | str | None], moderate_engine_primary_expenditure_baseline_share_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Recalibrate baseline primary expenditure in local currency units.

    Adjusts the baseline primary expenditure path in local currency terms, providing the expenditure level used for the climate scenarios.

    Args:
        moderate_engine_baseline_primary_expenditure_lcu: Time series of baseline primary expenditure in local currency units.
        moderate_engine_primary_expenditure_baseline_share_lcu: Time series of the share in local currency units to be netted from baseline primary expenditure.

    Returns:
        Time series of recalibrated primary expenditure in local currency units, with the provided share subtracted from the baseline expenditure.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(moderate_engine_baseline_primary_expenditure_lcu[time_period], moderate_engine_primary_expenditure_baseline_share_lcu[time_period]))

    return data.MODERATE_ENGINE_RECALIBRATION_LCU.collect(evaluate(formula, data.MODERATE_ENGINE_RECALIBRATION_LCU.required))

@dataclass(frozen=True, slots=True)
class ScanModerateEngineTotalExpenditurePctGdpResult:
    """Complete named results of one recurrence group evaluation."""
    moderate_engine_total_expenditure_pct_gdp: data.Series[float | str | None]
    moderate_engine_primary_balance_pct_gdp: data.Series[float | str | None]
    moderate_engine_total_expenditure_lcu: data.Series[float | str | None]
    moderate_engine_interest_expenditure_lcu: data.Series[float | str | None]
    moderate_engine_gross_debt_lcu: data.Series[float | str | None]
    moderate_engine_gross_debt_pct_gdp: data.Series[float | str | None]
    scenario_primary_expenditure_pct_gdp_moderate: data.ScenarioPrimaryExpenditurePctGdpModerate
    scenario_interest_expenditure_pct_gdp_moderate: data.ScenarioInterestExpenditurePctGdpModerate

def scan_moderate_engine_total_expenditure_pct_gdp(*, baseline_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_engine_total_expenditure_lcu: data.Series[float | str | None], baseline_engine_interest_expenditure_lcu: data.Series[float | str | None], baseline_engine_gross_debt_lcu: data.Series[float | str | None], moderate_engine_nominal_gdp_lcu: data.Series[float | str | None], moderate_engine_revenue_pct_gdp: data.Series[float | str | None], moderate_engine_primary_expenditure_lcu: data.Series[float | str | None], moderate_engine_weighted_interest_rate: data.Series[float | str | None], baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp, baseline_debt_to_gdp: data.BaselineDebtToGdp, scenario_nominal_gdp_growth_moderate: data.ScenarioNominalGdpGrowthModerate) -> ScanModerateEngineTotalExpenditurePctGdpResult:
    """Evaluate the recurrence group rooted at total expenditure for the Moderate climate scenario and publish all derived tensors.

    Project the Moderate climate scenario's total expenditure (as a share of GDP and in local currency units) together with its associated primary balance, interest expenditure, and gross debt series, holding baseline values through 2029 and applying the debt-dynamics relationships thereafter.

    Args:
        baseline_engine_total_expenditure_pct_gdp: Baseline total expenditure as a share of nominal GDP, used as the source for the Moderate scenario before the climate effect starts in 2030.
        baseline_engine_total_expenditure_lcu: Baseline total expenditure in billions of local currency units, used to seed the Moderate scenario total expenditure before 2030.
        baseline_engine_interest_expenditure_lcu: Baseline interest expenditure in billions of local currency units, seeding interest expenditure and, through the weighted interest rate, gross debt in the Moderate scenario before 2030.
        baseline_engine_gross_debt_lcu: Baseline gross government debt in billions of local currency units, seeding the Moderate scenario's debt stock before 2030.
        moderate_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units under the Moderate climate scenario, used to scale expenditure, interest, and debt aggregates.
        moderate_engine_revenue_pct_gdp: Government revenue as a share of nominal GDP under the Moderate scenario, assumed to remain at baseline levels and used to derive the primary balance.
        moderate_engine_primary_expenditure_lcu: Primary expenditure in billions of local currency units under the Moderate scenario, reflecting the expenditure rigidity assumption and combined with interest expenditure to give total expenditure.
        moderate_engine_weighted_interest_rate: Weighted average nominal interest rate on government debt under the Moderate scenario, applied to the previous period's debt stock to compute interest expenditure.
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure as a share of nominal GDP, carried forward into the Moderate scenario before the climate effect begins in 2030.
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure as a share of nominal GDP, carried forward into the Moderate scenario before 2030.
        baseline_primary_balance_pct_gdp: Baseline primary balance as a share of nominal GDP, carried forward into the Moderate scenario before 2030.
        baseline_debt_to_gdp: Baseline gross debt-to-GDP ratio, carried forward as the starting point for the Moderate scenario debt dynamics.
        scenario_nominal_gdp_growth_moderate: Nominal GDP growth rate under the Moderate scenario, used in the debt-dynamics equation to project gross debt relative to GDP.

    Returns:
        A ScanModerateEngineTotalExpenditurePctGdpResult holding the projected Moderate scenario series for total expenditure (as a share of GDP and in local currency units), primary balance, interest expenditure in local currency units, gross debt in local currency units and as a share of GDP, and primary and interest expenditure as shares of GDP.
    """
    def moderate_engine_total_expenditure_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(moderate_engine_total_expenditure_lcu[time_period], moderate_engine_nominal_gdp_lcu[time_period]), 100))

    moderate_engine_total_expenditure_pct_gdp = CoordinateReader('moderate_engine_total_expenditure_pct_gdp', data.MODERATE_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required, moderate_engine_total_expenditure_pct_gdp_formula)
    def moderate_engine_primary_balance_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_balance_pct_gdp[time_period])
        return as_measure(xl_sub(moderate_engine_revenue_pct_gdp[time_period], scenario_primary_expenditure_pct_gdp_moderate[time_period]))

    moderate_engine_primary_balance_pct_gdp = CoordinateReader('moderate_engine_primary_balance_pct_gdp', data.MODERATE_ENGINE_PRIMARY_BALANCE_PCT_GDP.required, moderate_engine_primary_balance_pct_gdp_formula)
    def moderate_engine_total_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_lcu[time_period])
        return as_measure(xl_add(moderate_engine_interest_expenditure_lcu[time_period], moderate_engine_primary_expenditure_lcu[time_period]))

    moderate_engine_total_expenditure_lcu = CoordinateReader('moderate_engine_total_expenditure_lcu', data.MODERATE_ENGINE_TOTAL_EXPENDITURE_LCU.required, moderate_engine_total_expenditure_lcu_formula)
    def moderate_engine_interest_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_interest_expenditure_lcu[time_period])
        return as_measure(xl_mul(xl_div(moderate_engine_weighted_interest_rate[time_period], 100), moderate_engine_gross_debt_lcu[time_period - 1]))

    moderate_engine_interest_expenditure_lcu = CoordinateReader('moderate_engine_interest_expenditure_lcu', data.MODERATE_ENGINE_INTEREST_EXPENDITURE_LCU.required, moderate_engine_interest_expenditure_lcu_formula)
    def moderate_engine_gross_debt_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_gross_debt_lcu[time_period])
        return as_measure(xl_mul(xl_div(moderate_engine_gross_debt_pct_gdp[time_period], 100), moderate_engine_nominal_gdp_lcu[time_period]))

    moderate_engine_gross_debt_lcu = CoordinateReader('moderate_engine_gross_debt_lcu', data.MODERATE_ENGINE_GROSS_DEBT_LCU.required, moderate_engine_gross_debt_lcu_formula)
    def moderate_engine_gross_debt_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_debt_to_gdp[time_period])
        return as_measure(xl_sub(xl_div(xl_mul(moderate_engine_gross_debt_pct_gdp[time_period - 1], xl_add(1, xl_div(moderate_engine_weighted_interest_rate[time_period], 100))), xl_add(1, xl_div(scenario_nominal_gdp_growth_moderate[time_period], 100))), moderate_engine_primary_balance_pct_gdp[time_period]))

    moderate_engine_gross_debt_pct_gdp = CoordinateReader('moderate_engine_gross_debt_pct_gdp', data.MODERATE_ENGINE_GROSS_DEBT_PCT_GDP.required, moderate_engine_gross_debt_pct_gdp_formula)
    def scenario_primary_expenditure_pct_gdp_moderate_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_expenditure_pct_gdp[time_period])
        return as_measure(xl_sub(moderate_engine_total_expenditure_pct_gdp[time_period], scenario_interest_expenditure_pct_gdp_moderate[time_period]))

    scenario_primary_expenditure_pct_gdp_moderate = CoordinateReader('scenario_primary_expenditure_pct_gdp_moderate', data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_MODERATE.required, scenario_primary_expenditure_pct_gdp_moderate_formula)
    def scenario_interest_expenditure_pct_gdp_moderate_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_interest_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(moderate_engine_interest_expenditure_lcu[time_period], moderate_engine_nominal_gdp_lcu[time_period]), 100))

    scenario_interest_expenditure_pct_gdp_moderate = CoordinateReader('scenario_interest_expenditure_pct_gdp_moderate', data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_MODERATE.required, scenario_interest_expenditure_pct_gdp_moderate_formula)
    return ScanModerateEngineTotalExpenditurePctGdpResult(
        moderate_engine_total_expenditure_pct_gdp=data.MODERATE_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.collect((coord, moderate_engine_total_expenditure_pct_gdp[coord]) for coord in data.MODERATE_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required),
        moderate_engine_primary_balance_pct_gdp=data.MODERATE_ENGINE_PRIMARY_BALANCE_PCT_GDP.collect((coord, moderate_engine_primary_balance_pct_gdp[coord]) for coord in data.MODERATE_ENGINE_PRIMARY_BALANCE_PCT_GDP.required),
        moderate_engine_total_expenditure_lcu=data.MODERATE_ENGINE_TOTAL_EXPENDITURE_LCU.collect((coord, moderate_engine_total_expenditure_lcu[coord]) for coord in data.MODERATE_ENGINE_TOTAL_EXPENDITURE_LCU.required),
        moderate_engine_interest_expenditure_lcu=data.MODERATE_ENGINE_INTEREST_EXPENDITURE_LCU.collect((coord, moderate_engine_interest_expenditure_lcu[coord]) for coord in data.MODERATE_ENGINE_INTEREST_EXPENDITURE_LCU.required),
        moderate_engine_gross_debt_lcu=data.MODERATE_ENGINE_GROSS_DEBT_LCU.collect((coord, moderate_engine_gross_debt_lcu[coord]) for coord in data.MODERATE_ENGINE_GROSS_DEBT_LCU.required),
        moderate_engine_gross_debt_pct_gdp=data.MODERATE_ENGINE_GROSS_DEBT_PCT_GDP.collect((coord, moderate_engine_gross_debt_pct_gdp[coord]) for coord in data.MODERATE_ENGINE_GROSS_DEBT_PCT_GDP.required),
        scenario_primary_expenditure_pct_gdp_moderate=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_MODERATE.collect((coord, scenario_primary_expenditure_pct_gdp_moderate[coord]) for coord in data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_MODERATE.required),
        scenario_interest_expenditure_pct_gdp_moderate=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_MODERATE.collect((coord, scenario_interest_expenditure_pct_gdp_moderate[coord]) for coord in data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_MODERATE.required),
    )

@publish(data.HIGH_ENGINE_EMPLOYMENT_GROWTH.schema, cells=data.HIGH_ENGINE_EMPLOYMENT_GROWTH.cells)
def high_engine_employment_growth(*, baseline_employment_growth: data.BaselineEmploymentGrowth) -> data.Series[float | str | None]:
    """Return the high-engine employment growth series.

    Provide the employment growth series used by the high climate change engine, drawn from the baseline employment growth assumption.

    Args:
        baseline_employment_growth: Baseline employment growth assumption series, expressed as growth in employment (projected to grow in line with the working-age population) by projection year.

    Returns:
        A series of employment growth values by projection year, taken from the baseline employment growth assumption.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_employment_growth[time_period])

    return data.HIGH_ENGINE_EMPLOYMENT_GROWTH.collect(evaluate(formula, data.HIGH_ENGINE_EMPLOYMENT_GROWTH.required))

@publish(data.HIGH_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.schema, cells=data.HIGH_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.cells)
def high_engine_labour_productivity_growth(*, climate_data_labour_productivity_growth_variation_high: data.Series[float | str | None], baseline_labour_productivity_growth: data.BaselineLabourProductivityGrowth) -> data.Series[float | str | None]:
    """Compute high-scenario labour productivity growth.

    Combine the baseline labour productivity growth path with the high climate scenario's variation in labour productivity growth to yield the high-scenario growth path.

    Args:
        climate_data_labour_productivity_growth_variation_high: Climate scenario data for the high emissions SSP3-7.0 scenario, giving the year-by-year variation in labour productivity growth (GDP per employed person growth) attributable to climate change.
        baseline_labour_productivity_growth: Baseline labour productivity growth path assumed in Q-CRAFT and entered by the user on the Productivity worksheet; it reflects the structural, no-climate-change productivity trajectory.

    Returns:
        The high-scenario labour productivity growth series, computed as the baseline labour productivity growth plus the high-scenario climate variation in labour productivity growth, on the tool's long-term projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(baseline_labour_productivity_growth[time_period], climate_data_labour_productivity_growth_variation_high[time_period]))

    return data.HIGH_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.collect(evaluate(formula, data.HIGH_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.required))

@publish(data.HIGH_ENGINE_REAL_GDP_GROWTH.schema, cells=data.HIGH_ENGINE_REAL_GDP_GROWTH.cells)
def high_engine_real_gdp_growth(*, high_engine_employment_growth: data.Series[float | str | None], high_engine_labour_productivity_growth: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute high-engine real GDP growth from employment growth and labour productivity growth.

    Derive the high-engine real GDP growth rate used by the baseline scenario, following the user guide's decomposition of real GDP growth as the sum of employment growth and labour productivity growth.

    Args:
        high_engine_employment_growth: High-engine employment growth, in percent, projected in line with working-age (15-64 year) population growth.
        high_engine_labour_productivity_growth: High-engine labour productivity growth, in percent, measured as growth in real GDP per employed person.

    Returns:
        High-engine real GDP growth series, in percent, computed per period as the compounded combination of employment growth and labour productivity growth.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(high_engine_employment_growth[time_period], 100)), xl_add(1, xl_div(high_engine_labour_productivity_growth[time_period], 100))), 100), 100))

    return data.HIGH_ENGINE_REAL_GDP_GROWTH.collect(evaluate(formula, data.HIGH_ENGINE_REAL_GDP_GROWTH.required))

@publish(data.HIGH_ENGINE_GDP_DEFLATOR_GROWTH.schema, cells=data.HIGH_ENGINE_GDP_DEFLATOR_GROWTH.cells)
def high_engine_gdp_deflator_growth(*, baseline_gdp_deflator_growth: data.BaselineGdpDeflatorGrowth) -> data.Series[float | str | None]:
    """Return the GDP deflator growth series under the high climate scenario.

    Provides the deflator growth path applied when projecting nominal GDP and fiscal aggregates under a high-emissions climate change scenario.

    Args:
        baseline_gdp_deflator_growth: Baseline GDP deflator growth assumption, used to derive the corresponding deflator growth values for the high scenario.

    Returns:
        A series of GDP deflator growth rates for the high scenario, aligned to the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_gdp_deflator_growth[time_period])

    return data.HIGH_ENGINE_GDP_DEFLATOR_GROWTH.collect(evaluate(formula, data.HIGH_ENGINE_GDP_DEFLATOR_GROWTH.required))

@publish(data.HIGH_ENGINE_NOMINAL_GDP_LCU.schema, cells=data.HIGH_ENGINE_NOMINAL_GDP_LCU.cells)
def high_engine_nominal_gdp_lcu(*, baseline_engine_nominal_gdp_lcu: data.Series[float | str | None], scenario_nominal_gdp_growth_high: data.ScenarioNominalGdpGrowthHigh) -> data.Series[float | str | None]:
    """Project nominal GDP in local currency units under the high climate change scenario.

    Extends baseline nominal GDP through 2099 by compounding an annual high-scenario growth rate, so fiscal aggregates can be assessed under high-emissions warming.

    Args:
        baseline_engine_nominal_gdp_lcu: Baseline nominal GDP in billions of local currency units; values through 2029 are carried into the high scenario unchanged, as climate change is assumed to affect fiscal projections only from 2030.
        scenario_nominal_gdp_growth_high: Nominal GDP growth rate (in percent) under the high scenario, reflecting the macroeconomic slowdown in productivity growth from rising temperatures; applied from 2030 onward.

    Returns:
        A series of nominal GDP in billions of local currency units for the high scenario along the projection horizon to 2099.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_nominal_gdp_lcu[time_period])
        return as_measure(xl_mul(high_engine_nominal_gdp_lcu[time_period - 1], xl_add(1, xl_div(scenario_nominal_gdp_growth_high[time_period], 100))))

    high_engine_nominal_gdp_lcu = CoordinateReader('high_engine_nominal_gdp_lcu', data.HIGH_ENGINE_NOMINAL_GDP_LCU.required, formula)
    return data.HIGH_ENGINE_NOMINAL_GDP_LCU.collect((coord, high_engine_nominal_gdp_lcu[coord]) for coord in data.HIGH_ENGINE_NOMINAL_GDP_LCU.required)

@publish(data.HIGH_ENGINE_REVENUE_PCT_GDP.schema, cells=data.HIGH_ENGINE_REVENUE_PCT_GDP.cells)
def high_engine_revenue_pct_gdp(*, high_engine_discrete_risk_revenue_shock: data.Series[float | str | None], baseline_revenue_pct_gdp: data.BaselineRevenuePctGdp) -> data.Series[float | str | None]:
    """Compute the high-scenario revenue-to-GDP ratio including discrete risk revenue shocks.

    Produces the high climate scenario revenue path by adding any registered discrete revenue shock to the baseline revenue-to-GDP ratio from 2030 onward, leaving the baseline unchanged through 2029.

    Args:
        high_engine_discrete_risk_revenue_shock: Revenue loss (as a percentage of GDP) from materialized discrete fiscal risks and natural disasters registered for the high emissions scenario, by projection year; zero where no risk is registered and absent before 2030.
        baseline_revenue_pct_gdp: Baseline revenue-to-GDP ratio by projection year, reflecting the constant revenue-to-GDP assumption of the no-policy-change baseline.

    Returns:
        A series of revenue-to-GDP ratios for the high emissions scenario, equal to the baseline ratio through 2029 and to the baseline ratio plus the discrete risk revenue shock thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_revenue_pct_gdp[time_period])
        return as_measure(xl_add(baseline_revenue_pct_gdp[time_period], high_engine_discrete_risk_revenue_shock[time_period]))

    return data.HIGH_ENGINE_REVENUE_PCT_GDP.collect(evaluate(formula, data.HIGH_ENGINE_REVENUE_PCT_GDP.required))

@publish(data.HIGH_ENGINE_OVERALL_BALANCE_PCT_GDP.schema, cells=data.HIGH_ENGINE_OVERALL_BALANCE_PCT_GDP.cells)
def high_engine_overall_balance_pct_gdp(*, high_engine_revenue_pct_gdp: data.Series[float | str | None], high_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Compute the high-engine overall balance as a share of GDP in percent.

    Projects the overall balance under the high climate change scenario, derived from revenue and total expenditure and anchored to the baseline before the climate horizon begins.

    Args:
        high_engine_revenue_pct_gdp: Government revenue as a share of nominal GDP in percent under the high climate change scenario, where revenue declines in line with nominal GDP while the revenue-to-GDP ratio remains unchanged from the baseline.
        high_engine_total_expenditure_pct_gdp: Total government expenditure as a share of nominal GDP in percent under the high climate change scenario, including interest payments.
        baseline_overall_balance_pct_gdp: Baseline overall balance as a share of nominal GDP in percent, reflecting 'no policy change' assumptions, used up to and including 2029 before climate change effects begin in 2030.

    Returns:
        Overall balance as a share of nominal GDP in percent under the high climate change scenario, equal to the baseline balance through 2029 and to high-engine revenue minus high-engine total expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_overall_balance_pct_gdp[time_period])
        return as_measure(xl_sub(high_engine_revenue_pct_gdp[time_period], high_engine_total_expenditure_pct_gdp[time_period]))

    return data.HIGH_ENGINE_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.HIGH_ENGINE_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.HIGH_ENGINE_REVENUE_LCU.schema, cells=data.HIGH_ENGINE_REVENUE_LCU.cells)
def high_engine_revenue_lcu(*, baseline_engine_revenue_lcu: data.Series[float | str | None], high_engine_nominal_gdp_lcu: data.Series[float | str | None], high_engine_revenue_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project government revenue in local currency units under the high climate change scenario.

    Derives high-scenario revenue by holding the revenue-to-GDP ratio constant while nominal GDP declines, except through 2029 where baseline revenue is carried forward.

    Args:
        baseline_engine_revenue_lcu: Baseline government revenue in billions of local currency units, used unchanged through 2029 before climate change effects begin in 2030.
        high_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units under the high climate change scenario (SSP3-7.0 emissions), which declines relative to the baseline as warming slows productivity growth.
        high_engine_revenue_pct_gdp: Government revenue as a percent of nominal GDP under the high climate change scenario, held constant at the baseline ratio because tax policy is assumed unchanged.

    Returns:
        Government revenue in billions of local currency units for each projected year under the high climate change scenario.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_revenue_lcu[time_period])
        return as_measure(xl_mul(xl_div(high_engine_revenue_pct_gdp[time_period], 100), high_engine_nominal_gdp_lcu[time_period]))

    return data.HIGH_ENGINE_REVENUE_LCU.collect(evaluate(formula, data.HIGH_ENGINE_REVENUE_LCU.required))

@publish(data.HIGH_ENGINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.HIGH_ENGINE_PRIMARY_EXPENDITURE_LCU.cells)
def high_engine_primary_expenditure_lcu(*, expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)], baseline_engine_primary_expenditure_lcu: data.Series[float | str | None], high_engine_nominal_gdp_lcu: data.Series[float | str | None], high_engine_discrete_risk_expenditure_shock: data.Series[float | str | None], high_engine_recalibration_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project primary expenditure in local currency units under the high climate scenario.

    Produces the high-scenario primary expenditure path by applying expenditure rigidity, discrete-risk shocks, and recalibration adjustments to the baseline.

    Args:
        expenditure_rigidity: Expenditure rigidity parameter between 0 (fully flexible) and 1 (completely rigid), controlling how much primary expenditure adjusts toward the baseline expenditure-to-GDP ratio as nominal GDP declines.
        baseline_engine_primary_expenditure_lcu: Primary expenditure under the baseline scenario, in billions of local currency units; used unchanged through 2029 and as the starting point thereafter.
        high_engine_nominal_gdp_lcu: Nominal GDP under the high climate scenario, in billions of local currency units, used to convert discrete-risk shocks expressed as a share of GDP into local currency amounts.
        high_engine_discrete_risk_expenditure_shock: Fiscal impact of materialized discrete risks and natural disasters under the high climate scenario, expressed as a percentage of GDP, which raises primary expenditure.
        high_engine_recalibration_lcu: Recalibration of primary expenditure in local currency units, scaled by (1 minus expenditure rigidity), that reduces the rigidity-implied gap from baseline primary expenditure.

    Returns:
        Time series of primary expenditure in billions of local currency units under the high climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_expenditure_lcu[time_period])
        return as_measure(xl_add(xl_sub(baseline_engine_primary_expenditure_lcu[time_period], xl_mul(xl_sub(1, expenditure_rigidity), high_engine_recalibration_lcu[time_period])), xl_mul(xl_div(high_engine_discrete_risk_expenditure_shock[time_period], 100), high_engine_nominal_gdp_lcu[time_period])))

    return data.HIGH_ENGINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.HIGH_ENGINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.HIGH_ENGINE_PRIMARY_BALANCE_LCU.schema, cells=data.HIGH_ENGINE_PRIMARY_BALANCE_LCU.cells)
def high_engine_primary_balance_lcu(*, baseline_engine_primary_balance_lcu: data.Series[float | str | None], high_engine_revenue_lcu: data.Series[float | str | None], high_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the primary balance under the high climate change scenario.

    Project the high scenario primary balance in local currency units, taking the baseline value before the climate impact start year and the difference between revenue and primary expenditure thereafter.

    Args:
        baseline_engine_primary_balance_lcu: Baseline scenario primary balance in local currency units, used up to 2029 before climate change effects begin.
        high_engine_revenue_lcu: Government revenue in local currency units under the high climate change scenario, which declines with nominal GDP while the revenue-to-GDP ratio stays at its baseline level.
        high_engine_primary_expenditure_lcu: Primary expenditure in local currency units under the high climate change scenario, held rigid at the baseline level so its ratio to GDP rises as nominal GDP falls.

    Returns:
        The high scenario primary balance in local currency units for each period, derived as revenue less primary expenditure from 2030 onward and from the baseline primary balance in earlier years.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_balance_lcu[time_period])
        return as_measure(xl_sub(high_engine_revenue_lcu[time_period], high_engine_primary_expenditure_lcu[time_period]))

    return data.HIGH_ENGINE_PRIMARY_BALANCE_LCU.collect(evaluate(formula, data.HIGH_ENGINE_PRIMARY_BALANCE_LCU.required))

@publish(data.HIGH_ENGINE_OVERALL_BALANCE_LCU.schema, cells=data.HIGH_ENGINE_OVERALL_BALANCE_LCU.cells)
def high_engine_overall_balance_lcu(*, baseline_engine_overall_balance_lcu: data.Series[float | str | None], high_engine_revenue_lcu: data.Series[float | str | None], high_engine_total_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the high climate scenario overall balance in local currency units.

    Derive the high-scenario overall fiscal balance as revenue minus total expenditure, defaulting to the baseline overall balance through 2029.

    Args:
        baseline_engine_overall_balance_lcu: Baseline scenario overall balance in local currency units, used for time periods through 2029.
        high_engine_revenue_lcu: Government revenue in local currency units under the high climate change scenario, calculated as a constant share of nominal GDP.
        high_engine_total_expenditure_lcu: Total government expenditure in local currency units under the high climate change scenario.

    Returns:
        Overall balance in local currency units under the high climate change scenario: the baseline overall balance through 2029 and high-scenario revenue minus total expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_overall_balance_lcu[time_period])
        return as_measure(xl_sub(high_engine_revenue_lcu[time_period], high_engine_total_expenditure_lcu[time_period]))

    return data.HIGH_ENGINE_OVERALL_BALANCE_LCU.collect(evaluate(formula, data.HIGH_ENGINE_OVERALL_BALANCE_LCU.required))

@publish(data.HIGH_ENGINE_WEIGHTED_INTEREST_RATE.schema, cells=data.HIGH_ENGINE_WEIGHTED_INTEREST_RATE.cells)
def high_engine_weighted_interest_rate(*, baseline_interest_rate: data.BaselineInterestRate) -> data.Series[float | str | None]:
    """Project the high climate scenario's weighted average nominal interest rate.

    Uses the baseline interest rate assumptions to project the weighted average nominal interest rate on government debt under the high-emissions climate scenario.

    Args:
        baseline_interest_rate: Baseline economic scenario's weighted average nominal interest rate on government debt, entering from the baseline assumption selected in the Dashboard.

    Returns:
        A series of the high climate scenario's weighted average nominal interest rate by projection year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_rate[time_period])

    return data.HIGH_ENGINE_WEIGHTED_INTEREST_RATE.collect(evaluate(formula, data.HIGH_ENGINE_WEIGHTED_INTEREST_RATE.required))

@publish(data.HIGH_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.schema, cells=data.HIGH_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.cells)
def high_engine_interest_expenditure_pct_revenue(*, high_engine_revenue_lcu: data.Series[float | str | None], high_engine_interest_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute interest expenditure as a percentage of revenue under the high climate scenario.

    Express the high-scenario interest burden relative to the government revenue base in percent.

    Args:
        high_engine_revenue_lcu: Government revenue under the high climate scenario, in billions of local currency units, serving as the denominator.
        high_engine_interest_expenditure_lcu: Interest expenditure under the high climate scenario, in billions of local currency units, serving as the numerator.

    Returns:
        Interest expenditure as a percentage of revenue under the high climate scenario, in percent, by time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(high_engine_interest_expenditure_lcu[time_period], high_engine_revenue_lcu[time_period]), 100))

    return data.HIGH_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.collect(evaluate(formula, data.HIGH_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.required))

@publish(data.HIGH_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.schema, cells=data.HIGH_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.cells)
def high_engine_discrete_risk_revenue_shock(*, discrete_revenue_shocks: data.DiscreteRevenueShocks) -> data.Series[float | str | None]:
    """Return the High climate scenario's discrete revenue-shock series.

    Provide the fiscal impact of registered discrete revenue risks under the High (SSP3-7.0) climate scenario as a percentage of GDP.

    Args:
        discrete_revenue_shocks: Registered discrete revenue shocks keyed by climate scenario and time period, holding the percentage-of-GDP revenue losses from materialized discrete fiscal risks; the High scenario entry is selected.

    Returns:
        A series indexed by time period holding the High scenario discrete revenue shock as a percentage of GDP, or None where no shock is registered.
    """
    data.DISCRETE_REVENUE_SHOCKS.schema.validate(discrete_revenue_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_revenue_shocks['High', time_period])

    return data.HIGH_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.collect(evaluate(formula, data.HIGH_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.required))

@publish(data.HIGH_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.schema, cells=data.HIGH_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.cells)
def high_engine_discrete_risk_expenditure_shock(*, discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks) -> data.Series[float | str | None]:
    """Retrieve the discrete risk expenditure shock series for the "High" climate change scenario.

    Provides the primary expenditure shock, in percent of GDP, from the discrete risks profile registered for the high-emissions SSP3-7.0 climate change scenario.

    Args:
        discrete_primary_expenditure_shocks: Discrete primary expenditure shocks, expressed as a percentage of GDP, registered for each climate change scenario; the "High" scenario coordinate is selected.

    Returns:
        A series of the primary expenditure shock values for the "High" climate change scenario along the projection horizon.
    """
    data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.schema.validate(discrete_primary_expenditure_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_primary_expenditure_shocks['High', time_period])

    return data.HIGH_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.collect(evaluate(formula, data.HIGH_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.required))

@publish(data.HIGH_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.schema, cells=data.HIGH_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.cells)
def high_engine_memo_interest_expenditure_pct_gdp(*, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp) -> data.Series[float | str | None]:
    """Return the high-scenario memo series of interest expenditure expressed as a percent of GDP.

    Exposes the baseline interest expenditure-to-GDP path as a memo item for the high climate scenario, so interest costs can be compared across scenarios without recomputation.

    Args:
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure as a percent of nominal GDP, indexed by projection year; values are carried over unchanged as the memo item.

    Returns:
        A series of interest expenditure as a percent of GDP by year for the high engine memo, matching the baseline input values.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_expenditure_pct_gdp[time_period])

    return data.HIGH_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.HIGH_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.required))

@publish(data.HIGH_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.schema, cells=data.HIGH_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.cells)
def high_engine_memo_primary_expenditure_pct_gdp(*, baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp) -> data.Series[float | str | None]:
    """Build the High scenario memo series for primary expenditure as a share of GDP.

    Provides the High scenario memo primary expenditure ratio by carrying over the baseline ratio, since primary expenditure is assumed rigid and the ratio rises as nominal GDP declines under climate change.

    Args:
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure as a percentage of nominal GDP, before the climate change impact on GDP.

    Returns:
        A series of primary expenditure-to-GDP ratios under the High scenario, indexed by projection year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_expenditure_pct_gdp[time_period])

    return data.HIGH_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.HIGH_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.required))

@publish(data.HIGH_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.schema, cells=data.HIGH_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.cells)
def high_engine_memo_primary_balance_pct_gdp(*, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Return the high-emissions-scenario memo series of the primary balance as a share of GDP.

    Provide the baseline primary balance ratio that underlies the primary balance memo series for the high climate change scenario.

    Args:
        baseline_primary_balance_pct_gdp: Baseline primary balance expressed as a percentage of nominal GDP, indexed by time period and aligned with the baseline scenario assumptions used throughout Q-CRAFT.

    Returns:
        A series of primary balance values as a percentage of nominal GDP, one value per time period, propagated from the baseline primary balance series.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_balance_pct_gdp[time_period])

    return data.HIGH_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.collect(evaluate(formula, data.HIGH_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.required))

@publish(data.HIGH_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.schema, cells=data.HIGH_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.cells)
def high_engine_memo_overall_balance_pct_gdp(*, baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Compute the high-scenario engine memo of the overall balance as a percent of GDP.

    Produces the engine memo series of the overall balance-to-GDP ratio used in the high climate change scenario for the fiscal projections.

    Args:
        baseline_overall_balance_pct_gdp: Baseline overall balance expressed as a percent of nominal GDP, projected over the horizon and used as the basis for the high-scenario engine memo series.

    Returns:
        A series of the overall balance as a percent of GDP by time period for the high-scenario engine memo.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_overall_balance_pct_gdp[time_period])

    return data.HIGH_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.HIGH_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.HIGH_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.schema, cells=data.HIGH_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.cells)
def high_engine_memo_gross_debt_pct_gdp(*, baseline_debt_to_gdp: data.BaselineDebtToGdp) -> data.Series[float | str | None]:
    """Compute the high-scenario memo series for the gross debt-to-GDP ratio.

    Provide the gross debt-to-GDP ratio over the projection horizon as computed under the high climate change scenario, for use as a memo item.

    Args:
        baseline_debt_to_gdp: Baseline gross debt-to-GDP ratio by projection year, used as the underlying debt level from which the high-scenario memo values are measured.

    Returns:
        A series of the gross debt-to-GDP ratio (as a percentage of nominal GDP) across the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_to_gdp[time_period])

    return data.HIGH_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.collect(evaluate(formula, data.HIGH_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.required))

@publish(data.HIGH_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.HIGH_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.cells)
def high_engine_baseline_primary_expenditure_lcu(*, baseline_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project baseline primary expenditure in local currency units under the 'high' climate scenario.

    Provides the 'high' climate scenario counterpart to the baseline primary expenditure series, expressed in local currency units, so that later fiscal steps can compute primary balance, deficits, and debt dynamics under the high-emissions SSP3-7.0 climate scenario.

    Args:
        baseline_engine_primary_expenditure_lcu: Baseline primary expenditure, in local currency units, excluding government interest payments, as projected under the baseline scenario; used as the level from which primary expenditure is held rigid under the high climate scenario.

    Returns:
        A series of baseline primary expenditure values in local currency units under the high climate scenario, aligned to the projection time periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_engine_primary_expenditure_lcu[time_period])

    return data.HIGH_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.HIGH_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.HIGH_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.schema, cells=data.HIGH_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.cells)
def high_engine_primary_expenditure_baseline_share_lcu(*, high_engine_nominal_gdp_lcu: data.Series[float | str | None], high_engine_memo_primary_expenditure_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the baseline primary expenditure level in local currency units.

    Derive the baseline primary expenditure series in local currency terms from a primary expenditure-to-GDP ratio and nominal GDP, supporting the fiscal projections used to assess long-term debt dynamics.

    Args:
        high_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units, the broadest measure of the tax base and the scale against which fiscal aggregates are expressed.
        high_engine_memo_primary_expenditure_pct_gdp: Primary expenditure expressed as a percent of nominal GDP, used to scale the expenditure level into local currency units.

    Returns:
        Primary expenditure in local currency units for each projected year, consistent with the baseline no-policy-change assumptions.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(high_engine_memo_primary_expenditure_pct_gdp[time_period], 100), high_engine_nominal_gdp_lcu[time_period]))

    return data.HIGH_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.collect(evaluate(formula, data.HIGH_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.required))

@publish(data.HIGH_ENGINE_RECALIBRATION_LCU.schema, cells=data.HIGH_ENGINE_RECALIBRATION_LCU.cells)
def high_engine_recalibration_lcu(*, high_engine_baseline_primary_expenditure_lcu: data.Series[float | str | None], high_engine_primary_expenditure_baseline_share_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Recalibrate baseline primary expenditure in local currency units for the high climate scenario.

    Derives the high-engine primary expenditure level in local currency terms by removing the baseline primary expenditure share, yielding an updated baseline against which expenditure rigidity is applied.

    Args:
        high_engine_baseline_primary_expenditure_lcu: Baseline primary expenditure in local currency units under the high climate scenario, before any expenditure flexibility adjustment.
        high_engine_primary_expenditure_baseline_share_lcu: Local currency component of baseline primary expenditure to be netted out against the high-scenario baseline primary expenditure, expressed in the same local currency units.

    Returns:
        Recalibrated high-scenario baseline primary expenditure in local currency units, calculated as the baseline primary expenditure less the baseline expenditure share for each projection year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(high_engine_baseline_primary_expenditure_lcu[time_period], high_engine_primary_expenditure_baseline_share_lcu[time_period]))

    return data.HIGH_ENGINE_RECALIBRATION_LCU.collect(evaluate(formula, data.HIGH_ENGINE_RECALIBRATION_LCU.required))

@dataclass(frozen=True, slots=True)
class ScanHighEngineTotalExpenditurePctGdpResult:
    """Complete named results of one recurrence group evaluation."""
    high_engine_total_expenditure_pct_gdp: data.Series[float | str | None]
    high_engine_primary_balance_pct_gdp: data.Series[float | str | None]
    high_engine_total_expenditure_lcu: data.Series[float | str | None]
    high_engine_interest_expenditure_lcu: data.Series[float | str | None]
    high_engine_gross_debt_lcu: data.Series[float | str | None]
    high_engine_gross_debt_pct_gdp: data.Series[float | str | None]
    scenario_primary_expenditure_pct_gdp_high: data.ScenarioPrimaryExpenditurePctGdpHigh
    scenario_interest_expenditure_pct_gdp_high: data.ScenarioInterestExpenditurePctGdpHigh

def scan_high_engine_total_expenditure_pct_gdp(*, baseline_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_engine_total_expenditure_lcu: data.Series[float | str | None], baseline_engine_interest_expenditure_lcu: data.Series[float | str | None], baseline_engine_gross_debt_lcu: data.Series[float | str | None], high_engine_nominal_gdp_lcu: data.Series[float | str | None], high_engine_revenue_pct_gdp: data.Series[float | str | None], high_engine_primary_expenditure_lcu: data.Series[float | str | None], high_engine_weighted_interest_rate: data.Series[float | str | None], baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp, baseline_debt_to_gdp: data.BaselineDebtToGdp, scenario_nominal_gdp_growth_high: data.ScenarioNominalGdpGrowthHigh) -> ScanHighEngineTotalExpenditurePctGdpResult:
    """Project total government expenditure under the high climate scenario.

    Project the high climate change scenario's total expenditure, primary balance, interest expenditure, and gross debt series to 2099, holding policy settings passive so that climate-driven GDP losses feed mechanically into the fiscal accounts.

    Args:
        baseline_engine_total_expenditure_pct_gdp: Baseline total government expenditure, in percent of nominal GDP, used through 2029 before scenario-specific values take over.
        baseline_engine_total_expenditure_lcu: Baseline total government expenditure in billions of local currency units, used through 2029.
        baseline_engine_interest_expenditure_lcu: Baseline government interest expenditure in billions of local currency units, used through 2029.
        baseline_engine_gross_debt_lcu: Baseline gross government debt in billions of local currency units, used through 2029.
        high_engine_nominal_gdp_lcu: Scenario nominal GDP in billions of local currency units, which declines relative to the baseline because climate change slows labor productivity growth starting in 2030.
        high_engine_revenue_pct_gdp: Scenario government revenue in percent of nominal GDP, held at the baseline ratio so that revenue falls in local currency terms as GDP declines.
        high_engine_primary_expenditure_lcu: Scenario primary (non-interest) government expenditure in billions of local currency units, reflecting the assumed degree of expenditure rigidity.
        high_engine_weighted_interest_rate: Scenario weighted average nominal interest rate on government debt, in percent, used to derive interest expenditure and the automatic debt dynamics.
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure in percent of nominal GDP, used to anchor the scenario primary expenditure ratio through 2029.
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure in percent of nominal GDP, used to anchor the scenario interest expenditure ratio through 2029.
        baseline_primary_balance_pct_gdp: Baseline primary balance in percent of nominal GDP, used to anchor the scenario primary balance through 2029.
        baseline_debt_to_gdp: Baseline gross debt-to-GDP ratio, used to anchor the scenario debt ratio through 2029.
        scenario_nominal_gdp_growth_high: Scenario nominal GDP growth rate, in percent, used in the debt dynamics equation to evolve the debt-to-GDP ratio.

    Returns:
        A ScanHighEngineTotalExpenditurePctGdpResult holding full tensors of the scenario total expenditure, primary balance, total expenditure in local currency units, interest expenditure, gross debt in local currency units, gross debt-to-GDP ratio, primary expenditure, and interest expenditure as percent of GDP.
    """
    def high_engine_total_expenditure_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(high_engine_total_expenditure_lcu[time_period], high_engine_nominal_gdp_lcu[time_period]), 100))

    high_engine_total_expenditure_pct_gdp = CoordinateReader('high_engine_total_expenditure_pct_gdp', data.HIGH_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required, high_engine_total_expenditure_pct_gdp_formula)
    def high_engine_primary_balance_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_balance_pct_gdp[time_period])
        return as_measure(xl_sub(high_engine_revenue_pct_gdp[time_period], scenario_primary_expenditure_pct_gdp_high[time_period]))

    high_engine_primary_balance_pct_gdp = CoordinateReader('high_engine_primary_balance_pct_gdp', data.HIGH_ENGINE_PRIMARY_BALANCE_PCT_GDP.required, high_engine_primary_balance_pct_gdp_formula)
    def high_engine_total_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_lcu[time_period])
        return as_measure(xl_add(high_engine_interest_expenditure_lcu[time_period], high_engine_primary_expenditure_lcu[time_period]))

    high_engine_total_expenditure_lcu = CoordinateReader('high_engine_total_expenditure_lcu', data.HIGH_ENGINE_TOTAL_EXPENDITURE_LCU.required, high_engine_total_expenditure_lcu_formula)
    def high_engine_interest_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_interest_expenditure_lcu[time_period])
        return as_measure(xl_mul(xl_div(high_engine_weighted_interest_rate[time_period], 100), high_engine_gross_debt_lcu[time_period - 1]))

    high_engine_interest_expenditure_lcu = CoordinateReader('high_engine_interest_expenditure_lcu', data.HIGH_ENGINE_INTEREST_EXPENDITURE_LCU.required, high_engine_interest_expenditure_lcu_formula)
    def high_engine_gross_debt_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_gross_debt_lcu[time_period])
        return as_measure(xl_mul(xl_div(high_engine_gross_debt_pct_gdp[time_period], 100), high_engine_nominal_gdp_lcu[time_period]))

    high_engine_gross_debt_lcu = CoordinateReader('high_engine_gross_debt_lcu', data.HIGH_ENGINE_GROSS_DEBT_LCU.required, high_engine_gross_debt_lcu_formula)
    def high_engine_gross_debt_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_debt_to_gdp[time_period])
        return as_measure(xl_sub(xl_div(xl_mul(high_engine_gross_debt_pct_gdp[time_period - 1], xl_add(1, xl_div(high_engine_weighted_interest_rate[time_period], 100))), xl_add(1, xl_div(scenario_nominal_gdp_growth_high[time_period], 100))), high_engine_primary_balance_pct_gdp[time_period]))

    high_engine_gross_debt_pct_gdp = CoordinateReader('high_engine_gross_debt_pct_gdp', data.HIGH_ENGINE_GROSS_DEBT_PCT_GDP.required, high_engine_gross_debt_pct_gdp_formula)
    def scenario_primary_expenditure_pct_gdp_high_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_expenditure_pct_gdp[time_period])
        return as_measure(xl_sub(high_engine_total_expenditure_pct_gdp[time_period], scenario_interest_expenditure_pct_gdp_high[time_period]))

    scenario_primary_expenditure_pct_gdp_high = CoordinateReader('scenario_primary_expenditure_pct_gdp_high', data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HIGH.required, scenario_primary_expenditure_pct_gdp_high_formula)
    def scenario_interest_expenditure_pct_gdp_high_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_interest_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(high_engine_interest_expenditure_lcu[time_period], high_engine_nominal_gdp_lcu[time_period]), 100))

    scenario_interest_expenditure_pct_gdp_high = CoordinateReader('scenario_interest_expenditure_pct_gdp_high', data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HIGH.required, scenario_interest_expenditure_pct_gdp_high_formula)
    return ScanHighEngineTotalExpenditurePctGdpResult(
        high_engine_total_expenditure_pct_gdp=data.HIGH_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.collect((coord, high_engine_total_expenditure_pct_gdp[coord]) for coord in data.HIGH_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required),
        high_engine_primary_balance_pct_gdp=data.HIGH_ENGINE_PRIMARY_BALANCE_PCT_GDP.collect((coord, high_engine_primary_balance_pct_gdp[coord]) for coord in data.HIGH_ENGINE_PRIMARY_BALANCE_PCT_GDP.required),
        high_engine_total_expenditure_lcu=data.HIGH_ENGINE_TOTAL_EXPENDITURE_LCU.collect((coord, high_engine_total_expenditure_lcu[coord]) for coord in data.HIGH_ENGINE_TOTAL_EXPENDITURE_LCU.required),
        high_engine_interest_expenditure_lcu=data.HIGH_ENGINE_INTEREST_EXPENDITURE_LCU.collect((coord, high_engine_interest_expenditure_lcu[coord]) for coord in data.HIGH_ENGINE_INTEREST_EXPENDITURE_LCU.required),
        high_engine_gross_debt_lcu=data.HIGH_ENGINE_GROSS_DEBT_LCU.collect((coord, high_engine_gross_debt_lcu[coord]) for coord in data.HIGH_ENGINE_GROSS_DEBT_LCU.required),
        high_engine_gross_debt_pct_gdp=data.HIGH_ENGINE_GROSS_DEBT_PCT_GDP.collect((coord, high_engine_gross_debt_pct_gdp[coord]) for coord in data.HIGH_ENGINE_GROSS_DEBT_PCT_GDP.required),
        scenario_primary_expenditure_pct_gdp_high=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HIGH.collect((coord, scenario_primary_expenditure_pct_gdp_high[coord]) for coord in data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HIGH.required),
        scenario_interest_expenditure_pct_gdp_high=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HIGH.collect((coord, scenario_interest_expenditure_pct_gdp_high[coord]) for coord in data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HIGH.required),
    )

@publish(data.HOT_ENGINE_EMPLOYMENT_GROWTH.schema, cells=data.HOT_ENGINE_EMPLOYMENT_GROWTH.cells)
def hot_engine_employment_growth(*, baseline_employment_growth: data.BaselineEmploymentGrowth) -> data.Series[float | str | None]:
    """Derive the Hot scenario employment growth series from the baseline projection.

    Supply the employment growth path used to build the Hot climate scenario's macro-fiscal projections.

    Args:
        baseline_employment_growth: Baseline employment growth series, by projection year.

    Returns:
        Series of Hot scenario employment growth values, one per projection year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_employment_growth[time_period])

    return data.HOT_ENGINE_EMPLOYMENT_GROWTH.collect(evaluate(formula, data.HOT_ENGINE_EMPLOYMENT_GROWTH.required))

@publish(data.HOT_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.schema, cells=data.HOT_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.cells)
def hot_engine_labour_productivity_growth(*, climate_data_labour_productivity_growth_variation_hot: data.Series[float | str | None], baseline_labour_productivity_growth: data.BaselineLabourProductivityGrowth) -> data.Series[float | str | None]:
    """Project labour productivity growth under the hot climate scenario by adding the hot-scenario climate variation to the baseline growth.

    Adjust the baseline labour productivity growth trajectory for the hot climate scenario, where emissions follow the high-emissions SSP3-7.0 path and temperature increases sit at the 90th percentile of climate model projections.

    Args:
        climate_data_labour_productivity_growth_variation_hot: Year-by-year climate-driven variation in labour productivity growth under the hot scenario, as derived from empirical estimates of temperature impacts on GDP per capita growth.
        baseline_labour_productivity_growth: Baseline labour productivity growth (GDP per employed person) for the no-climate-change scenario, used as the starting point for the hot scenario.

    Returns:
        Series of labour productivity growth under the hot climate scenario, combining the baseline growth with the hot-scenario climate variation in each period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(baseline_labour_productivity_growth[time_period], climate_data_labour_productivity_growth_variation_hot[time_period]))

    return data.HOT_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.collect(evaluate(formula, data.HOT_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.required))

@publish(data.HOT_ENGINE_REAL_GDP_GROWTH.schema, cells=data.HOT_ENGINE_REAL_GDP_GROWTH.cells)
def hot_engine_real_gdp_growth(*, hot_engine_employment_growth: data.Series[float | str | None], hot_engine_labour_productivity_growth: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Derive real GDP growth under the hot climate scenario.

    Combines the hot-scenario employment and labour productivity growth assumptions into a single real GDP growth projection consistent with the decomposition of real GDP into employment and GDP per employed person.

    Args:
        hot_engine_employment_growth: Growth rate of employment, in percent, under the hot scenario; projected to follow growth in the working-age population in the long run.
        hot_engine_labour_productivity_growth: Growth rate of labour productivity (GDP per employed person), in percent, under the hot scenario; climate change is captured as a slowdown in this productivity growth.

    Returns:
        A series of real GDP growth rates, in percent, under the hot scenario, aligned with the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(hot_engine_employment_growth[time_period], 100)), xl_add(1, xl_div(hot_engine_labour_productivity_growth[time_period], 100))), 100), 100))

    return data.HOT_ENGINE_REAL_GDP_GROWTH.collect(evaluate(formula, data.HOT_ENGINE_REAL_GDP_GROWTH.required))

@publish(data.HOT_ENGINE_GDP_DEFLATOR_GROWTH.schema, cells=data.HOT_ENGINE_GDP_DEFLATOR_GROWTH.cells)
def hot_engine_gdp_deflator_growth(*, baseline_gdp_deflator_growth: data.BaselineGdpDeflatorGrowth) -> data.Series[float | str | None]:
    """Project the GDP deflator growth series under the Hot climate scenario.

    Reuse the baseline GDP deflator growth path as the Hot scenario's nominal price growth, since inflation is assumed to remain unchanged across climate scenarios.

    Args:
        baseline_gdp_deflator_growth: Baseline GDP deflator growth by projection year, providing the price growth used to convert real GDP into nominal GDP under the Hot scenario.

    Returns:
        A series of GDP deflator growth values for the Hot scenario, aligned with the baseline series across all projection periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_gdp_deflator_growth[time_period])

    return data.HOT_ENGINE_GDP_DEFLATOR_GROWTH.collect(evaluate(formula, data.HOT_ENGINE_GDP_DEFLATOR_GROWTH.required))

@publish(data.HOT_ENGINE_NOMINAL_GDP_LCU.schema, cells=data.HOT_ENGINE_NOMINAL_GDP_LCU.cells)
def hot_engine_nominal_gdp_lcu(*, baseline_engine_nominal_gdp_lcu: data.Series[float | str | None], scenario_nominal_gdp_growth_hot: data.ScenarioNominalGdpGrowthHot) -> data.Series[float | str | None]:
    """Project nominal GDP in local currency units under the Hot climate scenario.

    Extend the baseline nominal GDP level into the Hot scenario by compounding it with the scenario-specific nominal GDP growth rate from 2030 onwards.

    Args:
        baseline_engine_nominal_gdp_lcu: Baseline scenario nominal GDP in local currency units, used for all periods through 2029.
        scenario_nominal_gdp_growth_hot: Hot scenario nominal GDP growth rates, in percent, applied from 2030 onward to build the nominal GDP path.

    Returns:
        The Hot scenario nominal GDP series in local currency units, equal to the baseline level through 2029 and grown by the Hot scenario growth rates thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_nominal_gdp_lcu[time_period])
        return as_measure(xl_mul(hot_engine_nominal_gdp_lcu[time_period - 1], xl_add(1, xl_div(scenario_nominal_gdp_growth_hot[time_period], 100))))

    hot_engine_nominal_gdp_lcu = CoordinateReader('hot_engine_nominal_gdp_lcu', data.HOT_ENGINE_NOMINAL_GDP_LCU.required, formula)
    return data.HOT_ENGINE_NOMINAL_GDP_LCU.collect((coord, hot_engine_nominal_gdp_lcu[coord]) for coord in data.HOT_ENGINE_NOMINAL_GDP_LCU.required)

@publish(data.HOT_ENGINE_REVENUE_PCT_GDP.schema, cells=data.HOT_ENGINE_REVENUE_PCT_GDP.cells)
def hot_engine_revenue_pct_gdp(*, hot_engine_discrete_risk_revenue_shock: data.Series[float | str | None], baseline_revenue_pct_gdp: data.BaselineRevenuePctGdp) -> data.Series[float | str | None]:
    """Compute the Hot scenario revenue-to-GDP ratio to 2099.

    Derives the Hot climate scenario revenue path as a share of nominal GDP by combining the baseline revenue ratio with the fiscal impact of registered discrete risk revenue shocks from 2030 onward.

    Args:
        hot_engine_discrete_risk_revenue_shock: Yearly revenue shock (in percent of GDP) registered in the Discrete Risks worksheet for materialized discrete fiscal risks under the Hot climate scenario; no shock is applied through 2029.
        baseline_revenue_pct_gdp: Baseline scenario revenue-to-GDP ratio, held constant in the Hot scenario and used as the starting point for the shock adjustment from 2030 onward.

    Returns:
        Yearly Hot scenario revenue as a percent of nominal GDP, equal to the baseline revenue ratio through 2029 and to the baseline ratio plus the discrete risk revenue shock thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_revenue_pct_gdp[time_period])
        return as_measure(xl_add(baseline_revenue_pct_gdp[time_period], hot_engine_discrete_risk_revenue_shock[time_period]))

    return data.HOT_ENGINE_REVENUE_PCT_GDP.collect(evaluate(formula, data.HOT_ENGINE_REVENUE_PCT_GDP.required))

@publish(data.HOT_ENGINE_OVERALL_BALANCE_PCT_GDP.schema, cells=data.HOT_ENGINE_OVERALL_BALANCE_PCT_GDP.cells)
def hot_engine_overall_balance_pct_gdp(*, hot_engine_revenue_pct_gdp: data.Series[float | str | None], hot_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Compute the overall balance as a share of GDP under the Hot climate scenario.

    Derive the Hot scenario overall balance from scenario revenue and total expenditure, defaulting to the baseline overall balance through the end of the IMF WEO horizon.

    Args:
        hot_engine_revenue_pct_gdp: Hot climate scenario government revenue as a share of nominal GDP.
        hot_engine_total_expenditure_pct_gdp: Hot climate scenario total government expenditure (including interest payments) as a share of nominal GDP.
        baseline_overall_balance_pct_gdp: Baseline overall balance as a share of nominal GDP, used through the medium-term horizon covered by the IMF WEO.

    Returns:
        Overall balance as a share of nominal GDP under the Hot climate scenario, in percent.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_overall_balance_pct_gdp[time_period])
        return as_measure(xl_sub(hot_engine_revenue_pct_gdp[time_period], hot_engine_total_expenditure_pct_gdp[time_period]))

    return data.HOT_ENGINE_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.HOT_ENGINE_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.HOT_ENGINE_REVENUE_LCU.schema, cells=data.HOT_ENGINE_REVENUE_LCU.cells)
def hot_engine_revenue_lcu(*, baseline_engine_revenue_lcu: data.Series[float | str | None], hot_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_engine_revenue_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project government revenue in local currency units under the hot climate scenario.

    Derive hot-scenario revenue from baseline revenue through 2029 and, thereafter, from the hot-scenario nominal GDP and revenue-to-GDP ratio.

    Args:
        baseline_engine_revenue_lcu: Government revenue in local currency units under the baseline scenario, used for projection years up to and including 2029.
        hot_engine_nominal_gdp_lcu: Nominal GDP in local currency units under the hot climate scenario, reflecting the climate-driven slowdown in productivity growth.
        hot_engine_revenue_pct_gdp: Government revenue as a percent of nominal GDP under the hot climate scenario, held unchanged from the baseline revenue-to-GDP ratio.

    Returns:
        Government revenue in local currency units under the hot climate scenario, equal to the baseline level through 2029 and thereafter to the hot-scenario revenue-to-GDP ratio applied to hot-scenario nominal GDP.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_revenue_lcu[time_period])
        return as_measure(xl_mul(xl_div(hot_engine_revenue_pct_gdp[time_period], 100), hot_engine_nominal_gdp_lcu[time_period]))

    return data.HOT_ENGINE_REVENUE_LCU.collect(evaluate(formula, data.HOT_ENGINE_REVENUE_LCU.required))

@publish(data.HOT_ENGINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.HOT_ENGINE_PRIMARY_EXPENDITURE_LCU.cells)
def hot_engine_primary_expenditure_lcu(*, expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)], baseline_engine_primary_expenditure_lcu: data.Series[float | str | None], hot_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_engine_discrete_risk_expenditure_shock: data.Series[float | str | None], hot_engine_recalibration_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project primary expenditure in local currency units under the "hot" climate scenario.

    Computes the climate-scenario path of primary expenditure, relaxing baseline expenditure rigidity and adding discrete-risk spending, for use in the fiscal projections.

    Args:
        expenditure_rigidity: Degree to which primary expenditure is held rigid in the face of declining GDP, ranging from 0 (fully flexible) to 1 (completely rigid).
        baseline_engine_primary_expenditure_lcu: Baseline primary expenditure in local currency units, excluding government interest payments.
        hot_engine_nominal_gdp_lcu: Nominal GDP in local currency units under the hot climate scenario, used to scale the discrete-risk expenditure shock.
        hot_engine_discrete_risk_expenditure_shock: Discrete-risk expenditure shock under the hot climate scenario, expressed as a percentage of nominal GDP.
        hot_engine_recalibration_lcu: Amount, in local currency units, by which primary expenditure may be recalibrated under the hot climate scenario when rigidity is relaxed.

    Returns:
        Primary expenditure in local currency units for each period under the hot climate scenario, equal to the baseline through 2029 and thereafter adjusted for expenditure recalibration and discrete-risk spending.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_expenditure_lcu[time_period])
        return as_measure(xl_add(xl_sub(baseline_engine_primary_expenditure_lcu[time_period], xl_mul(xl_sub(1, expenditure_rigidity), hot_engine_recalibration_lcu[time_period])), xl_mul(xl_div(hot_engine_discrete_risk_expenditure_shock[time_period], 100), hot_engine_nominal_gdp_lcu[time_period])))

    return data.HOT_ENGINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.HOT_ENGINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.HOT_ENGINE_PRIMARY_BALANCE_LCU.schema, cells=data.HOT_ENGINE_PRIMARY_BALANCE_LCU.cells)
def hot_engine_primary_balance_lcu(*, baseline_engine_primary_balance_lcu: data.Series[float | str | None], hot_engine_revenue_lcu: data.Series[float | str | None], hot_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the primary balance in local currency units under the hot climate scenario.

    Provide the hot scenario's primary balance, carried over from the baseline before 2030 and thereafter derived from climate-adjusted revenue and rigid primary expenditure.

    Args:
        baseline_engine_primary_balance_lcu: Baseline (no climate change) primary balance in local currency units, used for periods through 2029 because climate change effects are assumed to begin in 2030.
        hot_engine_revenue_lcu: Government revenue in local currency units under the hot climate scenario, which declines with nominal GDP while remaining constant as a share of GDP.
        hot_engine_primary_expenditure_lcu: Primary expenditure in local currency units under the hot climate scenario, assumed rigid and held at the baseline level so that its GDP ratio rises as nominal GDP declines.

    Returns:
        The hot climate scenario primary balance in local currency units for each period, equal to the baseline primary balance up to 2029 and to revenue less primary expenditure thereafter; the difference is revenue minus primary expenditure.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_balance_lcu[time_period])
        return as_measure(xl_sub(hot_engine_revenue_lcu[time_period], hot_engine_primary_expenditure_lcu[time_period]))

    return data.HOT_ENGINE_PRIMARY_BALANCE_LCU.collect(evaluate(formula, data.HOT_ENGINE_PRIMARY_BALANCE_LCU.required))

@publish(data.HOT_ENGINE_OVERALL_BALANCE_LCU.schema, cells=data.HOT_ENGINE_OVERALL_BALANCE_LCU.cells)
def hot_engine_overall_balance_lcu(*, baseline_engine_overall_balance_lcu: data.Series[float | str | None], hot_engine_revenue_lcu: data.Series[float | str | None], hot_engine_total_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the overall balance in local currency units under the hot climate scenario.

    Derive the hot-scenario overall balance for each year, carrying the baseline overall balance through 2029 and thereafter computing revenue less total expenditure in local currency units.

    Args:
        baseline_engine_overall_balance_lcu: Baseline scenario overall balance in billions of local currency units, carried through the last year of the IMF WEO horizon (2029) before the hot-scenario calculation takes over.
        hot_engine_revenue_lcu: Government revenue in billions of local currency units under the hot climate scenario, assumed to decline in line with nominal GDP so that the revenue-to-GDP ratio remains unchanged from the baseline.
        hot_engine_total_expenditure_lcu: Total government expenditure in billions of local currency units under the hot climate scenario, including interest payments on debt in addition to primary expenditure.

    Returns:
        A series of the overall balance in local currency units under the hot climate scenario, with values through 2029 taken from the baseline overall balance and later values equal to hot-scenario revenue minus hot-scenario total expenditure.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_overall_balance_lcu[time_period])
        return as_measure(xl_sub(hot_engine_revenue_lcu[time_period], hot_engine_total_expenditure_lcu[time_period]))

    return data.HOT_ENGINE_OVERALL_BALANCE_LCU.collect(evaluate(formula, data.HOT_ENGINE_OVERALL_BALANCE_LCU.required))

@publish(data.HOT_ENGINE_WEIGHTED_INTEREST_RATE.schema, cells=data.HOT_ENGINE_WEIGHTED_INTEREST_RATE.cells)
def hot_engine_weighted_interest_rate(*, baseline_interest_rate: data.BaselineInterestRate) -> data.Series[float | str | None]:
    """Return the weighted average nominal interest rate profile used by the hot climate engine.

    Aligns the interest rate path in the hot climate scenarios with the baseline interest assumptions so debt dynamics remain consistent with the baseline.

    Args:
        baseline_interest_rate: Series mapping each projection year to the baseline weighted average nominal interest rate assumption, adopted here for the hot climate scenario.

    Returns:
        Series indexed by projection year whose value in each year is the weighted average nominal interest rate assumption carried over from the baseline.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_rate[time_period])

    return data.HOT_ENGINE_WEIGHTED_INTEREST_RATE.collect(evaluate(formula, data.HOT_ENGINE_WEIGHTED_INTEREST_RATE.required))

@publish(data.HOT_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.schema, cells=data.HOT_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.cells)
def hot_engine_interest_expenditure_pct_revenue(*, hot_engine_revenue_lcu: data.Series[float | str | None], hot_engine_interest_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute interest expenditure as a percentage of revenue under the hot climate scenario.

    Express hot-scenario interest expenditure relative to government revenue, which remains constant as a share of nominal GDP, to gauge debt-service pressure when climate change lowers GDP.

    Args:
        hot_engine_revenue_lcu: Government revenue in billions of local currency units under the hot scenario, assumed to decline in line with nominal GDP so the revenue-to-GDP ratio is unchanged from the baseline.
        hot_engine_interest_expenditure_lcu: Interest expenditure in billions of local currency units under the hot scenario, rising as a worsening primary balance and higher debt raise the cost of servicing debt.

    Returns:
        Interest expenditure as a percentage of revenue under the hot scenario, by projection year to 2099.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(hot_engine_interest_expenditure_lcu[time_period], hot_engine_revenue_lcu[time_period]), 100))

    return data.HOT_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.collect(evaluate(formula, data.HOT_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.required))

@publish(data.HOT_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.schema, cells=data.HOT_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.cells)
def hot_engine_discrete_risk_revenue_shock(*, discrete_revenue_shocks: data.DiscreteRevenueShocks) -> data.Series[float | str | None]:
    """Project the Hot-scenario discrete revenue shock onto the output horizon.

    Align the registered Hot-scenario revenue-loss impacts to the discrete-risk output time index so they can be applied as a share of GDP.

    Args:
        discrete_revenue_shocks: Registered discrete fiscal risk impacts on revenue, expressed as a percent of GDP per scenario and time period; the Hot climate change scenario series supplies the values used here.

    Returns:
        A series of Hot-scenario discrete revenue shock values, as a percent of GDP, indexed by the output time periods.
    """
    data.DISCRETE_REVENUE_SHOCKS.schema.validate(discrete_revenue_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_revenue_shocks['Hot', time_period])

    return data.HOT_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.collect(evaluate(formula, data.HOT_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.required))

@publish(data.HOT_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.schema, cells=data.HOT_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.cells)
def hot_engine_discrete_risk_expenditure_shock(*, discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks) -> data.Series[float | str | None]:
    """Return the hot-scenario discrete risk primary expenditure shock series.

    Project the user-registered discrete risk impacts on primary expenditure as a share of GDP under the hot climate scenario, reflecting the assumption that fiscal shocks materialize more frequently and with greater magnitude as climate change intensifies.

    Args:
        discrete_primary_expenditure_shocks: Manually registered fiscal impacts of discrete risk materialization, expressed as a share of GDP, for the Hot climate change scenario.

    Returns:
        A time-indexed series of discrete risk primary expenditure shocks, as a share of GDP, for the Hot climate scenario.
    """
    data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.schema.validate(discrete_primary_expenditure_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_primary_expenditure_shocks['Hot', time_period])

    return data.HOT_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.collect(evaluate(formula, data.HOT_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.required))

@publish(data.HOT_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.schema, cells=data.HOT_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.cells)
def hot_engine_memo_interest_expenditure_pct_gdp(*, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp) -> data.Series[float | str | None]:
    """Materialize the interest expenditure-to-GDP series under the hot scenario.

    Provide a memo series for interest expenditure as a share of nominal GDP under the hot climate scenario, expressed as a coordinate transformation of the baseline interest expenditure ratio.

    Args:
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure as a share of nominal GDP, indexed by projection year; provides the interest expenditure-to-GDP ratio from which the hot scenario memo series is derived.

    Returns:
        A series of interest expenditure-to-GDP ratios under the hot scenario, indexed by projection year, with values mapped from the baseline interest expenditure series.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_expenditure_pct_gdp[time_period])

    return data.HOT_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.HOT_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.required))

@publish(data.HOT_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.schema, cells=data.HOT_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.cells)
def hot_engine_memo_primary_expenditure_pct_gdp(*, baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp) -> data.Series[float | str | None]:
    """Project baseline primary expenditure as a share of GDP into the hot climate scenario.

    Provides the memo series used to apply the expenditure rigidity assumption in climate scenarios, where primary expenditure is held unchanged from the baseline in local currency terms while nominal GDP declines.

    Args:
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure, excluding government interest payments, expressed as a share of nominal GDP for each year through the projection horizon.

    Returns:
        A series of baseline primary expenditure-to-GDP ratios indexed by projection year, with values as either floats or missing markers.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_expenditure_pct_gdp[time_period])

    return data.HOT_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.HOT_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.required))

@publish(data.HOT_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.schema, cells=data.HOT_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.cells)
def hot_engine_memo_primary_balance_pct_gdp(*, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Build the memo series for the primary balance-to-GDP ratio under the hot climate scenario.

    Exposes the primary balance (revenue less primary expenditure, in percent of GDP) used by the hot scenario as a memo series for the full projection horizon.

    Args:
        baseline_primary_balance_pct_gdp: Baseline primary balance expressed as a percentage of nominal GDP, indexed by projection year.

    Returns:
        Series of primary balance-to-GDP values (in percent) aligned to the projection horizon, carrying the baseline values forward under the hot climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_balance_pct_gdp[time_period])

    return data.HOT_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.collect(evaluate(formula, data.HOT_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.required))

@publish(data.HOT_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.schema, cells=data.HOT_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.cells)
def hot_engine_memo_overall_balance_pct_gdp(*, baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Project the overall balance (percent of GDP) for the Hot climate scenario using baseline identities.

    Supplies the overall balance series for the Hot scenario by reusing the baseline overall balance values rather than applying climate-specific adjustments.

    Args:
        baseline_overall_balance_pct_gdp: Baseline overall balance expressed as a share of nominal GDP, passing through unchanged because the Hot scenario memo does not adjust the overall balance.

    Returns:
        Series of overall balance as a percent of GDP for the Hot climate scenario at each projected time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_overall_balance_pct_gdp[time_period])

    return data.HOT_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.HOT_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.HOT_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.schema, cells=data.HOT_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.cells)
def hot_engine_memo_gross_debt_pct_gdp(*, baseline_debt_to_gdp: data.BaselineDebtToGdp) -> data.Series[float | str | None]:
    """Return the gross debt-to-GDP ratio memo series for the hot climate scenario.

    Expose the baseline debt-to-GDP ratio as a hot-engine memo series of gross government debt relative to nominal GDP.

    Args:
        baseline_debt_to_gdp: Baseline debt-to-GDP projection, expressed as gross government debt relative to nominal GDP, used as the unchanged baseline trajectory when memoizing the debt-to-GDP ratio.

    Returns:
        A series of gross debt-to-GDP ratios by projection year, spanning the hot-engine memo's required periods, where each value is the baseline debt-to-GDP ratio mapped onto that period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_to_gdp[time_period])

    return data.HOT_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.collect(evaluate(formula, data.HOT_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.required))

@publish(data.HOT_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.HOT_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.cells)
def hot_engine_baseline_primary_expenditure_lcu(*, baseline_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Returns the baseline primary expenditure series in local currency units under the Hot scenario.

    Provides the baseline profile of primary expenditure in local currency terms that the Hot climate scenario is anchored to.

    Args:
        baseline_engine_primary_expenditure_lcu: Baseline primary expenditure, excluding government interest payments, expressed in billions of local currency units for the general government sector.

    Returns:
        Baseline primary expenditure in local currency units, indexed by projection time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_engine_primary_expenditure_lcu[time_period])

    return data.HOT_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.HOT_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.HOT_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.schema, cells=data.HOT_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.cells)
def hot_engine_primary_expenditure_baseline_share_lcu(*, hot_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_engine_memo_primary_expenditure_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Derive the baseline primary expenditure level in local currency units from the memoized primary expenditure-to-GDP ratio and nominal GDP.

    Provides the baseline primary expenditure path (excluding interest payments) in local currency units, the benchmark against which climate-scenario expenditure rigidity and adjustments are assessed.

    Args:
        hot_engine_nominal_gdp_lcu: Baseline nominal GDP in billions of local currency units, the broadest measure of the economy's tax base and capacity to carry debt.
        hot_engine_memo_primary_expenditure_pct_gdp: Baseline primary expenditure expressed as a percent of nominal GDP, reflecting the passive 'no policy change' fiscal setting.

    Returns:
        Baseline primary expenditure in local currency units for each projected year, obtained as the primary expenditure-to-GDP ratio (divided by 100) multiplied by nominal GDP.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(hot_engine_memo_primary_expenditure_pct_gdp[time_period], 100), hot_engine_nominal_gdp_lcu[time_period]))

    return data.HOT_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.collect(evaluate(formula, data.HOT_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.required))

@publish(data.HOT_ENGINE_RECALIBRATION_LCU.schema, cells=data.HOT_ENGINE_RECALIBRATION_LCU.cells)
def hot_engine_recalibration_lcu(*, hot_engine_baseline_primary_expenditure_lcu: data.Series[float | str | None], hot_engine_primary_expenditure_baseline_share_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Recalibrate Hot scenario primary expenditure in local currency units.

    Derive the recalibrated Hot scenario primary expenditure path in local currency units by adjusting the baseline primary expenditure for the amount removed by the baseline share, so that the resulting level reflects the expenditure rigidity assumption applied under the Hot climate scenario.

    Args:
        hot_engine_baseline_primary_expenditure_lcu: Baseline primary expenditure in local currency units, i.e. primary expenditure excluding government interest payments before any climate-related recalibration, used as the starting level for the Hot scenario.
        hot_engine_primary_expenditure_baseline_share_lcu: Share of baseline primary expenditure in local currency units that is removed when recalibrating the Hot scenario, expressed as an amount in local currency units.

    Returns:
        A series of recalibrated Hot scenario primary expenditure levels in local currency units for each projected period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(hot_engine_baseline_primary_expenditure_lcu[time_period], hot_engine_primary_expenditure_baseline_share_lcu[time_period]))

    return data.HOT_ENGINE_RECALIBRATION_LCU.collect(evaluate(formula, data.HOT_ENGINE_RECALIBRATION_LCU.required))

@dataclass(frozen=True, slots=True)
class ScanHotEngineTotalExpenditurePctGdpResult:
    """Complete named results of one recurrence group evaluation."""
    hot_engine_total_expenditure_pct_gdp: data.Series[float | str | None]
    hot_engine_primary_balance_pct_gdp: data.Series[float | str | None]
    hot_engine_total_expenditure_lcu: data.Series[float | str | None]
    hot_engine_interest_expenditure_lcu: data.Series[float | str | None]
    hot_engine_gross_debt_lcu: data.Series[float | str | None]
    hot_engine_gross_debt_pct_gdp: data.Series[float | str | None]
    scenario_primary_expenditure_pct_gdp_hot: data.ScenarioPrimaryExpenditurePctGdpHot
    scenario_interest_expenditure_pct_gdp_hot: data.ScenarioInterestExpenditurePctGdpHot

def scan_hot_engine_total_expenditure_pct_gdp(*, baseline_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_engine_total_expenditure_lcu: data.Series[float | str | None], baseline_engine_interest_expenditure_lcu: data.Series[float | str | None], baseline_engine_gross_debt_lcu: data.Series[float | str | None], hot_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_engine_revenue_pct_gdp: data.Series[float | str | None], hot_engine_primary_expenditure_lcu: data.Series[float | str | None], hot_engine_weighted_interest_rate: data.Series[float | str | None], baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp, baseline_debt_to_gdp: data.BaselineDebtToGdp, scenario_nominal_gdp_growth_hot: data.ScenarioNominalGdpGrowthHot) -> ScanHotEngineTotalExpenditurePctGdpResult:
    """Project total expenditure and related fiscal aggregates under the hot climate scenario.

    Derive the hot-scenario total expenditure-to-GDP ratio and the accompanying recurrence group of fiscal indicators, holding policy settings unchanged from the baseline while climate change lowers nominal GDP.

    Args:
        baseline_engine_total_expenditure_pct_gdp: Baseline total government expenditure, in percent of nominal GDP, used to anchor the hot-scenario series through 2029.
        baseline_engine_total_expenditure_lcu: Baseline total government expenditure in local currency units, used through 2029 before the hot scenario departs from the baseline.
        baseline_engine_interest_expenditure_lcu: Baseline government interest expenditure in local currency units, used to anchor hot-scenario interest expenditure through 2029.
        baseline_engine_gross_debt_lcu: Baseline gross government debt in local currency units, used to anchor the hot-scenario debt stock through 2029.
        hot_engine_nominal_gdp_lcu: Nominal GDP in local currency units under the hot scenario, the denominator for expenditure and interest ratios and the scaling factor for the debt stock.
        hot_engine_revenue_pct_gdp: Government revenue in percent of nominal GDP under the hot scenario, held at its baseline ratio as GDP declines, and used to derive the primary balance.
        hot_engine_primary_expenditure_lcu: Primary government expenditure in local currency units under the hot scenario, assumed rigid and unchanged from the baseline as GDP falls.
        hot_engine_weighted_interest_rate: Weighted average nominal interest rate on government debt under the hot scenario, applied to the previous period's debt stock to derive interest expenditure.
        baseline_primary_expenditure_pct_gdp: Baseline primary government expenditure in percent of nominal GDP, used to anchor the hot-scenario ratio through 2029.
        baseline_interest_expenditure_pct_gdp: Baseline government interest expenditure in percent of nominal GDP, used to anchor the hot-scenario ratio through 2029.
        baseline_primary_balance_pct_gdp: Baseline primary balance in percent of nominal GDP, used to anchor the hot-scenario primary balance through 2029.
        baseline_debt_to_gdp: Baseline gross government debt in percent of nominal GDP, used to initialize the hot-scenario debt dynamics.
        scenario_nominal_gdp_growth_hot: Nominal GDP growth rate under the hot scenario, used in the debt dynamics equation to project the gross debt-to-GDP ratio.

    Returns:
        A result object holding complete tensors for the hot-scenario recurrence group: total expenditure and primary balance as percentages of GDP, total and interest expenditure and gross debt in local currency units, gross debt as a percentage of GDP, and the implied primary and interest expenditure ratios.
    """
    def hot_engine_total_expenditure_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(hot_engine_total_expenditure_lcu[time_period], hot_engine_nominal_gdp_lcu[time_period]), 100))

    hot_engine_total_expenditure_pct_gdp = CoordinateReader('hot_engine_total_expenditure_pct_gdp', data.HOT_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required, hot_engine_total_expenditure_pct_gdp_formula)
    def hot_engine_primary_balance_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_balance_pct_gdp[time_period])
        return as_measure(xl_sub(hot_engine_revenue_pct_gdp[time_period], scenario_primary_expenditure_pct_gdp_hot[time_period]))

    hot_engine_primary_balance_pct_gdp = CoordinateReader('hot_engine_primary_balance_pct_gdp', data.HOT_ENGINE_PRIMARY_BALANCE_PCT_GDP.required, hot_engine_primary_balance_pct_gdp_formula)
    def hot_engine_total_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_lcu[time_period])
        return as_measure(xl_add(hot_engine_interest_expenditure_lcu[time_period], hot_engine_primary_expenditure_lcu[time_period]))

    hot_engine_total_expenditure_lcu = CoordinateReader('hot_engine_total_expenditure_lcu', data.HOT_ENGINE_TOTAL_EXPENDITURE_LCU.required, hot_engine_total_expenditure_lcu_formula)
    def hot_engine_interest_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_interest_expenditure_lcu[time_period])
        return as_measure(xl_mul(xl_div(hot_engine_weighted_interest_rate[time_period], 100), hot_engine_gross_debt_lcu[time_period - 1]))

    hot_engine_interest_expenditure_lcu = CoordinateReader('hot_engine_interest_expenditure_lcu', data.HOT_ENGINE_INTEREST_EXPENDITURE_LCU.required, hot_engine_interest_expenditure_lcu_formula)
    def hot_engine_gross_debt_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_gross_debt_lcu[time_period])
        return as_measure(xl_mul(xl_div(hot_engine_gross_debt_pct_gdp[time_period], 100), hot_engine_nominal_gdp_lcu[time_period]))

    hot_engine_gross_debt_lcu = CoordinateReader('hot_engine_gross_debt_lcu', data.HOT_ENGINE_GROSS_DEBT_LCU.required, hot_engine_gross_debt_lcu_formula)
    def hot_engine_gross_debt_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_debt_to_gdp[time_period])
        return as_measure(xl_sub(xl_div(xl_mul(hot_engine_gross_debt_pct_gdp[time_period - 1], xl_add(1, xl_div(hot_engine_weighted_interest_rate[time_period], 100))), xl_add(1, xl_div(scenario_nominal_gdp_growth_hot[time_period], 100))), hot_engine_primary_balance_pct_gdp[time_period]))

    hot_engine_gross_debt_pct_gdp = CoordinateReader('hot_engine_gross_debt_pct_gdp', data.HOT_ENGINE_GROSS_DEBT_PCT_GDP.required, hot_engine_gross_debt_pct_gdp_formula)
    def scenario_primary_expenditure_pct_gdp_hot_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_expenditure_pct_gdp[time_period])
        return as_measure(xl_sub(hot_engine_total_expenditure_pct_gdp[time_period], scenario_interest_expenditure_pct_gdp_hot[time_period]))

    scenario_primary_expenditure_pct_gdp_hot = CoordinateReader('scenario_primary_expenditure_pct_gdp_hot', data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT.required, scenario_primary_expenditure_pct_gdp_hot_formula)
    def scenario_interest_expenditure_pct_gdp_hot_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_interest_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(hot_engine_interest_expenditure_lcu[time_period], hot_engine_nominal_gdp_lcu[time_period]), 100))

    scenario_interest_expenditure_pct_gdp_hot = CoordinateReader('scenario_interest_expenditure_pct_gdp_hot', data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT.required, scenario_interest_expenditure_pct_gdp_hot_formula)
    return ScanHotEngineTotalExpenditurePctGdpResult(
        hot_engine_total_expenditure_pct_gdp=data.HOT_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.collect((coord, hot_engine_total_expenditure_pct_gdp[coord]) for coord in data.HOT_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required),
        hot_engine_primary_balance_pct_gdp=data.HOT_ENGINE_PRIMARY_BALANCE_PCT_GDP.collect((coord, hot_engine_primary_balance_pct_gdp[coord]) for coord in data.HOT_ENGINE_PRIMARY_BALANCE_PCT_GDP.required),
        hot_engine_total_expenditure_lcu=data.HOT_ENGINE_TOTAL_EXPENDITURE_LCU.collect((coord, hot_engine_total_expenditure_lcu[coord]) for coord in data.HOT_ENGINE_TOTAL_EXPENDITURE_LCU.required),
        hot_engine_interest_expenditure_lcu=data.HOT_ENGINE_INTEREST_EXPENDITURE_LCU.collect((coord, hot_engine_interest_expenditure_lcu[coord]) for coord in data.HOT_ENGINE_INTEREST_EXPENDITURE_LCU.required),
        hot_engine_gross_debt_lcu=data.HOT_ENGINE_GROSS_DEBT_LCU.collect((coord, hot_engine_gross_debt_lcu[coord]) for coord in data.HOT_ENGINE_GROSS_DEBT_LCU.required),
        hot_engine_gross_debt_pct_gdp=data.HOT_ENGINE_GROSS_DEBT_PCT_GDP.collect((coord, hot_engine_gross_debt_pct_gdp[coord]) for coord in data.HOT_ENGINE_GROSS_DEBT_PCT_GDP.required),
        scenario_primary_expenditure_pct_gdp_hot=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT.collect((coord, scenario_primary_expenditure_pct_gdp_hot[coord]) for coord in data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT.required),
        scenario_interest_expenditure_pct_gdp_hot=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT.collect((coord, scenario_interest_expenditure_pct_gdp_hot[coord]) for coord in data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT.required),
    )

@publish(data.HOT_ADAPTED_ENGINE_EMPLOYMENT_GROWTH.schema, cells=data.HOT_ADAPTED_ENGINE_EMPLOYMENT_GROWTH.cells)
def hot_adapted_engine_employment_growth(*, baseline_employment_growth: data.BaselineEmploymentGrowth) -> data.Series[float | str | None]:
    """Return the employment growth path for the Hot Adapted climate scenario.

    Supply the long-term employment growth series used in the Hot Adapted scenario, in which countries adapt to higher temperatures within 20 years, so that nominal GDP and the fiscal projections can be built on the same employment basis as the baseline.

    Args:
        baseline_employment_growth: Baseline employment growth path, projected to grow in line with the UN working-age (15-64 year old) population after the end of the IMF WEO horizon, from which the Hot Adapted scenario's employment growth is read.

    Returns:
        A series of employment growth values by projection year for the Hot Adapted climate scenario, one entry per period in the scenario's required horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_employment_growth[time_period])

    return data.HOT_ADAPTED_ENGINE_EMPLOYMENT_GROWTH.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_EMPLOYMENT_GROWTH.required))

@publish(data.HOT_ADAPTED_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.schema, cells=data.HOT_ADAPTED_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.cells)
def hot_adapted_engine_labour_productivity_growth(*, climate_data_labour_productivity_growth_variation_hot_adapted: data.Series[float | str | None], baseline_labour_productivity_growth: data.BaselineLabourProductivityGrowth) -> data.Series[float | str | None]:
    """Combine baseline labour productivity growth with the hot-adapted climate variation in labour productivity growth.

    Produces the hot-adapted labour productivity growth path used to project nominal GDP under the climate scenario in which countries adapt more quickly to the same temperature increases as the hot scenario.

    Args:
        climate_data_labour_productivity_growth_variation_hot_adapted: Series of the estimated climate-driven variation in labour productivity growth under the hot-adapted climate scenario for each projection year.
        baseline_labour_productivity_growth: Baseline labour productivity growth, defined as the growth in GDP per employed person, in the absence of climate change.

    Returns:
        Series of labour productivity growth under the hot-adapted climate scenario, obtained by adding the climate variation to the baseline labour productivity growth for each projection year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(baseline_labour_productivity_growth[time_period], climate_data_labour_productivity_growth_variation_hot_adapted[time_period]))

    return data.HOT_ADAPTED_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.required))

@publish(data.HOT_ADAPTED_ENGINE_REAL_GDP_GROWTH.schema, cells=data.HOT_ADAPTED_ENGINE_REAL_GDP_GROWTH.cells)
def hot_adapted_engine_real_gdp_growth(*, hot_adapted_engine_employment_growth: data.Series[float | str | None], hot_adapted_engine_labour_productivity_growth: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project real GDP growth under the hot adapted climate scenario.

    Derive the hot adapted scenario's real GDP growth from employment growth and labour productivity growth, both expressed in percent.

    Args:
        hot_adapted_engine_employment_growth: Employment growth in the hot adapted scenario, in percent; long-run employment is assumed to grow with the working-age population.
        hot_adapted_engine_labour_productivity_growth: Labour productivity growth in the hot adapted scenario, in percent, where productivity is GDP per employed person and climate change slows its growth.

    Returns:
        Real GDP growth in the hot adapted scenario, in percent, approximated as the compounded sum of employment growth and labour productivity growth.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(hot_adapted_engine_employment_growth[time_period], 100)), xl_add(1, xl_div(hot_adapted_engine_labour_productivity_growth[time_period], 100))), 100), 100))

    return data.HOT_ADAPTED_ENGINE_REAL_GDP_GROWTH.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_REAL_GDP_GROWTH.required))

@publish(data.HOT_ADAPTED_ENGINE_GDP_DEFLATOR_GROWTH.schema, cells=data.HOT_ADAPTED_ENGINE_GDP_DEFLATOR_GROWTH.cells)
def hot_adapted_engine_gdp_deflator_growth(*, baseline_gdp_deflator_growth: data.BaselineGdpDeflatorGrowth) -> data.Series[float | str | None]:
    """Project the GDP deflator growth series under the hot adapted climate scenario.

    Rebase the baseline GDP deflator growth profile into the hot adapted engine scenario, in which countries adapt to the temperature increases of the hot scenario within 20 years rather than 30, so that climate effects on nominal GDP remain less severe than in the un-adapted hot scenario.

    Args:
        baseline_gdp_deflator_growth: Baseline GDP deflator growth series, indexed by projection year, used as the source of the GDP deflator growth path that is carried into the hot adapted climate scenario.

    Returns:
        A series of GDP deflator growth values for the hot adapted climate scenario, aligned to the projection horizon and carrying the same coordinate identities as the baseline GDP deflator growth series.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_gdp_deflator_growth[time_period])

    return data.HOT_ADAPTED_ENGINE_GDP_DEFLATOR_GROWTH.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_GDP_DEFLATOR_GROWTH.required))

@publish(data.HOT_ADAPTED_ENGINE_NOMINAL_GDP_LCU.schema, cells=data.HOT_ADAPTED_ENGINE_NOMINAL_GDP_LCU.cells)
def hot_adapted_engine_nominal_gdp_lcu(*, baseline_engine_nominal_gdp_lcu: data.Series[float | str | None], scenario_nominal_gdp_growth_hot_adapted: data.ScenarioNominalGdpGrowthHotAdapted) -> data.Series[float | str | None]:
    """Project nominal GDP in local currency units under the hot adapted climate scenario.

    Build the hot adapted scenario's nominal GDP path by compounding the baseline level with the scenario's nominal GDP growth from 2030 onward.

    Args:
        baseline_engine_nominal_gdp_lcu: Baseline nominal GDP in local currency units, used for all periods through 2029.
        scenario_nominal_gdp_growth_hot_adapted: Nominal GDP growth rates, in percent, under the hot adapted scenario, applied from 2030 onward.

    Returns:
        A series of hot adapted scenario nominal GDP levels in local currency units for every required period.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_nominal_gdp_lcu[time_period])
        return as_measure(xl_mul(hot_adapted_engine_nominal_gdp_lcu[time_period - 1], xl_add(1, xl_div(scenario_nominal_gdp_growth_hot_adapted[time_period], 100))))

    hot_adapted_engine_nominal_gdp_lcu = CoordinateReader('hot_adapted_engine_nominal_gdp_lcu', data.HOT_ADAPTED_ENGINE_NOMINAL_GDP_LCU.required, formula)
    return data.HOT_ADAPTED_ENGINE_NOMINAL_GDP_LCU.collect((coord, hot_adapted_engine_nominal_gdp_lcu[coord]) for coord in data.HOT_ADAPTED_ENGINE_NOMINAL_GDP_LCU.required)

@publish(data.HOT_ADAPTED_ENGINE_REVENUE_PCT_GDP.schema, cells=data.HOT_ADAPTED_ENGINE_REVENUE_PCT_GDP.cells)
def hot_adapted_engine_revenue_pct_gdp(*, hot_adapted_engine_discrete_risk_revenue_shock: data.Series[float | str | None], baseline_revenue_pct_gdp: data.BaselineRevenuePctGdp) -> data.Series[float | str | None]:
    """Project the hot-adapted scenario revenue-to-GDP ratio, including registered discrete-risk revenue shocks from 2030 onward.

    Combine the baseline revenue-to-GDP path with the registered fiscal impact of discrete risks under the hot-adapted climate scenario.

    Args:
        hot_adapted_engine_discrete_risk_revenue_shock: Revenue impact of materialized discrete fiscal risks under the hot-adapted scenario, expressed as a share of GDP; one-off events reduce revenue, so values are typically negative.
        baseline_revenue_pct_gdp: Baseline revenue-to-GDP ratio, which Q-CRAFT holds constant in the climate scenarios as nominal GDP declines.

    Returns:
        Series of the hot-adapted scenario revenue-to-GDP ratio, equal to the baseline ratio through 2029 and to the baseline ratio adjusted by the registered discrete-risk revenue shock from 2030 onward.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_revenue_pct_gdp[time_period])
        return as_measure(xl_add(baseline_revenue_pct_gdp[time_period], hot_adapted_engine_discrete_risk_revenue_shock[time_period]))

    return data.HOT_ADAPTED_ENGINE_REVENUE_PCT_GDP.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_REVENUE_PCT_GDP.required))

@publish(data.HOT_ADAPTED_ENGINE_OVERALL_BALANCE_PCT_GDP.schema, cells=data.HOT_ADAPTED_ENGINE_OVERALL_BALANCE_PCT_GDP.cells)
def hot_adapted_engine_overall_balance_pct_gdp(*, hot_adapted_engine_revenue_pct_gdp: data.Series[float | str | None], hot_adapted_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Compute the overall balance under the hot-adapted climate scenario as a share of GDP.

    Provide the hot-adapted scenario overall balance path, matching the baseline through 2029 and then reflecting the climate-driven revenue and rigid primary expenditure assumptions.

    Args:
        hot_adapted_engine_revenue_pct_gdp: Government revenue as a percentage of nominal GDP in the hot-adapted scenario, where the revenue-to-GDP ratio is assumed unchanged from the baseline as nominal GDP declines with climate change.
        hot_adapted_engine_total_expenditure_pct_gdp: Total government expenditure (interest payments plus primary expenditure) as a percentage of nominal GDP in the hot-adapted scenario, where primary expenditure is assumed rigid at the baseline level so its GDP ratio rises as GDP falls.
        baseline_overall_balance_pct_gdp: Baseline overall balance as a percentage of nominal GDP, used unchanged for periods through 2029 before climate change impacts are applied.

    Returns:
        A series of the hot-adapted scenario overall balance as a percentage of nominal GDP for each projection period, equal to the baseline balance through 2029 and revenue minus total expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_overall_balance_pct_gdp[time_period])
        return as_measure(xl_sub(hot_adapted_engine_revenue_pct_gdp[time_period], hot_adapted_engine_total_expenditure_pct_gdp[time_period]))

    return data.HOT_ADAPTED_ENGINE_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.HOT_ADAPTED_ENGINE_REVENUE_LCU.schema, cells=data.HOT_ADAPTED_ENGINE_REVENUE_LCU.cells)
def hot_adapted_engine_revenue_lcu(*, baseline_engine_revenue_lcu: data.Series[float | str | None], hot_adapted_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_adapted_engine_revenue_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute hot adapted scenario engine revenue in local currency units.

    Derive government revenue in the hot adapted climate scenario, holding revenue at baseline levels through 2029 and thereafter scaling nominal GDP by the scenario revenue-to-GDP ratio.

    Args:
        baseline_engine_revenue_lcu: Baseline scenario government revenue in billions of local currency units, assumed to remain constant as a share of nominal GDP; used for projection years up to and including 2029.
        hot_adapted_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units under the hot adapted climate scenario, where temperature increases match the hot scenario but countries adapt more quickly, softening the productivity slowdown.
        hot_adapted_engine_revenue_pct_gdp: Government revenue as a percent of nominal GDP under the hot adapted climate scenario, unchanged from the baseline ratio since tax policy settings are held constant.

    Returns:
        Government revenue in billions of local currency units under the hot adapted climate scenario for each projection year.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_revenue_lcu[time_period])
        return as_measure(xl_mul(xl_div(hot_adapted_engine_revenue_pct_gdp[time_period], 100), hot_adapted_engine_nominal_gdp_lcu[time_period]))

    return data.HOT_ADAPTED_ENGINE_REVENUE_LCU.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_REVENUE_LCU.required))

@publish(data.HOT_ADAPTED_ENGINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.HOT_ADAPTED_ENGINE_PRIMARY_EXPENDITURE_LCU.cells)
def hot_adapted_engine_primary_expenditure_lcu(*, expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)], baseline_engine_primary_expenditure_lcu: data.Series[float | str | None], hot_adapted_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_adapted_engine_discrete_risk_expenditure_shock: data.Series[float | str | None], hot_adapted_engine_recalibration_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project primary expenditure in local currency units under the Hot Adapted climate scenario.

    Provide the Hot Adapted scenario's primary expenditure path by holding expenditure rigid at the baseline and adding climate-related recalibration and discrete-risk shocks.

    Args:
        expenditure_rigidity: Degree to which primary expenditure is held fixed at the baseline in the face of lower GDP, ranging from 0 (fully flexible, ratio preserved) to 1 (completely rigid).
        baseline_engine_primary_expenditure_lcu: Baseline primary expenditure (excluding interest payments) in local currency units; used directly through 2029 and as the anchor for later periods.
        hot_adapted_engine_nominal_gdp_lcu: Nominal GDP in local currency units under the Hot Adapted scenario, used to convert discrete-risk expenditure shocks expressed as a percentage of GDP into local currency amounts.
        hot_adapted_engine_discrete_risk_expenditure_shock: Discrete-risk or natural-disaster expenditure shock under the Hot Adapted scenario, expressed as a percent of nominal GDP and added to primary expenditure.
        hot_adapted_engine_recalibration_lcu: Primary expenditure recalibration under the Hot Adapted scenario, in local currency units, scaled down as expenditure rigidity falls to reflect how much of the baseline expenditure is adjusted.

    Returns:
        Primary expenditure in local currency units under the Hot Adapted climate scenario; equals the baseline through 2029 and the rigid baseline less recalibration plus discrete-risk shocks thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_expenditure_lcu[time_period])
        return as_measure(xl_add(xl_sub(baseline_engine_primary_expenditure_lcu[time_period], xl_mul(xl_sub(1, expenditure_rigidity), hot_adapted_engine_recalibration_lcu[time_period])), xl_mul(xl_div(hot_adapted_engine_discrete_risk_expenditure_shock[time_period], 100), hot_adapted_engine_nominal_gdp_lcu[time_period])))

    return data.HOT_ADAPTED_ENGINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.HOT_ADAPTED_ENGINE_PRIMARY_BALANCE_LCU.schema, cells=data.HOT_ADAPTED_ENGINE_PRIMARY_BALANCE_LCU.cells)
def hot_adapted_engine_primary_balance_lcu(*, baseline_engine_primary_balance_lcu: data.Series[float | str | None], hot_adapted_engine_revenue_lcu: data.Series[float | str | None], hot_adapted_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the primary balance in local currency units under the hot adapted climate scenario.

    Projects the hot adapted scenario primary balance, which drives debt dynamics and the overall balance in that scenario.

    Args:
        baseline_engine_primary_balance_lcu: Baseline scenario primary balance in local currency units, used through 2029 before climate change effects begin in 2030.
        hot_adapted_engine_revenue_lcu: Government revenue in local currency units under the hot adapted scenario, where countries adapt quickly to the same temperature increases as the hot scenario.
        hot_adapted_engine_primary_expenditure_lcu: Primary expenditure in local currency units under the hot adapted scenario, which excludes interest payments and is assumed to remain rigid relative to the baseline.

    Returns:
        Primary balance in local currency units under the hot adapted scenario, equal to the baseline primary balance through 2029 and revenue less primary expenditure from 2030 onwards.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_balance_lcu[time_period])
        return as_measure(xl_sub(hot_adapted_engine_revenue_lcu[time_period], hot_adapted_engine_primary_expenditure_lcu[time_period]))

    return data.HOT_ADAPTED_ENGINE_PRIMARY_BALANCE_LCU.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_PRIMARY_BALANCE_LCU.required))

@publish(data.HOT_ADAPTED_ENGINE_OVERALL_BALANCE_LCU.schema, cells=data.HOT_ADAPTED_ENGINE_OVERALL_BALANCE_LCU.cells)
def hot_adapted_engine_overall_balance_lcu(*, baseline_engine_overall_balance_lcu: data.Series[float | str | None], hot_adapted_engine_revenue_lcu: data.Series[float | str | None], hot_adapted_engine_total_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the overall balance in local currency units under the hot adapted climate scenario.

    Derive the hot adapted scenario overall balance as revenue less total expenditure in local currency units, while carrying forward the baseline overall balance through the WEO horizon, consistent with climate effects beginning in 2030.

    Args:
        baseline_engine_overall_balance_lcu: Baseline overall balance in local currency units, used for periods through 2029 before climate change effects begin.
        hot_adapted_engine_revenue_lcu: Government revenue in local currency units under the hot adapted scenario, where countries adapt to higher temperatures more quickly.
        hot_adapted_engine_total_expenditure_lcu: Total government expenditure in local currency units under the hot adapted scenario, where countries adapt to higher temperatures more quickly.

    Returns:
        Overall balance in local currency units under the hot adapted climate scenario for each projection period; equals the baseline overall balance through 2029 and revenue less total expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_overall_balance_lcu[time_period])
        return as_measure(xl_sub(hot_adapted_engine_revenue_lcu[time_period], hot_adapted_engine_total_expenditure_lcu[time_period]))

    return data.HOT_ADAPTED_ENGINE_OVERALL_BALANCE_LCU.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_OVERALL_BALANCE_LCU.required))

@publish(data.HOT_ADAPTED_ENGINE_WEIGHTED_INTEREST_RATE.schema, cells=data.HOT_ADAPTED_ENGINE_WEIGHTED_INTEREST_RATE.cells)
def hot_adapted_engine_weighted_interest_rate(*, baseline_interest_rate: data.BaselineInterestRate) -> data.Series[float | str | None]:
    """Project the weighted average nominal interest rate along the Hot Adapted scenario.

    Provide the weighted average nominal interest rate on government debt used in the debt dynamics equation for the Hot Adapted climate scenario.

    Args:
        baseline_interest_rate: Baseline weighted average nominal interest rate on government debt, held unchanged across climate scenarios because interest rate assumptions are the same in all scenarios.

    Returns:
        A series of the weighted average nominal interest rate, by projection period, for the Hot Adapted climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_rate[time_period])

    return data.HOT_ADAPTED_ENGINE_WEIGHTED_INTEREST_RATE.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_WEIGHTED_INTEREST_RATE.required))

@publish(data.HOT_ADAPTED_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.schema, cells=data.HOT_ADAPTED_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.cells)
def hot_adapted_engine_interest_expenditure_pct_revenue(*, hot_adapted_engine_revenue_lcu: data.Series[float | str | None], hot_adapted_engine_interest_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute interest expenditure as a share of revenue under the hot adapted scenario.

    Expresses the hot adapted scenario's interest expenditure relative to revenue, showing the share of revenue absorbed by debt-service costs.

    Args:
        hot_adapted_engine_revenue_lcu: Hot adapted scenario government revenue, in billions of local currency units, consistent with the constant revenue-to-GDP ratio assumption.
        hot_adapted_engine_interest_expenditure_lcu: Hot adapted scenario government interest expenditure, in billions of local currency units, reflecting the higher debt-service costs implied by worse debt dynamics.

    Returns:
        Time series of interest expenditure as a percentage of revenue under the hot adapted scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(hot_adapted_engine_interest_expenditure_lcu[time_period], hot_adapted_engine_revenue_lcu[time_period]), 100))

    return data.HOT_ADAPTED_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.required))

@publish(data.HOT_ADAPTED_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.schema, cells=data.HOT_ADAPTED_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.cells)
def hot_adapted_engine_discrete_risk_revenue_shock(*, discrete_revenue_shocks: data.DiscreteRevenueShocks) -> data.Series[float | str | None]:
    """Project the discrete-risk revenue shock series for the Hot adapted climate scenario.

    Supplies the Hot adapted discrete-risk revenue shock along the projection horizon so registered revenue losses from materialized fiscal risks can be combined with the scenario's macro-fiscal projections.

    Args:
        discrete_revenue_shocks: Discrete fiscal risk revenue shocks registered by scenario and time period, expressed as a share of GDP; the Hot adapted scenario column holds the user-entered losses arising from materialized discrete risks and natural disasters.

    Returns:
        A series of revenue shock values for the Hot adapted scenario indexed by time period, empty where no shock is registered.
    """
    data.DISCRETE_REVENUE_SHOCKS.schema.validate(discrete_revenue_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_revenue_shocks['Hot adapted', time_period])

    return data.HOT_ADAPTED_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.required))

@publish(data.HOT_ADAPTED_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.schema, cells=data.HOT_ADAPTED_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.cells)
def hot_adapted_engine_discrete_risk_expenditure_shock(*, discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks) -> data.Series[float | str | None]:
    """Project the discrete risk primary expenditure shock under the hot adapted climate scenario.

    Provide the hot adapted scenario's registered discrete risk expenditure shock series, expressed as a share of GDP for the projection horizon.

    Args:
        discrete_primary_expenditure_shocks: Registered discrete risk fiscal impacts of materialized natural disasters and contingent liabilities, as a percent of GDP, by climate change scenario and time period.

    Returns:
        Time series of the discrete primary expenditure shock as a percentage of GDP in the hot adapted scenario, or None where no shock is registered.
    """
    data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.schema.validate(discrete_primary_expenditure_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_primary_expenditure_shocks['Hot adapted', time_period])

    return data.HOT_ADAPTED_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.required))

@publish(data.HOT_ADAPTED_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.schema, cells=data.HOT_ADAPTED_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.cells)
def hot_adapted_engine_memo_interest_expenditure_pct_gdp(*, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp) -> data.Series[float | str | None]:
    """Return the baseline interest expenditure as a share of GDP under the hot adapted climate scenario.

    Provides a memo series of interest expenditure (percent of GDP) for the hot adapted scenario, where temperatures rise as in the hot scenario but countries adapt more quickly.

    Args:
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure expressed as a percentage of nominal GDP, in local currency terms, for each projection year.

    Returns:
        A memo series of interest expenditure as a percentage of GDP under the hot adapted scenario, indexed by the projection time periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_expenditure_pct_gdp[time_period])

    return data.HOT_ADAPTED_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.required))

@publish(data.HOT_ADAPTED_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.schema, cells=data.HOT_ADAPTED_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.cells)
def hot_adapted_engine_memo_primary_expenditure_pct_gdp(*, baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp) -> data.Series[float | str | None]:
    """Project primary expenditure as a share of GDP under the Hot Adapted climate scenario.

    Produces the engine memo series of the primary expenditure-to-GDP ratio for the Hot Adapted scenario, in which countries adapt more quickly to the same temperature increases as in the Hot scenario so that the macroeconomic and fiscal effects of climate change are less severe.

    Args:
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure-to-GDP ratio series, taken from the passive no-policy-change baseline in which primary expenditure grows with productivity, inflation, and total population.

    Returns:
        Series of the primary expenditure-to-GDP ratio under the Hot Adapted scenario, expressed in percent of nominal GDP.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_expenditure_pct_gdp[time_period])

    return data.HOT_ADAPTED_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.required))

@publish(data.HOT_ADAPTED_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.schema, cells=data.HOT_ADAPTED_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.cells)
def hot_adapted_engine_memo_primary_balance_pct_gdp(*, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Return the baseline primary balance (percent of GDP) under the hot adapted climate scenario.

    Provides a memo series in which the hot adapted scenario's primary balance path is the same as the baseline, isolating the effect of climate change on other fiscal aggregates.

    Args:
        baseline_primary_balance_pct_gdp: Baseline primary balance expressed as a percentage of nominal GDP, assumed unchanged in the hot adapted scenario.

    Returns:
        A series of primary balance values as a percentage of nominal GDP under the hot adapted scenario, one value per projected year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_balance_pct_gdp[time_period])

    return data.HOT_ADAPTED_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.required))

@publish(data.HOT_ADAPTED_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.schema, cells=data.HOT_ADAPTED_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.cells)
def hot_adapted_engine_memo_overall_balance_pct_gdp(*, baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Return the climate-scenario memo overall balance as a share of nominal GDP under faster adaptation.

    Provide the overall balance memo line for the Hot Adapted scenario, in which countries adapt to higher temperatures within 20 years rather than 30.

    Args:
        baseline_overall_balance_pct_gdp: Baseline overall balance expressed as a percentage of nominal GDP, used as the coordinate path from which the Hot Adapted climate-scenario memo series is derived.

    Returns:
        A series of overall balance values as a percent of nominal GDP for the Hot Adapted climate scenario, aligned to the required time periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_overall_balance_pct_gdp[time_period])

    return data.HOT_ADAPTED_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.HOT_ADAPTED_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.schema, cells=data.HOT_ADAPTED_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.cells)
def hot_adapted_engine_memo_gross_debt_pct_gdp(*, baseline_debt_to_gdp: data.BaselineDebtToGdp) -> data.Series[float | str | None]:
    """Return the Hot Adapted scenario's memo gross debt-to-GDP path.

    Provide, under the Hot Adapted climate scenario, the memo item for the gross debt-to-GDP ratio implied by the baseline debt dynamics.

    Args:
        baseline_debt_to_gdp: Baseline gross debt-to-GDP ratio series, keyed by year, used as the memo input for the Hot Adapted climate scenario.

    Returns:
        Series of gross debt-to-GDP ratios (in percent of GDP) for the Hot Adapted climate scenario, with one value per projected year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_to_gdp[time_period])

    return data.HOT_ADAPTED_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.required))

@publish(data.HOT_ADAPTED_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.HOT_ADAPTED_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.cells)
def hot_adapted_engine_baseline_primary_expenditure_lcu(*, baseline_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Extract the baseline primary expenditure under the hot adapted climate scenario, expressed in local currency units.

    Provides the baseline primary expenditure level against which the hot adapted scenario's rigid primary expenditure is benchmarked.

    Args:
        baseline_engine_primary_expenditure_lcu: Baseline primary expenditure in billions of local currency units, excluding government interest payments, for the general government sector.

    Returns:
        A series of baseline primary expenditure values in local currency units indexed by the hot adapted scenario's required time periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_engine_primary_expenditure_lcu[time_period])

    return data.HOT_ADAPTED_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.HOT_ADAPTED_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.schema, cells=data.HOT_ADAPTED_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.cells)
def hot_adapted_engine_primary_expenditure_baseline_share_lcu(*, hot_adapted_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_adapted_engine_memo_primary_expenditure_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Derive the baseline primary expenditure level in local currency units implied by a memo expenditure-to-GDP share.

    Express the primary expenditure baseline (reported as a share of nominal GDP) back in local currency units so it can serve as the rigid baseline level in the hot adapted scenario.

    Args:
        hot_adapted_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units under the hot adapted scenario, taken as the scaling base for the baseline expenditure share.
        hot_adapted_engine_memo_primary_expenditure_pct_gdp: Baseline primary expenditure as a percent of nominal GDP, matching the constant primary expenditure-to-GDP setting of the baseline scenario.

    Returns:
        Time series of baseline primary expenditure in billions of local currency units, obtained by applying the percent-of-GDP share to nominal GDP.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(hot_adapted_engine_memo_primary_expenditure_pct_gdp[time_period], 100), hot_adapted_engine_nominal_gdp_lcu[time_period]))

    return data.HOT_ADAPTED_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.required))

@publish(data.HOT_ADAPTED_ENGINE_RECALIBRATION_LCU.schema, cells=data.HOT_ADAPTED_ENGINE_RECALIBRATION_LCU.cells)
def hot_adapted_engine_recalibration_lcu(*, hot_adapted_engine_baseline_primary_expenditure_lcu: data.Series[float | str | None], hot_adapted_engine_primary_expenditure_baseline_share_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Recalibrate primary expenditure for the hot adapted scenario in local currency units.

    Derive the hot adapted scenario primary expenditure level in local currency units by removing the baseline share component from the baseline primary expenditure level.

    Args:
        hot_adapted_engine_baseline_primary_expenditure_lcu: Baseline primary expenditure level in local currency units for the hot adapted recalibration.
        hot_adapted_engine_primary_expenditure_baseline_share_lcu: Baseline share of primary expenditure in local currency units to subtract from the baseline level during recalibration.

    Returns:
        Recalibrated hot adapted scenario primary expenditure in local currency units.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(hot_adapted_engine_baseline_primary_expenditure_lcu[time_period], hot_adapted_engine_primary_expenditure_baseline_share_lcu[time_period]))

    return data.HOT_ADAPTED_ENGINE_RECALIBRATION_LCU.collect(evaluate(formula, data.HOT_ADAPTED_ENGINE_RECALIBRATION_LCU.required))

@dataclass(frozen=True, slots=True)
class ScanHotAdaptedEngineTotalExpenditurePctGdpResult:
    """Complete named results of one recurrence group evaluation."""
    hot_adapted_engine_total_expenditure_pct_gdp: data.Series[float | str | None]
    hot_adapted_engine_primary_balance_pct_gdp: data.Series[float | str | None]
    hot_adapted_engine_total_expenditure_lcu: data.Series[float | str | None]
    hot_adapted_engine_interest_expenditure_lcu: data.Series[float | str | None]
    hot_adapted_engine_gross_debt_lcu: data.Series[float | str | None]
    hot_adapted_engine_gross_debt_pct_gdp: data.Series[float | str | None]
    scenario_primary_expenditure_pct_gdp_hot_adapted: data.ScenarioPrimaryExpenditurePctGdpHotAdapted
    scenario_interest_expenditure_pct_gdp_hot_adapted: data.ScenarioInterestExpenditurePctGdpHotAdapted

def scan_hot_adapted_engine_total_expenditure_pct_gdp(*, baseline_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_engine_total_expenditure_lcu: data.Series[float | str | None], baseline_engine_interest_expenditure_lcu: data.Series[float | str | None], baseline_engine_gross_debt_lcu: data.Series[float | str | None], hot_adapted_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_adapted_engine_revenue_pct_gdp: data.Series[float | str | None], hot_adapted_engine_primary_expenditure_lcu: data.Series[float | str | None], hot_adapted_engine_weighted_interest_rate: data.Series[float | str | None], baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp, baseline_debt_to_gdp: data.BaselineDebtToGdp, scenario_nominal_gdp_growth_hot_adapted: data.ScenarioNominalGdpGrowthHotAdapted) -> ScanHotAdaptedEngineTotalExpenditurePctGdpResult:
    """Compute the hot-adapted scenario total expenditure-to-GDP ratio and its related fiscal aggregates.

    Derive total expenditure, interest and primary expenditure, primary balance, and debt indicators for the hot-adapted climate scenario, carrying over baseline values through 2029 and solving the fiscal block forward thereafter.

    Args:
        baseline_engine_total_expenditure_pct_gdp: Baseline total government expenditure as a percent of nominal GDP.
        baseline_engine_total_expenditure_lcu: Baseline total government expenditure in local currency units.
        baseline_engine_interest_expenditure_lcu: Baseline government interest expenditure in local currency units.
        baseline_engine_gross_debt_lcu: Baseline gross government debt in local currency units.
        hot_adapted_engine_nominal_gdp_lcu: Nominal GDP in local currency units under the hot-adapted climate scenario.
        hot_adapted_engine_revenue_pct_gdp: Government revenue as a percent of nominal GDP under the hot-adapted scenario, assumed unchanged from the baseline ratio.
        hot_adapted_engine_primary_expenditure_lcu: Primary expenditure (excluding interest payments) in local currency units under the hot-adapted scenario.
        hot_adapted_engine_weighted_interest_rate: Weighted average nominal interest rate on government debt under the hot-adapted scenario.
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure as a percent of nominal GDP.
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure as a percent of nominal GDP.
        baseline_primary_balance_pct_gdp: Baseline primary balance as a percent of nominal GDP.
        baseline_debt_to_gdp: Baseline gross debt-to-GDP ratio.
        scenario_nominal_gdp_growth_hot_adapted: Nominal GDP growth rate under the hot-adapted climate scenario.

    Returns:
        A result holding the hot-adapted scenario series for total expenditure (percent of GDP and local currency units), primary balance, interest expenditure (local currency units and percent of GDP), gross debt (local currency units and percent of GDP), and primary expenditure as a percent of GDP.
    """
    def hot_adapted_engine_total_expenditure_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(hot_adapted_engine_total_expenditure_lcu[time_period], hot_adapted_engine_nominal_gdp_lcu[time_period]), 100))

    hot_adapted_engine_total_expenditure_pct_gdp = CoordinateReader('hot_adapted_engine_total_expenditure_pct_gdp', data.HOT_ADAPTED_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required, hot_adapted_engine_total_expenditure_pct_gdp_formula)
    def hot_adapted_engine_primary_balance_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_balance_pct_gdp[time_period])
        return as_measure(xl_sub(hot_adapted_engine_revenue_pct_gdp[time_period], scenario_primary_expenditure_pct_gdp_hot_adapted[time_period]))

    hot_adapted_engine_primary_balance_pct_gdp = CoordinateReader('hot_adapted_engine_primary_balance_pct_gdp', data.HOT_ADAPTED_ENGINE_PRIMARY_BALANCE_PCT_GDP.required, hot_adapted_engine_primary_balance_pct_gdp_formula)
    def hot_adapted_engine_total_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_lcu[time_period])
        return as_measure(xl_add(hot_adapted_engine_interest_expenditure_lcu[time_period], hot_adapted_engine_primary_expenditure_lcu[time_period]))

    hot_adapted_engine_total_expenditure_lcu = CoordinateReader('hot_adapted_engine_total_expenditure_lcu', data.HOT_ADAPTED_ENGINE_TOTAL_EXPENDITURE_LCU.required, hot_adapted_engine_total_expenditure_lcu_formula)
    def hot_adapted_engine_interest_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_interest_expenditure_lcu[time_period])
        return as_measure(xl_mul(xl_div(hot_adapted_engine_weighted_interest_rate[time_period], 100), hot_adapted_engine_gross_debt_lcu[time_period - 1]))

    hot_adapted_engine_interest_expenditure_lcu = CoordinateReader('hot_adapted_engine_interest_expenditure_lcu', data.HOT_ADAPTED_ENGINE_INTEREST_EXPENDITURE_LCU.required, hot_adapted_engine_interest_expenditure_lcu_formula)
    def hot_adapted_engine_gross_debt_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_gross_debt_lcu[time_period])
        return as_measure(xl_mul(xl_div(hot_adapted_engine_gross_debt_pct_gdp[time_period], 100), hot_adapted_engine_nominal_gdp_lcu[time_period]))

    hot_adapted_engine_gross_debt_lcu = CoordinateReader('hot_adapted_engine_gross_debt_lcu', data.HOT_ADAPTED_ENGINE_GROSS_DEBT_LCU.required, hot_adapted_engine_gross_debt_lcu_formula)
    def hot_adapted_engine_gross_debt_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_debt_to_gdp[time_period])
        return as_measure(xl_sub(xl_div(xl_mul(hot_adapted_engine_gross_debt_pct_gdp[time_period - 1], xl_add(1, xl_div(hot_adapted_engine_weighted_interest_rate[time_period], 100))), xl_add(1, xl_div(scenario_nominal_gdp_growth_hot_adapted[time_period], 100))), hot_adapted_engine_primary_balance_pct_gdp[time_period]))

    hot_adapted_engine_gross_debt_pct_gdp = CoordinateReader('hot_adapted_engine_gross_debt_pct_gdp', data.HOT_ADAPTED_ENGINE_GROSS_DEBT_PCT_GDP.required, hot_adapted_engine_gross_debt_pct_gdp_formula)
    def scenario_primary_expenditure_pct_gdp_hot_adapted_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_expenditure_pct_gdp[time_period])
        return as_measure(xl_sub(hot_adapted_engine_total_expenditure_pct_gdp[time_period], scenario_interest_expenditure_pct_gdp_hot_adapted[time_period]))

    scenario_primary_expenditure_pct_gdp_hot_adapted = CoordinateReader('scenario_primary_expenditure_pct_gdp_hot_adapted', data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_ADAPTED.required, scenario_primary_expenditure_pct_gdp_hot_adapted_formula)
    def scenario_interest_expenditure_pct_gdp_hot_adapted_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_interest_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(hot_adapted_engine_interest_expenditure_lcu[time_period], hot_adapted_engine_nominal_gdp_lcu[time_period]), 100))

    scenario_interest_expenditure_pct_gdp_hot_adapted = CoordinateReader('scenario_interest_expenditure_pct_gdp_hot_adapted', data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_ADAPTED.required, scenario_interest_expenditure_pct_gdp_hot_adapted_formula)
    return ScanHotAdaptedEngineTotalExpenditurePctGdpResult(
        hot_adapted_engine_total_expenditure_pct_gdp=data.HOT_ADAPTED_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.collect((coord, hot_adapted_engine_total_expenditure_pct_gdp[coord]) for coord in data.HOT_ADAPTED_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required),
        hot_adapted_engine_primary_balance_pct_gdp=data.HOT_ADAPTED_ENGINE_PRIMARY_BALANCE_PCT_GDP.collect((coord, hot_adapted_engine_primary_balance_pct_gdp[coord]) for coord in data.HOT_ADAPTED_ENGINE_PRIMARY_BALANCE_PCT_GDP.required),
        hot_adapted_engine_total_expenditure_lcu=data.HOT_ADAPTED_ENGINE_TOTAL_EXPENDITURE_LCU.collect((coord, hot_adapted_engine_total_expenditure_lcu[coord]) for coord in data.HOT_ADAPTED_ENGINE_TOTAL_EXPENDITURE_LCU.required),
        hot_adapted_engine_interest_expenditure_lcu=data.HOT_ADAPTED_ENGINE_INTEREST_EXPENDITURE_LCU.collect((coord, hot_adapted_engine_interest_expenditure_lcu[coord]) for coord in data.HOT_ADAPTED_ENGINE_INTEREST_EXPENDITURE_LCU.required),
        hot_adapted_engine_gross_debt_lcu=data.HOT_ADAPTED_ENGINE_GROSS_DEBT_LCU.collect((coord, hot_adapted_engine_gross_debt_lcu[coord]) for coord in data.HOT_ADAPTED_ENGINE_GROSS_DEBT_LCU.required),
        hot_adapted_engine_gross_debt_pct_gdp=data.HOT_ADAPTED_ENGINE_GROSS_DEBT_PCT_GDP.collect((coord, hot_adapted_engine_gross_debt_pct_gdp[coord]) for coord in data.HOT_ADAPTED_ENGINE_GROSS_DEBT_PCT_GDP.required),
        scenario_primary_expenditure_pct_gdp_hot_adapted=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_ADAPTED.collect((coord, scenario_primary_expenditure_pct_gdp_hot_adapted[coord]) for coord in data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_ADAPTED.required),
        scenario_interest_expenditure_pct_gdp_hot_adapted=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_ADAPTED.collect((coord, scenario_interest_expenditure_pct_gdp_hot_adapted[coord]) for coord in data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_ADAPTED.required),
    )

@publish(data.HOT_UNADAPTED_ENGINE_EMPLOYMENT_GROWTH.schema, cells=data.HOT_UNADAPTED_ENGINE_EMPLOYMENT_GROWTH.cells)
def hot_unadapted_engine_employment_growth(*, baseline_employment_growth: data.BaselineEmploymentGrowth) -> data.Series[float | str | None]:
    """Return the employment growth projection for the Hot Un-Adapted climate scenario.

    Provides the employment component of the nominal GDP decomposition under the Hot Un-Adapted scenario, where temperatures rise as in the Hot scenario but countries adapt to climate change over 50 years rather than 30.

    Args:
        baseline_employment_growth: Baseline employment growth series, projected after the WEO horizon to grow in line with the working-age (15-64) population; reused unchanged under the Hot Un-Adapted scenario.

    Returns:
        A series of annual employment growth values for the Hot Un-Adapted scenario, aligned to the scenario's projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_employment_growth[time_period])

    return data.HOT_UNADAPTED_ENGINE_EMPLOYMENT_GROWTH.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_EMPLOYMENT_GROWTH.required))

@publish(data.HOT_UNADAPTED_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.schema, cells=data.HOT_UNADAPTED_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.cells)
def hot_unadapted_engine_labour_productivity_growth(*, climate_data_labour_productivity_growth_variation_hot_unadapted: data.Series[float | str | None], baseline_labour_productivity_growth: data.BaselineLabourProductivityGrowth) -> data.Series[float | str | None]:
    """Project labour productivity growth under the hot un-adapted climate scenario.

    Adds the hot un-adapted climate variation in labour productivity growth to the baseline labour productivity growth trajectory, capturing slower adaptation (m = 50 years) to higher temperatures.

    Args:
        climate_data_labour_productivity_growth_variation_hot_unadapted: Climate-driven variation in labour productivity growth under the hot un-adapted scenario, where temperatures follow the hot scenario but countries adapt to higher temperatures over 50 years rather than 30.
        baseline_labour_productivity_growth: Baseline labour productivity growth trajectory, defined as growth in GDP per employed person, reflecting the user's start and end productivity assumptions before any climate change effects.

    Returns:
        Labour productivity growth by projection year under the hot un-adapted scenario, equal to the baseline growth plus the hot un-adapted climate variation.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(baseline_labour_productivity_growth[time_period], climate_data_labour_productivity_growth_variation_hot_unadapted[time_period]))

    return data.HOT_UNADAPTED_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_LABOUR_PRODUCTIVITY_GROWTH.required))

@publish(data.HOT_UNADAPTED_ENGINE_REAL_GDP_GROWTH.schema, cells=data.HOT_UNADAPTED_ENGINE_REAL_GDP_GROWTH.cells)
def hot_unadapted_engine_real_gdp_growth(*, hot_unadapted_engine_employment_growth: data.Series[float | str | None], hot_unadapted_engine_labour_productivity_growth: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project real GDP growth under the Hot Un-Adapted climate scenario.

    Derive real GDP growth from the combined effect of employment growth and labour productivity growth for the Hot Un-Adapted scenario.

    Args:
        hot_unadapted_engine_employment_growth: Projected growth in employment, in percent, under the Hot Un-Adapted climate scenario.
        hot_unadapted_engine_labour_productivity_growth: Projected growth in labour productivity, defined as real GDP per employed person in percent, under the Hot Un-Adapted climate scenario.

    Returns:
        Projected real GDP growth, in percent, under the Hot Un-Adapted climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(hot_unadapted_engine_employment_growth[time_period], 100)), xl_add(1, xl_div(hot_unadapted_engine_labour_productivity_growth[time_period], 100))), 100), 100))

    return data.HOT_UNADAPTED_ENGINE_REAL_GDP_GROWTH.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_REAL_GDP_GROWTH.required))

@publish(data.HOT_UNADAPTED_ENGINE_GDP_DEFLATOR_GROWTH.schema, cells=data.HOT_UNADAPTED_ENGINE_GDP_DEFLATOR_GROWTH.cells)
def hot_unadapted_engine_gdp_deflator_growth(*, baseline_gdp_deflator_growth: data.BaselineGdpDeflatorGrowth) -> data.Series[float | str | None]:
    """Return the baseline GDP deflator growth series for the Hot Un-Adapted climate scenario.

    Provides the GDP deflator growth path used to build the Hot Un-Adapted scenario, in which countries adapt to rising temperatures over 50 years rather than the 30 years assumed in the Hot scenario.

    Args:
        baseline_gdp_deflator_growth: Baseline GDP deflator growth series, used unchanged since inflation is assumed to be identical across the baseline and all climate change scenarios.

    Returns:
        A series of GDP deflator growth values for the Hot Un-Adapted climate scenario, matching the baseline because inflation is held constant across scenarios.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_gdp_deflator_growth[time_period])

    return data.HOT_UNADAPTED_ENGINE_GDP_DEFLATOR_GROWTH.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_GDP_DEFLATOR_GROWTH.required))

@publish(data.HOT_UNADAPTED_ENGINE_NOMINAL_GDP_LCU.schema, cells=data.HOT_UNADAPTED_ENGINE_NOMINAL_GDP_LCU.cells)
def hot_unadapted_engine_nominal_gdp_lcu(*, baseline_engine_nominal_gdp_lcu: data.Series[float | str | None], scenario_nominal_gdp_growth_hot_unadapted: data.ScenarioNominalGdpGrowthHotUnadapted) -> data.Series[float | str | None]:
    """Project nominal GDP in local currency units under the Hot Un-Adapted scenario.

    Builds the Hot Un-Adapted scenario's nominal GDP path by compounding the baseline level with the scenario's annual growth rate from 2030 onward.

    Args:
        baseline_engine_nominal_gdp_lcu: Baseline scenario nominal GDP in billions of local currency units, from which projections through 2029 are carried forward.
        scenario_nominal_gdp_growth_hot_unadapted: Annual nominal GDP growth rates, in percent, under the Hot Un-Adapted scenario, in which temperatures rise as in the Hot scenario but countries adapt only slowly.

    Returns:
        Nominal GDP in billions of local currency units under the Hot Un-Adapted scenario; it equals the baseline level through 2029 and thereafter compounds the prior year's value by the scenario growth rate.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_nominal_gdp_lcu[time_period])
        return as_measure(xl_mul(hot_unadapted_engine_nominal_gdp_lcu[time_period - 1], xl_add(1, xl_div(scenario_nominal_gdp_growth_hot_unadapted[time_period], 100))))

    hot_unadapted_engine_nominal_gdp_lcu = CoordinateReader('hot_unadapted_engine_nominal_gdp_lcu', data.HOT_UNADAPTED_ENGINE_NOMINAL_GDP_LCU.required, formula)
    return data.HOT_UNADAPTED_ENGINE_NOMINAL_GDP_LCU.collect((coord, hot_unadapted_engine_nominal_gdp_lcu[coord]) for coord in data.HOT_UNADAPTED_ENGINE_NOMINAL_GDP_LCU.required)

@publish(data.HOT_UNADAPTED_ENGINE_REVENUE_PCT_GDP.schema, cells=data.HOT_UNADAPTED_ENGINE_REVENUE_PCT_GDP.cells)
def hot_unadapted_engine_revenue_pct_gdp(*, hot_unadapted_engine_discrete_risk_revenue_shock: data.Series[float | str | None], baseline_revenue_pct_gdp: data.BaselineRevenuePctGdp) -> data.Series[float | str | None]:
    """Project the revenue-to-GDP ratio under the hot un-adapted climate scenario.

    Computes the hot un-adapted scenario revenue-to-GDP ratio by adding the discrete-risk revenue shock to the baseline revenue ratio from 2030 onward, while keeping the baseline ratio through 2029.

    Args:
        hot_unadapted_engine_discrete_risk_revenue_shock: Discrete-risk revenue shock (as a share of GDP) registered in the hot un-adapted scenario; added to the baseline revenue ratio from 2030 onward and not applied through 2029.
        baseline_revenue_pct_gdp: Baseline government revenue as a percentage of nominal GDP, which remains unchanged from the baseline under the climate scenarios.

    Returns:
        Series of the hot un-adapted scenario revenue-to-GDP ratio over the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_revenue_pct_gdp[time_period])
        return as_measure(xl_add(baseline_revenue_pct_gdp[time_period], hot_unadapted_engine_discrete_risk_revenue_shock[time_period]))

    return data.HOT_UNADAPTED_ENGINE_REVENUE_PCT_GDP.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_REVENUE_PCT_GDP.required))

@publish(data.HOT_UNADAPTED_ENGINE_OVERALL_BALANCE_PCT_GDP.schema, cells=data.HOT_UNADAPTED_ENGINE_OVERALL_BALANCE_PCT_GDP.cells)
def hot_unadapted_engine_overall_balance_pct_gdp(*, hot_unadapted_engine_revenue_pct_gdp: data.Series[float | str | None], hot_unadapted_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Project the overall balance under the hot un-adapted climate scenario.

    Derive the hot un-adapted overall balance as revenue less total expenditure from 2030 onward, carrying forward the baseline overall balance through 2029.

    Args:
        hot_unadapted_engine_revenue_pct_gdp: Government revenue under the hot un-adapted climate scenario, in percent of nominal GDP.
        hot_unadapted_engine_total_expenditure_pct_gdp: Total government expenditure under the hot un-adapted climate scenario, in percent of nominal GDP.
        baseline_overall_balance_pct_gdp: Overall balance in the baseline scenario, in percent of nominal GDP, used to proxy the overall balance through 2029 before climate change effects begin.

    Returns:
        The overall balance under the hot un-adapted climate scenario, in percent of nominal GDP, for each year of the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_overall_balance_pct_gdp[time_period])
        return as_measure(xl_sub(hot_unadapted_engine_revenue_pct_gdp[time_period], hot_unadapted_engine_total_expenditure_pct_gdp[time_period]))

    return data.HOT_UNADAPTED_ENGINE_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.HOT_UNADAPTED_ENGINE_REVENUE_LCU.schema, cells=data.HOT_UNADAPTED_ENGINE_REVENUE_LCU.cells)
def hot_unadapted_engine_revenue_lcu(*, baseline_engine_revenue_lcu: data.Series[float | str | None], hot_unadapted_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_unadapted_engine_revenue_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project government revenue in local currency units under the Hot Un-Adapted climate scenario.

    Derives the Hot Un-Adapted revenue path, holding the baseline revenue level through 2029 and thereafter scaling nominal GDP by the scenario's constant revenue-to-GDP ratio.

    Args:
        baseline_engine_revenue_lcu: Baseline government revenue in billions of local currency units, used unchanged for time periods up to and including 2029.
        hot_unadapted_engine_nominal_gdp_lcu: Nominal GDP in billions of local currency units under the Hot Un-Adapted scenario, in which temperatures rise as in the Hot scenario but adaptation occurs slowly over 50 years.
        hot_unadapted_engine_revenue_pct_gdp: Government revenue as a percent of nominal GDP under the Hot Un-Adapted scenario, held constant at the baseline ratio in line with the no-policy-change assumption.

    Returns:
        Time series of government revenue in billions of local currency units under the Hot Un-Adapted scenario, over the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_revenue_lcu[time_period])
        return as_measure(xl_mul(xl_div(hot_unadapted_engine_revenue_pct_gdp[time_period], 100), hot_unadapted_engine_nominal_gdp_lcu[time_period]))

    return data.HOT_UNADAPTED_ENGINE_REVENUE_LCU.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_REVENUE_LCU.required))

@publish(data.HOT_UNADAPTED_ENGINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.HOT_UNADAPTED_ENGINE_PRIMARY_EXPENDITURE_LCU.cells)
def hot_unadapted_engine_primary_expenditure_lcu(*, expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)], baseline_engine_primary_expenditure_lcu: data.Series[float | str | None], hot_unadapted_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_unadapted_engine_discrete_risk_expenditure_shock: data.Series[float | str | None], hot_unadapted_engine_recalibration_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute primary expenditure in local currency units under the Hot Un-Adapted climate scenario.

    Projects primary expenditure for the Hot Un-Adapted scenario, holding expenditure rigid at the baseline level and adding any registered discrete-risk expenditure shock, before 2030 and from 2030 onward.

    Args:
        expenditure_rigidity: Degree of spending rigidity, ranging from 0 (fully flexible) to 1 (completely rigid); 1 holds primary expenditure fixed at the baseline level and 0 allows it to fall so that the primary expenditure-to-GDP ratio matches the baseline.
        baseline_engine_primary_expenditure_lcu: Primary expenditure in local currency units under the baseline scenario, excluding government interest payments.
        hot_unadapted_engine_nominal_gdp_lcu: Nominal GDP in local currency units under the Hot Un-Adapted scenario, used to convert discrete-risk expenditure shocks expressed as a percentage of GDP into local currency amounts.
        hot_unadapted_engine_discrete_risk_expenditure_shock: Fiscal impact of materialized discrete risks or natural disasters under the Hot Un-Adapted scenario, expressed as a percentage of GDP and added to primary expenditure.
        hot_unadapted_engine_recalibration_lcu: Primary expenditure recalibration in local currency units under the Hot Un-Adapted scenario, scaled by the expenditure rigidity parameter before being deducted from the baseline.

    Returns:
        Primary expenditure in local currency units under the Hot Un-Adapted scenario, equal to the baseline level through 2029 and thereafter adjusted for expenditure recalibration and discrete-risk expenditure shocks.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_expenditure_lcu[time_period])
        return as_measure(xl_add(xl_sub(baseline_engine_primary_expenditure_lcu[time_period], xl_mul(xl_sub(1, expenditure_rigidity), hot_unadapted_engine_recalibration_lcu[time_period])), xl_mul(xl_div(hot_unadapted_engine_discrete_risk_expenditure_shock[time_period], 100), hot_unadapted_engine_nominal_gdp_lcu[time_period])))

    return data.HOT_UNADAPTED_ENGINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.HOT_UNADAPTED_ENGINE_PRIMARY_BALANCE_LCU.schema, cells=data.HOT_UNADAPTED_ENGINE_PRIMARY_BALANCE_LCU.cells)
def hot_unadapted_engine_primary_balance_lcu(*, baseline_engine_primary_balance_lcu: data.Series[float | str | None], hot_unadapted_engine_revenue_lcu: data.Series[float | str | None], hot_unadapted_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the primary balance in local currency units under the Hot Un-Adapted climate scenario.

    Derives the Hot Un-Adapted primary balance, carrying over the baseline primary balance through 2029 and thereafter taking revenue net of primary expenditure.

    Args:
        baseline_engine_primary_balance_lcu: Baseline primary balance in local currency units, used unchanged for periods through 2029.
        hot_unadapted_engine_revenue_lcu: Government revenue in local currency units under the Hot Un-Adapted scenario, where the revenue-to-GDP ratio remains at its baseline level as nominal GDP declines.
        hot_unadapted_engine_primary_expenditure_lcu: Primary expenditure in local currency units under the Hot Un-Adapted scenario, which is rigid and held at the baseline level.

    Returns:
        Primary balance in local currency units for the Hot Un-Adapted scenario, equal to the baseline value through 2029 and revenue less primary expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_primary_balance_lcu[time_period])
        return as_measure(xl_sub(hot_unadapted_engine_revenue_lcu[time_period], hot_unadapted_engine_primary_expenditure_lcu[time_period]))

    return data.HOT_UNADAPTED_ENGINE_PRIMARY_BALANCE_LCU.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_PRIMARY_BALANCE_LCU.required))

@publish(data.HOT_UNADAPTED_ENGINE_OVERALL_BALANCE_LCU.schema, cells=data.HOT_UNADAPTED_ENGINE_OVERALL_BALANCE_LCU.cells)
def hot_unadapted_engine_overall_balance_lcu(*, baseline_engine_overall_balance_lcu: data.Series[float | str | None], hot_unadapted_engine_revenue_lcu: data.Series[float | str | None], hot_unadapted_engine_total_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the overall balance for the hot un-adapted climate scenario.

    Provide the overall balance (revenue less total expenditure, in billions of local currency units) under the hot un-adapted scenario, in which temperatures follow the 90th percentile of SSP3-7.0 projections and countries adapt only slowly.

    Args:
        baseline_engine_overall_balance_lcu: Baseline scenario overall balance in billions of local currency units, used for time periods up to and including 2029 before climate change effects begin.
        hot_unadapted_engine_revenue_lcu: Government revenue in billions of local currency units under the hot un-adapted climate scenario, assumed to decline in line with nominal GDP so the revenue-to-GDP ratio stays at its baseline level.
        hot_unadapted_engine_total_expenditure_lcu: Total government expenditure in billions of local currency units under the hot un-adapted climate scenario, comprising rigid primary expenditure held at baseline levels plus interest expenditure.

    Returns:
        A series of overall balance values in billions of local currency units for the hot un-adapted scenario, equal to the baseline overall balance through 2029 and to revenue less total expenditure thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_overall_balance_lcu[time_period])
        return as_measure(xl_sub(hot_unadapted_engine_revenue_lcu[time_period], hot_unadapted_engine_total_expenditure_lcu[time_period]))

    return data.HOT_UNADAPTED_ENGINE_OVERALL_BALANCE_LCU.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_OVERALL_BALANCE_LCU.required))

@publish(data.HOT_UNADAPTED_ENGINE_WEIGHTED_INTEREST_RATE.schema, cells=data.HOT_UNADAPTED_ENGINE_WEIGHTED_INTEREST_RATE.cells)
def hot_unadapted_engine_weighted_interest_rate(*, baseline_interest_rate: data.BaselineInterestRate) -> data.Series[float | str | None]:
    """Compute the hot un-adapted scenario's weighted average nominal interest rate series.

    Produces the weighted average nominal interest rate on government debt for each projection year under the hot un-adapted climate scenario.

    Args:
        baseline_interest_rate: The baseline scenario's weighted average nominal interest rate on government debt, by projection year, used as the source for the hot un-adapted scenario's interest rate path.

    Returns:
        A series of the weighted average nominal interest rate by projection year under the hot un-adapted climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_rate[time_period])

    return data.HOT_UNADAPTED_ENGINE_WEIGHTED_INTEREST_RATE.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_WEIGHTED_INTEREST_RATE.required))

@publish(data.HOT_UNADAPTED_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.schema, cells=data.HOT_UNADAPTED_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.cells)
def hot_unadapted_engine_interest_expenditure_pct_revenue(*, hot_unadapted_engine_revenue_lcu: data.Series[float | str | None], hot_unadapted_engine_interest_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute interest expenditure as a share of revenue under the hot un-adapted climate scenario.

    Expresses interest expenditure relative to the revenue base, in percent, when countries adapt to higher temperatures only slowly.

    Args:
        hot_unadapted_engine_revenue_lcu: Government revenue, in billions of local currency units, under the hot un-adapted scenario.
        hot_unadapted_engine_interest_expenditure_lcu: Government interest expenditure, in billions of local currency units, under the hot un-adapted scenario.

    Returns:
        Interest expenditure as a percentage of revenue for each period of the hot un-adapted scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(hot_unadapted_engine_interest_expenditure_lcu[time_period], hot_unadapted_engine_revenue_lcu[time_period]), 100))

    return data.HOT_UNADAPTED_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_INTEREST_EXPENDITURE_PCT_REVENUE.required))

@publish(data.HOT_UNADAPTED_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.schema, cells=data.HOT_UNADAPTED_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.cells)
def hot_unadapted_engine_discrete_risk_revenue_shock(*, discrete_revenue_shocks: data.DiscreteRevenueShocks) -> data.Series[float | str | None]:
    """Build the discrete risk revenue shock series for the hot un-adapted climate scenario.

    Extract the user-registered discrete revenue shock impacts for each projection year under the hot un-adapted scenario, where countries adapt to higher temperatures over 50 years rather than 30.

    Args:
        discrete_revenue_shocks: Discrete fiscal risk revenue shock inputs registered by scenario and year, expressed as a percentage of GDP, from which the 'Hot unadapted' series is selected.

    Returns:
        A time-indexed series of discrete revenue shock values, as a percentage of GDP, for the hot un-adapted climate scenario.
    """
    data.DISCRETE_REVENUE_SHOCKS.schema.validate(discrete_revenue_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_revenue_shocks['Hot unadapted', time_period])

    return data.HOT_UNADAPTED_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_DISCRETE_RISK_REVENUE_SHOCK.required))

@publish(data.HOT_UNADAPTED_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.schema, cells=data.HOT_UNADAPTED_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.cells)
def hot_unadapted_engine_discrete_risk_expenditure_shock(*, discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks) -> data.Series[float | str | None]:
    """Project discrete primary expenditure shocks for the Hot Un-Adapted climate scenario.

    Selects the discrete risk expenditure shock series specific to the Hot Un-Adapted scenario so materialized fiscal risks raise primary expenditure under that scenario.

    Args:
        discrete_primary_expenditure_shocks: Discrete primary expenditure shocks entered as a share of GDP by scenario and time period, from which the Hot Un-Adapted scenario series is taken.

    Returns:
        A series of discrete primary expenditure shock values, as a share of GDP, for the Hot Un-Adapted climate scenario over the projection horizon.
    """
    data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.schema.validate(discrete_primary_expenditure_shocks)
    def formula(time_period: int) -> float | str | None:
        return as_measure(discrete_primary_expenditure_shocks['Hot unadapted', time_period])

    return data.HOT_UNADAPTED_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_DISCRETE_RISK_EXPENDITURE_SHOCK.required))

@publish(data.HOT_UNADAPTED_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.schema, cells=data.HOT_UNADAPTED_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.cells)
def hot_unadapted_engine_memo_interest_expenditure_pct_gdp(*, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp) -> data.Series[float | str | None]:
    """Return the interest-expenditure-to-GDP memo series under the Hot Un-Adapted scenario.

    Copies the baseline interest expenditure path into the Hot Un-Adapted climate scenario's engine memo, where countries adapt to higher temperatures over 50 years rather than 30 and so face the most severe macro-fiscal effects of the climate scenarios.

    Args:
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure as a percentage of nominal GDP, by time period, carried into the Hot Un-Adapted engine memo unchanged.

    Returns:
        The Hot Un-Adapted scenario engine memo series of interest expenditure as a percentage of nominal GDP, indexed by time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_expenditure_pct_gdp[time_period])

    return data.HOT_UNADAPTED_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_MEMO_INTEREST_EXPENDITURE_PCT_GDP.required))

@publish(data.HOT_UNADAPTED_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.schema, cells=data.HOT_UNADAPTED_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.cells)
def hot_unadapted_engine_memo_primary_expenditure_pct_gdp(*, baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp) -> data.Series[float | str | None]:
    """Compute the hot un-adapted engine memo for primary expenditure as a share of GDP.

    Produces the hot un-adapted scenario memo series of primary expenditure-to-GDP, carried over unchanged from the baseline under the rigid expenditure assumption.

    Args:
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure as a percent of GDP, before any climate change effects; primary expenditure excludes government interest payments and is assumed rigid in the hot un-adapted scenario, so its GDP ratio is unchanged from the baseline.

    Returns:
        A series of primary expenditure-to-GDP values for the hot un-adapted engine memo, indexed by time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_expenditure_pct_gdp[time_period])

    return data.HOT_UNADAPTED_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_MEMO_PRIMARY_EXPENDITURE_PCT_GDP.required))

@publish(data.HOT_UNADAPTED_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.schema, cells=data.HOT_UNADAPTED_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.cells)
def hot_unadapted_engine_memo_primary_balance_pct_gdp(*, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Return the baseline primary balance series re-labelled as the Hot Un-Adapted engine memo.

    Supplies the baseline primary-balance-to-GDP path as an input to the Hot Un-Adapted scenario, in which countries adapt to higher temperatures over 50 years rather than 30 and the macroeconomic effects are therefore more severe than in the Hot scenario.

    Args:
        baseline_primary_balance_pct_gdp: Baseline primary balance, in percent of nominal GDP, for each year of the projection horizon; this is the 'no policy change' path in which revenue stays constant relative to GDP and primary expenditure grows with productivity, inflation, and total population.

    Returns:
        A series of the baseline primary balance (percent of GDP) mapped onto the Hot Un-Adapted engine memo coordinate, with one value per projected time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_balance_pct_gdp[time_period])

    return data.HOT_UNADAPTED_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_MEMO_PRIMARY_BALANCE_PCT_GDP.required))

@publish(data.HOT_UNADAPTED_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.schema, cells=data.HOT_UNADAPTED_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.cells)
def hot_unadapted_engine_memo_overall_balance_pct_gdp(*, baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Project the overall balance under the hot un-adapted climate scenario.

    Supplies the hot un-adapted engine memo series for the overall balance as a share of GDP, carrying the baseline overall balance forward over the projection horizon.

    Args:
        baseline_overall_balance_pct_gdp: Baseline overall balance expressed as a percent of GDP for each time period, used unchanged as the memo value under the hot un-adapted scenario.

    Returns:
        Series of overall balance values as a percent of GDP for the hot un-adapted scenario, indexed by time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_overall_balance_pct_gdp[time_period])

    return data.HOT_UNADAPTED_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_MEMO_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.HOT_UNADAPTED_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.schema, cells=data.HOT_UNADAPTED_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.cells)
def hot_unadapted_engine_memo_gross_debt_pct_gdp(*, baseline_debt_to_gdp: data.BaselineDebtToGdp) -> data.Series[float | str | None]:
    """Report baseline gross debt-to-GDP ratios for the hot un-adapted memo series.

    Provide the baseline gross government debt-to-GDP trajectory as a memo series for the hot un-adapted climate scenario, which applies the same temperature increases as the hot scenario but assumes countries adapt to climate change very slowly.

    Args:
        baseline_debt_to_gdp: Baseline gross debt-to-GDP trajectory, projected to 2099, reported as a share of nominal GDP before any climate change scenario adjustments.

    Returns:
        Series of baseline gross debt-to-GDP values, as a percent of GDP, for each year in the hot un-adapted memo horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_to_gdp[time_period])

    return data.HOT_UNADAPTED_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_MEMO_GROSS_DEBT_PCT_GDP.required))

@publish(data.HOT_UNADAPTED_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.schema, cells=data.HOT_UNADAPTED_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.cells)
def hot_unadapted_engine_baseline_primary_expenditure_lcu(*, baseline_engine_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Return the baseline primary expenditure path in local currency units for the hot un-adapted climate scenario.

    The hot un-adapted scenario applies the same temperature increases as the hot scenario but assumes countries adapt to climate change far more slowly, so primary expenditure is carried over from the baseline (in local currency terms) rather than being adjusted for slower nominal GDP growth.

    Args:
        baseline_engine_primary_expenditure_lcu: Baseline primary expenditure, in billions of local currency units and excluding government interest payments, indexed by projection year.

    Returns:
        A series of baseline primary expenditure values in local currency units, indexed by projection year, to be used unchanged in the hot un-adapted climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_engine_primary_expenditure_lcu[time_period])

    return data.HOT_UNADAPTED_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_BASELINE_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.HOT_UNADAPTED_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.schema, cells=data.HOT_UNADAPTED_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.cells)
def hot_unadapted_engine_primary_expenditure_baseline_share_lcu(*, hot_unadapted_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_unadapted_engine_memo_primary_expenditure_pct_gdp: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute baseline primary expenditure in local currency units for the hot un-adapted scenario.

    Express the baseline primary expenditure share of GDP as a level in local currency units under the hot un-adapted scenario.

    Args:
        hot_unadapted_engine_nominal_gdp_lcu: Nominal GDP in local currency units under the hot un-adapted scenario, used to scale the expenditure share into a level.
        hot_unadapted_engine_memo_primary_expenditure_pct_gdp: Baseline primary expenditure expressed as a percent of nominal GDP under the hot un-adapted scenario.

    Returns:
        Primary expenditure baseline share in local currency units for the hot un-adapted scenario, indexed by time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(hot_unadapted_engine_memo_primary_expenditure_pct_gdp[time_period], 100), hot_unadapted_engine_nominal_gdp_lcu[time_period]))

    return data.HOT_UNADAPTED_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_PRIMARY_EXPENDITURE_BASELINE_SHARE_LCU.required))

@publish(data.HOT_UNADAPTED_ENGINE_RECALIBRATION_LCU.schema, cells=data.HOT_UNADAPTED_ENGINE_RECALIBRATION_LCU.cells)
def hot_unadapted_engine_recalibration_lcu(*, hot_unadapted_engine_baseline_primary_expenditure_lcu: data.Series[float | str | None], hot_unadapted_engine_primary_expenditure_baseline_share_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Subtract the baseline primary expenditure share from the baseline primary expenditure level.

    Recalibrate the Hot Un-Adapted scenario's baseline primary expenditure in local currency units by netting off its baseline share, thereby avoiding double counting.

    Args:
        hot_unadapted_engine_baseline_primary_expenditure_lcu: Baseline primary expenditure, in local currency units, for the Hot Un-Adapted climate scenario (where the economy adapts very slowly to temperature increases).
        hot_unadapted_engine_primary_expenditure_baseline_share_lcu: Portion of the Hot Un-Adapted scenario's baseline primary expenditure, in local currency units, attributable to the baseline share that must be removed from the primary expenditure level.

    Returns:
        Recalibrated Hot Un-Adapted baseline primary expenditure, in local currency units, after netting off the baseline share.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(hot_unadapted_engine_baseline_primary_expenditure_lcu[time_period], hot_unadapted_engine_primary_expenditure_baseline_share_lcu[time_period]))

    return data.HOT_UNADAPTED_ENGINE_RECALIBRATION_LCU.collect(evaluate(formula, data.HOT_UNADAPTED_ENGINE_RECALIBRATION_LCU.required))

@dataclass(frozen=True, slots=True)
class ScanHotUnadaptedEngineTotalExpenditurePctGdpResult:
    """Complete named results of one recurrence group evaluation."""
    hot_unadapted_engine_total_expenditure_pct_gdp: data.Series[float | str | None]
    hot_unadapted_engine_primary_balance_pct_gdp: data.Series[float | str | None]
    hot_unadapted_engine_total_expenditure_lcu: data.Series[float | str | None]
    hot_unadapted_engine_interest_expenditure_lcu: data.Series[float | str | None]
    hot_unadapted_engine_gross_debt_lcu: data.Series[float | str | None]
    hot_unadapted_engine_gross_debt_pct_gdp: data.Series[float | str | None]
    scenario_primary_expenditure_pct_gdp_hot_unadapted: data.ScenarioPrimaryExpenditurePctGdpHotUnadapted
    scenario_interest_expenditure_pct_gdp_hot_unadapted: data.ScenarioInterestExpenditurePctGdpHotUnadapted

def scan_hot_unadapted_engine_total_expenditure_pct_gdp(*, baseline_engine_total_expenditure_pct_gdp: data.Series[float | str | None], baseline_engine_total_expenditure_lcu: data.Series[float | str | None], baseline_engine_interest_expenditure_lcu: data.Series[float | str | None], baseline_engine_gross_debt_lcu: data.Series[float | str | None], hot_unadapted_engine_nominal_gdp_lcu: data.Series[float | str | None], hot_unadapted_engine_revenue_pct_gdp: data.Series[float | str | None], hot_unadapted_engine_primary_expenditure_lcu: data.Series[float | str | None], hot_unadapted_engine_weighted_interest_rate: data.Series[float | str | None], baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp, baseline_debt_to_gdp: data.BaselineDebtToGdp, scenario_nominal_gdp_growth_hot_unadapted: data.ScenarioNominalGdpGrowthHotUnadapted) -> ScanHotUnadaptedEngineTotalExpenditurePctGdpResult:
    """Evaluate the Hot Un-Adapted scenario total expenditure recurrence group.

    Compute the Hot Un-Adapted scenario total expenditure (as a share of GDP) and its dependent fiscal aggregates.

    Args:
        baseline_engine_total_expenditure_pct_gdp: Baseline government total expenditure as a percent of nominal GDP.
        baseline_engine_total_expenditure_lcu: Baseline government total expenditure in local currency units.
        baseline_engine_interest_expenditure_lcu: Baseline government interest expenditure in local currency units.
        baseline_engine_gross_debt_lcu: Baseline gross government debt in local currency units.
        hot_unadapted_engine_nominal_gdp_lcu: Hot Un-Adapted scenario nominal GDP in local currency units.
        hot_unadapted_engine_revenue_pct_gdp: Hot Un-Adapted scenario government revenue as a percent of nominal GDP.
        hot_unadapted_engine_primary_expenditure_lcu: Hot Un-Adapted scenario primary expenditure in local currency units.
        hot_unadapted_engine_weighted_interest_rate: Hot Un-Adapted scenario weighted average nominal interest rate on government debt.
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure as a percent of nominal GDP.
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure as a percent of nominal GDP.
        baseline_primary_balance_pct_gdp: Baseline primary balance as a percent of nominal GDP.
        baseline_debt_to_gdp: Baseline gross government debt-to-GDP ratio.
        scenario_nominal_gdp_growth_hot_unadapted: Hot Un-Adapted scenario nominal GDP growth rate.

    Returns:
        A result containing the Hot Un-Adapted scenario total expenditure percentage of GDP together with primary balance, total expenditure, interest expenditure, and gross debt in local currency units, gross debt as a percent of GDP, and primary and interest expenditure as a percent of GDP.
    """
    def hot_unadapted_engine_total_expenditure_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(hot_unadapted_engine_total_expenditure_lcu[time_period], hot_unadapted_engine_nominal_gdp_lcu[time_period]), 100))

    hot_unadapted_engine_total_expenditure_pct_gdp = CoordinateReader('hot_unadapted_engine_total_expenditure_pct_gdp', data.HOT_UNADAPTED_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required, hot_unadapted_engine_total_expenditure_pct_gdp_formula)
    def hot_unadapted_engine_primary_balance_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_balance_pct_gdp[time_period])
        return as_measure(xl_sub(hot_unadapted_engine_revenue_pct_gdp[time_period], scenario_primary_expenditure_pct_gdp_hot_unadapted[time_period]))

    hot_unadapted_engine_primary_balance_pct_gdp = CoordinateReader('hot_unadapted_engine_primary_balance_pct_gdp', data.HOT_UNADAPTED_ENGINE_PRIMARY_BALANCE_PCT_GDP.required, hot_unadapted_engine_primary_balance_pct_gdp_formula)
    def hot_unadapted_engine_total_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_total_expenditure_lcu[time_period])
        return as_measure(xl_add(hot_unadapted_engine_interest_expenditure_lcu[time_period], hot_unadapted_engine_primary_expenditure_lcu[time_period]))

    hot_unadapted_engine_total_expenditure_lcu = CoordinateReader('hot_unadapted_engine_total_expenditure_lcu', data.HOT_UNADAPTED_ENGINE_TOTAL_EXPENDITURE_LCU.required, hot_unadapted_engine_total_expenditure_lcu_formula)
    def hot_unadapted_engine_interest_expenditure_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_interest_expenditure_lcu[time_period])
        return as_measure(xl_mul(xl_div(hot_unadapted_engine_weighted_interest_rate[time_period], 100), hot_unadapted_engine_gross_debt_lcu[time_period - 1]))

    hot_unadapted_engine_interest_expenditure_lcu = CoordinateReader('hot_unadapted_engine_interest_expenditure_lcu', data.HOT_UNADAPTED_ENGINE_INTEREST_EXPENDITURE_LCU.required, hot_unadapted_engine_interest_expenditure_lcu_formula)
    def hot_unadapted_engine_gross_debt_lcu_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_gross_debt_lcu[time_period])
        return as_measure(xl_mul(xl_div(hot_unadapted_engine_gross_debt_pct_gdp[time_period], 100), hot_unadapted_engine_nominal_gdp_lcu[time_period]))

    hot_unadapted_engine_gross_debt_lcu = CoordinateReader('hot_unadapted_engine_gross_debt_lcu', data.HOT_UNADAPTED_ENGINE_GROSS_DEBT_LCU.required, hot_unadapted_engine_gross_debt_lcu_formula)
    def hot_unadapted_engine_gross_debt_pct_gdp_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_debt_to_gdp[time_period])
        return as_measure(xl_sub(xl_div(xl_mul(hot_unadapted_engine_gross_debt_pct_gdp[time_period - 1], xl_add(1, xl_div(hot_unadapted_engine_weighted_interest_rate[time_period], 100))), xl_add(1, xl_div(scenario_nominal_gdp_growth_hot_unadapted[time_period], 100))), hot_unadapted_engine_primary_balance_pct_gdp[time_period]))

    hot_unadapted_engine_gross_debt_pct_gdp = CoordinateReader('hot_unadapted_engine_gross_debt_pct_gdp', data.HOT_UNADAPTED_ENGINE_GROSS_DEBT_PCT_GDP.required, hot_unadapted_engine_gross_debt_pct_gdp_formula)
    def scenario_primary_expenditure_pct_gdp_hot_unadapted_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_primary_expenditure_pct_gdp[time_period])
        return as_measure(xl_sub(hot_unadapted_engine_total_expenditure_pct_gdp[time_period], scenario_interest_expenditure_pct_gdp_hot_unadapted[time_period]))

    scenario_primary_expenditure_pct_gdp_hot_unadapted = CoordinateReader('scenario_primary_expenditure_pct_gdp_hot_unadapted', data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.required, scenario_primary_expenditure_pct_gdp_hot_unadapted_formula)
    def scenario_interest_expenditure_pct_gdp_hot_unadapted_formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_interest_expenditure_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(hot_unadapted_engine_interest_expenditure_lcu[time_period], hot_unadapted_engine_nominal_gdp_lcu[time_period]), 100))

    scenario_interest_expenditure_pct_gdp_hot_unadapted = CoordinateReader('scenario_interest_expenditure_pct_gdp_hot_unadapted', data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.required, scenario_interest_expenditure_pct_gdp_hot_unadapted_formula)
    return ScanHotUnadaptedEngineTotalExpenditurePctGdpResult(
        hot_unadapted_engine_total_expenditure_pct_gdp=data.HOT_UNADAPTED_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.collect((coord, hot_unadapted_engine_total_expenditure_pct_gdp[coord]) for coord in data.HOT_UNADAPTED_ENGINE_TOTAL_EXPENDITURE_PCT_GDP.required),
        hot_unadapted_engine_primary_balance_pct_gdp=data.HOT_UNADAPTED_ENGINE_PRIMARY_BALANCE_PCT_GDP.collect((coord, hot_unadapted_engine_primary_balance_pct_gdp[coord]) for coord in data.HOT_UNADAPTED_ENGINE_PRIMARY_BALANCE_PCT_GDP.required),
        hot_unadapted_engine_total_expenditure_lcu=data.HOT_UNADAPTED_ENGINE_TOTAL_EXPENDITURE_LCU.collect((coord, hot_unadapted_engine_total_expenditure_lcu[coord]) for coord in data.HOT_UNADAPTED_ENGINE_TOTAL_EXPENDITURE_LCU.required),
        hot_unadapted_engine_interest_expenditure_lcu=data.HOT_UNADAPTED_ENGINE_INTEREST_EXPENDITURE_LCU.collect((coord, hot_unadapted_engine_interest_expenditure_lcu[coord]) for coord in data.HOT_UNADAPTED_ENGINE_INTEREST_EXPENDITURE_LCU.required),
        hot_unadapted_engine_gross_debt_lcu=data.HOT_UNADAPTED_ENGINE_GROSS_DEBT_LCU.collect((coord, hot_unadapted_engine_gross_debt_lcu[coord]) for coord in data.HOT_UNADAPTED_ENGINE_GROSS_DEBT_LCU.required),
        hot_unadapted_engine_gross_debt_pct_gdp=data.HOT_UNADAPTED_ENGINE_GROSS_DEBT_PCT_GDP.collect((coord, hot_unadapted_engine_gross_debt_pct_gdp[coord]) for coord in data.HOT_UNADAPTED_ENGINE_GROSS_DEBT_PCT_GDP.required),
        scenario_primary_expenditure_pct_gdp_hot_unadapted=data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.collect((coord, scenario_primary_expenditure_pct_gdp_hot_unadapted[coord]) for coord in data.SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.required),
        scenario_interest_expenditure_pct_gdp_hot_unadapted=data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.collect((coord, scenario_interest_expenditure_pct_gdp_hot_unadapted[coord]) for coord in data.SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_UNADAPTED.required),
    )

@publish(data.OUTPUT_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP_SUMMARY.schema, cells=data.OUTPUT_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP_SUMMARY.cells)
def output_baseline_primary_expenditure_pct_gdp_summary(*, output_baseline_primary_expenditure_pct_gdp_path: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Summarize the baseline primary expenditure-to-GDP path.

    Present the baseline primary expenditure-to-GDP ratio for reporting and for comparison with the climate scenarios.

    Args:
        output_baseline_primary_expenditure_pct_gdp_path: Baseline primary expenditure-to-GDP ratio by projection year, where primary expenditure excludes government interest payments and grows by productivity, inflation, and total population after the WEO horizon.

    Returns:
        A Series of the baseline primary expenditure-to-GDP ratio by year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_baseline_primary_expenditure_pct_gdp_path[time_period])

    return data.OUTPUT_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP_SUMMARY.collect(evaluate(formula, data.OUTPUT_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP_SUMMARY.required))

@publish(data.OUTPUT_BASELINE_INTEREST_EXPENDITURE_PCT_GDP_SUMMARY.schema, cells=data.OUTPUT_BASELINE_INTEREST_EXPENDITURE_PCT_GDP_SUMMARY.cells)
def output_baseline_interest_expenditure_pct_gdp_summary(*, output_baseline_interest_expenditure_pct_gdp_path: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Summarize baseline interest expenditure as a share of GDP.

    Produce the baseline interest-expenditure-to-GDP ratio series used in the debt dynamics and fiscal sustainability diagnostics.

    Args:
        output_baseline_interest_expenditure_pct_gdp_path: Baseline path of interest expenditure expressed as a percentage of nominal GDP, indexed by projection year.

    Returns:
        A series of baseline interest expenditure as a share of GDP, aligned to the summary output's required coordinates.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_baseline_interest_expenditure_pct_gdp_path[time_period])

    return data.OUTPUT_BASELINE_INTEREST_EXPENDITURE_PCT_GDP_SUMMARY.collect(evaluate(formula, data.OUTPUT_BASELINE_INTEREST_EXPENDITURE_PCT_GDP_SUMMARY.required))

@publish(data.OUTPUT_BASELINE_INTEREST_RATE_SUMMARY.schema, cells=data.OUTPUT_BASELINE_INTEREST_RATE_SUMMARY.cells)
def output_baseline_interest_rate_summary(*, output_baseline_interest_rate_path: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Summarize the baseline nominal interest rate path.

    Produce the baseline interest rate summary series used in the interest-growth differential and debt dynamics calculations.

    Args:
        output_baseline_interest_rate_path: Baseline profile of the weighted average nominal interest rate on government debt, expressed in percent.

    Returns:
        Interest rate summary series aligned to the required output baseline periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_baseline_interest_rate_path[time_period])

    return data.OUTPUT_BASELINE_INTEREST_RATE_SUMMARY.collect(evaluate(formula, data.OUTPUT_BASELINE_INTEREST_RATE_SUMMARY.required))

@publish(data.OUTPUT_BASELINE_PRIMARY_BALANCE_PCT_GDP_SUMMARY.schema, cells=data.OUTPUT_BASELINE_PRIMARY_BALANCE_PCT_GDP_SUMMARY.cells)
def output_baseline_primary_balance_pct_gdp_summary(*, output_baseline_primary_balance_pct_gdp_path: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Summarize the baseline primary balance-to-GDP path.

    Produce the summary series of the baseline primary balance expressed as a percentage of nominal GDP, passed through unchanged from the underlying baseline path.

    Args:
        output_baseline_primary_balance_pct_gdp_path: Baseline primary balance as a percent of nominal GDP, projected to 2099 under the no-policy-change assumptions of the baseline scenario.

    Returns:
        A series holding the baseline primary balance as a percent of nominal GDP for each projected period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_baseline_primary_balance_pct_gdp_path[time_period])

    return data.OUTPUT_BASELINE_PRIMARY_BALANCE_PCT_GDP_SUMMARY.collect(evaluate(formula, data.OUTPUT_BASELINE_PRIMARY_BALANCE_PCT_GDP_SUMMARY.required))

@publish(data.OUTPUT_BASELINE_OVERALL_BALANCE_PCT_GDP_SUMMARY.schema, cells=data.OUTPUT_BASELINE_OVERALL_BALANCE_PCT_GDP_SUMMARY.cells)
def output_baseline_overall_balance_pct_gdp_summary(*, output_baseline_overall_balance_pct_gdp_path: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Summarize the baseline overall balance as a share of GDP.

    Convert the baseline overall balance path into the summary measure of the overall balance-to-GDP ratio used for baseline reporting.

    Args:
        output_baseline_overall_balance_pct_gdp_path: Baseline overall balance expressed as a percentage of nominal GDP by time period.

    Returns:
        The overall balance-to-GDP summary series for the baseline scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_baseline_overall_balance_pct_gdp_path[time_period])

    return data.OUTPUT_BASELINE_OVERALL_BALANCE_PCT_GDP_SUMMARY.collect(evaluate(formula, data.OUTPUT_BASELINE_OVERALL_BALANCE_PCT_GDP_SUMMARY.required))

@publish(data.OUTPUT_BASELINE_DEBT_TO_GDP_SUMMARY.schema, cells=data.OUTPUT_BASELINE_DEBT_TO_GDP_SUMMARY.cells)
def output_baseline_debt_to_gdp_summary(*, output_baseline_debt_to_gdp_path: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Summarize the baseline debt-to-GDP path as a measure series.

    Present the projected baseline debt-to-GDP ratio, generated by the Q-CRAFT debt dynamics equation, as a measure series for downstream summary output.

    Args:
        output_baseline_debt_to_gdp_path: Baseline debt-to-GDP path series, giving the projected gross general government debt-to-GDP ratio for each year of the projection horizon under the user's baseline assumptions.

    Returns:
        Series aligned with the baseline debt-to-GDP summary coordinate, containing the baseline debt-to-GDP ratio as a measure value for each required time period, where the underlying path is unavailable or not numeric.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_baseline_debt_to_gdp_path[time_period])

    return data.OUTPUT_BASELINE_DEBT_TO_GDP_SUMMARY.collect(evaluate(formula, data.OUTPUT_BASELINE_DEBT_TO_GDP_SUMMARY.required))

@publish(data.OUTPUT_BASELINE_DSPB_MILESTONES_PB.schema, cells=data.OUTPUT_BASELINE_DSPB_MILESTONES_PB.cells)
def output_baseline_dspb_milestones_pb(*, output_baseline_primary_balance_pct_gdp_summary: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Extract baseline primary balance milestones at the 2023 and 2050 PB / PB* / PB Gap reference years.

    Reshape the baseline primary-balance-to-GDP summary into the standard milestone layout used for PB, debt-stabilizing PB, and PB Gap comparison.

    Args:
        output_baseline_primary_balance_pct_gdp_summary: Baseline primary balance (in percent of nominal GDP) keyed by year; supplies the values reindexed onto the 2023 and 2050 milestone years.

    Returns:
        A series of baseline primary balance milestone values aligned to the PB / PB* / PB Gap milestone labels at 2023 and 2050.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_baseline_primary_balance_pct_gdp_summary[time_period])

    return data.OUTPUT_BASELINE_DSPB_MILESTONES_PB.collect(evaluate(formula, data.OUTPUT_BASELINE_DSPB_MILESTONES_PB.required))

@publish(data.OUTPUT_BASELINE_DSPB_MILESTONES_PB_STAR.schema, cells=data.OUTPUT_BASELINE_DSPB_MILESTONES_PB_STAR.cells)
def output_baseline_dspb_milestones_pb_star(*, baseline_debt_stabilizing_primary_balance: data.BaselineDebtStabilizingPrimaryBalance) -> data.Series[float | str | None]:
    """Extract the debt-stabilizing primary balance (PB*) at the headline milestone years 2023 and 2050.

    Provide the debt-stabilizing primary balance at the PB/PB*/PB Gap milestone years so users can gauge the fiscal effort needed to stabilize debt relative to GDP.

    Args:
        baseline_debt_stabilizing_primary_balance: Baseline debt-stabilizing primary balance, expressed as a share of nominal GDP, from which the 2023 and 2050 milestone values are taken.

    Returns:
        Series of PB* milestone values for 2023 and 2050, as a share of nominal GDP.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_stabilizing_primary_balance[time_period])

    return data.OUTPUT_BASELINE_DSPB_MILESTONES_PB_STAR.collect(evaluate(formula, data.OUTPUT_BASELINE_DSPB_MILESTONES_PB_STAR.required))

@publish(data.OUTPUT_BASELINE_DSPB_MILESTONES_PB_GAP.schema, cells=data.OUTPUT_BASELINE_DSPB_MILESTONES_PB_GAP.cells)
def output_baseline_dspb_milestones_pb_gap(*, output_baseline_dspb_milestones_pb: data.Series[float | str | None], output_baseline_dspb_milestones_pb_star: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the PB Gap series as the difference between the debt-stabilizing primary balance and the projected primary balance at each milestone year.

    Quantifies, at the 2023 and 2050 PB / PB* / PB Gap milestones, the fiscal adjustment needed to stabilize debt relative to GDP.

    Args:
        output_baseline_dspb_milestones_pb: Projected primary balance for each milestone year, expressed in percent of nominal GDP.
        output_baseline_dspb_milestones_pb_star: Debt-stabilizing primary balance for each milestone year, expressed in percent of nominal GDP, consistent with a stable debt-to-GDP ratio.

    Returns:
        A series containing the PB Gap for each milestone year, equal to the debt-stabilizing primary balance minus the projected primary balance; a positive value indicates required fiscal consolidation, while a negative value indicates available fiscal space.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(output_baseline_dspb_milestones_pb_star[time_period], output_baseline_dspb_milestones_pb[time_period]))

    return data.OUTPUT_BASELINE_DSPB_MILESTONES_PB_GAP.collect(evaluate(formula, data.OUTPUT_BASELINE_DSPB_MILESTONES_PB_GAP.required))

@publish(data.OUTPUT_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP_PATH.schema, cells=data.OUTPUT_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP_PATH.cells)
def output_baseline_primary_expenditure_pct_gdp_path(*, baseline_primary_expenditure_pct_gdp: data.BaselinePrimaryExpenditurePctGdp) -> data.Series[float | str | None]:
    """Build the baseline primary expenditure-to-GDP path as an annual series.

    Mirrors the Baseline engine path of primary expenditure as a share of nominal GDP, with only the summary anchor columns (2023, 2050, 2075, and 2099) shown on the graph.

    Args:
        baseline_primary_expenditure_pct_gdp: Baseline primary expenditure as a percent of nominal GDP, keyed by time period, where primary expenditure excludes government interest payments.

    Returns:
        A series of baseline primary expenditure-to-GDP values (or None where unavailable) indexed by time period to 2099.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_expenditure_pct_gdp[time_period])

    return data.OUTPUT_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP_PATH.collect(evaluate(formula, data.OUTPUT_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP_PATH.required))

@publish(data.OUTPUT_BASELINE_INTEREST_EXPENDITURE_PCT_GDP_PATH.schema, cells=data.OUTPUT_BASELINE_INTEREST_EXPENDITURE_PCT_GDP_PATH.cells)
def output_baseline_interest_expenditure_pct_gdp_path(*, baseline_interest_expenditure_pct_gdp: data.BaselineInterestExpenditurePctGdp) -> data.Series[float | str | None]:
    """Assemble the baseline interest expenditure path as a share of GDP.

    Provide the annual mirror of the Baseline engine path, whose summary anchor columns (2023, 2050, 2075, and 2099) are the only points shown on the graph.

    Args:
        baseline_interest_expenditure_pct_gdp: Baseline interest expenditure expressed as a share of nominal GDP, indexed by projection year.

    Returns:
        A series of interest expenditure-to-GDP values over the projection horizon, keyed by year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_expenditure_pct_gdp[time_period])

    return data.OUTPUT_BASELINE_INTEREST_EXPENDITURE_PCT_GDP_PATH.collect(evaluate(formula, data.OUTPUT_BASELINE_INTEREST_EXPENDITURE_PCT_GDP_PATH.required))

@publish(data.OUTPUT_BASELINE_INTEREST_RATE_PATH.schema, cells=data.OUTPUT_BASELINE_INTEREST_RATE_PATH.cells)
def output_baseline_interest_rate_path(*, baseline_interest_rate: data.BaselineInterestRate) -> data.Series[float | str | None]:
    """Project the baseline nominal interest rate path to 2099.

    Provide the annual baseline interest rate trajectory used to derive the interest-growth differential and debt dynamics in the baseline scenario.

    Args:
        baseline_interest_rate: Baseline nominal interest rate by year, mirroring the Baseline engine path; the graph displays only the 2023, 2050, 2075, and 2099 summary anchor columns.

    Returns:
        Annual baseline interest rate series through 2099, aligned to the baseline projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_interest_rate[time_period])

    return data.OUTPUT_BASELINE_INTEREST_RATE_PATH.collect(evaluate(formula, data.OUTPUT_BASELINE_INTEREST_RATE_PATH.required))

@publish(data.OUTPUT_BASELINE_PRIMARY_BALANCE_PCT_GDP_PATH.schema, cells=data.OUTPUT_BASELINE_PRIMARY_BALANCE_PCT_GDP_PATH.cells)
def output_baseline_primary_balance_pct_gdp_path(*, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Project the baseline primary balance as a percent of GDP onto the output series grid.

    Provide the annual baseline primary balance-to-GDP path mirroring the Baseline engine, so climate scenario comparisons have an unchanged-policy benchmark.

    Args:
        baseline_primary_balance_pct_gdp: Baseline primary balance (revenue less primary expenditure) expressed as a percent of nominal GDP for each projection year, reflecting the 'no policy change' assumption that revenue stays constant relative to GDP while primary expenditure grows with productivity, inflation, and total population.

    Returns:
        An output series of the baseline primary balance as a percent of GDP by year; graph-anchored summary columns cover 2023, 2050, 2075, and 2099.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_balance_pct_gdp[time_period])

    return data.OUTPUT_BASELINE_PRIMARY_BALANCE_PCT_GDP_PATH.collect(evaluate(formula, data.OUTPUT_BASELINE_PRIMARY_BALANCE_PCT_GDP_PATH.required))

@publish(data.OUTPUT_BASELINE_OVERALL_BALANCE_PCT_GDP_PATH.schema, cells=data.OUTPUT_BASELINE_OVERALL_BALANCE_PCT_GDP_PATH.cells)
def output_baseline_overall_balance_pct_gdp_path(*, baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Build the output series for the baseline overall balance-to-GDP path.

    Convert the annual baseline overall balance-to-GDP projection into the output series used by the baseline summary charts.

    Args:
        baseline_overall_balance_pct_gdp: Baseline overall balance as a percent of nominal GDP, projected annually to 2099; only the 2023, 2050, 2075, and 2099 summary anchor columns are plotted.

    Returns:
        An output series of overall balance-to-GDP values (in percent) for each projected year, with missing values preserved.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_overall_balance_pct_gdp[time_period])

    return data.OUTPUT_BASELINE_OVERALL_BALANCE_PCT_GDP_PATH.collect(evaluate(formula, data.OUTPUT_BASELINE_OVERALL_BALANCE_PCT_GDP_PATH.required))

@publish(data.OUTPUT_BASELINE_DEBT_TO_GDP_PATH.schema, cells=data.OUTPUT_BASELINE_DEBT_TO_GDP_PATH.cells)
def output_baseline_debt_to_gdp_path(*, baseline_debt_to_gdp: data.BaselineDebtToGdp) -> data.Series[float | str | None]:
    """Build the annual baseline debt-to-GDP path for the output baseline graph.

    Expose the baseline engine's debt-to-GDP trajectory in the annual form required by the output baseline worksheet, whose charts display only the 2023, 2050, 2075, and 2099 summary anchors.

    Args:
        baseline_debt_to_gdp: Baseline debt-to-GDP series from which each annual value of the output path is taken.

    Returns:
        Annual baseline debt-to-GDP series over the projection horizon, with each year's value drawn from the baseline path and expressed as a share of nominal GDP.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_to_gdp[time_period])

    return data.OUTPUT_BASELINE_DEBT_TO_GDP_PATH.collect(evaluate(formula, data.OUTPUT_BASELINE_DEBT_TO_GDP_PATH.required))

@publish(data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_BASELINE.schema, cells=data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_BASELINE.cells)
def output_scenarios_primary_balance_pct_gdp_summary_baseline(*, output_scenarios_primary_balance_pct_gdp_baseline_path: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Summarize the baseline primary balance as a share of GDP under the climate scenarios.

    Provide the headline baseline primary balance path used to contextualize the fiscal effects of climate change scenarios.

    Args:
        output_scenarios_primary_balance_pct_gdp_baseline_path: Baseline primary balance as a percent of nominal GDP for each projection year.

    Returns:
        The baseline primary balance as a percent of nominal GDP summarized over the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_scenarios_primary_balance_pct_gdp_baseline_path[time_period])

    return data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_BASELINE.collect(evaluate(formula, data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_BASELINE.required))

@publish(data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_PARIS.schema, cells=data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_PARIS.cells)
def output_scenarios_primary_balance_pct_gdp_summary_paris(*, scenario_primary_balance_pct_gdp: data.ScenarioPrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Summarize the primary balance (percent of GDP) under the Paris climate scenario.

    Provides the Paris-scenario primary balance-to-GDP summary for assessing how meeting the 2015 Paris Agreement commitments affects the fiscal outlook over the long term.

    Args:
        scenario_primary_balance_pct_gdp: Climate-scenario primary balance projections, expressed as a share of nominal GDP, from which the Paris scenario is selected.

    Returns:
        A series of primary balance-to-GDP values for the Paris scenario, indexed by projection year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_primary_balance_pct_gdp['Paris', time_period])

    return data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_PARIS.collect(evaluate(formula, data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_PARIS.required))

@publish(data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_MODERATE.schema, cells=data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_MODERATE.cells)
def output_scenarios_primary_balance_pct_gdp_summary_moderate(*, scenario_primary_balance_pct_gdp: data.ScenarioPrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Summarize the projected primary balance under the Moderate climate scenario.

    Provide the primary balance (as a share of GDP) projected each year under the SSP2-4.5 Moderate climate scenario, in which mitigation policies continue along the observed trend.

    Args:
        scenario_primary_balance_pct_gdp: Climate scenario primary balance projections, indexed by scenario and time period; the Moderate scenario series is selected.

    Returns:
        A series of the projected primary balance as a share of GDP for each year under the Moderate climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_primary_balance_pct_gdp['Moderate', time_period])

    return data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_MODERATE.collect(evaluate(formula, data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_MODERATE.required))

@publish(data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HIGH.schema, cells=data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HIGH.cells)
def output_scenarios_primary_balance_pct_gdp_summary_high(*, scenario_primary_balance_pct_gdp: data.ScenarioPrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Summarize the primary balance (percent of GDP) path under the High climate scenario.

    Produce a compact series of the High-scenario primary balance as a share of nominal GDP, supporting fiscal risk and debt dynamics analysis.

    Args:
        scenario_primary_balance_pct_gdp: Primary balance as a percent of GDP for each climate scenario; the High scenario path is extracted across the projection horizon through 2099.

    Returns:
        A series of the High-scenario primary balance (percent of GDP) by year, or None or a string label where a value is unavailable.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_primary_balance_pct_gdp['High', time_period])

    return data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HIGH.collect(evaluate(formula, data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HIGH.required))

@publish(data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT.schema, cells=data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT.cells)
def output_scenarios_primary_balance_pct_gdp_summary_hot(*, scenario_primary_balance_pct_gdp: data.ScenarioPrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Summarize the primary balance under the Hot climate scenario as a percent of GDP.

    Produce the Hot-scenario primary balance-to-GDP summary series for fiscal risk analysis.

    Args:
        scenario_primary_balance_pct_gdp: Primary balance as a percent of GDP under the climate change scenarios, indexed by scenario and time period.

    Returns:
        Series of primary balance-to-GDP values under the Hot scenario across the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_primary_balance_pct_gdp['Hot', time_period])

    return data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT.collect(evaluate(formula, data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT.required))

@publish(data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT_ADAPTED.schema, cells=data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT_ADAPTED.cells)
def output_scenarios_primary_balance_pct_gdp_summary_hot_adapted(*, scenario_primary_balance_pct_gdp: data.ScenarioPrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Summarize the primary balance as a share of GDP under the Hot adapted climate scenario.

    Provide the Hot adapted scenario's primary balance-to-GDP path for comparison with the baseline and other climate scenarios.

    Args:
        scenario_primary_balance_pct_gdp: Primary balance projections as a percentage of nominal GDP, indexed by climate scenario and year; the 'Hot adapted' scenario is selected from this collection.

    Returns:
        A series of primary balance values as a percentage of nominal GDP for the Hot adapted scenario across projection years.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_primary_balance_pct_gdp['Hot adapted', time_period])

    return data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT_ADAPTED.collect(evaluate(formula, data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT_ADAPTED.required))

@publish(data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT_UNADAPTED.schema, cells=data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT_UNADAPTED.cells)
def output_scenarios_primary_balance_pct_gdp_summary_hot_unadapted(*, scenario_primary_balance_pct_gdp: data.ScenarioPrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Summarize the primary balance-to-GDP ratio under the Hot Un-Adapted climate scenario.

    Produce the "Hot Un-Adapted" primary balance summary series so users can compare fiscal trajectories when countries adapt to higher temperatures very slowly.

    Args:
        scenario_primary_balance_pct_gdp: Scenario primary balance expressed as a percentage of nominal GDP, from which the "Hot unadapted" coordinate values are read across the projection horizon.

    Returns:
        A series of primary balance-to-GDP values (as percentages, or missing where unavailable) for the Hot Un-Adapted scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_primary_balance_pct_gdp['Hot unadapted', time_period])

    return data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT_UNADAPTED.collect(evaluate(formula, data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_SUMMARY_HOT_UNADAPTED.required))

@publish(data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_BASELINE.schema, cells=data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_BASELINE.cells)
def output_scenarios_debt_to_gdp_summary_baseline(*, output_scenarios_debt_to_gdp_baseline_path: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Summarize the baseline debt-to-GDP path for the climate scenarios output table.

    Produce the baseline debt-to-GDP summary series that the climate scenario outputs use as the comparison benchmark.

    Args:
        output_scenarios_debt_to_gdp_baseline_path: Baseline debt-to-GDP ratio path (in percent of nominal GDP) projected to 2099 under the baseline scenario, indexed by projection year.

    Returns:
        Debt-to-GDP summary series for the baseline scenario, aligned to the output table's projection years with the same values as the supplied baseline path.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_scenarios_debt_to_gdp_baseline_path[time_period])

    return data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_BASELINE.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_BASELINE.required))

@publish(data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_PARIS.schema, cells=data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_PARIS.cells)
def output_scenarios_debt_to_gdp_summary_paris(*, scenario_debt_to_gdp: data.ScenarioDebtToGdp) -> data.Series[float | str | None]:
    """Summarize the debt-to-GDP ratio under the Paris climate scenario.

    Produce the output summary of the projected debt-to-GDP ratio for the Paris scenario, in which 2015 Paris Agreement commitments are met and global warming stays below 2°C above pre-industrial levels by end of century.

    Args:
        scenario_debt_to_gdp: Projected debt-to-GDP ratios by climate scenario and time period, used here to read the Paris scenario series.

    Returns:
        A series of projected debt-to-GDP values for the Paris climate scenario across the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_to_gdp['Paris', time_period])

    return data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_PARIS.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_PARIS.required))

@publish(data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_MODERATE.schema, cells=data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_MODERATE.cells)
def output_scenarios_debt_to_gdp_summary_moderate(*, scenario_debt_to_gdp: data.ScenarioDebtToGdp) -> data.Series[float | str | None]:
    """Summarize the debt-to-GDP ratio under the Moderate climate scenario.

    Produce the output series of debt-to-GDP ratios projected under the Moderate climate scenario, in which emissions continue in line with present trends and stabilize at the end of the century.

    Args:
        scenario_debt_to_gdp: Scenario debt-to-GDP projections providing the Moderate scenario series to be summarized.

    Returns:
        A series of debt-to-GDP ratios, as values or labels, for the Moderate climate scenario at each projected time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_to_gdp['Moderate', time_period])

    return data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_MODERATE.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_MODERATE.required))

@publish(data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HIGH.schema, cells=data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HIGH.cells)
def output_scenarios_debt_to_gdp_summary_high(*, scenario_debt_to_gdp: data.ScenarioDebtToGdp) -> data.Series[float | str | None]:
    """Summarize the high climate scenario's debt-to-GDP path as a series.

    Extract the projected debt-to-GDP ratio under the high emissions climate scenario into a summary series for comparison against the baseline.

    Args:
        scenario_debt_to_gdp: Scenario debt-to-GDP projection keyed by climate scenario and projection year; the high climate scenario slice supplies the debt-to-GDP ratio for each year to 2099.

    Returns:
        A series of the debt-to-GDP ratio, by projection year, under the high climate scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_to_gdp['High', time_period])

    return data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HIGH.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HIGH.required))

@publish(data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT.schema, cells=data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT.cells)
def output_scenarios_debt_to_gdp_summary_hot(*, scenario_debt_to_gdp: data.ScenarioDebtToGdp) -> data.Series[float | str | None]:
    """Summarize the debt-to-GDP path under the Hot climate scenario.

    Extract the Hot scenario debt-to-GDP trajectory for reporting alongside the other climate scenarios.

    Args:
        scenario_debt_to_gdp: Debt-to-GDP projections by climate scenario, from which the Hot scenario path is selected.

    Returns:
        Series of debt-to-GDP values for the Hot climate scenario across the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_to_gdp['Hot', time_period])

    return data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT.required))

@publish(data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT_ADAPTED.schema, cells=data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT_ADAPTED.cells)
def output_scenarios_debt_to_gdp_summary_hot_adapted(*, scenario_debt_to_gdp: data.ScenarioDebtToGdp) -> data.Series[float | str | None]:
    """Build the debt-to-GDP summary series for the Hot adapted climate scenario.

    Extract the debt-to-GDP ratio trajectory under the Hot adapted scenario so it can be reported alongside the other Q-CRAFT climate scenarios.

    Args:
        scenario_debt_to_gdp: Debt-to-GDP ratio projections by climate scenario and projection year, covering the baseline and the Paris, Moderate, High, Hot, Hot adapted, and Hot un-adapted scenarios; the Hot adapted series is selected here.

    Returns:
        A debt-to-GDP ratio series for the Hot adapted scenario, indexed by projection year, giving gross government debt as a share of nominal GDP where the scenario projection is available.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_to_gdp['Hot adapted', time_period])

    return data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT_ADAPTED.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT_ADAPTED.required))

@publish(data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT_UNADAPTED.schema, cells=data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT_UNADAPTED.cells)
def output_scenarios_debt_to_gdp_summary_hot_unadapted(*, scenario_debt_to_gdp: data.ScenarioDebtToGdp) -> data.Series[float | str | None]:
    """Build the Hot Un-Adapted debt-to-GDP summary series for a climate scenario.

    Extracts the projected debt-to-GDP ratio under the Hot Un-Adapted climate change scenario, in which temperatures follow the Hot scenario but countries adapt more slowly.

    Args:
        scenario_debt_to_gdp: Scenario debt-to-GDP projections holding each climate scenario's debt-to-GDP ratio, including the 'Hot unadapted' scenario.

    Returns:
        A series of projected debt-to-GDP ratios under the Hot Un-Adapted climate scenario across the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_to_gdp['Hot unadapted', time_period])

    return data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT_UNADAPTED.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT_UNADAPTED.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB.cells)
def output_scenarios_dspb_milestones_baseline_pb(*, output_scenarios_primary_balance_pct_gdp_summary_baseline: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Extract baseline primary balance milestones for the DSPB chart.

    Selects the baseline primary-balance-to-GDP path at the 2023, 2050, 2075, and 2099 milestone years for the debt-stabilizing primary balance (DSPB) comparison.

    Args:
        output_scenarios_primary_balance_pct_gdp_summary_baseline: Baseline primary balance (percent of GDP) summary series, aligned to the output scenario time axis; milestones are drawn from the 2023, 2050, 2075, and 2099 periods.

    Returns:
        Series of baseline primary balance (percent of GDP) values at the 2023/2050/2075/2099 milestone periods, preserving any missing entries.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_scenarios_primary_balance_pct_gdp_summary_baseline[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB_STAR.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB_STAR.cells)
def output_scenarios_dspb_milestones_baseline_pb_star(*, baseline_debt_stabilizing_primary_balance: data.BaselineDebtStabilizingPrimaryBalance) -> data.Series[float | str | None]:
    """Extract baseline debt-stabilizing primary balance (PB*) milestones for the climate scenarios output.

    Report the baseline PB* at the 2023, 2050, 2075, and 2099 milestone years so the PB, PB*, and PB Gap milestones can be compared across scenarios.

    Args:
        baseline_debt_stabilizing_primary_balance: Baseline debt-stabilizing primary balance (PB*), the primary balance needed to keep the debt-to-GDP ratio stable, evaluated at each milestone year.

    Returns:
        Series of baseline PB* values at the 2023, 2050, 2075, and 2099 milestone years.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_stabilizing_primary_balance[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB_STAR.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB_STAR.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB_GAP.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB_GAP.cells)
def output_scenarios_dspb_milestones_baseline_pb_gap(*, output_scenarios_dspb_milestones_baseline_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_baseline_pb_star: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the PB Gap milestone series as PB* minus PB for each projection period.

    Quantifies the gap between the debt-stabilizing and projected primary balance milestones at 2023/2050/2075/2099 in the baseline scenario.

    Args:
        output_scenarios_dspb_milestones_baseline_pb: Baseline projected primary balance milestone series (in percent of GDP) by projection period.
        output_scenarios_dspb_milestones_baseline_pb_star: Baseline debt-stabilizing primary balance milestone series (in percent of GDP) by projection period.

    Returns:
        Series of PB Gap milestone values (PB* less PB), in percent of GDP, aligned to the projection periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(output_scenarios_dspb_milestones_baseline_pb_star[time_period], output_scenarios_dspb_milestones_baseline_pb[time_period]))

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB_GAP.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_BASELINE_PB_GAP.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_PARIS_PB.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_PARIS_PB.cells)
def output_scenarios_dspb_milestones_paris_pb(*, output_scenarios_primary_balance_pct_gdp_summary_paris: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Extract the Paris-scenario PB/PB* milestone values into the DSPB milestones output shard.

    Selects the primary balance (percent of GDP) milestone readings for the Paris climate scenario so the 2050, 2075, and 2099 PB / PB* milestones can be reported.

    Args:
        output_scenarios_primary_balance_pct_gdp_summary_paris: Summary series of the Paris scenario's primary balance (percent of GDP); values are picked at the required milestone periods and passed through unchanged.

    Returns:
        Series of Paris-scenario primary balance milestone values (percent of GDP) aligned with the required milestone label shards, with missing entries preserved as null.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_scenarios_primary_balance_pct_gdp_summary_paris[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_PARIS_PB.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_PARIS_PB.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_PARIS_PB_STAR.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_PARIS_PB_STAR.cells)
def output_scenarios_dspb_milestones_paris_pb_star(*, scenario_debt_stabilizing_primary_balance_paris: data.ScenarioDebtStabilizingPrimaryBalanceParis) -> data.Series[float | str | None]:
    """Extract Paris-scenario debt-stabilizing primary balance (PB*) milestone values through 2099.

    Provide the public PB Gap output shard holding PB / PB* milestones at 2050, 2075, and 2099 under the Paris climate scenario.

    Args:
        scenario_debt_stabilizing_primary_balance_paris: Paris-scenario debt-stabilizing primary balance series, keyed by time period, whose entries supply the PB / PB* milestone values at 2050, 2075, and 2099.

    Returns:
        A Series of milestone values (floats, or strings or None where a milestone is unavailable) for the Paris debt-stabilizing primary balance.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_stabilizing_primary_balance_paris[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_PARIS_PB_STAR.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_PARIS_PB_STAR.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_MODERATE_PB.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_MODERATE_PB.cells)
def output_scenarios_dspb_milestones_moderate_pb(*, output_scenarios_primary_balance_pct_gdp_summary_moderate: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Extract moderate-scenario PB/PB* milestone values at 2050, 2075, and 2099.

    Reduce the moderate-scenario primary balance summary series to the debt-stabilizing primary balance milestone years for climate risk reporting.

    Args:
        output_scenarios_primary_balance_pct_gdp_summary_moderate: Moderate climate scenario primary balance summary series (percent of GDP); the milestone years 2050, 2075, and 2099 are read from it.

    Returns:
        Series of primary balance values (percent of GDP) indexed to the moderate-scenario PB/PB* milestone years 2050, 2075, and 2099.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_scenarios_primary_balance_pct_gdp_summary_moderate[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_MODERATE_PB.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_MODERATE_PB.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_MODERATE_PB_STAR.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_MODERATE_PB_STAR.cells)
def output_scenarios_dspb_milestones_moderate_pb_star(*, scenario_debt_stabilizing_primary_balance_moderate: data.ScenarioDebtStabilizingPrimaryBalanceModerate) -> data.Series[float | str | None]:
    """Extract the moderate climate scenario's debt-stabilizing primary balance at the 2050, 2075, and 2099 milestones.

    Provides the debt-stabilizing primary balance (PB*) milestones under the moderate climate scenario as a public PB Gap output shard.

    Args:
        scenario_debt_stabilizing_primary_balance_moderate: Year-indexed debt-stabilizing primary balance for the moderate climate scenario, the necessary primary balance to keep debt stable relative to GDP.

    Returns:
        A series of the moderate scenario's debt-stabilizing primary balance values at the 2050, 2075, and 2099 milestones.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_stabilizing_primary_balance_moderate[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_MODERATE_PB_STAR.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_MODERATE_PB_STAR.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HIGH_PB.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HIGH_PB.cells)
def output_scenarios_dspb_milestones_high_pb(*, output_scenarios_primary_balance_pct_gdp_summary_high: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Build the high-scenario debt-stabilizing primary balance (DSPB) milestone series for 2050, 2075, and 2099.

    Provide the high climate scenario's DSPB-GDP milestones, the primary balance-to-GDP ratios needed to keep public debt stable at each horizon year.

    Args:
        output_scenarios_primary_balance_pct_gdp_summary_high: Primary balance as a percent of GDP for the high climate change scenario, summarized as a series indexed by time period.

    Returns:
        Series of DSPB-to-GDP values for the high climate scenario at the 2050, 2075, and 2099 milestone years, preserving any published constants and string entries.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_scenarios_primary_balance_pct_gdp_summary_high[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HIGH_PB.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HIGH_PB.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HIGH_PB_STAR.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HIGH_PB_STAR.cells)
def output_scenarios_dspb_milestones_high_pb_star(*, scenario_debt_stabilizing_primary_balance_high: data.ScenarioDebtStabilizingPrimaryBalanceHigh) -> data.Series[float | str | None]:
    """Emit the high PB-star milestone series for the debt-stabilizing primary balance scenario.

    Report the public PB Gap shard values for the debt-stabilizing primary balance scenario at the 2050, 2075, and 2099 milestones.

    Args:
        scenario_debt_stabilizing_primary_balance_high: High-scenario debt-stabilizing primary balance series whose values are projected onto the high PB-star milestone shard.

    Returns:
        Series of milestone values for the high debt-stabilizing primary balance scenario, indexed by the 2050, 2075, and 2099 horizon years.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_stabilizing_primary_balance_high[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HIGH_PB_STAR.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HIGH_PB_STAR.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_PB.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_PB.cells)
def output_scenarios_dspb_milestones_hot_pb(*, output_scenarios_primary_balance_pct_gdp_summary_hot: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Extract the 2050, 2075, and 2099 primary balance milestones under the Hot climate scenario.

    Provides the Hot-scenario primary balance (PB) milestone values used in the debt-stabilizing primary balance (DSPB) summary.

    Args:
        output_scenarios_primary_balance_pct_gdp_summary_hot: Primary balance as a percent of GDP under the Hot climate scenario, indexed by milestone year; values are carried into the milestone series.

    Returns:
        Series of primary balance percent-of-GDP values labeled by the mapped coordinate identities for the 2050, 2075, and 2099 milestones.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_scenarios_primary_balance_pct_gdp_summary_hot[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_PB.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_PB.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_PB_STAR.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_PB_STAR.cells)
def output_scenarios_dspb_milestones_hot_pb_star(*, scenario_debt_stabilizing_primary_balance_hot: data.ScenarioDebtStabilizingPrimaryBalanceHot) -> data.Series[float | str | None]:
    """Extract the debt-stabilizing primary balance (PB*) milestones under the Hot climate scenario.

    Assemble a milestone series of debt-stabilizing primary balances for the Hot scenario, reported as PB* markers at the 2050, 2075, and 2099 horizons.

    Args:
        scenario_debt_stabilizing_primary_balance_hot: Hot-scenario debt-stabilizing primary balance (PB*) values indexed by time period, providing the primary balance needed to keep the debt-to-GDP ratio stable in each year through 2099.

    Returns:
        A series of PB* milestone values under the Hot scenario for each milestone period (2050, 2075, and 2099), in the order defined by the output coordinate.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_stabilizing_primary_balance_hot[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_PB_STAR.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_PB_STAR.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_ADAPTED_PB.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_ADAPTED_PB.cells)
def output_scenarios_dspb_milestones_hot_adapted_pb(*, output_scenarios_primary_balance_pct_gdp_summary_hot_adapted: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Align the primary-balance summary of the hot-adapted scenario onto the debt-stabilizing primary balance milestone coordinates.

    Re-index the hot-adapted primary-balance-to-GDP summary so it can be reported alongside the 2050, 2075, and 2099 DSPB milestones.

    Args:
        output_scenarios_primary_balance_pct_gdp_summary_hot_adapted: Primary balance in percent of GDP under the hot-adapted climate change scenario, where countries adapt to higher temperatures over 20 years rather than 30; carries the values to be mapped onto the debt-stabilizing primary balance milestone coordinates used for reporting.

    Returns:
        A series of the hot-adapted primary balance, in percent of GDP, aligned to the debt-stabilizing primary balance milestone coordinates at 2050, 2075, and 2099.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_scenarios_primary_balance_pct_gdp_summary_hot_adapted[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_ADAPTED_PB.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_ADAPTED_PB.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_ADAPTED_PB_STAR.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_ADAPTED_PB_STAR.cells)
def output_scenarios_dspb_milestones_hot_adapted_pb_star(*, scenario_debt_stabilizing_primary_balance_hot_adapted: data.ScenarioDebtStabilizingPrimaryBalanceHotAdapted) -> data.Series[float | str | None]:
    """Collect the Hot Adapted scenario's debt-stabilizing primary balance (PB*) milestone series.

    Publishes the debt-stabilizing primary balance shard for the Hot Adapted climate scenario at the PB* milestone horizon years (2050, 2075, 2099).

    Args:
        scenario_debt_stabilizing_primary_balance_hot_adapted: Scenario debt-stabilizing primary balance for the Hot Adapted climate scenario, projected to 2099 with an adaptation horizon of 20 years rather than the 30-year default; supplies the value that stabilizes debt relative to GDP in each year and is reported as the PB* milestone series.

    Returns:
        Series of debt-stabilizing primary balance values for the Hot Adapted scenario at the PB* milestone years (2050, 2075, 2099), with constant reference shards retained and public PB Gap output shards carried through; entries are floats where computable and None or a string otherwise.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_stabilizing_primary_balance_hot_adapted[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_ADAPTED_PB_STAR.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_ADAPTED_PB_STAR.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_UNADAPTED_PB.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_UNADAPTED_PB.cells)
def output_scenarios_dspb_milestones_hot_unadapted_pb(*, output_scenarios_primary_balance_pct_gdp_summary_hot_unadapted: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Extract PB/PB* milestone values for the Hot Un-Adapted scenario from the primary-balance-to-GDP summary shard.

    Map the primary balance (percent of GDP) summary for the Hot Un-Adapted climate scenario onto the PB/PB* milestone years 2050, 2075, and 2099.

    Args:
        output_scenarios_primary_balance_pct_gdp_summary_hot_unadapted: Public PB Gap output shard holding the Hot Un-Adapted scenario's primary balance as a percent of GDP, indexed by year; values are read at the milestone years and otherwise passed through unchanged.

    Returns:
        A series of primary balance (percent of GDP) under the Hot Un-Adapted scenario restricted to the 2050, 2075, and 2099 milestone periods, preserving the source values' types.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(output_scenarios_primary_balance_pct_gdp_summary_hot_unadapted[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_UNADAPTED_PB.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_UNADAPTED_PB.required))

@publish(data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_UNADAPTED_PB_STAR.schema, cells=data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_UNADAPTED_PB_STAR.cells)
def output_scenarios_dspb_milestones_hot_unadapted_pb_star(*, scenario_debt_stabilizing_primary_balance_hot_unadapted: data.ScenarioDebtStabilizingPrimaryBalanceHotUnadapted) -> data.Series[float | str | None]:
    """Extract the Hot Un-Adapted debt-stabilizing primary balance (PB*) milestones at 2050, 2075, and 2099.

    Produces the PB* milestone shard for the Hot Un-Adapted climate scenario, expressing each milestone year's debt-stabilizing primary balance as a measure.

    Args:
        scenario_debt_stabilizing_primary_balance_hot_unadapted: Hot Un-Adapted climate scenario debt-stabilizing primary balance series supplying the values for the 2050, 2075, and 2099 PB* milestone years.

    Returns:
        A series of the Hot Un-Adapted debt-stabilizing primary balance (PB*) at the 2050, 2075, and 2099 milestone years, with each entry converted to a measure.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(scenario_debt_stabilizing_primary_balance_hot_unadapted[time_period])

    return data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_UNADAPTED_PB_STAR.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DSPB_MILESTONES_HOT_UNADAPTED_PB_STAR.required))

@publish(data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_BASELINE_PATH.schema, cells=data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_BASELINE_PATH.cells)
def output_scenarios_primary_balance_pct_gdp_baseline_path(*, baseline_primary_balance_pct_gdp: data.BaselinePrimaryBalancePctGdp) -> data.Series[float | str | None]:
    """Build the baseline path of the primary balance-to-GDP ratio for the annual scenario matrix.

    Provides the baseline comparison row against which the climate-scenario primary balance paths are assessed, holding fiscal policy settings unchanged relative to nominal GDP.

    Args:
        baseline_primary_balance_pct_gdp: Baseline primary balance as a percent of nominal GDP, evaluated for each projection year of the scenario horizon.

    Returns:
        Annual series of the baseline primary balance-to-GDP ratio, aligned to the scenario matrix time axis and used as the reference row for the climate-scenario outputs.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_primary_balance_pct_gdp[time_period])

    return data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_BASELINE_PATH.collect(evaluate(formula, data.OUTPUT_SCENARIOS_PRIMARY_BALANCE_PCT_GDP_BASELINE_PATH.required))

@publish(data.OUTPUT_SCENARIOS_OVERALL_BALANCE_PCT_GDP_BASELINE_PATH.schema, cells=data.OUTPUT_SCENARIOS_OVERALL_BALANCE_PCT_GDP_BASELINE_PATH.cells)
def output_scenarios_overall_balance_pct_gdp_baseline_path(*, baseline_overall_balance_pct_gdp: data.BaselineOverallBalancePctGdp) -> data.Series[float | str | None]:
    """Return the baseline path of the overall balance as a share of GDP in the annual scenario matrix.

    Supply the baseline comparison row against which the climate-scenario overall balance rows are assessed.

    Args:
        baseline_overall_balance_pct_gdp: Baseline overall balance expressed as a percent of nominal GDP for each projection year to 2099.

    Returns:
        A series of overall balance values as a percent of GDP along the baseline path, indexed by projection year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_overall_balance_pct_gdp[time_period])

    return data.OUTPUT_SCENARIOS_OVERALL_BALANCE_PCT_GDP_BASELINE_PATH.collect(evaluate(formula, data.OUTPUT_SCENARIOS_OVERALL_BALANCE_PCT_GDP_BASELINE_PATH.required))

@publish(data.OUTPUT_SCENARIOS_DEBT_TO_GDP_BASELINE_PATH.schema, cells=data.OUTPUT_SCENARIOS_DEBT_TO_GDP_BASELINE_PATH.cells)
def output_scenarios_debt_to_gdp_baseline_path(*, baseline_debt_to_gdp: data.BaselineDebtToGdp) -> data.Series[float | str | None]:
    """Return the baseline debt-to-GDP path for the annual scenario matrix.

    Serves as the baseline comparison row against which the climate-scenario debt-to-GDP trajectories are assessed.

    Args:
        baseline_debt_to_gdp: Baseline gross debt-to-GDP ratio, in percent of nominal GDP, for each projection year, derived from the WEO-projected debt stock and the debt dynamics equation.

    Returns:
        Annual series of the baseline debt-to-GDP ratio covering the projection horizon, aligned with the climate-scenario rows of the annual scenario matrix.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(baseline_debt_to_gdp[time_period])

    return data.OUTPUT_SCENARIOS_DEBT_TO_GDP_BASELINE_PATH.collect(evaluate(formula, data.OUTPUT_SCENARIOS_DEBT_TO_GDP_BASELINE_PATH.required))

@publish(key=(), domain=None, cells=data.MACROFISCAL_COUNTRY_CELLS)
def macrofiscal_country(*, country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"]) -> str | int | float | bool:
    """Return the Dashboard country selection as the Macro-fiscal INDEX/MATCH key.

    Mirrors Dashboard!C12 so the selected country drives the Macro-fiscal worksheet and the data loaded for that economy.

    Args:
        country: Country selected in the Dashboard, provided as the country name (for example, "C\u00f4te d'Ivoire" or "United States").

    Returns:
        The country name for the selected economy, or an Excel error code when the selection is not a valid country.
    """
    try:
        return as_measure(country, 'str')
    except XlError as error:
        return error.code

@publish(data.MACROFISCAL_REAL_GDP_LCU.schema, cells=data.MACROFISCAL_REAL_GDP_LCU.cells)
def macrofiscal_real_gdp_lcu(*, constant_macrofiscal_a67_a264: data.Series[str | None], constant_macrofiscal_ag67_bb264: data.Series[float | str | None], macrofiscal_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Return a country's real GDP in billions of local currency units for 2008-2029.

    Provide the real GDP levels in local currency units that underpin the nominal GDP decomposition and the fiscal projections over the projection horizon.

    Args:
        constant_macrofiscal_a67_a264: Country identifiers along the country axis used to look up the selected economy.
        constant_macrofiscal_ag67_bb264: Real GDP in billions of local currency units by country for 2008-2029, the source of the projected levels.
        macrofiscal_country: Country selected in the Dashboard, matched against the country axis to pick the corresponding row.

    Returns:
        A series of real GDP in billions of local currency units for the selected country over 2008-2029, with the country name and unit metadata attached.
    """
    data.CONSTANT_MACROFISCAL_A67_A264.schema.validate(constant_macrofiscal_a67_a264)
    data.CONSTANT_MACROFISCAL_AG67_BB264.schema.validate(constant_macrofiscal_ag67_bb264)
    _macrofiscal_real_gdp_lcu_table_0 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2008,))
    _macrofiscal_real_gdp_lcu_table_1 = view(constant_macrofiscal_a67_a264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'))
    _macrofiscal_real_gdp_lcu_table_2 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2009,))
    _macrofiscal_real_gdp_lcu_table_3 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2010,))
    _macrofiscal_real_gdp_lcu_table_4 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2011,))
    _macrofiscal_real_gdp_lcu_table_5 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2012,))
    _macrofiscal_real_gdp_lcu_table_6 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2013,))
    _macrofiscal_real_gdp_lcu_table_7 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2014,))
    _macrofiscal_real_gdp_lcu_table_8 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2015,))
    _macrofiscal_real_gdp_lcu_table_9 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2016,))
    _macrofiscal_real_gdp_lcu_table_10 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2017,))
    _macrofiscal_real_gdp_lcu_table_11 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2018,))
    _macrofiscal_real_gdp_lcu_table_12 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2019,))
    _macrofiscal_real_gdp_lcu_table_13 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2020,))
    _macrofiscal_real_gdp_lcu_table_14 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2021,))
    _macrofiscal_real_gdp_lcu_table_15 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2022,))
    _macrofiscal_real_gdp_lcu_table_16 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2023,))
    _macrofiscal_real_gdp_lcu_table_17 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2024,))
    _macrofiscal_real_gdp_lcu_table_18 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2025,))
    _macrofiscal_real_gdp_lcu_table_19 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2026,))
    _macrofiscal_real_gdp_lcu_table_20 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2027,))
    _macrofiscal_real_gdp_lcu_table_21 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2028,))
    _macrofiscal_real_gdp_lcu_table_22 = view(constant_macrofiscal_ag67_bb264, rows=span(data.COUNTRY_AXIS, 'Afghanistan', 'Zimbabwe'), cols=(2029,))
    def formula(time_period: int) -> float | str | None:
        if time_period == 2008:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_0, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2009:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_2, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2010:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_3, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2011:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_4, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2012:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_5, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2013:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_6, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2014:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_7, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2015:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_8, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2016:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_9, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2017:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_10, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2018:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_11, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2019:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_12, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2020:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_13, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2021:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_14, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2022:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_15, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2023:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_16, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2024:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_17, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2025:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_18, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2026:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_19, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2027:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_20, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        elif time_period == 2028:
            return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_21, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))
        return as_measure(xl_index(_macrofiscal_real_gdp_lcu_table_22, xl_match(macrofiscal_country, _macrofiscal_real_gdp_lcu_table_1, 0), 1))

    return data.MACROFISCAL_REAL_GDP_LCU.collect(evaluate(formula, data.MACROFISCAL_REAL_GDP_LCU.required))

@publish(data.MACROFISCAL_NOMINAL_GDP_LCU.schema, cells=data.MACROFISCAL_NOMINAL_GDP_LCU.cells)
def macrofiscal_nominal_gdp_lcu(*, constant_macrofiscal_a268_a465: data.Series[str | None], constant_macrofiscal_ag268_bb465: data.Series[float | str | None], macrofiscal_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Retrieve the nominal GDP path in billions of local currency units for a single country.

    Supplies the nominal GDP projection for 2008–2029 that anchors the fiscal aggregates expressed as shares of nominal GDP.

    Args:
        constant_macrofiscal_a268_a465: Country axis used to locate the requested economy's row position across the macrofiscal country labels.
        constant_macrofiscal_ag268_bb465: Nominal GDP in billions of local currency units by country and year used as the underlying value table.
        macrofiscal_country: Identifier of the economy whose nominal GDP path is returned.

    Returns:
        A nominal GDP series in billions of local currency units for the selected country over the supported years.
    """
    data.CONSTANT_MACROFISCAL_A268_A465.schema.validate(constant_macrofiscal_a268_a465)
    data.CONSTANT_MACROFISCAL_AG268_BB465.schema.validate(constant_macrofiscal_ag268_bb465)
    _macrofiscal_nominal_gdp_lcu_table_0 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2008,))
    _macrofiscal_nominal_gdp_lcu_table_1 = view(constant_macrofiscal_a268_a465, rows=data.COUNTRY_AXIS_2.keys)
    _macrofiscal_nominal_gdp_lcu_table_2 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2009,))
    _macrofiscal_nominal_gdp_lcu_table_3 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2010,))
    _macrofiscal_nominal_gdp_lcu_table_4 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2011,))
    _macrofiscal_nominal_gdp_lcu_table_5 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2012,))
    _macrofiscal_nominal_gdp_lcu_table_6 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2013,))
    _macrofiscal_nominal_gdp_lcu_table_7 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2014,))
    _macrofiscal_nominal_gdp_lcu_table_8 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2015,))
    _macrofiscal_nominal_gdp_lcu_table_9 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2016,))
    _macrofiscal_nominal_gdp_lcu_table_10 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2017,))
    _macrofiscal_nominal_gdp_lcu_table_11 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2018,))
    _macrofiscal_nominal_gdp_lcu_table_12 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2019,))
    _macrofiscal_nominal_gdp_lcu_table_13 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2020,))
    _macrofiscal_nominal_gdp_lcu_table_14 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2021,))
    _macrofiscal_nominal_gdp_lcu_table_15 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2022,))
    _macrofiscal_nominal_gdp_lcu_table_16 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2023,))
    _macrofiscal_nominal_gdp_lcu_table_17 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2024,))
    _macrofiscal_nominal_gdp_lcu_table_18 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2025,))
    _macrofiscal_nominal_gdp_lcu_table_19 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2026,))
    _macrofiscal_nominal_gdp_lcu_table_20 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2027,))
    _macrofiscal_nominal_gdp_lcu_table_21 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2028,))
    _macrofiscal_nominal_gdp_lcu_table_22 = view(constant_macrofiscal_ag268_bb465, rows=data.COUNTRY_AXIS_2.keys, cols=(2029,))
    def formula(time_period: int) -> float | str | None:
        if time_period == 2008:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_0, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2009:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_2, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2010:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_3, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2011:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_4, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2012:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_5, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2013:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_6, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2014:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_7, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2015:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_8, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2016:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_9, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2017:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_10, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2018:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_11, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2019:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_12, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2020:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_13, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2021:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_14, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2022:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_15, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2023:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_16, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2024:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_17, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2025:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_18, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2026:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_19, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2027:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_20, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        elif time_period == 2028:
            return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_21, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))
        return as_measure(xl_index(_macrofiscal_nominal_gdp_lcu_table_22, xl_match(macrofiscal_country, _macrofiscal_nominal_gdp_lcu_table_1, 0), 1))

    return data.MACROFISCAL_NOMINAL_GDP_LCU.collect(evaluate(formula, data.MACROFISCAL_NOMINAL_GDP_LCU.required))

@publish(data.MACROFISCAL_GDP_DEFLATOR.schema, cells=data.MACROFISCAL_GDP_DEFLATOR.cells)
def macrofiscal_gdp_deflator(*, constant_macrofiscal_a469_a666: data.Series[str | None], constant_macrofiscal_ag469_bb666: data.Series[float | str | None], macrofiscal_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Extract the GDP deflator for a selected country across the projection horizon.

    Provides the price measure of nominal GDP—the GDP deflator—so nominal magnitudes can be decomposed into real output and prices in the macro-fiscal baseline.

    Args:
        constant_macrofiscal_a469_a666: Per-country lookup series used to match the supplied country to its row in the macro-fiscal table.
        constant_macrofiscal_ag469_bb666: Per-country macro-fiscal series holding the GDP deflator (an index) by year, from which the value for the selected country and period is read.
        macrofiscal_country: Identifier of the country whose GDP deflator is requested, as selected in the Q-CRAFT dashboard.

    Returns:
        A series of GDP deflator values (an index) for the selected country over the projection years.
    """
    data.CONSTANT_MACROFISCAL_A469_A666.schema.validate(constant_macrofiscal_a469_a666)
    data.CONSTANT_MACROFISCAL_AG469_BB666.schema.validate(constant_macrofiscal_ag469_bb666)
    _macrofiscal_gdp_deflator_table_0 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2008,))
    _macrofiscal_gdp_deflator_table_1 = view(constant_macrofiscal_a469_a666, rows=data.COUNTRY_AXIS_2.keys)
    _macrofiscal_gdp_deflator_table_2 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2009,))
    _macrofiscal_gdp_deflator_table_3 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2010,))
    _macrofiscal_gdp_deflator_table_4 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2011,))
    _macrofiscal_gdp_deflator_table_5 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2012,))
    _macrofiscal_gdp_deflator_table_6 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2013,))
    _macrofiscal_gdp_deflator_table_7 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2014,))
    _macrofiscal_gdp_deflator_table_8 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2015,))
    _macrofiscal_gdp_deflator_table_9 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2016,))
    _macrofiscal_gdp_deflator_table_10 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2017,))
    _macrofiscal_gdp_deflator_table_11 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2018,))
    _macrofiscal_gdp_deflator_table_12 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2019,))
    _macrofiscal_gdp_deflator_table_13 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2020,))
    _macrofiscal_gdp_deflator_table_14 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2021,))
    _macrofiscal_gdp_deflator_table_15 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2022,))
    _macrofiscal_gdp_deflator_table_16 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2023,))
    _macrofiscal_gdp_deflator_table_17 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2024,))
    _macrofiscal_gdp_deflator_table_18 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2025,))
    _macrofiscal_gdp_deflator_table_19 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2026,))
    _macrofiscal_gdp_deflator_table_20 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2027,))
    _macrofiscal_gdp_deflator_table_21 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2028,))
    _macrofiscal_gdp_deflator_table_22 = view(constant_macrofiscal_ag469_bb666, rows=data.COUNTRY_AXIS_2.keys, cols=(2029,))
    def formula(time_period: int) -> float | str | None:
        if time_period == 2008:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_0, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2009:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_2, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2010:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_3, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2011:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_4, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2012:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_5, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2013:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_6, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2014:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_7, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2015:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_8, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2016:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_9, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2017:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_10, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2018:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_11, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2019:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_12, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2020:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_13, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2021:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_14, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2022:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_15, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2023:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_16, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2024:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_17, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2025:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_18, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2026:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_19, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2027:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_20, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        elif time_period == 2028:
            return as_measure(xl_index(_macrofiscal_gdp_deflator_table_21, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))
        return as_measure(xl_index(_macrofiscal_gdp_deflator_table_22, xl_match(macrofiscal_country, _macrofiscal_gdp_deflator_table_1, 0), 1))

    return data.MACROFISCAL_GDP_DEFLATOR.collect(evaluate(formula, data.MACROFISCAL_GDP_DEFLATOR.required))

@publish(data.MACROFISCAL_REVENUE_LCU.schema, cells=data.MACROFISCAL_REVENUE_LCU.cells)
def macrofiscal_revenue_lcu(*, constant_macrofiscal_a670_a867: data.Series[str | None], constant_macrofiscal_ah670_bb867: data.Series[float | str | None], macrofiscal_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Select general government revenue in local currency units by country and year.

    Provide the macrofiscal revenue series in billions of local currency units for the general government sector.

    Args:
        constant_macrofiscal_a670_a867: Country dimension keyed by the IMF country axis, used to match the requested economy.
        constant_macrofiscal_ah670_bb867: Macrofiscal revenue table in billions of local currency units, indexed by country across the projection years 2009-2029.
        macrofiscal_country: Identifier of the economy whose macrofiscal revenue is to be retrieved.

    Returns:
        A series of general government revenue in billions of local currency units by year for the selected economy, with non-numeric observations returned as text.
    """
    data.CONSTANT_MACROFISCAL_A670_A867.schema.validate(constant_macrofiscal_a670_a867)
    data.CONSTANT_MACROFISCAL_AH670_BB867.schema.validate(constant_macrofiscal_ah670_bb867)
    _macrofiscal_revenue_lcu_table_0 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2009,))
    _macrofiscal_revenue_lcu_table_1 = view(constant_macrofiscal_a670_a867, rows=data.COUNTRY_AXIS_2.keys)
    _macrofiscal_revenue_lcu_table_2 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2010,))
    _macrofiscal_revenue_lcu_table_3 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2011,))
    _macrofiscal_revenue_lcu_table_4 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2012,))
    _macrofiscal_revenue_lcu_table_5 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2013,))
    _macrofiscal_revenue_lcu_table_6 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2014,))
    _macrofiscal_revenue_lcu_table_7 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2015,))
    _macrofiscal_revenue_lcu_table_8 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2016,))
    _macrofiscal_revenue_lcu_table_9 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2017,))
    _macrofiscal_revenue_lcu_table_10 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2018,))
    _macrofiscal_revenue_lcu_table_11 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2019,))
    _macrofiscal_revenue_lcu_table_12 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2020,))
    _macrofiscal_revenue_lcu_table_13 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2021,))
    _macrofiscal_revenue_lcu_table_14 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2022,))
    _macrofiscal_revenue_lcu_table_15 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2023,))
    _macrofiscal_revenue_lcu_table_16 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2024,))
    _macrofiscal_revenue_lcu_table_17 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2025,))
    _macrofiscal_revenue_lcu_table_18 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2026,))
    _macrofiscal_revenue_lcu_table_19 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2027,))
    _macrofiscal_revenue_lcu_table_20 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2028,))
    _macrofiscal_revenue_lcu_table_21 = view(constant_macrofiscal_ah670_bb867, rows=data.COUNTRY_AXIS_2.keys, cols=(2029,))
    def formula(time_period: int) -> float | str | None:
        if time_period == 2009:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_0, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2010:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_2, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2011:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_3, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2012:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_4, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2013:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_5, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2014:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_6, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2015:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_7, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2016:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_8, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2017:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_9, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2018:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_10, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2019:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_11, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2020:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_12, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2021:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_13, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2022:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_14, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2023:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_15, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2024:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_16, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2025:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_17, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2026:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_18, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2027:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_19, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        elif time_period == 2028:
            return as_measure(xl_index(_macrofiscal_revenue_lcu_table_20, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))
        return as_measure(xl_index(_macrofiscal_revenue_lcu_table_21, xl_match(macrofiscal_country, _macrofiscal_revenue_lcu_table_1, 0), 1))

    return data.MACROFISCAL_REVENUE_LCU.collect(evaluate(formula, data.MACROFISCAL_REVENUE_LCU.required))

@publish(data.MACROFISCAL_EXPENDITURE_LCU.schema, cells=data.MACROFISCAL_EXPENDITURE_LCU.cells)
def macrofiscal_expenditure_lcu(*, constant_macrofiscal_a871_a1068: data.Series[str | None], constant_macrofiscal_ah871_bb1068: data.Series[float | str | None], macrofiscal_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Project general government primary expenditure in local currency units for the selected country.

    Retrieve the annual primary expenditure path from the preloaded macro-fiscal data, expressed in billions of local currency units, for the reference country across the projection horizon.

    Args:
        constant_macrofiscal_a871_a1068: Country identifiers aligned to the country axis, used to locate the row of the selected economy in the macro-fiscal table.
        constant_macrofiscal_ah871_bb1068: Annual primary expenditure in billions of local currency units by country for each year from 2009 onward, from which the selected country's expenditure path is drawn.
        macrofiscal_country: The country selected in the Dashboard, given as its country identifier or name and matched against the country axis.

    Returns:
        A series of general government primary expenditure in billions of local currency units for the selected country, covering the years from 2009 onward.
    """
    data.CONSTANT_MACROFISCAL_A871_A1068.schema.validate(constant_macrofiscal_a871_a1068)
    data.CONSTANT_MACROFISCAL_AH871_BB1068.schema.validate(constant_macrofiscal_ah871_bb1068)
    _macrofiscal_expenditure_lcu_table_0 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2009,))
    _macrofiscal_expenditure_lcu_table_1 = view(constant_macrofiscal_a871_a1068, rows=data.COUNTRY_AXIS_2.keys)
    _macrofiscal_expenditure_lcu_table_2 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2010,))
    _macrofiscal_expenditure_lcu_table_3 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2011,))
    _macrofiscal_expenditure_lcu_table_4 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2012,))
    _macrofiscal_expenditure_lcu_table_5 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2013,))
    _macrofiscal_expenditure_lcu_table_6 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2014,))
    _macrofiscal_expenditure_lcu_table_7 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2015,))
    _macrofiscal_expenditure_lcu_table_8 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2016,))
    _macrofiscal_expenditure_lcu_table_9 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2017,))
    _macrofiscal_expenditure_lcu_table_10 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2018,))
    _macrofiscal_expenditure_lcu_table_11 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2019,))
    _macrofiscal_expenditure_lcu_table_12 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2020,))
    _macrofiscal_expenditure_lcu_table_13 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2021,))
    _macrofiscal_expenditure_lcu_table_14 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2022,))
    _macrofiscal_expenditure_lcu_table_15 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2023,))
    _macrofiscal_expenditure_lcu_table_16 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2024,))
    _macrofiscal_expenditure_lcu_table_17 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2025,))
    _macrofiscal_expenditure_lcu_table_18 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2026,))
    _macrofiscal_expenditure_lcu_table_19 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2027,))
    _macrofiscal_expenditure_lcu_table_20 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2028,))
    _macrofiscal_expenditure_lcu_table_21 = view(constant_macrofiscal_ah871_bb1068, rows=data.COUNTRY_AXIS_2.keys, cols=(2029,))
    def formula(time_period: int) -> float | str | None:
        if time_period == 2009:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_0, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2010:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_2, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2011:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_3, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2012:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_4, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2013:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_5, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2014:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_6, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2015:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_7, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2016:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_8, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2017:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_9, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2018:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_10, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2019:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_11, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2020:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_12, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2021:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_13, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2022:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_14, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2023:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_15, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2024:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_16, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2025:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_17, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2026:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_18, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2027:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_19, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        elif time_period == 2028:
            return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_20, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))
        return as_measure(xl_index(_macrofiscal_expenditure_lcu_table_21, xl_match(macrofiscal_country, _macrofiscal_expenditure_lcu_table_1, 0), 1))

    return data.MACROFISCAL_EXPENDITURE_LCU.collect(evaluate(formula, data.MACROFISCAL_EXPENDITURE_LCU.required))

@publish(data.MACROFISCAL_OVERALL_BALANCE_LCU.schema, cells=data.MACROFISCAL_OVERALL_BALANCE_LCU.cells)
def macrofiscal_overall_balance_lcu(*, constant_macrofiscal_a1072_a1269: data.Series[str | None], constant_macrofiscal_ah1072_bb1269: data.Series[float | str | None], macrofiscal_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Project the overall balance in local currency units for a selected country over 2009-2029.

    Derive the general government overall balance, in billions of local currency units, from the country's macrofiscal series so it can be used in debt dynamics and fiscal risk analysis.

    Args:
        constant_macrofiscal_a1072_a1269: Constant macrofiscal series holding the country identifiers along the country axis used to match the selected country to its row.
        constant_macrofiscal_ah1072_bb1269: Constant macrofiscal series containing the annual overall balance figures, in billions of local currency units, for each country from 2009 through 2029.
        macrofiscal_country: Country selected in the Dashboard, given as a country name or code, whose overall balance trajectory is returned.

    Returns:
        A series of the selected country's overall balance in billions of local currency units for each projected year; missing values are preserved where source data are unavailable.
    """
    data.CONSTANT_MACROFISCAL_A1072_A1269.schema.validate(constant_macrofiscal_a1072_a1269)
    data.CONSTANT_MACROFISCAL_AH1072_BB1269.schema.validate(constant_macrofiscal_ah1072_bb1269)
    _macrofiscal_overall_balance_lcu_table_0 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2009,))
    _macrofiscal_overall_balance_lcu_table_1 = view(constant_macrofiscal_a1072_a1269, rows=data.COUNTRY_AXIS_2.keys)
    _macrofiscal_overall_balance_lcu_table_2 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2010,))
    _macrofiscal_overall_balance_lcu_table_3 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2011,))
    _macrofiscal_overall_balance_lcu_table_4 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2012,))
    _macrofiscal_overall_balance_lcu_table_5 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2013,))
    _macrofiscal_overall_balance_lcu_table_6 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2014,))
    _macrofiscal_overall_balance_lcu_table_7 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2015,))
    _macrofiscal_overall_balance_lcu_table_8 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2016,))
    _macrofiscal_overall_balance_lcu_table_9 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2017,))
    _macrofiscal_overall_balance_lcu_table_10 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2018,))
    _macrofiscal_overall_balance_lcu_table_11 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2019,))
    _macrofiscal_overall_balance_lcu_table_12 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2020,))
    _macrofiscal_overall_balance_lcu_table_13 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2021,))
    _macrofiscal_overall_balance_lcu_table_14 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2022,))
    _macrofiscal_overall_balance_lcu_table_15 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2023,))
    _macrofiscal_overall_balance_lcu_table_16 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2024,))
    _macrofiscal_overall_balance_lcu_table_17 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2025,))
    _macrofiscal_overall_balance_lcu_table_18 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2026,))
    _macrofiscal_overall_balance_lcu_table_19 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2027,))
    _macrofiscal_overall_balance_lcu_table_20 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2028,))
    _macrofiscal_overall_balance_lcu_table_21 = view(constant_macrofiscal_ah1072_bb1269, rows=data.COUNTRY_AXIS_2.keys, cols=(2029,))
    def formula(time_period: int) -> float | str | None:
        if time_period == 2009:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_0, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2010:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_2, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2011:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_3, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2012:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_4, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2013:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_5, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2014:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_6, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2015:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_7, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2016:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_8, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2017:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_9, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2018:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_10, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2019:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_11, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2020:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_12, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2021:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_13, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2022:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_14, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2023:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_15, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2024:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_16, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2025:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_17, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2026:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_18, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2027:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_19, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        elif time_period == 2028:
            return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_20, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))
        return as_measure(xl_index(_macrofiscal_overall_balance_lcu_table_21, xl_match(macrofiscal_country, _macrofiscal_overall_balance_lcu_table_1, 0), 1))

    return data.MACROFISCAL_OVERALL_BALANCE_LCU.collect(evaluate(formula, data.MACROFISCAL_OVERALL_BALANCE_LCU.required))

@publish(data.MACROFISCAL_PRIMARY_BALANCE_LCU.schema, cells=data.MACROFISCAL_PRIMARY_BALANCE_LCU.cells)
def macrofiscal_primary_balance_lcu(*, constant_macrofiscal_a1273_a1470: data.Series[str | None], constant_macrofiscal_ah1273_bb1470: data.Series[float | str | None], macrofiscal_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Look up the primary balance in local currency units for a country and year from the Macro-fiscal worksheet.

    Return the general government primary balance, in billions of local currency units, for the selected country and projection year by matching the country identifier to its row in the Macro-fiscal worksheet.

    Args:
        constant_macrofiscal_a1273_a1470: Macro-fiscal worksheet range providing the country dimension used to match the requested country identifier when looking up the primary balance row.
        constant_macrofiscal_ah1273_bb1470: Macro-fiscal worksheet range holding the primary balance, in billions of local currency units, by country row and year column from 2009 to 2029.
        macrofiscal_country: Country identifier selected in the Dashboard, used to locate the matching country row in the Macro-fiscal worksheet.

    Returns:
        The primary balance in billions of local currency units for the selected country and requested year, excluding government interest payments, or a null or non-numeric value where the Macro-fiscal worksheet has no primary balance observation.
    """
    data.CONSTANT_MACROFISCAL_A1273_A1470.schema.validate(constant_macrofiscal_a1273_a1470)
    data.CONSTANT_MACROFISCAL_AH1273_BB1470.schema.validate(constant_macrofiscal_ah1273_bb1470)
    _macrofiscal_primary_balance_lcu_table_0 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2009,))
    _macrofiscal_primary_balance_lcu_table_1 = view(constant_macrofiscal_a1273_a1470, rows=data.COUNTRY_AXIS_3.keys)
    _macrofiscal_primary_balance_lcu_table_2 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2010,))
    _macrofiscal_primary_balance_lcu_table_3 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2011,))
    _macrofiscal_primary_balance_lcu_table_4 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2012,))
    _macrofiscal_primary_balance_lcu_table_5 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2013,))
    _macrofiscal_primary_balance_lcu_table_6 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2014,))
    _macrofiscal_primary_balance_lcu_table_7 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2015,))
    _macrofiscal_primary_balance_lcu_table_8 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2016,))
    _macrofiscal_primary_balance_lcu_table_9 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2017,))
    _macrofiscal_primary_balance_lcu_table_10 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2018,))
    _macrofiscal_primary_balance_lcu_table_11 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2019,))
    _macrofiscal_primary_balance_lcu_table_12 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2020,))
    _macrofiscal_primary_balance_lcu_table_13 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2021,))
    _macrofiscal_primary_balance_lcu_table_14 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2022,))
    _macrofiscal_primary_balance_lcu_table_15 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2023,))
    _macrofiscal_primary_balance_lcu_table_16 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2024,))
    _macrofiscal_primary_balance_lcu_table_17 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2025,))
    _macrofiscal_primary_balance_lcu_table_18 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2026,))
    _macrofiscal_primary_balance_lcu_table_19 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2027,))
    _macrofiscal_primary_balance_lcu_table_20 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2028,))
    _macrofiscal_primary_balance_lcu_table_21 = view(constant_macrofiscal_ah1273_bb1470, rows=data.COUNTRY_AXIS_3.keys, cols=(2029,))
    def formula(time_period: int) -> float | str | None:
        if time_period == 2009:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_0, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2010:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_2, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2011:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_3, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2012:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_4, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2013:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_5, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2014:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_6, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2015:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_7, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2016:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_8, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2017:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_9, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2018:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_10, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2019:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_11, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2020:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_12, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2021:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_13, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2022:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_14, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2023:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_15, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2024:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_16, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2025:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_17, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2026:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_18, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2027:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_19, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        elif time_period == 2028:
            return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_20, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))
        return as_measure(xl_index(_macrofiscal_primary_balance_lcu_table_21, xl_match(macrofiscal_country, _macrofiscal_primary_balance_lcu_table_1, 0), 1))

    return data.MACROFISCAL_PRIMARY_BALANCE_LCU.collect(evaluate(formula, data.MACROFISCAL_PRIMARY_BALANCE_LCU.required))

@publish(data.MACROFISCAL_DEBT_LCU.schema, cells=data.MACROFISCAL_DEBT_LCU.cells)
def macrofiscal_debt_lcu(*, constant_macrofiscal_a1474_a1671: data.Series[str | None], constant_macrofiscal_ah1474_bb1671: data.Series[float | str | None], macrofiscal_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Extract the general government gross debt series in local currency units for a selected country.

    Return the long-term general government debt trajectory, expressed in billions of local currency units, for the chosen economy so that debt dynamics under the baseline and climate scenarios can be assessed.

    Args:
        constant_macrofiscal_a1474_a1671: Country identifier series used to locate the selected economy's row in the macro-fiscal worksheet.
        constant_macrofiscal_ah1474_bb1671: Macro-fiscal worksheet data holding the general government gross debt figures, in billions of local currency units, by country and year.
        macrofiscal_country: The country selected for analysis, whose debt series is retrieved along the country axis.

    Returns:
        A series of general government gross debt in billions of local currency units for the selected country, covering the years from 2009 onward; entries may be missing where no debt data are available.
    """
    data.CONSTANT_MACROFISCAL_A1474_A1671.schema.validate(constant_macrofiscal_a1474_a1671)
    data.CONSTANT_MACROFISCAL_AH1474_BB1671.schema.validate(constant_macrofiscal_ah1474_bb1671)
    _macrofiscal_debt_lcu_table_0 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2009,))
    _macrofiscal_debt_lcu_table_1 = view(constant_macrofiscal_a1474_a1671, rows=data.COUNTRY_AXIS_2.keys)
    _macrofiscal_debt_lcu_table_2 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2010,))
    _macrofiscal_debt_lcu_table_3 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2011,))
    _macrofiscal_debt_lcu_table_4 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2012,))
    _macrofiscal_debt_lcu_table_5 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2013,))
    _macrofiscal_debt_lcu_table_6 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2014,))
    _macrofiscal_debt_lcu_table_7 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2015,))
    _macrofiscal_debt_lcu_table_8 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2016,))
    _macrofiscal_debt_lcu_table_9 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2017,))
    _macrofiscal_debt_lcu_table_10 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2018,))
    _macrofiscal_debt_lcu_table_11 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2019,))
    _macrofiscal_debt_lcu_table_12 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2020,))
    _macrofiscal_debt_lcu_table_13 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2021,))
    _macrofiscal_debt_lcu_table_14 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2022,))
    _macrofiscal_debt_lcu_table_15 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2023,))
    _macrofiscal_debt_lcu_table_16 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2024,))
    _macrofiscal_debt_lcu_table_17 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2025,))
    _macrofiscal_debt_lcu_table_18 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2026,))
    _macrofiscal_debt_lcu_table_19 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2027,))
    _macrofiscal_debt_lcu_table_20 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2028,))
    _macrofiscal_debt_lcu_table_21 = view(constant_macrofiscal_ah1474_bb1671, rows=data.COUNTRY_AXIS_2.keys, cols=(2029,))
    def formula(time_period: int) -> float | str | None:
        if time_period == 2009:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_0, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2010:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_2, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2011:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_3, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2012:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_4, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2013:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_5, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2014:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_6, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2015:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_7, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2016:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_8, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2017:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_9, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2018:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_10, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2019:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_11, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2020:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_12, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2021:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_13, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2022:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_14, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2023:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_15, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2024:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_16, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2025:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_17, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2026:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_18, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2027:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_19, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        elif time_period == 2028:
            return as_measure(xl_index(_macrofiscal_debt_lcu_table_20, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))
        return as_measure(xl_index(_macrofiscal_debt_lcu_table_21, xl_match(macrofiscal_country, _macrofiscal_debt_lcu_table_1, 0), 1))

    return data.MACROFISCAL_DEBT_LCU.collect(evaluate(formula, data.MACROFISCAL_DEBT_LCU.required))

@publish(data.MACROFISCAL_INTEREST_EXPENDITURE_LCU.schema, cells=data.MACROFISCAL_INTEREST_EXPENDITURE_LCU.cells)
def macrofiscal_interest_expenditure_lcu(*, macrofiscal_overall_balance_lcu: data.Series[float | str | None], macrofiscal_primary_balance_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute interest expenditure in local currency units.

    Derive nominal interest expenditure as the difference between the primary balance and the overall balance.

    Args:
        macrofiscal_overall_balance_lcu: Overall fiscal balance of the general government, in billions of local currency units.
        macrofiscal_primary_balance_lcu: Primary fiscal balance of the general government (overall balance excluding interest payments), in billions of local currency units.

    Returns:
        Interest expenditure in billions of local currency units, equivalent to the primary balance minus the overall balance.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(macrofiscal_primary_balance_lcu[time_period], macrofiscal_overall_balance_lcu[time_period]))

    return data.MACROFISCAL_INTEREST_EXPENDITURE_LCU.collect(evaluate(formula, data.MACROFISCAL_INTEREST_EXPENDITURE_LCU.required))

@publish(data.MACROFISCAL_PRIMARY_EXPENDITURE_LCU.schema, cells=data.MACROFISCAL_PRIMARY_EXPENDITURE_LCU.cells)
def macrofiscal_primary_expenditure_lcu(*, macrofiscal_expenditure_lcu: data.Series[float | str | None], macrofiscal_interest_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Derive primary expenditure in local currency units by netting interest payments out of total expenditure.

    Isolates primary expenditure (total expenditure excluding government interest payments) to support the baseline and climate scenario fiscal projections.

    Args:
        macrofiscal_expenditure_lcu: Total general government expenditure in billions of local currency units for each projection period.
        macrofiscal_interest_expenditure_lcu: General government interest expenditure in billions of local currency units for each projection period.

    Returns:
        Primary expenditure in billions of local currency units for each period, aligned to the primary expenditure coordinate.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(macrofiscal_expenditure_lcu[time_period], macrofiscal_interest_expenditure_lcu[time_period]))

    return data.MACROFISCAL_PRIMARY_EXPENDITURE_LCU.collect(evaluate(formula, data.MACROFISCAL_PRIMARY_EXPENDITURE_LCU.required))

@publish(data.MACROFISCAL_REAL_GDP_GROWTH.schema, cells=data.MACROFISCAL_REAL_GDP_GROWTH.cells)
def macrofiscal_real_gdp_growth(*, macrofiscal_real_gdp_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute year-over-year real GDP growth from real GDP in local currency units.

    Derive the growth rate of real GDP in local currency units for the baseline macro-fiscal projections.

    Args:
        macrofiscal_real_gdp_lcu: Real GDP in billions of local currency units for the general government sector, as loaded from the IMF WEO database in the Macro-fiscal worksheet.

    Returns:
        A series of year-over-year real GDP growth rates, expressed as percentages.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(macrofiscal_real_gdp_lcu[time_period], macrofiscal_real_gdp_lcu[time_period - 1]), 100), 100))

    return data.MACROFISCAL_REAL_GDP_GROWTH.collect(evaluate(formula, data.MACROFISCAL_REAL_GDP_GROWTH.required))

@publish(data.MACROFISCAL_NOMINAL_GDP_GROWTH.schema, cells=data.MACROFISCAL_NOMINAL_GDP_GROWTH.cells)
def macrofiscal_nominal_gdp_growth(*, macrofiscal_nominal_gdp_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Derive nominal GDP growth using nominal GDP levels.

    Provide nominal GDP growth, the growth rate of nominal GDP that, together with revenue and primary expenditure, drives the baseline debt dynamics.

    Args:
        macrofiscal_nominal_gdp_lcu: Nominal GDP in billions of local currency units, indexed by time period.

    Returns:
        A time-indexed series of nominal GDP growth in percent, the percentage change in nominal GDP from the previous period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(macrofiscal_nominal_gdp_lcu[time_period], macrofiscal_nominal_gdp_lcu[time_period - 1]), 100), 100))

    return data.MACROFISCAL_NOMINAL_GDP_GROWTH.collect(evaluate(formula, data.MACROFISCAL_NOMINAL_GDP_GROWTH.required))

@publish(data.MACROFISCAL_GDP_DEFLATOR_GROWTH.schema, cells=data.MACROFISCAL_GDP_DEFLATOR_GROWTH.cells)
def macrofiscal_gdp_deflator_growth(*, macrofiscal_gdp_deflator: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the year-over-year growth rate of the GDP deflator.

    Provide the inflation measure used to derive nominal GDP projections from real GDP in the baseline scenario.

    Args:
        macrofiscal_gdp_deflator: GDP deflator series, expressed as an index, from the Macro-fiscal worksheet; the growth rate is computed relative to its value in the preceding period.

    Returns:
        Series of GDP deflator growth rates, expressed in percent.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(macrofiscal_gdp_deflator[time_period], macrofiscal_gdp_deflator[time_period - 1]), 100), 100))

    return data.MACROFISCAL_GDP_DEFLATOR_GROWTH.collect(evaluate(formula, data.MACROFISCAL_GDP_DEFLATOR_GROWTH.required))

@publish(data.MACROFISCAL_REVENUE_PCT_GDP.schema, cells=data.MACROFISCAL_REVENUE_PCT_GDP.cells)
def macrofiscal_revenue_pct_gdp(*, macrofiscal_nominal_gdp_lcu: data.Series[float | str | None], macrofiscal_revenue_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Express general government revenue as a share of nominal GDP.

    Provides the revenue-to-GDP ratio, the effective tax rate that Q-CRAFT holds constant across the baseline and climate change scenarios.

    Args:
        macrofiscal_nominal_gdp_lcu: Nominal GDP in billions of local currency units, the broadest measure of the economy and the denominator of the ratio.
        macrofiscal_revenue_lcu: General government revenue in billions of local currency units, the numerator of the ratio.

    Returns:
        Revenue-to-GDP ratio in percent for each projected period, as `None` where either input is missing.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(macrofiscal_revenue_lcu[time_period], macrofiscal_nominal_gdp_lcu[time_period]), 100))

    return data.MACROFISCAL_REVENUE_PCT_GDP.collect(evaluate(formula, data.MACROFISCAL_REVENUE_PCT_GDP.required))

@publish(data.MACROFISCAL_PRIMARY_EXPENDITURE_PCT_GDP.schema, cells=data.MACROFISCAL_PRIMARY_EXPENDITURE_PCT_GDP.cells)
def macrofiscal_primary_expenditure_pct_gdp(*, macrofiscal_nominal_gdp_lcu: data.Series[float | str | None], macrofiscal_primary_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Primary expenditure as a share of nominal GDP in percent.

    Express primary expenditure as a percentage of nominal GDP.

    Args:
        macrofiscal_nominal_gdp_lcu: Nominal GDP in billions of local currency units.
        macrofiscal_primary_expenditure_lcu: Primary expenditure (excluding government interest payments) in billions of local currency units.

    Returns:
        Primary expenditure as a percent of nominal GDP.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(macrofiscal_primary_expenditure_lcu[time_period], macrofiscal_nominal_gdp_lcu[time_period]), 100))

    return data.MACROFISCAL_PRIMARY_EXPENDITURE_PCT_GDP.collect(evaluate(formula, data.MACROFISCAL_PRIMARY_EXPENDITURE_PCT_GDP.required))

@publish(data.MACROFISCAL_INTEREST_RATE.schema, cells=data.MACROFISCAL_INTEREST_RATE.cells)
def macrofiscal_interest_rate(*, macrofiscal_debt_lcu: data.Series[float | str | None], macrofiscal_interest_expenditure_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the macrofiscal interest rate as interest expenditure over debt, in percent.

    Derives the effective interest rate on gross general government debt from interest expenditure, supporting the interest rate assumptions and debt dynamics used in the baseline and climate scenarios.

    Args:
        macrofiscal_debt_lcu: Gross general government debt, in billions of local currency units.
        macrofiscal_interest_expenditure_lcu: General government interest expenditure on debt, in billions of local currency units.

    Returns:
        The macrofiscal interest rate for each period, expressed in percent of gross debt.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(macrofiscal_interest_expenditure_lcu[time_period], macrofiscal_debt_lcu[time_period]), 100))

    return data.MACROFISCAL_INTEREST_RATE.collect(evaluate(formula, data.MACROFISCAL_INTEREST_RATE.required))

@publish(data.MACROFISCAL_DEBT_TO_GDP.schema, cells=data.MACROFISCAL_DEBT_TO_GDP.cells)
def macrofiscal_debt_to_gdp(*, macrofiscal_nominal_gdp_lcu: data.Series[float | str | None], macrofiscal_debt_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the gross debt-to-GDP ratio in percent from nominal GDP and gross debt in local currency units.

    Expresses general government gross debt relative to the broadest measure of the tax base, providing the debt burden indicator used in the debt dynamics equation.

    Args:
        macrofiscal_nominal_gdp_lcu: Nominal GDP in billions of local currency units for the general government sector.
        macrofiscal_debt_lcu: Gross government debt in billions of local currency units for the general government sector.

    Returns:
        Time series of the gross debt-to-GDP ratio expressed in percent.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(macrofiscal_debt_lcu[time_period], macrofiscal_nominal_gdp_lcu[time_period]), 100))

    return data.MACROFISCAL_DEBT_TO_GDP.collect(evaluate(formula, data.MACROFISCAL_DEBT_TO_GDP.required))

@publish(data.MACROFISCAL_OVERALL_BALANCE_PCT_GDP.schema, cells=data.MACROFISCAL_OVERALL_BALANCE_PCT_GDP.cells)
def macrofiscal_overall_balance_pct_gdp(*, macrofiscal_nominal_gdp_lcu: data.Series[float | str | None], macrofiscal_overall_balance_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the overall balance as a percentage of nominal GDP.

    Express the general government overall balance relative to nominal GDP, the broadest measure of the tax base.

    Args:
        macrofiscal_nominal_gdp_lcu: Nominal GDP in billions of local currency units, used as the denominator in the ratio.
        macrofiscal_overall_balance_lcu: Overall balance of the general government in billions of local currency units, used as the numerator in the ratio.

    Returns:
        The overall balance-to-GDP ratio, in percent, for each period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(macrofiscal_overall_balance_lcu[time_period], macrofiscal_nominal_gdp_lcu[time_period]), 100))

    return data.MACROFISCAL_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.MACROFISCAL_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.MACROFISCAL_PRIMARY_BALANCE_PCT_GDP.schema, cells=data.MACROFISCAL_PRIMARY_BALANCE_PCT_GDP.cells)
def macrofiscal_primary_balance_pct_gdp(*, macrofiscal_nominal_gdp_lcu: data.Series[float | str | None], macrofiscal_primary_balance_lcu: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the primary balance as a share of nominal GDP.

    Express the primary balance in percent of GDP, the ratio used to gauge fiscal sustainability and the pace of debt dynamics.

    Args:
        macrofiscal_nominal_gdp_lcu: Nominal GDP in billions of local currency units, the broadest measure of the tax base and a government's ability to carry debt.
        macrofiscal_primary_balance_lcu: Primary balance in billions of local currency units, that is, revenue less primary expenditure excluding government interest payments.

    Returns:
        The primary balance as a percent of nominal GDP, in local currency unit terms; a primary surplus reduces the debt-to-GDP ratio and a primary deficit raises it, all else equal.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(macrofiscal_primary_balance_lcu[time_period], macrofiscal_nominal_gdp_lcu[time_period]), 100))

    return data.MACROFISCAL_PRIMARY_BALANCE_PCT_GDP.collect(evaluate(formula, data.MACROFISCAL_PRIMARY_BALANCE_PCT_GDP.required))

@publish(data.MACROFISCAL_INTEREST_GROWTH_DIFFERENTIAL.schema, cells=data.MACROFISCAL_INTEREST_GROWTH_DIFFERENTIAL.cells)
def macrofiscal_interest_growth_differential(*, macrofiscal_nominal_gdp_growth: data.Series[float | str | None], macrofiscal_interest_rate: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the nominal interest-growth differential for each projection year.

    Provides the interest-growth differential underlying the debt dynamics equation used to project the debt-to-GDP ratio.

    Args:
        macrofiscal_nominal_gdp_growth: Projected nominal GDP growth rate, in percent, for each projection year.
        macrofiscal_interest_rate: Projected weighted average nominal interest rate on government debt, in percent, for each projection year.

    Returns:
        Series of the interest-growth differential, in percent, expressed as (i - g) / (1 + g) so that the debt-to-GDP ratio evolves by D(t+1) = D(t) * (1 + differential) - primary balance.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(xl_sub(xl_div(macrofiscal_interest_rate[time_period], 100), xl_div(macrofiscal_nominal_gdp_growth[time_period], 100)), xl_add(1, xl_div(macrofiscal_nominal_gdp_growth[time_period], 100))), 100))

    return data.MACROFISCAL_INTEREST_GROWTH_DIFFERENTIAL.collect(evaluate(formula, data.MACROFISCAL_INTEREST_GROWTH_DIFFERENTIAL.required))

@publish(key=(), domain=None, cells=data.DEMOGRAPHY_COUNTRY_CELLS)
def demography_country(*, country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"]) -> str | int | float | bool:
    """Resolve the demography controller's selected country.

    Mirrors Dashboard!C12 as the INDEX/MATCH country controller that selects which economy's UN population projections drive the demographic assumptions.

    Args:
        country: Country selected in the Dashboard, identifying which economy's demographic projections are used for the medium, high, or low population scenario.

    Returns:
        The country value as a string, or the spreadsheet error code if it cannot be resolved.
    """
    try:
        return as_measure(country, 'str')
    except XlError as error:
        return error.code

@publish(key=(), domain=None, cells=data.DEMOGRAPHY_SCENARIO_FLAG_CELLS)
def demography_scenario_flag(*, demography_scenario: Literal["High", "Low", "Medium"]) -> str | int | float | bool:
    """Return the dashboard demography scenario selection verbatim.

    Mirrors Dashboard!C17 so the chosen UN demographic variant (medium, high, or low) drives population and employment projections downstream.

    Args:
        demography_scenario: Demographic scenario selected in the Dashboard: 'Medium', 'High', or 'Low', reflecting the UN population projection's fertility assumptions.

    Returns:
        The demography scenario label as a string, or an error code if the value cannot be read.
    """
    try:
        return as_measure(demography_scenario, 'str')
    except XlError as error:
        return error.code

@publish(data.DEMOGRAPHY_WORKING_AGE_POPULATION.schema, cells=data.DEMOGRAPHY_WORKING_AGE_POPULATION.cells)
def demography_working_age_population(*, demography_variant_label_medium: str, demography_variant_label_high: str, demography_variant_label_low: str, demography_scenario_flag: str | int | float | bool, demography_working_age_population_medium: data.Series[float | str | None], demography_working_age_population_high: data.Series[float | str | None], demography_working_age_population_low: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Return the working-age (15-64) population projection for the selected demographic scenario.

    Selects the medium, high, or low UN working-age population projection according to the demographic scenario chosen in the Demography worksheet, supporting long-run employment growth.

    Args:
        demography_variant_label_medium: Label identifying the medium demographic scenario (based on UN fertility assumptions) within the Demography worksheet.
        demography_variant_label_high: Label identifying the high demographic scenario (based on UN fertility assumptions) within the Demography worksheet.
        demography_variant_label_low: Label identifying the low demographic scenario (based on UN fertility assumptions) within the Demography worksheet.
        demography_scenario_flag: The demographic scenario selected in the Dashboard, matched against the variant labels to determine which projection to use.
        demography_working_age_population_medium: Working-age (15-64) population projection for the medium demographic scenario, by time period.
        demography_working_age_population_high: Working-age (15-64) population projection for the high demographic scenario, by time period.
        demography_working_age_population_low: Working-age (15-64) population projection for the low demographic scenario, by time period.

    Returns:
        A series of working-age (15-64) population projections for the selected demographic scenario; empty where the scenario flag matches no variant label.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure((demography_working_age_population_medium[time_period] if xl_bool(xl_eq(demography_scenario_flag, demography_variant_label_medium)) else (demography_working_age_population_high[time_period] if xl_bool(xl_eq(demography_scenario_flag, demography_variant_label_high)) else (demography_working_age_population_low[time_period] if xl_bool(xl_eq(demography_scenario_flag, demography_variant_label_low)) else '"'))))

    return data.DEMOGRAPHY_WORKING_AGE_POPULATION.collect(evaluate(formula, data.DEMOGRAPHY_WORKING_AGE_POPULATION.required))

@publish(data.DEMOGRAPHY_TOTAL_POPULATION.schema, cells=data.DEMOGRAPHY_TOTAL_POPULATION.cells)
def demography_total_population(*, demography_variant_label_medium: str, demography_variant_label_high: str, demography_variant_label_low: str, demography_scenario_flag: str | int | float | bool, demography_total_population_medium: data.Series[float | str | None], demography_total_population_high: data.Series[float | str | None], demography_total_population_low: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Select total population by the chosen UN demographic scenario.

    Resolves total population for each projection year from the medium, high, or low UN scenario series based on the Demography worksheet scenario flag.

    Args:
        demography_variant_label_medium: Label identifying the medium fertility variant in the Demography worksheet scenario selection.
        demography_variant_label_high: Label identifying the high fertility variant in the Demography worksheet scenario selection.
        demography_variant_label_low: Label identifying the low fertility variant in the Demography worksheet scenario selection.
        demography_scenario_flag: Scenario choice entered in the Dashboard Demography cell that selects which UN demographic variant drives total population.
        demography_total_population_medium: Preloaded UN total population projections under the medium fertility scenario, covering 1950-2100.
        demography_total_population_high: Preloaded UN total population projections under the high fertility scenario, covering 1950-2100.
        demography_total_population_low: Preloaded UN total population projections under the low fertility scenario, covering 1950-2100.

    Returns:
        Total population by projection year for the selected demographic scenario, used to project primary expenditure growth alongside productivity and inflation.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure((demography_total_population_medium[time_period] if xl_bool(xl_eq(demography_scenario_flag, demography_variant_label_medium)) else (demography_total_population_high[time_period] if xl_bool(xl_eq(demography_scenario_flag, demography_variant_label_high)) else (demography_total_population_low[time_period] if xl_bool(xl_eq(demography_scenario_flag, demography_variant_label_low)) else '"'))))

    return data.DEMOGRAPHY_TOTAL_POPULATION.collect(evaluate(formula, data.DEMOGRAPHY_TOTAL_POPULATION.required))

@publish(data.DEMOGRAPHY_WORKING_AGE_POPULATION_MEDIUM.schema, cells=data.DEMOGRAPHY_WORKING_AGE_POPULATION_MEDIUM.cells)
def demography_working_age_population_medium(*, constant_demography_b120_b317: data.Series[str | None], constant_demography_bv120_ev317: data.Series[float | str | None], demography_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Project the medium-scenario working-age (15-64) population by country.

    Supplies the long-run employment growth driver used to project nominal GDP from 2029 onward under the UN medium demographic scenario.

    Args:
        constant_demography_b120_b317: Per-country lookup table of country identifiers used to map the requested country to its row in the medium-scenario population data.
        constant_demography_bv120_ev317: Medium-scenario working-age population levels by time period and country; values are selected using the matched country row.
        demography_country: Country identifier whose medium-scenario working-age population projection is requested.

    Returns:
        A series of medium-scenario working-age (15-64) population values indexed by time period for the requested country.
    """
    data.CONSTANT_DEMOGRAPHY_B120_B317.schema.validate(constant_demography_b120_b317)
    data.CONSTANT_DEMOGRAPHY_BV120_EV317.schema.validate(constant_demography_bv120_ev317)
    _demography_working_age_population_medium_table_0 = view(constant_demography_b120_b317, rows=data.COUNTRY_AXIS_2.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(view(constant_demography_bv120_ev317, rows=data.COUNTRY_AXIS_2.keys, cols=(time_period,)), xl_match(demography_country, _demography_working_age_population_medium_table_0, 0), 1))

    return data.DEMOGRAPHY_WORKING_AGE_POPULATION_MEDIUM.collect(evaluate(formula, data.DEMOGRAPHY_WORKING_AGE_POPULATION_MEDIUM.required))

@publish(data.DEMOGRAPHY_WORKING_AGE_POPULATION_HIGH.schema, cells=data.DEMOGRAPHY_WORKING_AGE_POPULATION_HIGH.cells)
def demography_working_age_population_high(*, constant_demography_b321_b518: data.Series[str | None], constant_demography_bv321_ev518: data.Series[float | str | None], demography_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Project working-age population under the UN high-fertility demographic scenario.

    Provide the high-fertility (15-64 year old) population path used for long-term employment and GDP growth in the baseline scenario.

    Args:
        constant_demography_b321_b518: Country-indexed series of constant demographic identifiers used to locate the requested economy along the country axis.
        constant_demography_bv321_ev518: Time-by-country series of the constant high-scenario working-age population values from which the projection is read.
        demography_country: Country selected in the Dashboard whose high-scenario working-age population is to be returned.

    Returns:
        Time series of projected working-age (15-64 year old) population under the high demographic scenario for the selected country.
    """
    data.CONSTANT_DEMOGRAPHY_B321_B518.schema.validate(constant_demography_b321_b518)
    data.CONSTANT_DEMOGRAPHY_BV321_EV518.schema.validate(constant_demography_bv321_ev518)
    _demography_working_age_population_high_table_0 = view(constant_demography_b321_b518, rows=data.COUNTRY_AXIS_3.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(view(constant_demography_bv321_ev518, rows=data.COUNTRY_AXIS_3.keys, cols=(time_period,)), xl_match(demography_country, _demography_working_age_population_high_table_0, 0), 1))

    return data.DEMOGRAPHY_WORKING_AGE_POPULATION_HIGH.collect(evaluate(formula, data.DEMOGRAPHY_WORKING_AGE_POPULATION_HIGH.required))

@publish(data.DEMOGRAPHY_WORKING_AGE_POPULATION_LOW.schema, cells=data.DEMOGRAPHY_WORKING_AGE_POPULATION_LOW.cells)
def demography_working_age_population_low(*, constant_demography_b522_b719: data.Series[str | None], constant_demography_bv522_ev719: data.Series[float | str | None], demography_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Compute the low-scenario working-age (15-64) population series.

    Derive Q-CRAFT's low demographic scenario working-age population projection, the driver of long-run employment growth in the baseline.

    Args:
        constant_demography_b522_b719: Country lookup series used to resolve the requested country to its matching country row when indexing the low-scenario population table.
        constant_demography_bv522_ev719: Low-scenario demography table providing working-age population values by country row and time period.
        demography_country: Country identifier whose low-scenario working-age population projection is to be selected.

    Returns:
        A series of working-age (15-64) population values under the low demographic scenario for the selected country over the projection horizon.
    """
    data.CONSTANT_DEMOGRAPHY_B522_B719.schema.validate(constant_demography_b522_b719)
    data.CONSTANT_DEMOGRAPHY_BV522_EV719.schema.validate(constant_demography_bv522_ev719)
    _demography_working_age_population_low_table_0 = view(constant_demography_b522_b719, rows=data.COUNTRY_AXIS_2.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(view(constant_demography_bv522_ev719, rows=data.COUNTRY_AXIS_2.keys, cols=(time_period,)), xl_match(demography_country, _demography_working_age_population_low_table_0, 0), 1))

    return data.DEMOGRAPHY_WORKING_AGE_POPULATION_LOW.collect(evaluate(formula, data.DEMOGRAPHY_WORKING_AGE_POPULATION_LOW.required))

@publish(data.DEMOGRAPHY_TOTAL_POPULATION_MEDIUM.schema, cells=data.DEMOGRAPHY_TOTAL_POPULATION_MEDIUM.cells)
def demography_total_population_medium(*, constant_demography_b723_b920: data.Series[str | None], constant_demography_bi723_ev920: data.Series[float | str | None], demography_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Return the medium-scenario total population series.

    Provides the UN medium demographic projection of total population used in the baseline scenario.

    Args:
        constant_demography_b723_b920: Country-identifying labels used to align each row with the medium-scenario population table.
        constant_demography_bi723_ev920: Medium-scenario population values by country and time period for the total population series.
        demography_country: Selected country whose medium-scenario total population is returned.

    Returns:
        Total population for the selected country under the medium demographic scenario, reported as a numeric series (or missing values where unavailable).
    """
    data.CONSTANT_DEMOGRAPHY_B723_B920.schema.validate(constant_demography_b723_b920)
    data.CONSTANT_DEMOGRAPHY_BI723_EV920.schema.validate(constant_demography_bi723_ev920)
    _demography_total_population_medium_table_0 = view(constant_demography_b723_b920, rows=data.COUNTRY_AXIS_2.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(view(constant_demography_bi723_ev920, rows=data.COUNTRY_AXIS_2.keys, cols=(time_period,)), xl_match(demography_country, _demography_total_population_medium_table_0, 0), 1))

    return data.DEMOGRAPHY_TOTAL_POPULATION_MEDIUM.collect(evaluate(formula, data.DEMOGRAPHY_TOTAL_POPULATION_MEDIUM.required))

@publish(data.DEMOGRAPHY_TOTAL_POPULATION_HIGH.schema, cells=data.DEMOGRAPHY_TOTAL_POPULATION_HIGH.cells)
def demography_total_population_high(*, constant_demography_b924_b1121: data.Series[str | None], constant_demography_bi924_ev1121: data.Series[float | str | None], demography_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Retrieve total population projections for a country under the high demographic scenario.

    Supplies the UN high-fertility total population path used by Q-CRAFT to drive long-term primary expenditure growth.

    Args:
        constant_demography_b924_b1121: Country-labelled reference series used as a row lookup so the requested economy can be aligned across the demography data.
        constant_demography_bi924_ev1121: Series of indexed demography values by time period from which the country's total population projection is read at each projection year.
        demography_country: Identifier of the country whose high-scenario total population projection is to be returned.

    Returns:
        A series of high-scenario total population values (or missing values) for the selected country across the projection periods.
    """
    data.CONSTANT_DEMOGRAPHY_B924_B1121.schema.validate(constant_demography_b924_b1121)
    data.CONSTANT_DEMOGRAPHY_BI924_EV1121.schema.validate(constant_demography_bi924_ev1121)
    _demography_total_population_high_table_0 = view(constant_demography_b924_b1121, rows=data.COUNTRY_AXIS_2.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(view(constant_demography_bi924_ev1121, rows=data.COUNTRY_AXIS_2.keys, cols=(time_period,)), xl_match(demography_country, _demography_total_population_high_table_0, 0), 1))

    return data.DEMOGRAPHY_TOTAL_POPULATION_HIGH.collect(evaluate(formula, data.DEMOGRAPHY_TOTAL_POPULATION_HIGH.required))

@publish(data.DEMOGRAPHY_TOTAL_POPULATION_LOW.schema, cells=data.DEMOGRAPHY_TOTAL_POPULATION_LOW.cells)
def demography_total_population_low(*, constant_demography_b1125_b1322: data.Series[str | None], constant_demography_bi1125_ev1322: data.Series[float | str | None], demography_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Compute total population for the low UN demographic scenario by country and projection period.

    Derives the low-scenario total population series used to grow primary expenditure in the long run, where spending per capita is held constant in the baseline.

    Args:
        constant_demography_b1125_b1322: Series providing the country lookup values used to align each country with its row in the low demography data.
        constant_demography_bi1125_ev1322: Series of low UN demographic scenario population figures by country and projection period, from which the total population value is drawn.
        demography_country: Country identifier for the economy whose low-scenario total population is being retrieved.

    Returns:
        The low UN demographic scenario total population series for the selected country across the projection horizon.
    """
    data.CONSTANT_DEMOGRAPHY_B1125_B1322.schema.validate(constant_demography_b1125_b1322)
    data.CONSTANT_DEMOGRAPHY_BI1125_EV1322.schema.validate(constant_demography_bi1125_ev1322)
    _demography_total_population_low_table_0 = view(constant_demography_b1125_b1322, rows=data.COUNTRY_AXIS_2.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(view(constant_demography_bi1125_ev1322, rows=data.COUNTRY_AXIS_2.keys, cols=(time_period,)), xl_match(demography_country, _demography_total_population_low_table_0, 0), 1))

    return data.DEMOGRAPHY_TOTAL_POPULATION_LOW.collect(evaluate(formula, data.DEMOGRAPHY_TOTAL_POPULATION_LOW.required))

@publish(key=(), domain=None, cells=data.PRODUCTIVITY_COUNTRY_CELLS)
def productivity_country(*, country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"]) -> str | int | float | bool:
    """Retrieve the productivity controller value for a country.

    Mirrors the Dashboard!C12 INDEX/MATCH country controller that selects the economy used for the Productivity worksheet projections.

    Args:
        country: Country name selecting the economy whose productivity controller value is returned; must be one of the Q-CRAFT supported economies.

    Returns:
        The productivity controller value selected through the Dashboard INDEX/MATCH lookup, or an error code string if the lookup fails.
    """
    try:
        return as_measure(country, 'str')
    except XlError as error:
        return error.code

@publish(key=(), domain=None, cells=data.PRODUCTIVITY_START_FLAG_CELLS)
def productivity_start_flag(*, productivity_start: Annotated[float, RealBetween(-100.0, 100.0)]) -> float | str:
    """Report the convergence start growth rate used to seed the productivity trajectory.

    Exposes the Dashboard productivity convergence start assumption so the long-run productivity path can be validated and traced to its source cell.

    Args:
        productivity_start: Convergence start growth rate for labor productivity, expressed in percent per year; the productivity growth rate carried into the start of the projection period.

    Returns:
        The convergence start growth rate as a numeric measure, or the spreadsheet error code if the value cannot be represented.
    """
    try:
        return as_measure(productivity_start)
    except XlError as error:
        return error.code

@publish(key=(), domain=None, cells=data.PRODUCTIVITY_END_FLAG_CELLS)
def productivity_end_flag(*, productivity_end: Annotated[float, RealBetween(-100.0, 100.0)]) -> float | str:
    """Flag the convergence end growth rate for the productivity path.

    Reads the long-run structural labor productivity growth rate the user enters as the 'end period' assumption for the 2090s, which Q-CRAFT uses to shape the productivity trajectory to 2100.

    Args:
        productivity_end: Structural labor productivity growth rate for the end period (2090s), in percent, expressed as GDP per employed person.

    Returns:
        The validated productivity end growth rate, or the spreadsheet error code if it falls outside the permitted range.
    """
    try:
        return as_measure(productivity_end)
    except XlError as error:
        return error.code

@publish(data.PRODUCTIVITY_LEVEL.schema, cells=data.PRODUCTIVITY_LEVEL.cells)
def productivity_level(*, constant_productivity_a63_a260: data.Series[str | None], constant_productivity_s63_ag260: data.Series[float | str | None], productivity_country: str | int | float | bool, productivity_start_flag: float | str, productivity_convergence_trajectory: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project labor productivity levels for the baseline scenario.

    Builds the GDP-per-employed-person trajectory used to grow nominal GDP, revenue, and primary expenditure over the long term.

    Args:
        constant_productivity_a63_a260: Country axis used to align the productivity level series with the economy selected in the dashboard.
        constant_productivity_s63_ag260: Historical productivity level by country and year, derived from WB WDI data, used for periods through 2022.
        productivity_country: Identifier of the country whose productivity level is being projected.
        productivity_start_flag: Start productivity growth rate, in percent a year, applied from 2023 to 2029.
        productivity_convergence_trajectory: Productivity growth rate, in percent a year, applied from 2030 onwards as the economy transitions to its long-run structural rate.

    Returns:
        The productivity level for each required year in the projection horizon, from historical data through the convergence path to 2100.
    """
    data.CONSTANT_PRODUCTIVITY_A63_A260.schema.validate(constant_productivity_a63_a260)
    data.CONSTANT_PRODUCTIVITY_S63_AG260.schema.validate(constant_productivity_s63_ag260)
    _productivity_level_table_0 = view(constant_productivity_a63_a260, rows=data.COUNTRY_AXIS_6.keys)
    def formula(time_period: int) -> float | str | None:
        if 2023 <= time_period <= 2029:
            return as_measure(xl_mul(productivity_level[time_period - 1], xl_add(1, xl_div(productivity_start_flag, 100))))
        elif time_period <= 2022:
            return as_measure(xl_index(((constant_productivity_s63_ag260['Afghanistan', time_period],), (constant_productivity_s63_ag260['Albania', time_period],), (constant_productivity_s63_ag260['Algeria', time_period],), (constant_productivity_s63_ag260['Andorra', time_period],), (constant_productivity_s63_ag260['Angola', time_period],), (None,), (constant_productivity_s63_ag260['Antigua and Barbuda', time_period],), (constant_productivity_s63_ag260['Argentina', time_period],), (constant_productivity_s63_ag260['Armenia', time_period],), (constant_productivity_s63_ag260['Aruba', time_period],), (constant_productivity_s63_ag260['Australia', time_period],), (constant_productivity_s63_ag260['Austria', time_period],), (constant_productivity_s63_ag260['Azerbaijan', time_period],), (constant_productivity_s63_ag260['The Bahamas', time_period],), (constant_productivity_s63_ag260['Bahrain', time_period],), (constant_productivity_s63_ag260['Bangladesh', time_period],), (constant_productivity_s63_ag260['Barbados', time_period],), (constant_productivity_s63_ag260['Belarus', time_period],), (constant_productivity_s63_ag260['Belgium', time_period],), (constant_productivity_s63_ag260['Belize', time_period],), (constant_productivity_s63_ag260['Benin', time_period],), (constant_productivity_s63_ag260['Bhutan', time_period],), (constant_productivity_s63_ag260['Bolivia', time_period],), (constant_productivity_s63_ag260['Bosnia and Herzegovina', time_period],), (constant_productivity_s63_ag260['Botswana', time_period],), (constant_productivity_s63_ag260['Brazil', time_period],), (constant_productivity_s63_ag260['Brunei Darussalam', time_period],), (constant_productivity_s63_ag260['Bulgaria', time_period],), (constant_productivity_s63_ag260['Burkina Faso', time_period],), (constant_productivity_s63_ag260['Burundi', time_period],), (constant_productivity_s63_ag260['Cabo Verde', time_period],), (constant_productivity_s63_ag260['Cambodia', time_period],), (constant_productivity_s63_ag260['Cameroon', time_period],), (constant_productivity_s63_ag260['Canada', time_period],), (constant_productivity_s63_ag260['Central African Republic', time_period],), (constant_productivity_s63_ag260['Chad', time_period],), (constant_productivity_s63_ag260['Chile', time_period],), (constant_productivity_s63_ag260['China', time_period],), (constant_productivity_s63_ag260['Colombia', time_period],), (constant_productivity_s63_ag260['Comoros', time_period],), (constant_productivity_s63_ag260['Democratic Republic of the Congo', time_period],), (constant_productivity_s63_ag260['Republic of Congo', time_period],), (constant_productivity_s63_ag260['Costa Rica', time_period],), (constant_productivity_s63_ag260["Côte d'Ivoire", time_period],), (constant_productivity_s63_ag260['Croatia', time_period],), (constant_productivity_s63_ag260['Cyprus', time_period],), (constant_productivity_s63_ag260['Czech Republic', time_period],), (constant_productivity_s63_ag260['Denmark', time_period],), (constant_productivity_s63_ag260['Djibouti', time_period],), (constant_productivity_s63_ag260['Dominica', time_period],), (constant_productivity_s63_ag260['Dominican Republic', time_period],), (constant_productivity_s63_ag260['Ecuador', time_period],), (constant_productivity_s63_ag260['Egypt', time_period],), (constant_productivity_s63_ag260['El Salvador', time_period],), (constant_productivity_s63_ag260['Equatorial Guinea', time_period],), (constant_productivity_s63_ag260['Eritrea', time_period],), (constant_productivity_s63_ag260['Estonia', time_period],), (constant_productivity_s63_ag260['Eswatini', time_period],), (constant_productivity_s63_ag260['Ethiopia', time_period],), (constant_productivity_s63_ag260['Fiji', time_period],), (constant_productivity_s63_ag260['Finland', time_period],), (constant_productivity_s63_ag260['France', time_period],), (constant_productivity_s63_ag260['Gabon', time_period],), (constant_productivity_s63_ag260['The Gambia', time_period],), (constant_productivity_s63_ag260['Georgia', time_period],), (constant_productivity_s63_ag260['Germany', time_period],), (constant_productivity_s63_ag260['Ghana', time_period],), (constant_productivity_s63_ag260['Greece', time_period],), (constant_productivity_s63_ag260['Grenada', time_period],), (constant_productivity_s63_ag260['Guatemala', time_period],), (constant_productivity_s63_ag260['Guinea', time_period],), (constant_productivity_s63_ag260['Guinea-Bissau', time_period],), (constant_productivity_s63_ag260['Guyana', time_period],), (constant_productivity_s63_ag260['Haiti', time_period],), (constant_productivity_s63_ag260['Honduras', time_period],), (constant_productivity_s63_ag260['Hong Kong SAR', time_period],), (constant_productivity_s63_ag260['Hungary', time_period],), (constant_productivity_s63_ag260['Iceland', time_period],), (constant_productivity_s63_ag260['India', time_period],), (constant_productivity_s63_ag260['Indonesia', time_period],), (constant_productivity_s63_ag260['Islamic Republic of Iran', time_period],), (constant_productivity_s63_ag260['Iraq', time_period],), (constant_productivity_s63_ag260['Ireland', time_period],), (constant_productivity_s63_ag260['Israel', time_period],), (constant_productivity_s63_ag260['Italy', time_period],), (constant_productivity_s63_ag260['Jamaica', time_period],), (constant_productivity_s63_ag260['Japan', time_period],), (constant_productivity_s63_ag260['Jordan', time_period],), (constant_productivity_s63_ag260['Kazakhstan', time_period],), (constant_productivity_s63_ag260['Kenya', time_period],), (constant_productivity_s63_ag260['Kiribati', time_period],), (constant_productivity_s63_ag260['Korea', time_period],), (constant_productivity_s63_ag260['Kosovo', time_period],), (constant_productivity_s63_ag260['Kuwait', time_period],), (constant_productivity_s63_ag260['Kyrgyz Republic', time_period],), (constant_productivity_s63_ag260['Lao P.D.R.', time_period],), (constant_productivity_s63_ag260['Latvia', time_period],), (constant_productivity_s63_ag260['Lebanon', time_period],), (constant_productivity_s63_ag260['Lesotho', time_period],), (constant_productivity_s63_ag260['Liberia', time_period],), (constant_productivity_s63_ag260['Libya', time_period],), (constant_productivity_s63_ag260['Lithuania', time_period],), (constant_productivity_s63_ag260['Luxembourg', time_period],), (constant_productivity_s63_ag260['Macao SAR', time_period],), (constant_productivity_s63_ag260['Madagascar', time_period],), (constant_productivity_s63_ag260['Malawi', time_period],), (constant_productivity_s63_ag260['Malaysia', time_period],), (constant_productivity_s63_ag260['Maldives', time_period],), (constant_productivity_s63_ag260['Mali', time_period],), (constant_productivity_s63_ag260['Malta', time_period],), (constant_productivity_s63_ag260['Marshall Islands', time_period],), (constant_productivity_s63_ag260['Mauritania', time_period],), (constant_productivity_s63_ag260['Mauritius', time_period],), (constant_productivity_s63_ag260['Mexico', time_period],), (constant_productivity_s63_ag260['Micronesia', time_period],), (constant_productivity_s63_ag260['Moldova', time_period],), (constant_productivity_s63_ag260['Mongolia', time_period],), (constant_productivity_s63_ag260['Montenegro', time_period],), (None,), (constant_productivity_s63_ag260['Morocco', time_period],), (constant_productivity_s63_ag260['Mozambique', time_period],), (constant_productivity_s63_ag260['Myanmar', time_period],), (constant_productivity_s63_ag260['Namibia', time_period],), (constant_productivity_s63_ag260['Nauru', time_period],), (constant_productivity_s63_ag260['Nepal', time_period],), (constant_productivity_s63_ag260['Netherlands', time_period],), (constant_productivity_s63_ag260['New Zealand', time_period],), (constant_productivity_s63_ag260['Nicaragua', time_period],), (constant_productivity_s63_ag260['Niger', time_period],), (constant_productivity_s63_ag260['Nigeria', time_period],), (constant_productivity_s63_ag260['North Macedonia', time_period],), (constant_productivity_s63_ag260['Norway', time_period],), (constant_productivity_s63_ag260['Oman', time_period],), (constant_productivity_s63_ag260['Pakistan', time_period],), (constant_productivity_s63_ag260['Palau', time_period],), (constant_productivity_s63_ag260['Panama', time_period],), (constant_productivity_s63_ag260['Papua New Guinea', time_period],), (constant_productivity_s63_ag260['Paraguay', time_period],), (constant_productivity_s63_ag260['Peru', time_period],), (constant_productivity_s63_ag260['Philippines', time_period],), (constant_productivity_s63_ag260['Poland', time_period],), (constant_productivity_s63_ag260['Portugal', time_period],), (constant_productivity_s63_ag260['Puerto Rico', time_period],), (constant_productivity_s63_ag260['Qatar', time_period],), (constant_productivity_s63_ag260['Romania', time_period],), (constant_productivity_s63_ag260['Russia', time_period],), (constant_productivity_s63_ag260['Rwanda', time_period],), (constant_productivity_s63_ag260['Samoa', time_period],), (constant_productivity_s63_ag260['San Marino', time_period],), (constant_productivity_s63_ag260['São Tomé and Príncipe', time_period],), (constant_productivity_s63_ag260['Saudi Arabia', time_period],), (constant_productivity_s63_ag260['Senegal', time_period],), (constant_productivity_s63_ag260['Serbia', time_period],), (constant_productivity_s63_ag260['Seychelles', time_period],), (constant_productivity_s63_ag260['Sierra Leone', time_period],), (constant_productivity_s63_ag260['Singapore', time_period],), (constant_productivity_s63_ag260['Slovak Republic', time_period],), (constant_productivity_s63_ag260['Slovenia', time_period],), (constant_productivity_s63_ag260['Solomon Islands', time_period],), (constant_productivity_s63_ag260['Somalia', time_period],), (constant_productivity_s63_ag260['South Africa', time_period],), (constant_productivity_s63_ag260['South Sudan', time_period],), (constant_productivity_s63_ag260['Spain', time_period],), (constant_productivity_s63_ag260['Sri Lanka', time_period],), (constant_productivity_s63_ag260['St. Kitts and Nevis', time_period],), (constant_productivity_s63_ag260['St. Lucia', time_period],), (constant_productivity_s63_ag260['St. Vincent and the Grenadines', time_period],), (constant_productivity_s63_ag260['Sudan', time_period],), (constant_productivity_s63_ag260['Suriname', time_period],), (constant_productivity_s63_ag260['Sweden', time_period],), (constant_productivity_s63_ag260['Switzerland', time_period],), (constant_productivity_s63_ag260['Syria', time_period],), (None,), (constant_productivity_s63_ag260['Tajikistan', time_period],), (constant_productivity_s63_ag260['Tanzania', time_period],), (constant_productivity_s63_ag260['Thailand', time_period],), (constant_productivity_s63_ag260['Timor-Leste', time_period],), (constant_productivity_s63_ag260['Togo', time_period],), (constant_productivity_s63_ag260['Tonga', time_period],), (constant_productivity_s63_ag260['Trinidad and Tobago', time_period],), (constant_productivity_s63_ag260['Tunisia', time_period],), (constant_productivity_s63_ag260['Turkiye', time_period],), (constant_productivity_s63_ag260['Turkmenistan', time_period],), (constant_productivity_s63_ag260['Tuvalu', time_period],), (constant_productivity_s63_ag260['Uganda', time_period],), (constant_productivity_s63_ag260['Ukraine', time_period],), (constant_productivity_s63_ag260['United Arab Emirates', time_period],), (constant_productivity_s63_ag260['United Kingdom', time_period],), (constant_productivity_s63_ag260['United States', time_period],), (constant_productivity_s63_ag260['Uruguay', time_period],), (constant_productivity_s63_ag260['Uzbekistan', time_period],), (constant_productivity_s63_ag260['Vanuatu', time_period],), (constant_productivity_s63_ag260['Venezuela', time_period],), (constant_productivity_s63_ag260['Vietnam', time_period],), (constant_productivity_s63_ag260['West Bank and Gaza', time_period],), (constant_productivity_s63_ag260['Yemen', time_period],), (constant_productivity_s63_ag260['Zambia', time_period],), (constant_productivity_s63_ag260['Zimbabwe', time_period],),), xl_match(productivity_country, _productivity_level_table_0, 0), 1))
        return as_measure(xl_mul(productivity_level[time_period - 1], xl_add(1, xl_div(productivity_convergence_trajectory[time_period - 29], 100))))

    productivity_level = CoordinateReader('productivity_level', data.PRODUCTIVITY_LEVEL.required, formula)
    return data.PRODUCTIVITY_LEVEL.collect((coord, productivity_level[coord]) for coord in data.PRODUCTIVITY_LEVEL.required)

@publish(data.PRODUCTIVITY_GROWTH.schema, cells=data.PRODUCTIVITY_GROWTH.cells)
def productivity_growth(*, productivity_level: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute year-over-year productivity growth as a percentage.

    Derives the annual growth rate of labor productivity, defined as GDP per employed person, from the level series so the long-term productivity trajectory can be projected.

    Args:
        productivity_level: Labor productivity level, measured as GDP per employed person, indexed by time period; the growth rate is the percent change from the prior period to the current period.

    Returns:
        Time series of productivity growth rates in percent, expressed as the year-over-year percentage change in the productivity level.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(productivity_level[time_period], productivity_level[time_period - 1]), 100), 100))

    return data.PRODUCTIVITY_GROWTH.collect(evaluate(formula, data.PRODUCTIVITY_GROWTH.required))

@publish(data.PRODUCTIVITY_CONVERGENCE_TRAJECTORY.schema, cells=data.PRODUCTIVITY_CONVERGENCE_TRAJECTORY.cells)
def productivity_convergence_trajectory(*, productivity_convergence_logistic_steepness: float | str, productivity_convergence_logistic_midpoint: float | str, productivity_convergence_period_index: data.Series[float | str | None], productivity_start_flag: float | str, productivity_end_flag: float | str) -> data.Series[float | str | None]:
    """Compute the logistic productivity convergence trajectory from a start to an end productivity growth rate.

    Produces the projected labor productivity growth rate for each period of the Q-CRAFT projection horizon, transitioning from the start-period productivity growth assumption to the end-period structural productivity growth assumption along a logistic path.

    Args:
        productivity_convergence_logistic_steepness: Steepness parameter of the logistic convergence function; determines the slope of the productivity growth transition. Set at 0.5 in Q-CRAFT and not intended to be changed.
        productivity_convergence_logistic_midpoint: Turning point of the logistic convergence function; the number of years into the projection horizon at which the economy transitions from the start productivity growth rate to the end productivity growth rate. Adjustable by the user.
        productivity_convergence_period_index: Index of the projection period used as the argument of the logistic function, giving the position in time at which the convergence path is evaluated for each period.
        productivity_start_flag: Start-period labor productivity growth rate assumption for the beginning of the projection horizon (2029).
        productivity_end_flag: End-period structural labor productivity growth rate assumption that the economy converges to by the end of the projection horizon (2090 to 2100).

    Returns:
        A series of projected labor productivity growth rates for each period of the projection horizon, transitioning from the start assumption to the end assumption along the logistic convergence trajectory.
    """
    data.PRODUCTIVITY_CONVERGENCE_PERIOD_INDEX.schema.validate(productivity_convergence_period_index)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(productivity_start_flag, xl_mul(xl_sub(productivity_end_flag, productivity_start_flag), xl_div(1, xl_pow(xl_add(1, xl_exp(xl_mul(xl_neg(productivity_convergence_logistic_steepness), xl_sub(productivity_convergence_period_index[time_period], productivity_convergence_logistic_midpoint)))), productivity_convergence_logistic_steepness)))))

    return data.PRODUCTIVITY_CONVERGENCE_TRAJECTORY.collect(evaluate(formula, data.PRODUCTIVITY_CONVERGENCE_TRAJECTORY.required))

@publish(key=(), domain=None, cells=data.INFLATION_START_FLAG_CELLS)
def inflation_start_flag(*, inflation_start: Annotated[float, RealBetween(-100.0, 100.0)]) -> float | str:
    """Return the convergence start inflation value as a measure.

    Captures the inflation rate at which convergence begins, mirroring Dashboard!C24.

    Args:
        inflation_start: Convergence start inflation rate, in percent, bounded between -100.0 and 100.0.

    Returns:
        The convergence start inflation as a measure, or the error code string if the value cannot be converted.
    """
    try:
        return as_measure(inflation_start)
    except XlError as error:
        return error.code

@publish(key=(), domain=None, cells=data.INFLATION_END_FLAG_CELLS)
def inflation_end_flag(*, inflation_end: Annotated[float, RealBetween(-100.0, 100.0)]) -> float | str:
    """Return the long-run end-period inflation assumption as a measure.

    Provides the convergence end inflation rate that anchors the baseline inflation trajectory, mirroring the Dashboard's convergence end inflation input.

    Args:
        inflation_end: Long-run end-period inflation rate, in percent, that inflation converges to by the end of the projection horizon; should reflect the central bank's inflation target.

    Returns:
        The end-period inflation rate as a measure, or an Excel error code string if the value is invalid.
    """
    try:
        return as_measure(inflation_end)
    except XlError as error:
        return error.code

@publish(data.INFLATION_PATH.schema, cells=data.INFLATION_PATH.cells)
def inflation_path(*, macrofiscal_gdp_deflator_growth: data.Series[float | str | None], inflation_convergence_trajectory: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Build the long-run inflation path from the WEO GDP deflator growth and the user's inflation convergence trajectory.

    Stitches the final IMF WEO GDP deflator growth onto the constant long-run inflation assumption so that a single inflation path is available for the nominal GDP projection.

    Args:
        macrofiscal_gdp_deflator_growth: Growth of the GDP deflator over the WEO horizon, taken from the Macro-fiscal worksheet; the 2029 value of this series provides the start of the long-run inflation path.
        inflation_convergence_trajectory: User-specified long-run inflation assumption, entered in the Dashboard and reflecting the Central Bank's inflation target, which keeps inflation constant over the projection period.

    Returns:
        The inflation path, which starts from the WEO GDP deflator growth at the end of the WEO horizon and then follows the user's constant long-run inflation assumption.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period == 2029:
            return as_measure(macrofiscal_gdp_deflator_growth[time_period])
        return as_measure(inflation_convergence_trajectory[time_period - 28])

    return data.INFLATION_PATH.collect(evaluate(formula, data.INFLATION_PATH.required))

@publish(data.INFLATION_CONVERGENCE_TRAJECTORY.schema, cells=data.INFLATION_CONVERGENCE_TRAJECTORY.cells)
def inflation_convergence_trajectory(*, inflation_convergence_logistic_steepness: float | str, inflation_convergence_logistic_midpoint: float | str, inflation_convergence_period_index: data.Series[float | str | None], inflation_start_flag: float | str, inflation_end_flag: float | str) -> data.Series[float | str | None]:
    """Project an inflation convergence trajectory over the projection horizon.

    Interpolate the inflation path from the start-period to the end-period assumption using a logistic convergence profile.

    Args:
        inflation_convergence_logistic_steepness: Slope parameter of the logistic function that governs how quickly inflation transitions from the start-period to the end-period assumption.
        inflation_convergence_logistic_midpoint: Turning point of the logistic function, expressed as the time period at which the inflation transition is halfway between the start-period and end-period assumptions.
        inflation_convergence_period_index: Time-period index aligned with the projection horizon, used to evaluate the logistic convergence profile at each period.
        inflation_start_flag: Inflation rate assumed at the start of the projection horizon, typically the WEO projection for the first projection year.
        inflation_end_flag: Inflation rate assumed for the end period, reflecting the Central Bank's long-run inflation target or structural inflation assumption.

    Returns:
        A series of inflation rates along the projection horizon, converging from the start-period assumption to the end-period assumption in line with stable long-run inflation.
    """
    data.INFLATION_CONVERGENCE_PERIOD_INDEX.schema.validate(inflation_convergence_period_index)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(inflation_start_flag, xl_mul(xl_sub(inflation_end_flag, inflation_start_flag), xl_div(1, xl_pow(xl_add(1, xl_exp(xl_mul(xl_neg(inflation_convergence_logistic_steepness), xl_sub(inflation_convergence_period_index[time_period], inflation_convergence_logistic_midpoint)))), inflation_convergence_logistic_steepness)))))

    return data.INFLATION_CONVERGENCE_TRAJECTORY.collect(evaluate(formula, data.INFLATION_CONVERGENCE_TRAJECTORY.required))

@publish(key=(), domain=None, cells=data.INTEREST_RATE_MODE_FLAG_CELLS)
def interest_rate_mode_flag(*, interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"]) -> str | int | float | bool:
    """Read the selected long-run interest rate assumption.

    Mirrors Dashboard!C28 so the chosen interest rate assumption row is identified for the projection.

    Args:
        interest_rate_mode: Interest rate assumption selected in the Dashboard; one of the constant nominal interest rate, the constant (nominal) interest-growth differential, or the constant real interest rate options offered by Q-CRAFT.

    Returns:
        The interest rate assumption label, or the spreadsheet error code if the mode cannot be read as a string.
    """
    try:
        return as_measure(interest_rate_mode, 'str')
    except XlError as error:
        return error.code

@publish(key=(), domain=None, cells=data.INTEREST_RATE_END_OF_MTFF_CELLS)
def interest_rate_end_of_mtff(*, macrofiscal_interest_rate: data.Series[float | str | None]) -> float | str:
    """Return the interest rate at the end of the medium-term fiscal framework.

    Provides the terminal interest rate assumption for the medium-term fiscal framework so it can anchor long-term debt-dynamics projections.

    Args:
        macrofiscal_interest_rate: Series of interest rate assumptions for the macrofiscal projection horizon; the value for 2029, the end of the medium-term fiscal framework, is selected.

    Returns:
        The interest rate at the end of the medium-term fiscal framework as a float, or the error code string if the value cannot be resolved.
    """
    try:
        return as_measure(macrofiscal_interest_rate[2029])
    except XlError as error:
        return error.code

@publish(key=(), domain=None, cells=data.INTEREST_GROWTH_DIFFERENTIAL_END_OF_MTFF_CELLS)
def interest_growth_differential_end_of_mtff(*, macrofiscal_interest_growth_differential: data.Series[float | str | None]) -> float | str:
    """Return the interest-growth differential at the end of the medium-term fiscal framework.

    Provides the terminal interest-growth differential used to anchor long-term debt dynamics beyond the medium-term fiscal framework horizon.

    Args:
        macrofiscal_interest_growth_differential: Interest-growth differential series from the macro-fiscal projections; the value at the end of the medium-term fiscal framework is extracted and converted to a measure.

    Returns:
        The interest-growth differential at the end of the medium-term fiscal framework as a float, or the error code string if the underlying value cannot be converted to a measure.
    """
    try:
        return as_measure(macrofiscal_interest_growth_differential[2029])
    except XlError as error:
        return error.code

@publish(key=(), domain=None, cells=data.INTEREST_RATE_LONG_RUN_REAL_RATE_CELLS)
def interest_rate_long_run_real_rate(*, real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)]) -> float | str:
    """Return the assumed long-run real interest rate as a measure.

    Provide the long-run real interest rate assumption used by the interest rate worksheet, mirroring Dashboard!C29.

    Args:
        real_interest_rate: Assumed long-run real interest rate, expressed in percent, used for the constant real interest rate projection option.

    Returns:
        The real interest rate as a measure, or the spreadsheet error code if the value is invalid.
    """
    try:
        return as_measure(real_interest_rate)
    except XlError as error:
        return error.code

@publish(data.INTEREST_RATE_NOMINAL_INTEREST_RATE.schema, cells=data.INTEREST_RATE_NOMINAL_INTEREST_RATE.cells)
def interest_rate_nominal_interest_rate(*, macrofiscal_interest_rate: data.Series[float | str | None], interest_rate_long_run_assumption: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the nominal interest rate over the Q-CRAFT horizon by splicing the macrofiscal rate into the long-run assumption.

    Provides the weighted average nominal interest rate on government debt used in the debt-dynamics equation for the baseline and climate scenarios.

    Args:
        macrofiscal_interest_rate: Nominal interest rate from the macrofiscal worksheet used through the end of the WEO horizon (to 2029).
        interest_rate_long_run_assumption: Long-run nominal interest rate path applied from 2030 onward, per the constant nominal interest rate, constant interest-growth differential, or constant real interest rate assumption.

    Returns:
        A series of the projected nominal interest rate for each year of the projection horizon, taken from the macrofiscal rate up to 2029 and the long-run assumption thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_interest_rate[time_period])
        return as_measure(interest_rate_long_run_assumption[time_period - 28])

    return data.INTEREST_RATE_NOMINAL_INTEREST_RATE.collect(evaluate(formula, data.INTEREST_RATE_NOMINAL_INTEREST_RATE.required))

@publish(data.INTEREST_RATE_NOMINAL_GDP_GROWTH_BASELINE.schema, cells=data.INTEREST_RATE_NOMINAL_GDP_GROWTH_BASELINE.cells)
def interest_rate_nominal_gdp_growth_baseline(*, macrofiscal_nominal_gdp_growth: data.Series[float | str | None], baseline_nominal_gdp_growth: data.BaselineNominalGdpGrowth) -> data.Series[float | str | None]:
    """Build the baseline nominal interest-growth differential series for the interest rate projection.

    Provides the long-run interest-growth differential used in the debt dynamics equation, anchored to the observed macro-fiscal nominal GDP growth in the final year of the WEO horizon and to the assumed growth thereafter.

    Args:
        macrofiscal_nominal_gdp_growth: Nominal GDP growth from the macro-fiscal data; its 2029 value, the last year before the Q-CRAFT projection period, anchors the interest-growth differential at the start of the projection.
        baseline_nominal_gdp_growth: Baseline scenario nominal GDP growth, expressed as the sum of employment growth, productivity growth, and inflation, which governs the interest-growth differential from 2030 onward.

    Returns:
        A series of the baseline nominal interest-growth differential over the projection horizon, equal to macro-fiscal nominal GDP growth in 2029 and to baseline nominal GDP growth thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period == 2029:
            return as_measure(macrofiscal_nominal_gdp_growth[time_period])
        return as_measure(baseline_nominal_gdp_growth[time_period])

    return data.INTEREST_RATE_NOMINAL_GDP_GROWTH_BASELINE.collect(evaluate(formula, data.INTEREST_RATE_NOMINAL_GDP_GROWTH_BASELINE.required))

@publish(data.INTEREST_RATE_INFLATION_BASELINE.schema, cells=data.INTEREST_RATE_INFLATION_BASELINE.cells)
def interest_rate_inflation_baseline(*, macrofiscal_gdp_deflator_growth: data.Series[float | str | None], baseline_gdp_deflator_growth: data.BaselineGdpDeflatorGrowth) -> data.Series[float | str | None]:
    """Assemble the interest rate inflation baseline from GDP deflator growth.

    Provides the long-run inflation profile used to derive nominal interest rate paths in the baseline scenario, anchoring inflation to the Central Bank's target while nominal GDP and revenue are projected.

    Args:
        macrofiscal_gdp_deflator_growth: Growth in the GDP deflator over the macro-fiscal projection period, taken from the loaded macro-fiscal data; its 2029 value serves as the starting inflation rate.
        baseline_gdp_deflator_growth: Growth in the GDP deflator under the user's baseline assumptions, used as the long-run constant inflation rate from 2030 onward.

    Returns:
        A series of GDP deflator growth rates that starts from the macro-fiscal 2029 value and continues with the baseline assumptions for later years.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period == 2029:
            return as_measure(macrofiscal_gdp_deflator_growth[time_period])
        return as_measure(baseline_gdp_deflator_growth[time_period])

    return data.INTEREST_RATE_INFLATION_BASELINE.collect(evaluate(formula, data.INTEREST_RATE_INFLATION_BASELINE.required))

@publish(data.INTEREST_RATE_LONG_RUN_ASSUMPTION.schema, cells=data.INTEREST_RATE_LONG_RUN_ASSUMPTION.cells)
def interest_rate_long_run_assumption(*, interest_rate_assumption_label_nominal: str, interest_rate_assumption_label_differential: str, interest_rate_assumption_label_real: str, interest_rate_mode_flag: str | int | float | bool, interest_rate_long_run_nominal_interest_rate: data.Series[float | str | None], interest_rate_long_run_interest_growth_differential: data.Series[float | str | None], interest_rate_long_run_real_interest_rate: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Select the long-run interest rate assumption consistent with the chosen interest rate mode.

    Resolve, for each projection year, the long-run interest rate path implied by the user's choice between the constant nominal interest rate, constant (nominal) interest-growth differential, and constant real interest rate options.

    Args:
        interest_rate_assumption_label_nominal: Mode label identifying the constant nominal interest rate assumption.
        interest_rate_assumption_label_differential: Mode label identifying the constant (nominal) interest-growth differential assumption.
        interest_rate_assumption_label_real: Mode label identifying the constant real interest rate assumption.
        interest_rate_mode_flag: Selected interest rate assumption mode, matched against the mode labels to determine which long-run interest rate profile is used.
        interest_rate_long_run_nominal_interest_rate: Long-run nominal interest rate profile used when the constant nominal interest rate assumption is selected.
        interest_rate_long_run_interest_growth_differential: Long-run (nominal) interest-growth differential profile used when the constant interest-growth differential assumption is selected.
        interest_rate_long_run_real_interest_rate: Long-run real interest rate profile used when the constant real interest rate assumption is selected.

    Returns:
        The long-run interest rate assumption series over the projection horizon, drawn from the profile matching the selected interest rate mode.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure((interest_rate_long_run_nominal_interest_rate[time_period] if xl_bool(xl_eq(interest_rate_mode_flag, interest_rate_assumption_label_nominal)) else (interest_rate_long_run_interest_growth_differential[time_period] if xl_bool(xl_eq(interest_rate_mode_flag, interest_rate_assumption_label_differential)) else (interest_rate_long_run_real_interest_rate[time_period] if xl_bool(xl_eq(interest_rate_mode_flag, interest_rate_assumption_label_real)) else '"'))))

    return data.INTEREST_RATE_LONG_RUN_ASSUMPTION.collect(evaluate(formula, data.INTEREST_RATE_LONG_RUN_ASSUMPTION.required))

@publish(data.INTEREST_RATE_LONG_RUN_NOMINAL_INTEREST_RATE.schema, cells=data.INTEREST_RATE_LONG_RUN_NOMINAL_INTEREST_RATE.cells)
def interest_rate_long_run_nominal_interest_rate(*, interest_rate_end_of_mtff: float | str) -> data.Series[float | str | None]:
    """Project the long-run nominal interest rate from the end of the medium-term fiscal framework horizon.

    Establish the nominal interest rate assumption used in the interest rate assumptions of the baseline scenario for the long-term horizon.

    Args:
        interest_rate_end_of_mtff: Nominal interest rate at the last year of the medium-term fiscal framework horizon, which is held constant in the long run.

    Returns:
        Time series of the projected long-run nominal interest rate.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(interest_rate_end_of_mtff)

    return data.INTEREST_RATE_LONG_RUN_NOMINAL_INTEREST_RATE.collect(evaluate(formula, data.INTEREST_RATE_LONG_RUN_NOMINAL_INTEREST_RATE.required))

@publish(data.INTEREST_RATE_LONG_RUN_INTEREST_GROWTH_DIFFERENTIAL.schema, cells=data.INTEREST_RATE_LONG_RUN_INTEREST_GROWTH_DIFFERENTIAL.cells)
def interest_rate_long_run_interest_growth_differential(*, interest_growth_differential_end_of_mtff: float | str, interest_rate_nominal_gdp_growth_baseline: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Project the long-run nominal interest rate path implied by a constant interest-growth differential.

    Translate the user's chosen interest-growth differential assumption into a nominal interest rate series for the long-term baseline, consistent with the projected nominal GDP growth path.

    Args:
        interest_growth_differential_end_of_mtff: Assumed interest-growth differential (percentage points) held constant from the end of the medium-term fiscal framework horizon onward; widens the effective growth-adjusted discount factor applied to debt in the baseline.
        interest_rate_nominal_gdp_growth_baseline: Baseline growth rate of nominal GDP (in percent) used to reanchor the constant differential into a nominal interest rate profile over the projection horizon.

    Returns:
        A series of long-run nominal interest rates for each projection period, derived by combining the baseline nominal GDP growth path with the assumed constant interest-growth differential.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(interest_rate_nominal_gdp_growth_baseline[time_period + 27], 100)), xl_add(1, xl_div(interest_growth_differential_end_of_mtff, 100))), 100), 100))

    return data.INTEREST_RATE_LONG_RUN_INTEREST_GROWTH_DIFFERENTIAL.collect(evaluate(formula, data.INTEREST_RATE_LONG_RUN_INTEREST_GROWTH_DIFFERENTIAL.required))

@publish(data.INTEREST_RATE_LONG_RUN_REAL_INTEREST_RATE.schema, cells=data.INTEREST_RATE_LONG_RUN_REAL_INTEREST_RATE.cells)
def interest_rate_long_run_real_interest_rate(*, interest_rate_long_run_real_rate: float | str, interest_rate_inflation_baseline: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the long-run constant real interest rate path from the user's real rate assumption and the baseline inflation path.

    Supports the constant real interest rate option in Q-CRAFT's Interest Rate worksheet, where the user sets a long-run real interest rate (which could be aligned with the country's estimated neutral rate of real interest, or r-star) that remains constant from 2029 onward.

    Args:
        interest_rate_long_run_real_rate: The user's assumption for the long-run real interest rate, in percent, used when interest rates are projected under the constant real interest rate option.
        interest_rate_inflation_baseline: The baseline inflation path, in percent, reflecting the assumed long-run stable inflation consistent with the Central Bank's target; used together with the real rate to derive the long-run profile of the real interest rate.

    Returns:
        A series holding the projected long-run real interest rate for each period of the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(interest_rate_long_run_real_rate, 100)), xl_add(1, xl_div(interest_rate_inflation_baseline[time_period + 27], 100))), 100), 100))

    return data.INTEREST_RATE_LONG_RUN_REAL_INTEREST_RATE.collect(evaluate(formula, data.INTEREST_RATE_LONG_RUN_REAL_INTEREST_RATE.required))

@publish(key=(), domain=None, cells=data.CLIMATE_DATABASE_COUNTRY_CELLS)
def climate_database_country(*, country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"]) -> str | int | float | bool:
    """Resolve the Q-CRAFT climate database entry for the selected country.

    Mirrors the Dashboard!C12 INDEX/MATCH country controller so the climate data used in scenario generation follows the country chosen on the Dashboard.

    Args:
        country: Country selected in the Dashboard, matching the Q-CRAFT climate database coverage.

    Returns:
        The climate database country entry, or the Excel error code if the lookup fails.
    """
    try:
        return as_measure(country, 'str')
    except XlError as error:
        return error.code

@publish(data.CLIMATE_DATABASE_GDP_LOSS_PCT_PARIS.schema, cells=data.CLIMATE_DATABASE_GDP_LOSS_PCT_PARIS.cells)
def climate_database_gdp_loss_pct_paris(*, constant_climate_database_b26_b223: data.Series[str | None], constant_climate_database_q26_ci223: data.Series[float | str | None], climate_database_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Extract the Paris scenario GDP loss percentage for a selected country.

    Populates the GDP loss (in percent) relative to the baseline under the Paris (SSP1-2.6) climate scenario, which assumes the 2015 Paris Agreement commitments are met.

    Args:
        constant_climate_database_b26_b223: Constant climate database table supplying the country axis used to align the Paris scenario series by country.
        constant_climate_database_q26_ci223: Constant climate database series, indexed by country and time period, of GDP loss estimates under the Paris climate scenario.
        climate_database_country: Country whose Paris scenario GDP loss percentage is to be extracted.

    Returns:
        A series of GDP loss percentages under the Paris climate scenario for the selected country, aligned to the projection time periods.
    """
    data.CONSTANT_CLIMATE_DATABASE_B26_B223.schema.validate(constant_climate_database_b26_b223)
    data.CONSTANT_CLIMATE_DATABASE_Q26_CI223.schema.validate(constant_climate_database_q26_ci223)
    _climate_database_gdp_loss_pct_paris_table_0 = view(constant_climate_database_b26_b223, rows=data.COUNTRY_AXIS_4.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(((constant_climate_database_q26_ci223['Afghanistan', time_period],), (constant_climate_database_q26_ci223['Albania', time_period],), (constant_climate_database_q26_ci223['Algeria', time_period],), (None,), (constant_climate_database_q26_ci223['Angola', time_period],), (None,), (None,), (constant_climate_database_q26_ci223['Argentina', time_period],), (constant_climate_database_q26_ci223['Armenia', time_period],), (None,), (constant_climate_database_q26_ci223['Australia', time_period],), (constant_climate_database_q26_ci223['Austria', time_period],), (constant_climate_database_q26_ci223['Azerbaijan', time_period],), (constant_climate_database_q26_ci223['The Bahamas', time_period],), (None,), (constant_climate_database_q26_ci223['Bangladesh', time_period],), (None,), (constant_climate_database_q26_ci223['Belarus', time_period],), (constant_climate_database_q26_ci223['Belgium', time_period],), (constant_climate_database_q26_ci223['Belize', time_period],), (constant_climate_database_q26_ci223['Benin', time_period],), (constant_climate_database_q26_ci223['Bhutan', time_period],), (constant_climate_database_q26_ci223['Bolivia', time_period],), (constant_climate_database_q26_ci223['Bosnia and Herzegovina', time_period],), (constant_climate_database_q26_ci223['Botswana', time_period],), (constant_climate_database_q26_ci223['Brazil', time_period],), (constant_climate_database_q26_ci223['Brunei Darussalam', time_period],), (constant_climate_database_q26_ci223['Bulgaria', time_period],), (constant_climate_database_q26_ci223['Burkina Faso', time_period],), (constant_climate_database_q26_ci223['Burundi', time_period],), (constant_climate_database_q26_ci223['Cabo Verde', time_period],), (constant_climate_database_q26_ci223['Cambodia', time_period],), (constant_climate_database_q26_ci223['Cameroon', time_period],), (constant_climate_database_q26_ci223['Canada', time_period],), (constant_climate_database_q26_ci223['Central African Republic', time_period],), (constant_climate_database_q26_ci223['Chad', time_period],), (constant_climate_database_q26_ci223['Chile', time_period],), (constant_climate_database_q26_ci223['China', time_period],), (constant_climate_database_q26_ci223['Colombia', time_period],), (constant_climate_database_q26_ci223['Comoros', time_period],), (constant_climate_database_q26_ci223['Democratic Republic of the Congo', time_period],), (constant_climate_database_q26_ci223['Republic of Congo', time_period],), (constant_climate_database_q26_ci223['Costa Rica', time_period],), (constant_climate_database_q26_ci223["Côte d'Ivoire", time_period],), (constant_climate_database_q26_ci223['Croatia', time_period],), (constant_climate_database_q26_ci223['Cyprus', time_period],), (constant_climate_database_q26_ci223['Czech Republic', time_period],), (constant_climate_database_q26_ci223['Denmark', time_period],), (constant_climate_database_q26_ci223['Djibouti', time_period],), (None,), (constant_climate_database_q26_ci223['Dominican Republic', time_period],), (constant_climate_database_q26_ci223['Ecuador', time_period],), (constant_climate_database_q26_ci223['Egypt', time_period],), (constant_climate_database_q26_ci223['El Salvador', time_period],), (constant_climate_database_q26_ci223['Equatorial Guinea', time_period],), (constant_climate_database_q26_ci223['Eritrea', time_period],), (constant_climate_database_q26_ci223['Estonia', time_period],), (constant_climate_database_q26_ci223['Eswatini', time_period],), (constant_climate_database_q26_ci223['Ethiopia', time_period],), (constant_climate_database_q26_ci223['Fiji', time_period],), (constant_climate_database_q26_ci223['Finland', time_period],), (constant_climate_database_q26_ci223['France', time_period],), (constant_climate_database_q26_ci223['Gabon', time_period],), (constant_climate_database_q26_ci223['The Gambia', time_period],), (constant_climate_database_q26_ci223['Georgia', time_period],), (constant_climate_database_q26_ci223['Germany', time_period],), (constant_climate_database_q26_ci223['Ghana', time_period],), (constant_climate_database_q26_ci223['Greece', time_period],), (constant_climate_database_q26_ci223['Grenada', time_period],), (constant_climate_database_q26_ci223['Guatemala', time_period],), (constant_climate_database_q26_ci223['Guinea', time_period],), (constant_climate_database_q26_ci223['Guinea-Bissau', time_period],), (constant_climate_database_q26_ci223['Guyana', time_period],), (constant_climate_database_q26_ci223['Haiti', time_period],), (constant_climate_database_q26_ci223['Honduras', time_period],), (None,), (constant_climate_database_q26_ci223['Hungary', time_period],), (constant_climate_database_q26_ci223['Iceland', time_period],), (constant_climate_database_q26_ci223['India', time_period],), (constant_climate_database_q26_ci223['Indonesia', time_period],), (constant_climate_database_q26_ci223['Islamic Republic of Iran', time_period],), (constant_climate_database_q26_ci223['Iraq', time_period],), (constant_climate_database_q26_ci223['Ireland', time_period],), (constant_climate_database_q26_ci223['Israel', time_period],), (constant_climate_database_q26_ci223['Italy', time_period],), (constant_climate_database_q26_ci223['Jamaica', time_period],), (constant_climate_database_q26_ci223['Japan', time_period],), (constant_climate_database_q26_ci223['Jordan', time_period],), (constant_climate_database_q26_ci223['Kazakhstan', time_period],), (constant_climate_database_q26_ci223['Kenya', time_period],), (None,), (constant_climate_database_q26_ci223['Korea', time_period],), (None,), (constant_climate_database_q26_ci223['Kuwait', time_period],), (constant_climate_database_q26_ci223['Kyrgyz Republic', time_period],), (constant_climate_database_q26_ci223['Lao P.D.R.', time_period],), (constant_climate_database_q26_ci223['Latvia', time_period],), (constant_climate_database_q26_ci223['Lebanon', time_period],), (constant_climate_database_q26_ci223['Lesotho', time_period],), (constant_climate_database_q26_ci223['Liberia', time_period],), (constant_climate_database_q26_ci223['Libya', time_period],), (constant_climate_database_q26_ci223['Lithuania', time_period],), (constant_climate_database_q26_ci223['Luxembourg', time_period],), (None,), (constant_climate_database_q26_ci223['Madagascar', time_period],), (constant_climate_database_q26_ci223['Malawi', time_period],), (constant_climate_database_q26_ci223['Malaysia', time_period],), (None,), (constant_climate_database_q26_ci223['Mali', time_period],), (None,), (None,), (constant_climate_database_q26_ci223['Mauritania', time_period],), (constant_climate_database_q26_ci223['Mauritius', time_period],), (constant_climate_database_q26_ci223['Mexico', time_period],), (None,), (constant_climate_database_q26_ci223['Moldova', time_period],), (constant_climate_database_q26_ci223['Mongolia', time_period],), (constant_climate_database_q26_ci223['Montenegro', time_period],), (None,), (constant_climate_database_q26_ci223['Morocco', time_period],), (constant_climate_database_q26_ci223['Mozambique', time_period],), (constant_climate_database_q26_ci223['Myanmar', time_period],), (constant_climate_database_q26_ci223['Namibia', time_period],), (None,), (constant_climate_database_q26_ci223['Nepal', time_period],), (constant_climate_database_q26_ci223['Netherlands', time_period],), (constant_climate_database_q26_ci223['New Zealand', time_period],), (constant_climate_database_q26_ci223['Nicaragua', time_period],), (constant_climate_database_q26_ci223['Niger', time_period],), (constant_climate_database_q26_ci223['Nigeria', time_period],), (constant_climate_database_q26_ci223['North Macedonia', time_period],), (constant_climate_database_q26_ci223['Norway', time_period],), (constant_climate_database_q26_ci223['Oman', time_period],), (constant_climate_database_q26_ci223['Pakistan', time_period],), (None,), (constant_climate_database_q26_ci223['Panama', time_period],), (constant_climate_database_q26_ci223['Papua New Guinea', time_period],), (constant_climate_database_q26_ci223['Paraguay', time_period],), (constant_climate_database_q26_ci223['Peru', time_period],), (constant_climate_database_q26_ci223['Philippines', time_period],), (constant_climate_database_q26_ci223['Poland', time_period],), (constant_climate_database_q26_ci223['Portugal', time_period],), (constant_climate_database_q26_ci223['Puerto Rico', time_period],), (constant_climate_database_q26_ci223['Qatar', time_period],), (constant_climate_database_q26_ci223['Romania', time_period],), (constant_climate_database_q26_ci223['Russia', time_period],), (constant_climate_database_q26_ci223['Rwanda', time_period],), (constant_climate_database_q26_ci223['Samoa', time_period],), (constant_climate_database_q26_ci223['San Marino', time_period],), (constant_climate_database_q26_ci223['Sao Tome and Principe', time_period],), (constant_climate_database_q26_ci223['Saudi Arabia', time_period],), (constant_climate_database_q26_ci223['Senegal', time_period],), (constant_climate_database_q26_ci223['Serbia', time_period],), (None,), (constant_climate_database_q26_ci223['Sierra Leone', time_period],), (None,), (constant_climate_database_q26_ci223['Slovak Republic', time_period],), (constant_climate_database_q26_ci223['Slovenia', time_period],), (constant_climate_database_q26_ci223['Solomon Islands', time_period],), (constant_climate_database_q26_ci223['Somalia', time_period],), (constant_climate_database_q26_ci223['South Africa', time_period],), (constant_climate_database_q26_ci223['South Sudan', time_period],), (constant_climate_database_q26_ci223['Spain', time_period],), (constant_climate_database_q26_ci223['Sri Lanka', time_period],), (None,), (None,), (constant_climate_database_q26_ci223['St. Vincent and the Grenadines', time_period],), (constant_climate_database_q26_ci223['Sudan', time_period],), (constant_climate_database_q26_ci223['Suriname', time_period],), (constant_climate_database_q26_ci223['Sweden', time_period],), (constant_climate_database_q26_ci223['Switzerland', time_period],), (constant_climate_database_q26_ci223['Syria', time_period],), (None,), (constant_climate_database_q26_ci223['Tajikistan', time_period],), (constant_climate_database_q26_ci223['Tanzania', time_period],), (constant_climate_database_q26_ci223['Thailand', time_period],), (None,), (constant_climate_database_q26_ci223['Togo', time_period],), (None,), (constant_climate_database_q26_ci223['Trinidad and Tobago', time_period],), (constant_climate_database_q26_ci223['Tunisia', time_period],), (constant_climate_database_q26_ci223['Türkiye', time_period],), (constant_climate_database_q26_ci223['Turkmenistan', time_period],), (None,), (constant_climate_database_q26_ci223['Uganda', time_period],), (constant_climate_database_q26_ci223['Ukraine', time_period],), (constant_climate_database_q26_ci223['United Arab Emirates', time_period],), (constant_climate_database_q26_ci223['United Kingdom', time_period],), (constant_climate_database_q26_ci223['United States', time_period],), (constant_climate_database_q26_ci223['Uruguay', time_period],), (constant_climate_database_q26_ci223['Uzbekistan', time_period],), (constant_climate_database_q26_ci223['Vanuatu', time_period],), (constant_climate_database_q26_ci223['Venezuela', time_period],), (constant_climate_database_q26_ci223['Vietnam', time_period],), (None,), (constant_climate_database_q26_ci223['Yemen', time_period],), (constant_climate_database_q26_ci223['Zambia', time_period],), (constant_climate_database_q26_ci223['Zimbabwe', time_period],),), xl_match(climate_database_country, _climate_database_gdp_loss_pct_paris_table_0, 0), 1))

    return data.CLIMATE_DATABASE_GDP_LOSS_PCT_PARIS.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_LOSS_PCT_PARIS.required))

@publish(data.CLIMATE_DATABASE_GDP_LOSS_PCT_MODERATE.schema, cells=data.CLIMATE_DATABASE_GDP_LOSS_PCT_MODERATE.cells)
def climate_database_gdp_loss_pct_moderate(*, constant_climate_database_b226_b423: data.Series[str | None], constant_climate_database_q226_ci423: data.Series[float | str | None], climate_database_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Return the projected GDP loss under the moderate climate scenario for a given country.

    Provide the moderate-scenario GDP loss (percent) used to quantify the long-term macroeconomic effects of climate change in Q-CRAFT.

    Args:
        constant_climate_database_b226_b423: Constant climate database series supplying the country dimension used to align the moderate-scenario lookup.
        constant_climate_database_q226_ci423: Constant climate database series of moderate-scenario GDP loss estimates indexed by country and projection period.
        climate_database_country: Country identifier (name or code) selecting which economy's moderate-scenario GDP loss is returned.

    Returns:
        A series of projected GDP losses in percent under the moderate climate scenario, aligned to the projection horizon.
    """
    data.CONSTANT_CLIMATE_DATABASE_B226_B423.schema.validate(constant_climate_database_b226_b423)
    data.CONSTANT_CLIMATE_DATABASE_Q226_CI423.schema.validate(constant_climate_database_q226_ci423)
    _climate_database_gdp_loss_pct_moderate_table_0 = view(constant_climate_database_b226_b423, rows=data.COUNTRY_AXIS_5.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(((constant_climate_database_q226_ci423['Afghanistan', time_period],), (constant_climate_database_q226_ci423['Albania', time_period],), (constant_climate_database_q226_ci423['Algeria', time_period],), (None,), (constant_climate_database_q226_ci423['Angola', time_period],), (None,), (None,), (constant_climate_database_q226_ci423['Argentina', time_period],), (constant_climate_database_q226_ci423['Armenia', time_period],), (None,), (constant_climate_database_q226_ci423['Australia', time_period],), (constant_climate_database_q226_ci423['Austria', time_period],), (constant_climate_database_q226_ci423['Azerbaijan', time_period],), (constant_climate_database_q226_ci423['The Bahamas', time_period],), (None,), (constant_climate_database_q226_ci423['Bangladesh', time_period],), (None,), (constant_climate_database_q226_ci423['Belarus', time_period],), (constant_climate_database_q226_ci423['Belgium', time_period],), (constant_climate_database_q226_ci423['Belize', time_period],), (constant_climate_database_q226_ci423['Benin', time_period],), (constant_climate_database_q226_ci423['Bhutan', time_period],), (constant_climate_database_q226_ci423['Bolivia', time_period],), (constant_climate_database_q226_ci423['Bosnia and Herzegovina', time_period],), (constant_climate_database_q226_ci423['Botswana', time_period],), (constant_climate_database_q226_ci423['Brazil', time_period],), (constant_climate_database_q226_ci423['Brunei Darussalam', time_period],), (constant_climate_database_q226_ci423['Bulgaria', time_period],), (constant_climate_database_q226_ci423['Burkina Faso', time_period],), (constant_climate_database_q226_ci423['Burundi', time_period],), (constant_climate_database_q226_ci423['Cabo Verde', time_period],), (constant_climate_database_q226_ci423['Cambodia', time_period],), (constant_climate_database_q226_ci423['Cameroon', time_period],), (constant_climate_database_q226_ci423['Canada', time_period],), (constant_climate_database_q226_ci423['Central African Republic', time_period],), (constant_climate_database_q226_ci423['Chad', time_period],), (constant_climate_database_q226_ci423['Chile', time_period],), (constant_climate_database_q226_ci423['China', time_period],), (constant_climate_database_q226_ci423['Colombia', time_period],), (constant_climate_database_q226_ci423['Comoros', time_period],), (constant_climate_database_q226_ci423['Democratic Republic of the Congo', time_period],), (constant_climate_database_q226_ci423['Republic of Congo', time_period],), (constant_climate_database_q226_ci423['Costa Rica', time_period],), (constant_climate_database_q226_ci423["Côte d'Ivoire", time_period],), (constant_climate_database_q226_ci423['Croatia', time_period],), (constant_climate_database_q226_ci423['Cyprus', time_period],), (constant_climate_database_q226_ci423['Czech Republic', time_period],), (constant_climate_database_q226_ci423['Denmark', time_period],), (constant_climate_database_q226_ci423['Djibouti', time_period],), (None,), (constant_climate_database_q226_ci423['Dominican Republic', time_period],), (constant_climate_database_q226_ci423['Ecuador', time_period],), (constant_climate_database_q226_ci423['Egypt', time_period],), (constant_climate_database_q226_ci423['El Salvador', time_period],), (constant_climate_database_q226_ci423['Equatorial Guinea', time_period],), (constant_climate_database_q226_ci423['Eritrea', time_period],), (constant_climate_database_q226_ci423['Estonia', time_period],), (constant_climate_database_q226_ci423['Eswatini', time_period],), (constant_climate_database_q226_ci423['Ethiopia', time_period],), (constant_climate_database_q226_ci423['Fiji', time_period],), (constant_climate_database_q226_ci423['Finland', time_period],), (constant_climate_database_q226_ci423['France', time_period],), (constant_climate_database_q226_ci423['Gabon', time_period],), (constant_climate_database_q226_ci423['The Gambia', time_period],), (constant_climate_database_q226_ci423['Georgia', time_period],), (constant_climate_database_q226_ci423['Germany', time_period],), (constant_climate_database_q226_ci423['Ghana', time_period],), (constant_climate_database_q226_ci423['Greece', time_period],), (constant_climate_database_q226_ci423['Grenada', time_period],), (constant_climate_database_q226_ci423['Guatemala', time_period],), (constant_climate_database_q226_ci423['Guinea', time_period],), (constant_climate_database_q226_ci423['Guinea-Bissau', time_period],), (constant_climate_database_q226_ci423['Guyana', time_period],), (constant_climate_database_q226_ci423['Haiti', time_period],), (constant_climate_database_q226_ci423['Honduras', time_period],), (None,), (constant_climate_database_q226_ci423['Hungary', time_period],), (constant_climate_database_q226_ci423['Iceland', time_period],), (constant_climate_database_q226_ci423['India', time_period],), (constant_climate_database_q226_ci423['Indonesia', time_period],), (constant_climate_database_q226_ci423['Islamic Republic of Iran', time_period],), (constant_climate_database_q226_ci423['Iraq', time_period],), (constant_climate_database_q226_ci423['Ireland', time_period],), (constant_climate_database_q226_ci423['Israel', time_period],), (constant_climate_database_q226_ci423['Italy', time_period],), (constant_climate_database_q226_ci423['Jamaica', time_period],), (constant_climate_database_q226_ci423['Japan', time_period],), (constant_climate_database_q226_ci423['Jordan', time_period],), (constant_climate_database_q226_ci423['Kazakhstan', time_period],), (constant_climate_database_q226_ci423['Kenya', time_period],), (None,), (constant_climate_database_q226_ci423['Korea', time_period],), (None,), (constant_climate_database_q226_ci423['Kuwait', time_period],), (constant_climate_database_q226_ci423['Kyrgyz Republic', time_period],), (constant_climate_database_q226_ci423['Lao P.D.R.', time_period],), (constant_climate_database_q226_ci423['Latvia', time_period],), (constant_climate_database_q226_ci423['Lebanon', time_period],), (constant_climate_database_q226_ci423['Lesotho', time_period],), (constant_climate_database_q226_ci423['Liberia', time_period],), (constant_climate_database_q226_ci423['Libya', time_period],), (constant_climate_database_q226_ci423['Lithuania', time_period],), (constant_climate_database_q226_ci423['Luxembourg', time_period],), (None,), (constant_climate_database_q226_ci423['Madagascar', time_period],), (constant_climate_database_q226_ci423['Malawi', time_period],), (constant_climate_database_q226_ci423['Malaysia', time_period],), (None,), (constant_climate_database_q226_ci423['Mali', time_period],), (None,), (None,), (constant_climate_database_q226_ci423['Mauritania', time_period],), (constant_climate_database_q226_ci423['Mauritius', time_period],), (constant_climate_database_q226_ci423['Mexico', time_period],), (None,), (constant_climate_database_q226_ci423['Moldova', time_period],), (constant_climate_database_q226_ci423['Mongolia', time_period],), (constant_climate_database_q226_ci423['Montenegro', time_period],), (None,), (constant_climate_database_q226_ci423['Morocco', time_period],), (constant_climate_database_q226_ci423['Mozambique', time_period],), (constant_climate_database_q226_ci423['Myanmar', time_period],), (constant_climate_database_q226_ci423['Namibia', time_period],), (None,), (constant_climate_database_q226_ci423['Nepal', time_period],), (constant_climate_database_q226_ci423['Netherlands', time_period],), (constant_climate_database_q226_ci423['New Zealand', time_period],), (constant_climate_database_q226_ci423['Nicaragua', time_period],), (constant_climate_database_q226_ci423['Niger', time_period],), (constant_climate_database_q226_ci423['Nigeria', time_period],), (constant_climate_database_q226_ci423['North Macedonia', time_period],), (constant_climate_database_q226_ci423['Norway', time_period],), (constant_climate_database_q226_ci423['Oman', time_period],), (constant_climate_database_q226_ci423['Pakistan', time_period],), (None,), (constant_climate_database_q226_ci423['Panama', time_period],), (constant_climate_database_q226_ci423['Papua New Guinea', time_period],), (constant_climate_database_q226_ci423['Paraguay', time_period],), (constant_climate_database_q226_ci423['Peru', time_period],), (constant_climate_database_q226_ci423['Philippines', time_period],), (constant_climate_database_q226_ci423['Poland', time_period],), (constant_climate_database_q226_ci423['Portugal', time_period],), (constant_climate_database_q226_ci423['Puerto Rico', time_period],), (constant_climate_database_q226_ci423['Qatar', time_period],), (constant_climate_database_q226_ci423['Romania', time_period],), (constant_climate_database_q226_ci423['Russia', time_period],), (constant_climate_database_q226_ci423['Rwanda', time_period],), (constant_climate_database_q226_ci423['Samoa', time_period],), (constant_climate_database_q226_ci423['San Marino', time_period],), (constant_climate_database_q226_ci423['Sao Tome and Principe', time_period],), (constant_climate_database_q226_ci423['Saudi Arabia', time_period],), (constant_climate_database_q226_ci423['Senegal', time_period],), (constant_climate_database_q226_ci423['Serbia', time_period],), (None,), (constant_climate_database_q226_ci423['Sierra Leone', time_period],), (None,), (constant_climate_database_q226_ci423['Slovak Republic', time_period],), (constant_climate_database_q226_ci423['Slovenia', time_period],), (constant_climate_database_q226_ci423['Solomon Islands', time_period],), (constant_climate_database_q226_ci423['Somalia', time_period],), (constant_climate_database_q226_ci423['South Africa', time_period],), (constant_climate_database_q226_ci423['South Sudan', time_period],), (constant_climate_database_q226_ci423['Spain', time_period],), (constant_climate_database_q226_ci423['Sri Lanka', time_period],), (None,), (None,), (constant_climate_database_q226_ci423['St. Vincent and the Grenadines', time_period],), (constant_climate_database_q226_ci423['Sudan', time_period],), (constant_climate_database_q226_ci423['Suriname', time_period],), (constant_climate_database_q226_ci423['Sweden', time_period],), (constant_climate_database_q226_ci423['Switzerland', time_period],), (constant_climate_database_q226_ci423['Syria', time_period],), (None,), (constant_climate_database_q226_ci423['Tajikistan', time_period],), (constant_climate_database_q226_ci423['Tanzania', time_period],), (constant_climate_database_q226_ci423['Thailand', time_period],), (None,), (constant_climate_database_q226_ci423['Togo', time_period],), (None,), (constant_climate_database_q226_ci423['Trinidad and Tobago', time_period],), (constant_climate_database_q226_ci423['Tunisia', time_period],), (constant_climate_database_q226_ci423['Türkiye', time_period],), (constant_climate_database_q226_ci423['Turkmenistan', time_period],), (None,), (constant_climate_database_q226_ci423['Uganda', time_period],), (constant_climate_database_q226_ci423['Ukraine', time_period],), (constant_climate_database_q226_ci423['United Arab Emirates', time_period],), (constant_climate_database_q226_ci423['United Kingdom', time_period],), (constant_climate_database_q226_ci423['United States', time_period],), (constant_climate_database_q226_ci423['Uruguay', time_period],), (constant_climate_database_q226_ci423['Uzbekistan', time_period],), (constant_climate_database_q226_ci423['Vanuatu', time_period],), (constant_climate_database_q226_ci423['Venezuela', time_period],), (constant_climate_database_q226_ci423['Vietnam', time_period],), (None,), (constant_climate_database_q226_ci423['Yemen', time_period],), (constant_climate_database_q226_ci423['Zambia', time_period],), (constant_climate_database_q226_ci423['Zimbabwe', time_period],),), xl_match(climate_database_country, _climate_database_gdp_loss_pct_moderate_table_0, 0), 1))

    return data.CLIMATE_DATABASE_GDP_LOSS_PCT_MODERATE.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_LOSS_PCT_MODERATE.required))

@publish(data.CLIMATE_DATABASE_GDP_LOSS_PCT_HIGH.schema, cells=data.CLIMATE_DATABASE_GDP_LOSS_PCT_HIGH.cells)
def climate_database_gdp_loss_pct_high(*, constant_climate_database_b426_b623: data.Series[str | None], constant_climate_database_q426_ci623: data.Series[float | str | None], climate_database_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Extract projected GDP losses relative to the baseline under the "high" climate change scenario for a selected country over the projection horizon.

    Provide, by country and year, the GDP loss (as a percentage of the baseline level) implied by the high-emissions SSP3-7.0 climate scenario, so that these climate-driven output losses can be carried into the macro-fiscal projections.

    Args:
        constant_climate_database_b426_b623: Series of country identifiers aligned with the country axis, used to position each row of the climate data table so it can be matched against the requested country.
        constant_climate_database_q426_ci623: Climate database series holding the per-country GDP loss estimates (percent of baseline GDP) for the high climate change scenario, indexed by country and time period; missing entries arise for economies not covered by the empirical estimates.
        climate_database_country: Country to report the high-scenario GDP losses for; matched against the country axis to select the corresponding row of the climate data table.

    Returns:
        Series of high-scenario GDP losses, expressed in percent of baseline GDP, for the selected country across all time periods; entries are missing where the country is not covered by the climate estimates.
    """
    data.CONSTANT_CLIMATE_DATABASE_B426_B623.schema.validate(constant_climate_database_b426_b623)
    data.CONSTANT_CLIMATE_DATABASE_Q426_CI623.schema.validate(constant_climate_database_q426_ci623)
    _climate_database_gdp_loss_pct_high_table_0 = view(constant_climate_database_b426_b623, rows=data.COUNTRY_AXIS_5.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(((constant_climate_database_q426_ci623['Afghanistan', time_period],), (constant_climate_database_q426_ci623['Albania', time_period],), (constant_climate_database_q426_ci623['Algeria', time_period],), (None,), (constant_climate_database_q426_ci623['Angola', time_period],), (None,), (None,), (constant_climate_database_q426_ci623['Argentina', time_period],), (constant_climate_database_q426_ci623['Armenia', time_period],), (None,), (constant_climate_database_q426_ci623['Australia', time_period],), (constant_climate_database_q426_ci623['Austria', time_period],), (constant_climate_database_q426_ci623['Azerbaijan', time_period],), (constant_climate_database_q426_ci623['The Bahamas', time_period],), (None,), (constant_climate_database_q426_ci623['Bangladesh', time_period],), (None,), (constant_climate_database_q426_ci623['Belarus', time_period],), (constant_climate_database_q426_ci623['Belgium', time_period],), (constant_climate_database_q426_ci623['Belize', time_period],), (constant_climate_database_q426_ci623['Benin', time_period],), (constant_climate_database_q426_ci623['Bhutan', time_period],), (constant_climate_database_q426_ci623['Bolivia', time_period],), (constant_climate_database_q426_ci623['Bosnia and Herzegovina', time_period],), (constant_climate_database_q426_ci623['Botswana', time_period],), (constant_climate_database_q426_ci623['Brazil', time_period],), (constant_climate_database_q426_ci623['Brunei Darussalam', time_period],), (constant_climate_database_q426_ci623['Bulgaria', time_period],), (constant_climate_database_q426_ci623['Burkina Faso', time_period],), (constant_climate_database_q426_ci623['Burundi', time_period],), (constant_climate_database_q426_ci623['Cabo Verde', time_period],), (constant_climate_database_q426_ci623['Cambodia', time_period],), (constant_climate_database_q426_ci623['Cameroon', time_period],), (constant_climate_database_q426_ci623['Canada', time_period],), (constant_climate_database_q426_ci623['Central African Republic', time_period],), (constant_climate_database_q426_ci623['Chad', time_period],), (constant_climate_database_q426_ci623['Chile', time_period],), (constant_climate_database_q426_ci623['China', time_period],), (constant_climate_database_q426_ci623['Colombia', time_period],), (constant_climate_database_q426_ci623['Comoros', time_period],), (constant_climate_database_q426_ci623['Democratic Republic of the Congo', time_period],), (constant_climate_database_q426_ci623['Republic of Congo', time_period],), (constant_climate_database_q426_ci623['Costa Rica', time_period],), (constant_climate_database_q426_ci623["Côte d'Ivoire", time_period],), (constant_climate_database_q426_ci623['Croatia', time_period],), (constant_climate_database_q426_ci623['Cyprus', time_period],), (constant_climate_database_q426_ci623['Czech Republic', time_period],), (constant_climate_database_q426_ci623['Denmark', time_period],), (constant_climate_database_q426_ci623['Djibouti', time_period],), (None,), (constant_climate_database_q426_ci623['Dominican Republic', time_period],), (constant_climate_database_q426_ci623['Ecuador', time_period],), (constant_climate_database_q426_ci623['Egypt', time_period],), (constant_climate_database_q426_ci623['El Salvador', time_period],), (constant_climate_database_q426_ci623['Equatorial Guinea', time_period],), (constant_climate_database_q426_ci623['Eritrea', time_period],), (constant_climate_database_q426_ci623['Estonia', time_period],), (constant_climate_database_q426_ci623['Eswatini', time_period],), (constant_climate_database_q426_ci623['Ethiopia', time_period],), (constant_climate_database_q426_ci623['Fiji', time_period],), (constant_climate_database_q426_ci623['Finland', time_period],), (constant_climate_database_q426_ci623['France', time_period],), (constant_climate_database_q426_ci623['Gabon', time_period],), (constant_climate_database_q426_ci623['The Gambia', time_period],), (constant_climate_database_q426_ci623['Georgia', time_period],), (constant_climate_database_q426_ci623['Germany', time_period],), (constant_climate_database_q426_ci623['Ghana', time_period],), (constant_climate_database_q426_ci623['Greece', time_period],), (constant_climate_database_q426_ci623['Grenada', time_period],), (constant_climate_database_q426_ci623['Guatemala', time_period],), (constant_climate_database_q426_ci623['Guinea', time_period],), (constant_climate_database_q426_ci623['Guinea-Bissau', time_period],), (constant_climate_database_q426_ci623['Guyana', time_period],), (constant_climate_database_q426_ci623['Haiti', time_period],), (constant_climate_database_q426_ci623['Honduras', time_period],), (None,), (constant_climate_database_q426_ci623['Hungary', time_period],), (constant_climate_database_q426_ci623['Iceland', time_period],), (constant_climate_database_q426_ci623['India', time_period],), (constant_climate_database_q426_ci623['Indonesia', time_period],), (constant_climate_database_q426_ci623['Islamic Republic of Iran', time_period],), (constant_climate_database_q426_ci623['Iraq', time_period],), (constant_climate_database_q426_ci623['Ireland', time_period],), (constant_climate_database_q426_ci623['Israel', time_period],), (constant_climate_database_q426_ci623['Italy', time_period],), (constant_climate_database_q426_ci623['Jamaica', time_period],), (constant_climate_database_q426_ci623['Japan', time_period],), (constant_climate_database_q426_ci623['Jordan', time_period],), (constant_climate_database_q426_ci623['Kazakhstan', time_period],), (constant_climate_database_q426_ci623['Kenya', time_period],), (None,), (constant_climate_database_q426_ci623['Korea', time_period],), (None,), (constant_climate_database_q426_ci623['Kuwait', time_period],), (constant_climate_database_q426_ci623['Kyrgyz Republic', time_period],), (constant_climate_database_q426_ci623['Lao P.D.R.', time_period],), (constant_climate_database_q426_ci623['Latvia', time_period],), (constant_climate_database_q426_ci623['Lebanon', time_period],), (constant_climate_database_q426_ci623['Lesotho', time_period],), (constant_climate_database_q426_ci623['Liberia', time_period],), (constant_climate_database_q426_ci623['Libya', time_period],), (constant_climate_database_q426_ci623['Lithuania', time_period],), (constant_climate_database_q426_ci623['Luxembourg', time_period],), (None,), (constant_climate_database_q426_ci623['Madagascar', time_period],), (constant_climate_database_q426_ci623['Malawi', time_period],), (constant_climate_database_q426_ci623['Malaysia', time_period],), (None,), (constant_climate_database_q426_ci623['Mali', time_period],), (None,), (None,), (constant_climate_database_q426_ci623['Mauritania', time_period],), (constant_climate_database_q426_ci623['Mauritius', time_period],), (constant_climate_database_q426_ci623['Mexico', time_period],), (None,), (constant_climate_database_q426_ci623['Moldova', time_period],), (constant_climate_database_q426_ci623['Mongolia', time_period],), (constant_climate_database_q426_ci623['Montenegro', time_period],), (None,), (constant_climate_database_q426_ci623['Morocco', time_period],), (constant_climate_database_q426_ci623['Mozambique', time_period],), (constant_climate_database_q426_ci623['Myanmar', time_period],), (constant_climate_database_q426_ci623['Namibia', time_period],), (None,), (constant_climate_database_q426_ci623['Nepal', time_period],), (constant_climate_database_q426_ci623['Netherlands', time_period],), (constant_climate_database_q426_ci623['New Zealand', time_period],), (constant_climate_database_q426_ci623['Nicaragua', time_period],), (constant_climate_database_q426_ci623['Niger', time_period],), (constant_climate_database_q426_ci623['Nigeria', time_period],), (constant_climate_database_q426_ci623['North Macedonia', time_period],), (constant_climate_database_q426_ci623['Norway', time_period],), (constant_climate_database_q426_ci623['Oman', time_period],), (constant_climate_database_q426_ci623['Pakistan', time_period],), (None,), (constant_climate_database_q426_ci623['Panama', time_period],), (constant_climate_database_q426_ci623['Papua New Guinea', time_period],), (constant_climate_database_q426_ci623['Paraguay', time_period],), (constant_climate_database_q426_ci623['Peru', time_period],), (constant_climate_database_q426_ci623['Philippines', time_period],), (constant_climate_database_q426_ci623['Poland', time_period],), (constant_climate_database_q426_ci623['Portugal', time_period],), (constant_climate_database_q426_ci623['Puerto Rico', time_period],), (constant_climate_database_q426_ci623['Qatar', time_period],), (constant_climate_database_q426_ci623['Romania', time_period],), (constant_climate_database_q426_ci623['Russia', time_period],), (constant_climate_database_q426_ci623['Rwanda', time_period],), (constant_climate_database_q426_ci623['Samoa', time_period],), (constant_climate_database_q426_ci623['San Marino', time_period],), (constant_climate_database_q426_ci623['Sao Tome and Principe', time_period],), (constant_climate_database_q426_ci623['Saudi Arabia', time_period],), (constant_climate_database_q426_ci623['Senegal', time_period],), (constant_climate_database_q426_ci623['Serbia', time_period],), (None,), (constant_climate_database_q426_ci623['Sierra Leone', time_period],), (None,), (constant_climate_database_q426_ci623['Slovak Republic', time_period],), (constant_climate_database_q426_ci623['Slovenia', time_period],), (constant_climate_database_q426_ci623['Solomon Islands', time_period],), (constant_climate_database_q426_ci623['Somalia', time_period],), (constant_climate_database_q426_ci623['South Africa', time_period],), (constant_climate_database_q426_ci623['South Sudan', time_period],), (constant_climate_database_q426_ci623['Spain', time_period],), (constant_climate_database_q426_ci623['Sri Lanka', time_period],), (None,), (None,), (constant_climate_database_q426_ci623['St. Vincent and the Grenadines', time_period],), (constant_climate_database_q426_ci623['Sudan', time_period],), (constant_climate_database_q426_ci623['Suriname', time_period],), (constant_climate_database_q426_ci623['Sweden', time_period],), (constant_climate_database_q426_ci623['Switzerland', time_period],), (constant_climate_database_q426_ci623['Syria', time_period],), (None,), (constant_climate_database_q426_ci623['Tajikistan', time_period],), (constant_climate_database_q426_ci623['Tanzania', time_period],), (constant_climate_database_q426_ci623['Thailand', time_period],), (None,), (constant_climate_database_q426_ci623['Togo', time_period],), (None,), (constant_climate_database_q426_ci623['Trinidad and Tobago', time_period],), (constant_climate_database_q426_ci623['Tunisia', time_period],), (constant_climate_database_q426_ci623['Türkiye', time_period],), (constant_climate_database_q426_ci623['Turkmenistan', time_period],), (None,), (constant_climate_database_q426_ci623['Uganda', time_period],), (constant_climate_database_q426_ci623['Ukraine', time_period],), (constant_climate_database_q426_ci623['United Arab Emirates', time_period],), (constant_climate_database_q426_ci623['United Kingdom', time_period],), (constant_climate_database_q426_ci623['United States', time_period],), (constant_climate_database_q426_ci623['Uruguay', time_period],), (constant_climate_database_q426_ci623['Uzbekistan', time_period],), (constant_climate_database_q426_ci623['Vanuatu', time_period],), (constant_climate_database_q426_ci623['Venezuela', time_period],), (constant_climate_database_q426_ci623['Vietnam', time_period],), (None,), (constant_climate_database_q426_ci623['Yemen', time_period],), (constant_climate_database_q426_ci623['Zambia', time_period],), (constant_climate_database_q426_ci623['Zimbabwe', time_period],),), xl_match(climate_database_country, _climate_database_gdp_loss_pct_high_table_0, 0), 1))

    return data.CLIMATE_DATABASE_GDP_LOSS_PCT_HIGH.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_LOSS_PCT_HIGH.required))

@publish(data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT.schema, cells=data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT.cells)
def climate_database_gdp_loss_pct_hot(*, constant_climate_database_b626_b823: data.Series[str | None], constant_climate_database_q626_ci823: data.Series[float | str | None], climate_database_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Extract GDP loss percentages under the hot climate scenario for every country.

    Provide the hot-scenario GDP loss percentages used to translate temperature increases into macroeconomic and fiscal effects in Q-CRAFT.

    Args:
        constant_climate_database_b626_b823: Series of country identifiers defining the rows of the GDP loss table.
        constant_climate_database_q626_ci823: Series of GDP loss percentages by country and time period under the hot climate scenario.
        climate_database_country: Country to select within the GDP loss table.

    Returns:
        A series of GDP loss percentages for the selected country's hot scenario.
    """
    data.CONSTANT_CLIMATE_DATABASE_B626_B823.schema.validate(constant_climate_database_b626_b823)
    data.CONSTANT_CLIMATE_DATABASE_Q626_CI823.schema.validate(constant_climate_database_q626_ci823)
    _climate_database_gdp_loss_pct_hot_table_0 = view(constant_climate_database_b626_b823, rows=data.COUNTRY_AXIS_5.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(((constant_climate_database_q626_ci823['Afghanistan', time_period],), (constant_climate_database_q626_ci823['Albania', time_period],), (constant_climate_database_q626_ci823['Algeria', time_period],), (None,), (constant_climate_database_q626_ci823['Angola', time_period],), (None,), (None,), (constant_climate_database_q626_ci823['Argentina', time_period],), (constant_climate_database_q626_ci823['Armenia', time_period],), (None,), (constant_climate_database_q626_ci823['Australia', time_period],), (constant_climate_database_q626_ci823['Austria', time_period],), (constant_climate_database_q626_ci823['Azerbaijan', time_period],), (constant_climate_database_q626_ci823['The Bahamas', time_period],), (None,), (constant_climate_database_q626_ci823['Bangladesh', time_period],), (None,), (constant_climate_database_q626_ci823['Belarus', time_period],), (constant_climate_database_q626_ci823['Belgium', time_period],), (constant_climate_database_q626_ci823['Belize', time_period],), (constant_climate_database_q626_ci823['Benin', time_period],), (constant_climate_database_q626_ci823['Bhutan', time_period],), (constant_climate_database_q626_ci823['Bolivia', time_period],), (constant_climate_database_q626_ci823['Bosnia and Herzegovina', time_period],), (constant_climate_database_q626_ci823['Botswana', time_period],), (constant_climate_database_q626_ci823['Brazil', time_period],), (constant_climate_database_q626_ci823['Brunei Darussalam', time_period],), (constant_climate_database_q626_ci823['Bulgaria', time_period],), (constant_climate_database_q626_ci823['Burkina Faso', time_period],), (constant_climate_database_q626_ci823['Burundi', time_period],), (constant_climate_database_q626_ci823['Cabo Verde', time_period],), (constant_climate_database_q626_ci823['Cambodia', time_period],), (constant_climate_database_q626_ci823['Cameroon', time_period],), (constant_climate_database_q626_ci823['Canada', time_period],), (constant_climate_database_q626_ci823['Central African Republic', time_period],), (constant_climate_database_q626_ci823['Chad', time_period],), (constant_climate_database_q626_ci823['Chile', time_period],), (constant_climate_database_q626_ci823['China', time_period],), (constant_climate_database_q626_ci823['Colombia', time_period],), (constant_climate_database_q626_ci823['Comoros', time_period],), (constant_climate_database_q626_ci823['Democratic Republic of the Congo', time_period],), (constant_climate_database_q626_ci823['Republic of Congo', time_period],), (constant_climate_database_q626_ci823['Costa Rica', time_period],), (constant_climate_database_q626_ci823["Côte d'Ivoire", time_period],), (constant_climate_database_q626_ci823['Croatia', time_period],), (constant_climate_database_q626_ci823['Cyprus', time_period],), (constant_climate_database_q626_ci823['Czech Republic', time_period],), (constant_climate_database_q626_ci823['Denmark', time_period],), (constant_climate_database_q626_ci823['Djibouti', time_period],), (None,), (constant_climate_database_q626_ci823['Dominican Republic', time_period],), (constant_climate_database_q626_ci823['Ecuador', time_period],), (constant_climate_database_q626_ci823['Egypt', time_period],), (constant_climate_database_q626_ci823['El Salvador', time_period],), (constant_climate_database_q626_ci823['Equatorial Guinea', time_period],), (constant_climate_database_q626_ci823['Eritrea', time_period],), (constant_climate_database_q626_ci823['Estonia', time_period],), (constant_climate_database_q626_ci823['Eswatini', time_period],), (constant_climate_database_q626_ci823['Ethiopia', time_period],), (constant_climate_database_q626_ci823['Fiji', time_period],), (constant_climate_database_q626_ci823['Finland', time_period],), (constant_climate_database_q626_ci823['France', time_period],), (constant_climate_database_q626_ci823['Gabon', time_period],), (constant_climate_database_q626_ci823['The Gambia', time_period],), (constant_climate_database_q626_ci823['Georgia', time_period],), (constant_climate_database_q626_ci823['Germany', time_period],), (constant_climate_database_q626_ci823['Ghana', time_period],), (constant_climate_database_q626_ci823['Greece', time_period],), (constant_climate_database_q626_ci823['Grenada', time_period],), (constant_climate_database_q626_ci823['Guatemala', time_period],), (constant_climate_database_q626_ci823['Guinea', time_period],), (constant_climate_database_q626_ci823['Guinea-Bissau', time_period],), (constant_climate_database_q626_ci823['Guyana', time_period],), (constant_climate_database_q626_ci823['Haiti', time_period],), (constant_climate_database_q626_ci823['Honduras', time_period],), (None,), (constant_climate_database_q626_ci823['Hungary', time_period],), (constant_climate_database_q626_ci823['Iceland', time_period],), (constant_climate_database_q626_ci823['India', time_period],), (constant_climate_database_q626_ci823['Indonesia', time_period],), (constant_climate_database_q626_ci823['Islamic Republic of Iran', time_period],), (constant_climate_database_q626_ci823['Iraq', time_period],), (constant_climate_database_q626_ci823['Ireland', time_period],), (constant_climate_database_q626_ci823['Israel', time_period],), (constant_climate_database_q626_ci823['Italy', time_period],), (constant_climate_database_q626_ci823['Jamaica', time_period],), (constant_climate_database_q626_ci823['Japan', time_period],), (constant_climate_database_q626_ci823['Jordan', time_period],), (constant_climate_database_q626_ci823['Kazakhstan', time_period],), (constant_climate_database_q626_ci823['Kenya', time_period],), (None,), (constant_climate_database_q626_ci823['Korea', time_period],), (None,), (constant_climate_database_q626_ci823['Kuwait', time_period],), (constant_climate_database_q626_ci823['Kyrgyz Republic', time_period],), (constant_climate_database_q626_ci823['Lao P.D.R.', time_period],), (constant_climate_database_q626_ci823['Latvia', time_period],), (constant_climate_database_q626_ci823['Lebanon', time_period],), (constant_climate_database_q626_ci823['Lesotho', time_period],), (constant_climate_database_q626_ci823['Liberia', time_period],), (constant_climate_database_q626_ci823['Libya', time_period],), (constant_climate_database_q626_ci823['Lithuania', time_period],), (constant_climate_database_q626_ci823['Luxembourg', time_period],), (None,), (constant_climate_database_q626_ci823['Madagascar', time_period],), (constant_climate_database_q626_ci823['Malawi', time_period],), (constant_climate_database_q626_ci823['Malaysia', time_period],), (None,), (constant_climate_database_q626_ci823['Mali', time_period],), (None,), (None,), (constant_climate_database_q626_ci823['Mauritania', time_period],), (constant_climate_database_q626_ci823['Mauritius', time_period],), (constant_climate_database_q626_ci823['Mexico', time_period],), (None,), (constant_climate_database_q626_ci823['Moldova', time_period],), (constant_climate_database_q626_ci823['Mongolia', time_period],), (constant_climate_database_q626_ci823['Montenegro', time_period],), (None,), (constant_climate_database_q626_ci823['Morocco', time_period],), (constant_climate_database_q626_ci823['Mozambique', time_period],), (constant_climate_database_q626_ci823['Myanmar', time_period],), (constant_climate_database_q626_ci823['Namibia', time_period],), (None,), (constant_climate_database_q626_ci823['Nepal', time_period],), (constant_climate_database_q626_ci823['Netherlands', time_period],), (constant_climate_database_q626_ci823['New Zealand', time_period],), (constant_climate_database_q626_ci823['Nicaragua', time_period],), (constant_climate_database_q626_ci823['Niger', time_period],), (constant_climate_database_q626_ci823['Nigeria', time_period],), (constant_climate_database_q626_ci823['North Macedonia', time_period],), (constant_climate_database_q626_ci823['Norway', time_period],), (constant_climate_database_q626_ci823['Oman', time_period],), (constant_climate_database_q626_ci823['Pakistan', time_period],), (None,), (constant_climate_database_q626_ci823['Panama', time_period],), (constant_climate_database_q626_ci823['Papua New Guinea', time_period],), (constant_climate_database_q626_ci823['Paraguay', time_period],), (constant_climate_database_q626_ci823['Peru', time_period],), (constant_climate_database_q626_ci823['Philippines', time_period],), (constant_climate_database_q626_ci823['Poland', time_period],), (constant_climate_database_q626_ci823['Portugal', time_period],), (constant_climate_database_q626_ci823['Puerto Rico', time_period],), (constant_climate_database_q626_ci823['Qatar', time_period],), (constant_climate_database_q626_ci823['Romania', time_period],), (constant_climate_database_q626_ci823['Russia', time_period],), (constant_climate_database_q626_ci823['Rwanda', time_period],), (constant_climate_database_q626_ci823['Samoa', time_period],), (constant_climate_database_q626_ci823['San Marino', time_period],), (constant_climate_database_q626_ci823['Sao Tome and Principe', time_period],), (constant_climate_database_q626_ci823['Saudi Arabia', time_period],), (constant_climate_database_q626_ci823['Senegal', time_period],), (constant_climate_database_q626_ci823['Serbia', time_period],), (None,), (constant_climate_database_q626_ci823['Sierra Leone', time_period],), (None,), (constant_climate_database_q626_ci823['Slovak Republic', time_period],), (constant_climate_database_q626_ci823['Slovenia', time_period],), (constant_climate_database_q626_ci823['Solomon Islands', time_period],), (constant_climate_database_q626_ci823['Somalia', time_period],), (constant_climate_database_q626_ci823['South Africa', time_period],), (constant_climate_database_q626_ci823['South Sudan', time_period],), (constant_climate_database_q626_ci823['Spain', time_period],), (constant_climate_database_q626_ci823['Sri Lanka', time_period],), (None,), (None,), (constant_climate_database_q626_ci823['St. Vincent and the Grenadines', time_period],), (constant_climate_database_q626_ci823['Sudan', time_period],), (constant_climate_database_q626_ci823['Suriname', time_period],), (constant_climate_database_q626_ci823['Sweden', time_period],), (constant_climate_database_q626_ci823['Switzerland', time_period],), (constant_climate_database_q626_ci823['Syria', time_period],), (None,), (constant_climate_database_q626_ci823['Tajikistan', time_period],), (constant_climate_database_q626_ci823['Tanzania', time_period],), (constant_climate_database_q626_ci823['Thailand', time_period],), (None,), (constant_climate_database_q626_ci823['Togo', time_period],), (None,), (constant_climate_database_q626_ci823['Trinidad and Tobago', time_period],), (constant_climate_database_q626_ci823['Tunisia', time_period],), (constant_climate_database_q626_ci823['Türkiye', time_period],), (constant_climate_database_q626_ci823['Turkmenistan', time_period],), (None,), (constant_climate_database_q626_ci823['Uganda', time_period],), (constant_climate_database_q626_ci823['Ukraine', time_period],), (constant_climate_database_q626_ci823['United Arab Emirates', time_period],), (constant_climate_database_q626_ci823['United Kingdom', time_period],), (constant_climate_database_q626_ci823['United States', time_period],), (constant_climate_database_q626_ci823['Uruguay', time_period],), (constant_climate_database_q626_ci823['Uzbekistan', time_period],), (constant_climate_database_q626_ci823['Vanuatu', time_period],), (constant_climate_database_q626_ci823['Venezuela', time_period],), (constant_climate_database_q626_ci823['Vietnam', time_period],), (None,), (constant_climate_database_q626_ci823['Yemen', time_period],), (constant_climate_database_q626_ci823['Zambia', time_period],), (constant_climate_database_q626_ci823['Zimbabwe', time_period],),), xl_match(climate_database_country, _climate_database_gdp_loss_pct_hot_table_0, 0), 1))

    return data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT.required))

@publish(data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT_ADAPTED.schema, cells=data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT_ADAPTED.cells)
def climate_database_gdp_loss_pct_hot_adapted(*, constant_climate_database_b826_b1023: data.Series[str | None], constant_climate_database_q826_ci1023: data.Series[float | str | None], climate_database_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Extract the Hot Adapted climate scenario GDP loss percentage by country and time period.

    Provides the projected GDP loss (in percent) relative to the no-climate-change baseline under the Hot Adapted scenario, in which temperatures rise as in the Hot scenario but countries adapt more quickly.

    Args:
        constant_climate_database_b826_b1023: Country lookup series used to resolve the requested country into the internal country index for the Hot Adapted climate data.
        constant_climate_database_q826_ci1023: Hot Adapted scenario GDP loss percentage series, indexed by country and time period, that supplies the returned values.
        climate_database_country: Country identifier (name or code) selecting the row of the Hot Adapted climate data to return.

    Returns:
        A series of GDP loss percentages (relative to the baseline) under the Hot Adapted climate scenario, aligned to the projected time periods.
    """
    data.CONSTANT_CLIMATE_DATABASE_B826_B1023.schema.validate(constant_climate_database_b826_b1023)
    data.CONSTANT_CLIMATE_DATABASE_Q826_CI1023.schema.validate(constant_climate_database_q826_ci1023)
    _climate_database_gdp_loss_pct_hot_adapted_table_0 = view(constant_climate_database_b826_b1023, rows=data.COUNTRY_AXIS_5.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(((constant_climate_database_q826_ci1023['Afghanistan', time_period],), (constant_climate_database_q826_ci1023['Albania', time_period],), (constant_climate_database_q826_ci1023['Algeria', time_period],), (None,), (constant_climate_database_q826_ci1023['Angola', time_period],), (None,), (None,), (constant_climate_database_q826_ci1023['Argentina', time_period],), (constant_climate_database_q826_ci1023['Armenia', time_period],), (None,), (constant_climate_database_q826_ci1023['Australia', time_period],), (constant_climate_database_q826_ci1023['Austria', time_period],), (constant_climate_database_q826_ci1023['Azerbaijan', time_period],), (constant_climate_database_q826_ci1023['The Bahamas', time_period],), (None,), (constant_climate_database_q826_ci1023['Bangladesh', time_period],), (None,), (constant_climate_database_q826_ci1023['Belarus', time_period],), (constant_climate_database_q826_ci1023['Belgium', time_period],), (constant_climate_database_q826_ci1023['Belize', time_period],), (constant_climate_database_q826_ci1023['Benin', time_period],), (constant_climate_database_q826_ci1023['Bhutan', time_period],), (constant_climate_database_q826_ci1023['Bolivia', time_period],), (constant_climate_database_q826_ci1023['Bosnia and Herzegovina', time_period],), (constant_climate_database_q826_ci1023['Botswana', time_period],), (constant_climate_database_q826_ci1023['Brazil', time_period],), (constant_climate_database_q826_ci1023['Brunei Darussalam', time_period],), (constant_climate_database_q826_ci1023['Bulgaria', time_period],), (constant_climate_database_q826_ci1023['Burkina Faso', time_period],), (constant_climate_database_q826_ci1023['Burundi', time_period],), (constant_climate_database_q826_ci1023['Cabo Verde', time_period],), (constant_climate_database_q826_ci1023['Cambodia', time_period],), (constant_climate_database_q826_ci1023['Cameroon', time_period],), (constant_climate_database_q826_ci1023['Canada', time_period],), (constant_climate_database_q826_ci1023['Central African Republic', time_period],), (constant_climate_database_q826_ci1023['Chad', time_period],), (constant_climate_database_q826_ci1023['Chile', time_period],), (constant_climate_database_q826_ci1023['China', time_period],), (constant_climate_database_q826_ci1023['Colombia', time_period],), (constant_climate_database_q826_ci1023['Comoros', time_period],), (constant_climate_database_q826_ci1023['Democratic Republic of the Congo', time_period],), (constant_climate_database_q826_ci1023['Republic of Congo', time_period],), (constant_climate_database_q826_ci1023['Costa Rica', time_period],), (constant_climate_database_q826_ci1023["Côte d'Ivoire", time_period],), (constant_climate_database_q826_ci1023['Croatia', time_period],), (constant_climate_database_q826_ci1023['Cyprus', time_period],), (constant_climate_database_q826_ci1023['Czech Republic', time_period],), (constant_climate_database_q826_ci1023['Denmark', time_period],), (constant_climate_database_q826_ci1023['Djibouti', time_period],), (None,), (constant_climate_database_q826_ci1023['Dominican Republic', time_period],), (constant_climate_database_q826_ci1023['Ecuador', time_period],), (constant_climate_database_q826_ci1023['Egypt', time_period],), (constant_climate_database_q826_ci1023['El Salvador', time_period],), (constant_climate_database_q826_ci1023['Equatorial Guinea', time_period],), (constant_climate_database_q826_ci1023['Eritrea', time_period],), (constant_climate_database_q826_ci1023['Estonia', time_period],), (constant_climate_database_q826_ci1023['Eswatini', time_period],), (constant_climate_database_q826_ci1023['Ethiopia', time_period],), (constant_climate_database_q826_ci1023['Fiji', time_period],), (constant_climate_database_q826_ci1023['Finland', time_period],), (constant_climate_database_q826_ci1023['France', time_period],), (constant_climate_database_q826_ci1023['Gabon', time_period],), (constant_climate_database_q826_ci1023['The Gambia', time_period],), (constant_climate_database_q826_ci1023['Georgia', time_period],), (constant_climate_database_q826_ci1023['Germany', time_period],), (constant_climate_database_q826_ci1023['Ghana', time_period],), (constant_climate_database_q826_ci1023['Greece', time_period],), (constant_climate_database_q826_ci1023['Grenada', time_period],), (constant_climate_database_q826_ci1023['Guatemala', time_period],), (constant_climate_database_q826_ci1023['Guinea', time_period],), (constant_climate_database_q826_ci1023['Guinea-Bissau', time_period],), (constant_climate_database_q826_ci1023['Guyana', time_period],), (constant_climate_database_q826_ci1023['Haiti', time_period],), (constant_climate_database_q826_ci1023['Honduras', time_period],), (None,), (constant_climate_database_q826_ci1023['Hungary', time_period],), (constant_climate_database_q826_ci1023['Iceland', time_period],), (constant_climate_database_q826_ci1023['India', time_period],), (constant_climate_database_q826_ci1023['Indonesia', time_period],), (constant_climate_database_q826_ci1023['Islamic Republic of Iran', time_period],), (constant_climate_database_q826_ci1023['Iraq', time_period],), (constant_climate_database_q826_ci1023['Ireland', time_period],), (constant_climate_database_q826_ci1023['Israel', time_period],), (constant_climate_database_q826_ci1023['Italy', time_period],), (constant_climate_database_q826_ci1023['Jamaica', time_period],), (constant_climate_database_q826_ci1023['Japan', time_period],), (constant_climate_database_q826_ci1023['Jordan', time_period],), (constant_climate_database_q826_ci1023['Kazakhstan', time_period],), (constant_climate_database_q826_ci1023['Kenya', time_period],), (None,), (constant_climate_database_q826_ci1023['Korea', time_period],), (None,), (constant_climate_database_q826_ci1023['Kuwait', time_period],), (constant_climate_database_q826_ci1023['Kyrgyz Republic', time_period],), (constant_climate_database_q826_ci1023['Lao P.D.R.', time_period],), (constant_climate_database_q826_ci1023['Latvia', time_period],), (constant_climate_database_q826_ci1023['Lebanon', time_period],), (constant_climate_database_q826_ci1023['Lesotho', time_period],), (constant_climate_database_q826_ci1023['Liberia', time_period],), (constant_climate_database_q826_ci1023['Libya', time_period],), (constant_climate_database_q826_ci1023['Lithuania', time_period],), (constant_climate_database_q826_ci1023['Luxembourg', time_period],), (None,), (constant_climate_database_q826_ci1023['Madagascar', time_period],), (constant_climate_database_q826_ci1023['Malawi', time_period],), (constant_climate_database_q826_ci1023['Malaysia', time_period],), (None,), (constant_climate_database_q826_ci1023['Mali', time_period],), (None,), (None,), (constant_climate_database_q826_ci1023['Mauritania', time_period],), (constant_climate_database_q826_ci1023['Mauritius', time_period],), (constant_climate_database_q826_ci1023['Mexico', time_period],), (None,), (constant_climate_database_q826_ci1023['Moldova', time_period],), (constant_climate_database_q826_ci1023['Mongolia', time_period],), (constant_climate_database_q826_ci1023['Montenegro', time_period],), (None,), (constant_climate_database_q826_ci1023['Morocco', time_period],), (constant_climate_database_q826_ci1023['Mozambique', time_period],), (constant_climate_database_q826_ci1023['Myanmar', time_period],), (constant_climate_database_q826_ci1023['Namibia', time_period],), (None,), (constant_climate_database_q826_ci1023['Nepal', time_period],), (constant_climate_database_q826_ci1023['Netherlands', time_period],), (constant_climate_database_q826_ci1023['New Zealand', time_period],), (constant_climate_database_q826_ci1023['Nicaragua', time_period],), (constant_climate_database_q826_ci1023['Niger', time_period],), (constant_climate_database_q826_ci1023['Nigeria', time_period],), (constant_climate_database_q826_ci1023['North Macedonia', time_period],), (constant_climate_database_q826_ci1023['Norway', time_period],), (constant_climate_database_q826_ci1023['Oman', time_period],), (constant_climate_database_q826_ci1023['Pakistan', time_period],), (None,), (constant_climate_database_q826_ci1023['Panama', time_period],), (constant_climate_database_q826_ci1023['Papua New Guinea', time_period],), (constant_climate_database_q826_ci1023['Paraguay', time_period],), (constant_climate_database_q826_ci1023['Peru', time_period],), (constant_climate_database_q826_ci1023['Philippines', time_period],), (constant_climate_database_q826_ci1023['Poland', time_period],), (constant_climate_database_q826_ci1023['Portugal', time_period],), (constant_climate_database_q826_ci1023['Puerto Rico', time_period],), (constant_climate_database_q826_ci1023['Qatar', time_period],), (constant_climate_database_q826_ci1023['Romania', time_period],), (constant_climate_database_q826_ci1023['Russia', time_period],), (constant_climate_database_q826_ci1023['Rwanda', time_period],), (constant_climate_database_q826_ci1023['Samoa', time_period],), (constant_climate_database_q826_ci1023['San Marino', time_period],), (constant_climate_database_q826_ci1023['Sao Tome and Principe', time_period],), (constant_climate_database_q826_ci1023['Saudi Arabia', time_period],), (constant_climate_database_q826_ci1023['Senegal', time_period],), (constant_climate_database_q826_ci1023['Serbia', time_period],), (None,), (constant_climate_database_q826_ci1023['Sierra Leone', time_period],), (None,), (constant_climate_database_q826_ci1023['Slovak Republic', time_period],), (constant_climate_database_q826_ci1023['Slovenia', time_period],), (constant_climate_database_q826_ci1023['Solomon Islands', time_period],), (constant_climate_database_q826_ci1023['Somalia', time_period],), (constant_climate_database_q826_ci1023['South Africa', time_period],), (constant_climate_database_q826_ci1023['South Sudan', time_period],), (constant_climate_database_q826_ci1023['Spain', time_period],), (constant_climate_database_q826_ci1023['Sri Lanka', time_period],), (None,), (None,), (constant_climate_database_q826_ci1023['St. Vincent and the Grenadines', time_period],), (constant_climate_database_q826_ci1023['Sudan', time_period],), (constant_climate_database_q826_ci1023['Suriname', time_period],), (constant_climate_database_q826_ci1023['Sweden', time_period],), (constant_climate_database_q826_ci1023['Switzerland', time_period],), (constant_climate_database_q826_ci1023['Syria', time_period],), (None,), (constant_climate_database_q826_ci1023['Tajikistan', time_period],), (constant_climate_database_q826_ci1023['Tanzania', time_period],), (constant_climate_database_q826_ci1023['Thailand', time_period],), (None,), (constant_climate_database_q826_ci1023['Togo', time_period],), (None,), (constant_climate_database_q826_ci1023['Trinidad and Tobago', time_period],), (constant_climate_database_q826_ci1023['Tunisia', time_period],), (constant_climate_database_q826_ci1023['Türkiye', time_period],), (constant_climate_database_q826_ci1023['Turkmenistan', time_period],), (None,), (constant_climate_database_q826_ci1023['Uganda', time_period],), (constant_climate_database_q826_ci1023['Ukraine', time_period],), (constant_climate_database_q826_ci1023['United Arab Emirates', time_period],), (constant_climate_database_q826_ci1023['United Kingdom', time_period],), (constant_climate_database_q826_ci1023['United States', time_period],), (constant_climate_database_q826_ci1023['Uruguay', time_period],), (constant_climate_database_q826_ci1023['Uzbekistan', time_period],), (constant_climate_database_q826_ci1023['Vanuatu', time_period],), (constant_climate_database_q826_ci1023['Venezuela', time_period],), (constant_climate_database_q826_ci1023['Vietnam', time_period],), (None,), (constant_climate_database_q826_ci1023['Yemen', time_period],), (constant_climate_database_q826_ci1023['Zambia', time_period],), (constant_climate_database_q826_ci1023['Zimbabwe', time_period],),), xl_match(climate_database_country, _climate_database_gdp_loss_pct_hot_adapted_table_0, 0), 1))

    return data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT_ADAPTED.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT_ADAPTED.required))

@publish(data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT_UNADAPTED.schema, cells=data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT_UNADAPTED.cells)
def climate_database_gdp_loss_pct_hot_unadapted(*, constant_climate_database_b1026_b1223: data.Series[str | None], constant_climate_database_q1026_ci1223: data.Series[float | str | None], climate_database_country: str | int | float | bool) -> data.Series[float | str | None]:
    """Extract the 'Hot Un-Adapted' climate scenario GDP loss (percent) for a selected country.

    Provide the country-specific GDP loss percentage under the 'Hot Un-Adapted' scenario, in which temperature increases match the 'Hot' scenario but countries adapt more slowly, for use in climate fiscal risk analysis.

    Args:
        constant_climate_database_b1026_b1223: Constant climate database series providing the country axis used to align the selected country with its position in the GDP loss data.
        constant_climate_database_q1026_ci1223: Constant climate database series of GDP loss percentages by country and time period under the 'Hot Un-Adapted' scenario.
        climate_database_country: Country identifier selecting the economy whose 'Hot Un-Adapted' GDP loss percentage is to be returned.

    Returns:
        A series of GDP loss percentages (relative to baseline GDP) under the 'Hot Un-Adapted' climate scenario, indexed by time period for the selected country.
    """
    data.CONSTANT_CLIMATE_DATABASE_B1026_B1223.schema.validate(constant_climate_database_b1026_b1223)
    data.CONSTANT_CLIMATE_DATABASE_Q1026_CI1223.schema.validate(constant_climate_database_q1026_ci1223)
    _climate_database_gdp_loss_pct_hot_unadapted_table_0 = view(constant_climate_database_b1026_b1223, rows=data.COUNTRY_AXIS_5.keys)
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_index(((constant_climate_database_q1026_ci1223['Afghanistan', time_period],), (constant_climate_database_q1026_ci1223['Albania', time_period],), (constant_climate_database_q1026_ci1223['Algeria', time_period],), (None,), (constant_climate_database_q1026_ci1223['Angola', time_period],), (None,), (None,), (constant_climate_database_q1026_ci1223['Argentina', time_period],), (constant_climate_database_q1026_ci1223['Armenia', time_period],), (None,), (constant_climate_database_q1026_ci1223['Australia', time_period],), (constant_climate_database_q1026_ci1223['Austria', time_period],), (constant_climate_database_q1026_ci1223['Azerbaijan', time_period],), (constant_climate_database_q1026_ci1223['The Bahamas', time_period],), (None,), (constant_climate_database_q1026_ci1223['Bangladesh', time_period],), (None,), (constant_climate_database_q1026_ci1223['Belarus', time_period],), (constant_climate_database_q1026_ci1223['Belgium', time_period],), (constant_climate_database_q1026_ci1223['Belize', time_period],), (constant_climate_database_q1026_ci1223['Benin', time_period],), (constant_climate_database_q1026_ci1223['Bhutan', time_period],), (constant_climate_database_q1026_ci1223['Bolivia', time_period],), (constant_climate_database_q1026_ci1223['Bosnia and Herzegovina', time_period],), (constant_climate_database_q1026_ci1223['Botswana', time_period],), (constant_climate_database_q1026_ci1223['Brazil', time_period],), (constant_climate_database_q1026_ci1223['Brunei Darussalam', time_period],), (constant_climate_database_q1026_ci1223['Bulgaria', time_period],), (constant_climate_database_q1026_ci1223['Burkina Faso', time_period],), (constant_climate_database_q1026_ci1223['Burundi', time_period],), (constant_climate_database_q1026_ci1223['Cabo Verde', time_period],), (constant_climate_database_q1026_ci1223['Cambodia', time_period],), (constant_climate_database_q1026_ci1223['Cameroon', time_period],), (constant_climate_database_q1026_ci1223['Canada', time_period],), (constant_climate_database_q1026_ci1223['Central African Republic', time_period],), (constant_climate_database_q1026_ci1223['Chad', time_period],), (constant_climate_database_q1026_ci1223['Chile', time_period],), (constant_climate_database_q1026_ci1223['China', time_period],), (constant_climate_database_q1026_ci1223['Colombia', time_period],), (constant_climate_database_q1026_ci1223['Comoros', time_period],), (constant_climate_database_q1026_ci1223['Democratic Republic of the Congo', time_period],), (constant_climate_database_q1026_ci1223['Republic of Congo', time_period],), (constant_climate_database_q1026_ci1223['Costa Rica', time_period],), (constant_climate_database_q1026_ci1223["Côte d'Ivoire", time_period],), (constant_climate_database_q1026_ci1223['Croatia', time_period],), (constant_climate_database_q1026_ci1223['Cyprus', time_period],), (constant_climate_database_q1026_ci1223['Czech Republic', time_period],), (constant_climate_database_q1026_ci1223['Denmark', time_period],), (constant_climate_database_q1026_ci1223['Djibouti', time_period],), (None,), (constant_climate_database_q1026_ci1223['Dominican Republic', time_period],), (constant_climate_database_q1026_ci1223['Ecuador', time_period],), (constant_climate_database_q1026_ci1223['Egypt', time_period],), (constant_climate_database_q1026_ci1223['El Salvador', time_period],), (constant_climate_database_q1026_ci1223['Equatorial Guinea', time_period],), (constant_climate_database_q1026_ci1223['Eritrea', time_period],), (constant_climate_database_q1026_ci1223['Estonia', time_period],), (constant_climate_database_q1026_ci1223['Eswatini', time_period],), (constant_climate_database_q1026_ci1223['Ethiopia', time_period],), (constant_climate_database_q1026_ci1223['Fiji', time_period],), (constant_climate_database_q1026_ci1223['Finland', time_period],), (constant_climate_database_q1026_ci1223['France', time_period],), (constant_climate_database_q1026_ci1223['Gabon', time_period],), (constant_climate_database_q1026_ci1223['The Gambia', time_period],), (constant_climate_database_q1026_ci1223['Georgia', time_period],), (constant_climate_database_q1026_ci1223['Germany', time_period],), (constant_climate_database_q1026_ci1223['Ghana', time_period],), (constant_climate_database_q1026_ci1223['Greece', time_period],), (None,), (constant_climate_database_q1026_ci1223['Guatemala', time_period],), (constant_climate_database_q1026_ci1223['Guinea', time_period],), (constant_climate_database_q1026_ci1223['Guinea-Bissau', time_period],), (constant_climate_database_q1026_ci1223['Guyana', time_period],), (constant_climate_database_q1026_ci1223['Haiti', time_period],), (constant_climate_database_q1026_ci1223['Honduras', time_period],), (None,), (constant_climate_database_q1026_ci1223['Hungary', time_period],), (constant_climate_database_q1026_ci1223['Iceland', time_period],), (constant_climate_database_q1026_ci1223['India', time_period],), (constant_climate_database_q1026_ci1223['Indonesia', time_period],), (constant_climate_database_q1026_ci1223['Islamic Republic of Iran', time_period],), (constant_climate_database_q1026_ci1223['Iraq', time_period],), (constant_climate_database_q1026_ci1223['Ireland', time_period],), (constant_climate_database_q1026_ci1223['Israel', time_period],), (constant_climate_database_q1026_ci1223['Italy', time_period],), (constant_climate_database_q1026_ci1223['Jamaica', time_period],), (constant_climate_database_q1026_ci1223['Japan', time_period],), (constant_climate_database_q1026_ci1223['Jordan', time_period],), (constant_climate_database_q1026_ci1223['Kazakhstan', time_period],), (constant_climate_database_q1026_ci1223['Kenya', time_period],), (None,), (constant_climate_database_q1026_ci1223['Korea', time_period],), (None,), (constant_climate_database_q1026_ci1223['Kuwait', time_period],), (constant_climate_database_q1026_ci1223['Kyrgyz Republic', time_period],), (constant_climate_database_q1026_ci1223['Lao P.D.R.', time_period],), (constant_climate_database_q1026_ci1223['Latvia', time_period],), (constant_climate_database_q1026_ci1223['Lebanon', time_period],), (constant_climate_database_q1026_ci1223['Lesotho', time_period],), (constant_climate_database_q1026_ci1223['Liberia', time_period],), (constant_climate_database_q1026_ci1223['Libya', time_period],), (constant_climate_database_q1026_ci1223['Lithuania', time_period],), (constant_climate_database_q1026_ci1223['Luxembourg', time_period],), (None,), (constant_climate_database_q1026_ci1223['Madagascar', time_period],), (constant_climate_database_q1026_ci1223['Malawi', time_period],), (constant_climate_database_q1026_ci1223['Malaysia', time_period],), (None,), (constant_climate_database_q1026_ci1223['Mali', time_period],), (None,), (None,), (constant_climate_database_q1026_ci1223['Mauritania', time_period],), (constant_climate_database_q1026_ci1223['Mauritius', time_period],), (constant_climate_database_q1026_ci1223['Mexico', time_period],), (None,), (constant_climate_database_q1026_ci1223['Moldova', time_period],), (constant_climate_database_q1026_ci1223['Mongolia', time_period],), (constant_climate_database_q1026_ci1223['Montenegro', time_period],), (None,), (constant_climate_database_q1026_ci1223['Morocco', time_period],), (constant_climate_database_q1026_ci1223['Mozambique', time_period],), (constant_climate_database_q1026_ci1223['Myanmar', time_period],), (constant_climate_database_q1026_ci1223['Namibia', time_period],), (None,), (constant_climate_database_q1026_ci1223['Nepal', time_period],), (constant_climate_database_q1026_ci1223['Netherlands', time_period],), (constant_climate_database_q1026_ci1223['New Zealand', time_period],), (constant_climate_database_q1026_ci1223['Nicaragua', time_period],), (constant_climate_database_q1026_ci1223['Niger', time_period],), (constant_climate_database_q1026_ci1223['Nigeria', time_period],), (constant_climate_database_q1026_ci1223['North Macedonia', time_period],), (constant_climate_database_q1026_ci1223['Norway', time_period],), (constant_climate_database_q1026_ci1223['Oman', time_period],), (constant_climate_database_q1026_ci1223['Pakistan', time_period],), (None,), (constant_climate_database_q1026_ci1223['Panama', time_period],), (constant_climate_database_q1026_ci1223['Papua New Guinea', time_period],), (constant_climate_database_q1026_ci1223['Paraguay', time_period],), (constant_climate_database_q1026_ci1223['Peru', time_period],), (constant_climate_database_q1026_ci1223['Philippines', time_period],), (constant_climate_database_q1026_ci1223['Poland', time_period],), (constant_climate_database_q1026_ci1223['Portugal', time_period],), (constant_climate_database_q1026_ci1223['Puerto Rico', time_period],), (constant_climate_database_q1026_ci1223['Qatar', time_period],), (constant_climate_database_q1026_ci1223['Romania', time_period],), (constant_climate_database_q1026_ci1223['Russia', time_period],), (constant_climate_database_q1026_ci1223['Rwanda', time_period],), (constant_climate_database_q1026_ci1223['Samoa', time_period],), (None,), (constant_climate_database_q1026_ci1223['Sao Tome and Principe', time_period],), (constant_climate_database_q1026_ci1223['Saudi Arabia', time_period],), (constant_climate_database_q1026_ci1223['Senegal', time_period],), (constant_climate_database_q1026_ci1223['Serbia', time_period],), (None,), (constant_climate_database_q1026_ci1223['Sierra Leone', time_period],), (None,), (constant_climate_database_q1026_ci1223['Slovak Republic', time_period],), (constant_climate_database_q1026_ci1223['Slovenia', time_period],), (constant_climate_database_q1026_ci1223['Solomon Islands', time_period],), (constant_climate_database_q1026_ci1223['Somalia', time_period],), (constant_climate_database_q1026_ci1223['South Africa', time_period],), (constant_climate_database_q1026_ci1223['South Sudan', time_period],), (constant_climate_database_q1026_ci1223['Spain', time_period],), (constant_climate_database_q1026_ci1223['Sri Lanka', time_period],), (None,), (None,), (None,), (constant_climate_database_q1026_ci1223['Sudan', time_period],), (constant_climate_database_q1026_ci1223['Suriname', time_period],), (constant_climate_database_q1026_ci1223['Sweden', time_period],), (constant_climate_database_q1026_ci1223['Switzerland', time_period],), (constant_climate_database_q1026_ci1223['Syria', time_period],), (None,), (constant_climate_database_q1026_ci1223['Tajikistan', time_period],), (constant_climate_database_q1026_ci1223['Tanzania', time_period],), (constant_climate_database_q1026_ci1223['Thailand', time_period],), (None,), (constant_climate_database_q1026_ci1223['Togo', time_period],), (None,), (constant_climate_database_q1026_ci1223['Trinidad and Tobago', time_period],), (constant_climate_database_q1026_ci1223['Tunisia', time_period],), (constant_climate_database_q1026_ci1223['Türkiye', time_period],), (constant_climate_database_q1026_ci1223['Turkmenistan', time_period],), (None,), (constant_climate_database_q1026_ci1223['Uganda', time_period],), (constant_climate_database_q1026_ci1223['Ukraine', time_period],), (constant_climate_database_q1026_ci1223['United Arab Emirates', time_period],), (constant_climate_database_q1026_ci1223['United Kingdom', time_period],), (constant_climate_database_q1026_ci1223['United States', time_period],), (constant_climate_database_q1026_ci1223['Uruguay', time_period],), (constant_climate_database_q1026_ci1223['Uzbekistan', time_period],), (constant_climate_database_q1026_ci1223['Vanuatu', time_period],), (constant_climate_database_q1026_ci1223['Venezuela', time_period],), (constant_climate_database_q1026_ci1223['Vietnam', time_period],), (None,), (constant_climate_database_q1026_ci1223['Yemen', time_period],), (constant_climate_database_q1026_ci1223['Zambia', time_period],), (constant_climate_database_q1026_ci1223['Zimbabwe', time_period],),), xl_match(climate_database_country, _climate_database_gdp_loss_pct_hot_unadapted_table_0, 0), 1))

    return data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT_UNADAPTED.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_LOSS_PCT_HOT_UNADAPTED.required))

@publish(data.CLIMATE_DATABASE_GDP_INDEX_PARIS.schema, cells=data.CLIMATE_DATABASE_GDP_INDEX_PARIS.cells)
def climate_database_gdp_index_paris(*, climate_database_gdp_loss_pct_paris: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Build the Paris-scenario GDP index from climate-driven GDP losses.

    Express the cumulative GDP effect of the Paris (SSP1-2.6) climate scenario as an index level relative to a baseline of 100.

    Args:
        climate_database_gdp_loss_pct_paris: Percentage loss in GDP relative to the baseline under the Paris climate change scenario, in which the 2015 Paris Agreement commitments are met and global warming is kept below 2 degrees Celsius above pre-industrial levels; used as the reference for constructing the index.

    Returns:
        A series of the Paris-scenario GDP index, set to 100 minus the GDP loss percentage, aligned with the time periods of the input loss series.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(100, climate_database_gdp_loss_pct_paris[time_period]))

    return data.CLIMATE_DATABASE_GDP_INDEX_PARIS.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_INDEX_PARIS.required))

@publish(data.CLIMATE_DATABASE_GDP_INDEX_MODERATE.schema, cells=data.CLIMATE_DATABASE_GDP_INDEX_MODERATE.cells)
def climate_database_gdp_index_moderate(*, climate_database_gdp_loss_pct_moderate: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Convert moderate-scenario GDP losses into a GDP index.

    Express the moderate-scenario GDP path relative to a no-climate-change baseline as an index with 100 denoting the baseline level.

    Args:
        climate_database_gdp_loss_pct_moderate: Moderate-scenario GDP losses, in percent of the baseline level, from the climate database; used to derive the corresponding GDP index.

    Returns:
        The reconstructed moderate-scenario GDP index series, expressed as an index with 100 denoting the baseline level.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(100, climate_database_gdp_loss_pct_moderate[time_period]))

    return data.CLIMATE_DATABASE_GDP_INDEX_MODERATE.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_INDEX_MODERATE.required))

@publish(data.CLIMATE_DATABASE_GDP_INDEX_HIGH.schema, cells=data.CLIMATE_DATABASE_GDP_INDEX_HIGH.cells)
def climate_database_gdp_index_high(*, climate_database_gdp_loss_pct_high: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Build the high-scenario GDP index from climate-driven GDP losses.

    Convert high-scenario GDP loss percentages into an indexed GDP level for climate risk assessment.

    Args:
        climate_database_gdp_loss_pct_high: Percentage loss in GDP under the high climate change scenario, expressed as percentage points relative to the baseline.

    Returns:
        Series of GDP index values, where 100 represents the baseline level and values above 100 indicate the percentage loss applied to that base.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(100, climate_database_gdp_loss_pct_high[time_period]))

    return data.CLIMATE_DATABASE_GDP_INDEX_HIGH.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_INDEX_HIGH.required))

@publish(data.CLIMATE_DATABASE_GDP_INDEX_HOT.schema, cells=data.CLIMATE_DATABASE_GDP_INDEX_HOT.cells)
def climate_database_gdp_index_hot(*, climate_database_gdp_loss_pct_hot: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Build the 'hot' scenario GDP index by adding each period's GDP loss percentage to a base of 100.

    Expresses the climate-driven GDP effect under the 'hot' scenario (SSP3-7.0 emissions with 90th-percentile temperature increases) as an indexed level relative to the no-climate-change baseline of 100.

    Args:
        climate_database_gdp_loss_pct_hot: GDP loss (in percent, relative to the baseline) under the 'hot' climate scenario for each period, sourced from the Climate Data worksheet; values may be missing where no climate estimates are available.

    Returns:
        A Series of indexed GDP levels under the 'hot' scenario, where a value below 100 indicates a GDP level below the no-climate-change baseline, aligned to the required periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(100, climate_database_gdp_loss_pct_hot[time_period]))

    return data.CLIMATE_DATABASE_GDP_INDEX_HOT.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_INDEX_HOT.required))

@publish(data.CLIMATE_DATABASE_GDP_INDEX_HOT_ADAPTED.schema, cells=data.CLIMATE_DATABASE_GDP_INDEX_HOT_ADAPTED.cells)
def climate_database_gdp_index_hot_adapted(*, climate_database_gdp_loss_pct_hot_adapted: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the GDP index for the hot adapted climate scenario.

    Converts the hot adapted scenario's GDP loss percentage into a GDP index level, where 100 represents the baseline GDP, so that climate-adjusted output can be compared against the baseline in the macro-fiscal projections.

    Args:
        climate_database_gdp_loss_pct_hot_adapted: Percentage loss in GDP relative to the baseline under the hot adapted climate scenario, in which countries adapt to the higher temperatures of the hot scenario more quickly.

    Returns:
        GDP index for the hot adapted scenario, equal to 100 plus the GDP loss percentage.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(100, climate_database_gdp_loss_pct_hot_adapted[time_period]))

    return data.CLIMATE_DATABASE_GDP_INDEX_HOT_ADAPTED.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_INDEX_HOT_ADAPTED.required))

@publish(data.CLIMATE_DATABASE_GDP_INDEX_HOT_UNADAPTED.schema, cells=data.CLIMATE_DATABASE_GDP_INDEX_HOT_UNADAPTED.cells)
def climate_database_gdp_index_hot_unadapted(*, climate_database_gdp_loss_pct_hot_unadapted: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the hot un-adapted climate scenario GDP index.

    Convert the hot un-adapted climate scenario GDP loss into an index level relative to a baseline of 100.

    Args:
        climate_database_gdp_loss_pct_hot_unadapted: Series of GDP losses (in percent) under the hot un-adapted climate scenario, in which countries adopt very slowly to climate change and temperature increases match the hot scenario.

    Returns:
        Series of GDP index levels for the hot un-adapted climate scenario, where 100 denotes the baseline level of GDP before climate change losses are applied.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_add(100, climate_database_gdp_loss_pct_hot_unadapted[time_period]))

    return data.CLIMATE_DATABASE_GDP_INDEX_HOT_UNADAPTED.collect(evaluate(formula, data.CLIMATE_DATABASE_GDP_INDEX_HOT_UNADAPTED.required))

@publish(data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_PARIS.schema, cells=data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_PARIS.cells)
def climate_database_labour_productivity_growth_variation_paris(*, climate_database_gdp_index_paris: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the annual labour productivity growth variation under the Paris climate scenario.

    Derives the year-on-year percentage change in labour productivity growth under the Paris scenario, capturing how climate change slows GDP per employed person.

    Args:
        climate_database_gdp_index_paris: GDP index under the Paris climate scenario, indexed by time period, used to derive the annual labour productivity growth variation.

    Returns:
        A series of annual labour productivity growth variation values under the Paris climate scenario, indexed by time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(climate_database_gdp_index_paris[time_period], climate_database_gdp_index_paris[time_period - 1]), 100), 100))

    return data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_PARIS.collect(evaluate(formula, data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_PARIS.required))

@publish(data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_MODERATE.schema, cells=data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_MODERATE.cells)
def climate_database_labour_productivity_growth_variation_moderate(*, climate_database_gdp_index_moderate: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Derive the year-over-year labour productivity growth variation under the moderate climate scenario.

    Expresses the period-on-period growth variation in labour productivity as a percentage, given a GDP index for the moderate emissions pathway.

    Args:
        climate_database_gdp_index_moderate: GDP index series for the moderate (SSP2-4.5) climate scenario, indexed by time period; used to form the period-on-period growth variation.

    Returns:
        Series of labour productivity growth variation values for the moderate climate scenario, expressed as percentages, aligned to the required periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(climate_database_gdp_index_moderate[time_period], climate_database_gdp_index_moderate[time_period - 1]), 100), 100))

    return data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_MODERATE.collect(evaluate(formula, data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_MODERATE.required))

@publish(data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HIGH.schema, cells=data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HIGH.cells)
def climate_database_labour_productivity_growth_variation_high(*, climate_database_gdp_index_high: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the annual variation in labour productivity growth under the high climate scenario.

    Derives year-on-year labour productivity growth variation under the high-emissions scenario from the climate database GDP index.

    Args:
        climate_database_gdp_index_high: Climate database GDP index series for the high scenario, in which countries scale back mitigation policies in a fragmented world with limited energy efficiency improvements and continued fossil fuel use; the index level is used to derive annual labour productivity growth variation.

    Returns:
        A series of annual labour productivity growth variation values for the high climate scenario, expressed as the percentage change in the GDP index relative to the prior period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(climate_database_gdp_index_high[time_period], climate_database_gdp_index_high[time_period - 1]), 100), 100))

    return data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HIGH.collect(evaluate(formula, data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HIGH.required))

@publish(data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT.schema, cells=data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT.cells)
def climate_database_labour_productivity_growth_variation_hot(*, climate_database_gdp_index_hot: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the year-over-year variation in hot-scenario labour productivity growth.

    Derives the labour productivity growth variation under the hot climate scenario from the associated GDP index.

    Args:
        climate_database_gdp_index_hot: Hot-scenario GDP index series, indexed by time period, used to derive the annual labour productivity growth variation.

    Returns:
        A series of the hot-scenario labour productivity growth variation for each projected time period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(climate_database_gdp_index_hot[time_period], climate_database_gdp_index_hot[time_period - 1]), 100), 100))

    return data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT.collect(evaluate(formula, data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT.required))

@publish(data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_ADAPTED.schema, cells=data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_ADAPTED.cells)
def climate_database_labour_productivity_growth_variation_hot_adapted(*, climate_database_gdp_index_hot_adapted: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the year-on-year variation in the hot-adapted labour productivity growth index.

    Derive the growth rate of labour productivity under the hot-adapted climate scenario from the corresponding GDP index.

    Args:
        climate_database_gdp_index_hot_adapted: GDP index series for the hot-adapted climate scenario; each value is compared with its preceding period to obtain the labour productivity growth variation.

    Returns:
        A series of labour productivity growth variations for the hot-adapted scenario, expressed as percentage-point changes relative to the prior period.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(climate_database_gdp_index_hot_adapted[time_period], climate_database_gdp_index_hot_adapted[time_period - 1]), 100), 100))

    return data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_ADAPTED.collect(evaluate(formula, data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_ADAPTED.required))

@publish(data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_UNADAPTED.schema, cells=data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_UNADAPTED.cells)
def climate_database_labour_productivity_growth_variation_hot_unadapted(*, climate_database_gdp_index_hot_unadapted: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Compute the year-on-year percentage variation in labor productivity for the hot un-adapted climate scenario.

    Express the climate-driven GDP impact under the hot un-adapted scenario as an annual growth variation in labor productivity.

    Args:
        climate_database_gdp_index_hot_unadapted: Climate-database index of climate-driven GDP effects under the hot un-adapted scenario, where countries adapt to higher temperatures over 50 years and macroeconomic effects are more severe than in the hot scenario.

    Returns:
        Series of annual percentage variations in labor productivity implied by the hot un-adapted GDP index.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_sub(xl_mul(xl_div(climate_database_gdp_index_hot_unadapted[time_period], climate_database_gdp_index_hot_unadapted[time_period - 1]), 100), 100))

    return data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_UNADAPTED.collect(evaluate(formula, data.CLIMATE_DATABASE_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_UNADAPTED.required))

@publish(data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_PARIS.schema, cells=data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_PARIS.cells)
def climate_data_labour_productivity_growth_variation_paris(*, climate_database_labour_productivity_growth_variation_paris: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Collect the Paris-scenario labour productivity growth variation block from the climate database.

    Provides the mirror of the Climate Database variation block for the Paris scenario so that labour productivity growth variation can be drawn into downstream macro-fiscal projections.

    Args:
        climate_database_labour_productivity_growth_variation_paris: Series holding the labour productivity growth variation values associated with the Paris climate change scenario, indexed by time period, mirroring the Climate Database variation block.

    Returns:
        A Series of the collected Paris labour productivity growth variation values, aligned to the required periods of the climate database variation block.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(climate_database_labour_productivity_growth_variation_paris[time_period])

    return data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_PARIS.collect(evaluate(formula, data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_PARIS.required))

@publish(data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_MODERATE.schema, cells=data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_MODERATE.cells)
def climate_data_labour_productivity_growth_variation_moderate(*, climate_database_labour_productivity_growth_variation_moderate: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Return the moderate-scenario climate variation in labour productivity growth.

    Provide the moderate-scenario climate adjustment applied to labour productivity growth, mirroring the Climate Database variation block.

    Args:
        climate_database_labour_productivity_growth_variation_moderate: Climate Database series of labour productivity growth variations under the moderate climate scenario, indexed by projection period.

    Returns:
        A series of labour productivity growth variation values under the moderate climate scenario, expressed in percentage points relative to the baseline and aligned to the required periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(climate_database_labour_productivity_growth_variation_moderate[time_period])

    return data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_MODERATE.collect(evaluate(formula, data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_MODERATE.required))

@publish(data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HIGH.schema, cells=data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HIGH.cells)
def climate_data_labour_productivity_growth_variation_high(*, climate_database_labour_productivity_growth_variation_high: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Build the high climate scenario's labour productivity growth variation series.

    Resolves the mirrored Climate Database variation block for the high-emissions SSP3-7.0 scenario into a time-indexed series of labour productivity growth variations used by Q-CRAFT.

    Args:
        climate_database_labour_productivity_growth_variation_high: High climate scenario labour productivity growth variation values from the Climate Data block, keyed by projection year and evaluated per time period.

    Returns:
        A series of labour productivity growth variation values for the high climate scenario, indexed by year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(climate_database_labour_productivity_growth_variation_high[time_period])

    return data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HIGH.collect(evaluate(formula, data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HIGH.required))

@publish(data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT.schema, cells=data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT.cells)
def climate_data_labour_productivity_growth_variation_hot(*, climate_database_labour_productivity_growth_variation_hot: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Return the "hot" climate scenario labour productivity growth variation series.

    Provide the per-period labour productivity growth variation under the hot climate scenario, mirroring the Climate Database variation block.

    Args:
        climate_database_labour_productivity_growth_variation_hot: Climate Database labour productivity growth variation series for the hot scenario, indexed by time period.

    Returns:
        Series of labour productivity growth variations for the hot scenario, aligned to the modelled time periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(climate_database_labour_productivity_growth_variation_hot[time_period])

    return data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT.collect(evaluate(formula, data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT.required))

@publish(data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_ADAPTED.schema, cells=data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_ADAPTED.cells)
def climate_data_labour_productivity_growth_variation_hot_adapted(*, climate_database_labour_productivity_growth_variation_hot_adapted: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Return the hot-adapted climate scenario's labour productivity growth variation series.

    Mirrors the Climate Database variation block so the hot-adapted scenario's labour productivity growth impacts can be carried into the macro-fiscal projections.

    Args:
        climate_database_labour_productivity_growth_variation_hot_adapted: Climate Database series holding the variation in labour productivity growth under the hot-adapted scenario, in which countries adapt more quickly to the same temperature increases as the hot scenario.

    Returns:
        A series of the hot-adapted labour productivity growth variation values by time period, expressed as numeric shares where available and otherwise as the underlying series entries.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(climate_database_labour_productivity_growth_variation_hot_adapted[time_period])

    return data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_ADAPTED.collect(evaluate(formula, data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_ADAPTED.required))

@publish(data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_UNADAPTED.schema, cells=data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_UNADAPTED.cells)
def climate_data_labour_productivity_growth_variation_hot_unadapted(*, climate_database_labour_productivity_growth_variation_hot_unadapted: data.Series[float | str | None]) -> data.Series[float | str | None]:
    """Retrieve the "Hot Un-Adapted" climate change scenario's labor productivity growth variation series.

    Expose the climate-driven productivity growth variation applied to the labour productivity baseline under the Hot Un-Adapted scenario.

    Args:
        climate_database_labour_productivity_growth_variation_hot_unadapted: Series of per-period labour productivity growth variations (as decimals or strings) for the Hot Un-Adapted climate change scenario, mirroring the Climate Database variation block; values are taken as measures over time.

    Returns:
        Series of per-period labour productivity growth variations under the Hot Un-Adapted scenario, aligned to the series' required time periods.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(climate_database_labour_productivity_growth_variation_hot_unadapted[time_period])

    return data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_UNADAPTED.collect(evaluate(formula, data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_HOT_UNADAPTED.required))

@publish(data.BASELINE_INTEREST_RATE.schema, cells=data.BASELINE_INTEREST_RATE.cells)
def baseline_interest_rate(*, interest_rate_nominal_interest_rate: data.Series[float | str | None]) -> data.BaselineInterestRate:
    """Collect the baseline nominal interest rate profile from the user's interest rate assumption input.

    Provide the baseline interest rate path used to project debt-to-GDP dynamics before any climate change scenario effects are applied.

    Args:
        interest_rate_nominal_interest_rate: Nominal interest rate assumption by year, expressed as a rate; taken as selected in the Interest Rate worksheet.

    Returns:
        The baseline nominal interest rate time series used in the debt dynamics calculation.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(interest_rate_nominal_interest_rate[time_period])

    return data.BASELINE_INTEREST_RATE.collect(evaluate(formula, data.BASELINE_INTEREST_RATE.required))

@publish(data.BASELINE_OVERALL_BALANCE_PCT_GDP.schema, cells=data.BASELINE_OVERALL_BALANCE_PCT_GDP.cells)
def baseline_overall_balance_pct_gdp(*, baseline_engine_total_expenditure_pct_gdp: data.Series[float | str | None], macrofiscal_overall_balance_pct_gdp: data.Series[float | str | None], baseline_revenue_pct_gdp: data.BaselineRevenuePctGdp) -> data.BaselineOverallBalancePctGdp:
    """Project the baseline overall balance as a share of GDP.

    Yields the headline overall fiscal balance under a 'no policy change' baseline, which reflects unchanged revenue and primary expenditure settings over the long run.

    Args:
        baseline_engine_total_expenditure_pct_gdp: Total expenditure under the baseline scenario, expressed as a share of nominal GDP.
        macrofiscal_overall_balance_pct_gdp: Overall balance (revenue and grants less total expenditure) as a share of nominal GDP from the macro-fiscal data, reflecting the IMF WEO horizon where available.
        baseline_revenue_pct_gdp: Government revenue under the baseline scenario, expressed as a share of nominal GDP and assumed to remain constant in the long run.

    Returns:
        A series of the baseline overall balance as a share of nominal GDP for each projection year; it is taken from the macro-fiscal overall balance through the last WEO year and computed as revenue less total expenditure (as shares of GDP) thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_overall_balance_pct_gdp[time_period])
        return as_measure(xl_sub(baseline_revenue_pct_gdp[time_period], baseline_engine_total_expenditure_pct_gdp[time_period]))

    return data.BASELINE_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.BASELINE_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.BASELINE_NOMINAL_GDP_GROWTH.schema, cells=data.BASELINE_NOMINAL_GDP_GROWTH.cells)
def baseline_nominal_gdp_growth(*, baseline_engine_nominal_gdp_lcu: data.Series[float | str | None], macrofiscal_nominal_gdp_growth: data.Series[float | str | None]) -> data.BaselineNominalGdpGrowth:
    """Derive baseline nominal GDP growth from the baseline engine and macro-fiscal projections.

    Provide the year-on-year percentage growth in nominal GDP for the baseline scenario, using WEO-aligned macro-fiscal growth through the end of the WEO horizon and growth implied by the baseline engine thereafter.

    Args:
        baseline_engine_nominal_gdp_lcu: Baseline nominal GDP levels in billions of local currency units, projected by the tool's baseline engine; used to compute year-on-year growth after the end of the WEO horizon.
        macrofiscal_nominal_gdp_growth: Nominal GDP growth rate (in percent) from the IMF WEO-based macro-fiscal projections, applied up to and including the last year of the WEO horizon.

    Returns:
        A BaselineNominalGdpGrowth series of nominal GDP growth rates in percent per year, covering the projection horizon.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_nominal_gdp_growth[time_period])
        return as_measure(xl_sub(xl_mul(xl_div(baseline_engine_nominal_gdp_lcu[time_period], baseline_engine_nominal_gdp_lcu[time_period - 1]), 100), 100))

    return data.BASELINE_NOMINAL_GDP_GROWTH.collect(evaluate(formula, data.BASELINE_NOMINAL_GDP_GROWTH.required))

@publish(data.BASELINE_REVENUE_PCT_GDP.schema, cells=data.BASELINE_REVENUE_PCT_GDP.cells)
def baseline_revenue_pct_gdp(*, baseline_engine_nominal_gdp_lcu: data.Series[float | str | None], baseline_engine_revenue_lcu: data.Series[float | str | None], macrofiscal_revenue_pct_gdp: data.Series[float | str | None]) -> data.BaselineRevenuePctGdp:
    """Compute the baseline government revenue-to-GDP ratio.

    Derive revenue as a share of nominal GDP (in percent) for the baseline scenario, using the constant revenue-to-GDP assumption after the IMF WEO horizon.

    Args:
        baseline_engine_nominal_gdp_lcu: Baseline nominal GDP in billions of local currency units, projected from employment, productivity, and GDP deflator growth.
        baseline_engine_revenue_lcu: Baseline general government revenue in billions of local currency units, growing in line with nominal GDP over the projection horizon.
        macrofiscal_revenue_pct_gdp: Revenue-to-GDP ratio (in percent) loaded from the Macro-fiscal worksheet for the period through the end of the WEO horizon (2029).

    Returns:
        A BaselineRevenuePctGdp series giving the baseline revenue-to-GDP ratio (in percent) for each projection year, using the Macro-fiscal ratio through 2029 and the revenue-to-nominal-GDP ratio thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(macrofiscal_revenue_pct_gdp[time_period])
        return as_measure(xl_mul(xl_div(baseline_engine_revenue_lcu[time_period], baseline_engine_nominal_gdp_lcu[time_period]), 100))

    return data.BASELINE_REVENUE_PCT_GDP.collect(evaluate(formula, data.BASELINE_REVENUE_PCT_GDP.required))

@publish(data.BASELINE_GDP_DEFLATOR_GROWTH.schema, cells=data.BASELINE_GDP_DEFLATOR_GROWTH.cells)
def baseline_gdp_deflator_growth(*, macrofiscal_gdp_deflator_growth: data.Series[float | str | None], inflation_path: data.Series[float | str | None]) -> data.BaselineGdpDeflatorGrowth:
    """Derive the baseline GDP deflator growth trajectory that stitches WEO data to the long-run inflation assumption.

    Builds the price-side growth path used to convert real GDP growth into the nominal GDP projections that underpin revenue, expenditure, and debt dynamics in the baseline scenario.

    Args:
        macrofiscal_gdp_deflator_growth: Baseline GDP deflator growth loaded from the Macro-fiscal worksheet, covering the period through the IMF WEO horizon; used as the source of deflator growth up to and including 2028.
        inflation_path: User-assumed long-run inflation path derived from the GDP deflator, typically set to the Central Bank's inflation target or the WEO projection for the final WEO year; used for deflator growth from 2029 onwards.

    Returns:
        A baseline series of GDP deflator growth rates by projection period, equal to the Macro-fiscal deflator growth through 2028 and to the long-run inflation assumption thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2028:
            return as_measure(macrofiscal_gdp_deflator_growth[time_period])
        return as_measure(inflation_path[time_period])

    return data.BASELINE_GDP_DEFLATOR_GROWTH.collect(evaluate(formula, data.BASELINE_GDP_DEFLATOR_GROWTH.required))

@publish(data.BASELINE_POPULATION_GROWTH.schema, cells=data.BASELINE_POPULATION_GROWTH.cells)
def baseline_population_growth(*, baseline_engine_total_population: data.Series[float | str | None], demography_total_population: data.Series[float | str | None]) -> data.BaselinePopulationGrowth:
    """Compute the baseline growth rate of total population.

    Derive the year-on-year growth rate of total population used to drive the baseline macro-fiscal scenario.

    Args:
        baseline_engine_total_population: Projected total population levels from the baseline engine, indexed by year, used to compute population growth from 2012 onwards.
        demography_total_population: Historical total population levels from the Demography worksheet, indexed by year, used to compute population growth through 2011.

    Returns:
        A BaselinePopulationGrowth series of year-on-year total population growth rates, in percent, calculated from historical demography through 2011 and from the baseline population projection thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2011:
            return as_measure(xl_sub(xl_mul(xl_div(demography_total_population[time_period], demography_total_population[time_period - 1]), 100), 100))
        return as_measure(xl_sub(xl_mul(xl_div(baseline_engine_total_population[time_period], baseline_engine_total_population[time_period - 1]), 100), 100))

    return data.BASELINE_POPULATION_GROWTH.collect(evaluate(formula, data.BASELINE_POPULATION_GROWTH.required))

@publish(data.SCENARIO_PRIMARY_BALANCE_PCT_GDP.schema, cells=data.SCENARIO_PRIMARY_BALANCE_PCT_GDP.cells)
def scenario_primary_balance_pct_gdp(*, paris_engine_primary_balance_pct_gdp: data.Series[float | str | None], moderate_engine_primary_balance_pct_gdp: data.Series[float | str | None], high_engine_primary_balance_pct_gdp: data.Series[float | str | None], hot_engine_primary_balance_pct_gdp: data.Series[float | str | None], hot_adapted_engine_primary_balance_pct_gdp: data.Series[float | str | None], hot_unadapted_engine_primary_balance_pct_gdp: data.Series[float | str | None]) -> data.ScenarioPrimaryBalancePctGdp:
    """Assemble the climate-scenario primary balance (percent of GDP) projection.

    Selects, for each climate scenario path, the projected primary balance as a share of nominal GDP, excluding the baseline comparison row.

    Args:
        paris_engine_primary_balance_pct_gdp: Primary balance as a share of nominal GDP under the Paris scenario, where the 2015 Paris Agreement commitments are met and the global temperature increase above pre-industrial levels stays below 2°C at the end of the century.
        moderate_engine_primary_balance_pct_gdp: Primary balance as a share of nominal GDP under the Moderate scenario, where mitigation policies continue along observed trends but more aggressive action to meet Paris commitments is not taken.
        high_engine_primary_balance_pct_gdp: Primary balance as a share of nominal GDP under the High scenario, where mitigation efforts are scaled back in a fragmented world with limited energy efficiency gains and continued fossil fuel use.
        hot_engine_primary_balance_pct_gdp: Primary balance as a share of nominal GDP under the Hot scenario, using the 90th percentile of temperature increases among climate models applying SSP3-7.0 emissions instead of the median.
        hot_adapted_engine_primary_balance_pct_gdp: Primary balance as a share of nominal GDP under the Hot adapted scenario, in which countries adapt more quickly (within 20 years) to the same temperature increases as the Hot scenario.
        hot_unadapted_engine_primary_balance_pct_gdp: Primary balance as a share of nominal GDP under the Hot un-adapted scenario, in which countries adapt more slowly (within 50 years) to the same temperature increases as the Hot scenario.

    Returns:
        A climate-scenario primary balance projection holding, for each time period, the primary balance as a share of nominal GDP for every scenario path, excluding the baseline comparison row.
    """
    def formula(scenario: str, time_period: int) -> float | str | None:
        if scenario == 'Paris':
            return as_measure(paris_engine_primary_balance_pct_gdp[time_period])
        elif scenario == 'Moderate':
            return as_measure(moderate_engine_primary_balance_pct_gdp[time_period])
        elif scenario == 'High':
            return as_measure(high_engine_primary_balance_pct_gdp[time_period])
        elif scenario == 'Hot':
            return as_measure(hot_engine_primary_balance_pct_gdp[time_period])
        elif scenario == 'Hot adapted':
            return as_measure(hot_adapted_engine_primary_balance_pct_gdp[time_period])
        return as_measure(hot_unadapted_engine_primary_balance_pct_gdp[time_period])

    return data.SCENARIO_PRIMARY_BALANCE_PCT_GDP.collect(evaluate(formula, data.SCENARIO_PRIMARY_BALANCE_PCT_GDP.required))

@publish(data.SCENARIO_OVERALL_BALANCE_PCT_GDP.schema, cells=data.SCENARIO_OVERALL_BALANCE_PCT_GDP.cells)
def scenario_overall_balance_pct_gdp(*, paris_engine_overall_balance_pct_gdp: data.Series[float | str | None], moderate_engine_overall_balance_pct_gdp: data.Series[float | str | None], high_engine_overall_balance_pct_gdp: data.Series[float | str | None], hot_engine_overall_balance_pct_gdp: data.Series[float | str | None], hot_adapted_engine_overall_balance_pct_gdp: data.Series[float | str | None], hot_unadapted_engine_overall_balance_pct_gdp: data.Series[float | str | None]) -> data.ScenarioOverallBalancePctGdp:
    """Assemble scenario-specific overall balance paths as a share of nominal GDP.

    Expose the overall fiscal balance (percent of GDP) for each climate scenario path, excluding the baseline comparison row, so projections to 2099 can be reported and compared across scenarios.

    Args:
        paris_engine_overall_balance_pct_gdp: Overall balance (percent of GDP) time series for the Paris scenario, in which international commitments from the 2015 Paris summit are met.
        moderate_engine_overall_balance_pct_gdp: Overall balance (percent of GDP) time series for the Moderate scenario, based on the SSP2-4.5 pathway with mitigation policies continuing along observed trends.
        high_engine_overall_balance_pct_gdp: Overall balance (percent of GDP) time series for the High scenario, based on the high-emissions SSP3-7.0 pathway.
        hot_engine_overall_balance_pct_gdp: Overall balance (percent of GDP) time series for the Hot scenario, which uses the 90th percentile of temperature increases among models using SSP3-7.0 emissions.
        hot_adapted_engine_overall_balance_pct_gdp: Overall balance (percent of GDP) time series for the Hot adapted scenario, reflecting the same temperature increases as Hot but faster adaptation.
        hot_unadapted_engine_overall_balance_pct_gdp: Overall balance (percent of GDP) time series for the Hot un-adapted scenario, reflecting the same temperature increases as Hot but slower adaptation.

    Returns:
        An assembled scenario coordinate holding, for each climate scenario and time period, the overall balance as a share of nominal GDP; values may be numeric or string where source data are non-numeric.
    """
    def formula(scenario: str, time_period: int) -> float | str | None:
        if scenario == 'Paris':
            return as_measure(paris_engine_overall_balance_pct_gdp[time_period])
        elif scenario == 'Moderate':
            return as_measure(moderate_engine_overall_balance_pct_gdp[time_period])
        elif scenario == 'High':
            return as_measure(high_engine_overall_balance_pct_gdp[time_period])
        elif scenario == 'Hot':
            return as_measure(hot_engine_overall_balance_pct_gdp[time_period])
        elif scenario == 'Hot adapted':
            return as_measure(hot_adapted_engine_overall_balance_pct_gdp[time_period])
        return as_measure(hot_unadapted_engine_overall_balance_pct_gdp[time_period])

    return data.SCENARIO_OVERALL_BALANCE_PCT_GDP.collect(evaluate(formula, data.SCENARIO_OVERALL_BALANCE_PCT_GDP.required))

@publish(data.SCENARIO_DEBT_TO_GDP.schema, cells=data.SCENARIO_DEBT_TO_GDP.cells)
def scenario_debt_to_gdp(*, paris_engine_gross_debt_pct_gdp: data.Series[float | str | None], moderate_engine_gross_debt_pct_gdp: data.Series[float | str | None], high_engine_gross_debt_pct_gdp: data.Series[float | str | None], hot_engine_gross_debt_pct_gdp: data.Series[float | str | None], hot_adapted_engine_gross_debt_pct_gdp: data.Series[float | str | None], hot_unadapted_engine_gross_debt_pct_gdp: data.Series[float | str | None]) -> data.ScenarioDebtToGdp:
    """Assemble the projected debt-to-GDP ratio for each climate change scenario.

    Compiles the scenario-specific gross debt-to-GDP projections into a single scenario results object covering the Paris, Moderate, High, Hot, Hot adapted, and Hot un-adapted climate paths.

    Args:
        paris_engine_gross_debt_pct_gdp: Gross debt-to-GDP ratio under the Paris scenario, which assumes international commitments from the 2015 Paris summit are met and global temperature increase stays below 2 degrees Celsius above pre-industrial levels.
        moderate_engine_gross_debt_pct_gdp: Gross debt-to-GDP ratio under the Moderate scenario, which assumes mitigation policies continue along observed trends without more aggressive action to fulfill Paris commitments.
        high_engine_gross_debt_pct_gdp: Gross debt-to-GDP ratio under the High scenario, which assumes a fragmented world with scaled-back mitigation policies and continued use of fossil fuels.
        hot_engine_gross_debt_pct_gdp: Gross debt-to-GDP ratio under the Hot scenario, which uses high-scenario emissions with the 90th percentile of temperature increases across climate models.
        hot_adapted_engine_gross_debt_pct_gdp: Gross debt-to-GDP ratio under the Hot adapted scenario, which uses the same temperature increases as the Hot scenario but assumes countries adapt more quickly.
        hot_unadapted_engine_gross_debt_pct_gdp: Gross debt-to-GDP ratio under the Hot un-adapted scenario, which uses the same temperature increases as the Hot scenario but assumes countries adapt more slowly.

    Returns:
        A ScenarioDebtToGdp collection mapping each climate scenario to its projected gross debt-to-GDP ratio by time period.
    """
    def formula(scenario: str, time_period: int) -> float | str | None:
        if scenario == 'Paris':
            return as_measure(paris_engine_gross_debt_pct_gdp[time_period])
        elif scenario == 'Moderate':
            return as_measure(moderate_engine_gross_debt_pct_gdp[time_period])
        elif scenario == 'High':
            return as_measure(high_engine_gross_debt_pct_gdp[time_period])
        elif scenario == 'Hot':
            return as_measure(hot_engine_gross_debt_pct_gdp[time_period])
        elif scenario == 'Hot adapted':
            return as_measure(hot_adapted_engine_gross_debt_pct_gdp[time_period])
        return as_measure(hot_unadapted_engine_gross_debt_pct_gdp[time_period])

    return data.SCENARIO_DEBT_TO_GDP.collect(evaluate(formula, data.SCENARIO_DEBT_TO_GDP.required))

@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_PARIS.schema, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_PARIS.cells)
def scenario_debt_stabilizing_primary_balance_paris(*, paris_engine_weighted_interest_rate: data.Series[float | str | None], paris_engine_gross_debt_pct_gdp: data.Series[float | str | None], scenario_nominal_gdp_growth_paris: data.ScenarioNominalGdpGrowthParis) -> data.ScenarioDebtStabilizingPrimaryBalanceParis:
    """Compute the Paris-scenario debt-stabilizing primary balance.

    Derives the primary balance needed each year to hold the debt-to-GDP ratio stable under the Paris climate scenario, so users can gauge the fiscal task of stabilizing debt as climate change lowers nominal GDP.

    Args:
        paris_engine_weighted_interest_rate: Weighted average nominal interest rate on gross government debt under the Paris scenario, in percent.
        paris_engine_gross_debt_pct_gdp: Gross government debt as a percent of nominal GDP under the Paris scenario; the prior-year value scales the automatic debt dynamics.
        scenario_nominal_gdp_growth_paris: Nominal GDP growth under the Paris scenario, in percent, reflecting employment, productivity, and inflation assumptions.

    Returns:
        The debt-stabilizing primary balance as a percent of nominal GDP for each projection year of the Paris scenario; the first year is excluded because it lacks a prior-year debt value.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(xl_div(xl_sub(paris_engine_weighted_interest_rate[time_period], scenario_nominal_gdp_growth_paris[time_period]), 100), xl_add(1, xl_div(scenario_nominal_gdp_growth_paris[time_period], 100))), paris_engine_gross_debt_pct_gdp[time_period - 1]))

    return data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_PARIS.collect(evaluate(formula, data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_PARIS.required))

@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_MODERATE.schema, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_MODERATE.cells)
def scenario_debt_stabilizing_primary_balance_moderate(*, moderate_engine_weighted_interest_rate: data.Series[float | str | None], moderate_engine_gross_debt_pct_gdp: data.Series[float | str | None], scenario_nominal_gdp_growth_moderate: data.ScenarioNominalGdpGrowthModerate) -> data.ScenarioDebtStabilizingPrimaryBalanceModerate:
    """Compute the debt-stabilizing primary balance under the moderate climate scenario.

    Derive the primary balance that would hold the debt-to-GDP ratio stable each year under the moderate scenario, so users can compare it against the projected primary balance to gauge the fiscal task of stabilizing debt.

    Args:
        moderate_engine_weighted_interest_rate: Weighted average nominal interest rate on government debt under the moderate scenario, in percent per year and consistent with the interest rate assumption selected in the Dashboard.
        moderate_engine_gross_debt_pct_gdp: Gross debt-to-GDP ratio under the moderate scenario, in percent of nominal GDP; the value from the preceding year enters the debt dynamics identity.
        scenario_nominal_gdp_growth_moderate: Nominal GDP growth under the moderate scenario, in percent per year, reflecting employment growth, productivity growth, and inflation.

    Returns:
        A scenario series of the debt-stabilizing primary balance under the moderate climate scenario, in percent of nominal GDP, for each projected year to 2099.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(xl_div(xl_sub(moderate_engine_weighted_interest_rate[time_period], scenario_nominal_gdp_growth_moderate[time_period]), 100), xl_add(1, xl_div(scenario_nominal_gdp_growth_moderate[time_period], 100))), moderate_engine_gross_debt_pct_gdp[time_period - 1]))

    return data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_MODERATE.collect(evaluate(formula, data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_MODERATE.required))

@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HIGH.schema, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HIGH.cells)
def scenario_debt_stabilizing_primary_balance_high(*, high_engine_weighted_interest_rate: data.Series[float | str | None], high_engine_gross_debt_pct_gdp: data.Series[float | str | None], scenario_nominal_gdp_growth_high: data.ScenarioNominalGdpGrowthHigh) -> data.ScenarioDebtStabilizingPrimaryBalanceHigh:
    """Compute the debt-stabilizing primary balance under the High climate scenario.

    Derive the primary balance (in percent of GDP) needed each year to hold the debt-to-GDP ratio stable in the High emissions scenario.

    Args:
        high_engine_weighted_interest_rate: Weighted average nominal interest rate on gross government debt under the High scenario, in percent.
        high_engine_gross_debt_pct_gdp: Gross government debt as a share of nominal GDP under the High scenario, in percent; the prior-year value is used.
        scenario_nominal_gdp_growth_high: Nominal GDP growth rate under the High scenario, in percent, used in the automatic debt dynamics term.

    Returns:
        The High scenario debt-stabilizing primary balance for each year (percent of GDP), or a missing value where inputs are unavailable.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(xl_div(xl_sub(high_engine_weighted_interest_rate[time_period], scenario_nominal_gdp_growth_high[time_period]), 100), xl_add(1, xl_div(scenario_nominal_gdp_growth_high[time_period], 100))), high_engine_gross_debt_pct_gdp[time_period - 1]))

    return data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HIGH.collect(evaluate(formula, data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HIGH.required))

@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT.schema, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT.cells)
def scenario_debt_stabilizing_primary_balance_hot(*, hot_engine_weighted_interest_rate: data.Series[float | str | None], hot_engine_gross_debt_pct_gdp: data.Series[float | str | None], scenario_nominal_gdp_growth_hot: data.ScenarioNominalGdpGrowthHot) -> data.ScenarioDebtStabilizingPrimaryBalanceHot:
    """Project the debt-stabilizing primary balance under the hot climate scenario.

    Derive the primary balance needed to keep the debt-to-GDP ratio stable year by year in the hot climate change scenario, using the debt dynamics equation.

    Args:
        hot_engine_weighted_interest_rate: Weighted average nominal interest rate on government debt under the hot scenario, in percent.
        hot_engine_gross_debt_pct_gdp: Gross general government debt under the hot scenario, expressed as a percent of nominal GDP; the previous-year value enters the debt dynamics equation.
        scenario_nominal_gdp_growth_hot: Nominal GDP growth under the hot scenario, derived from employment growth, productivity growth, and inflation, in percent.

    Returns:
        A series of the debt-stabilizing primary balance as a percent of nominal GDP for each projection year under the hot scenario.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(xl_div(xl_sub(hot_engine_weighted_interest_rate[time_period], scenario_nominal_gdp_growth_hot[time_period]), 100), xl_add(1, xl_div(scenario_nominal_gdp_growth_hot[time_period], 100))), hot_engine_gross_debt_pct_gdp[time_period - 1]))

    return data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT.collect(evaluate(formula, data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT.required))

@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_ADAPTED.schema, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_ADAPTED.cells)
def scenario_debt_stabilizing_primary_balance_hot_adapted(*, hot_adapted_engine_weighted_interest_rate: data.Series[float | str | None], hot_adapted_engine_gross_debt_pct_gdp: data.Series[float | str | None], scenario_nominal_gdp_growth_hot_adapted: data.ScenarioNominalGdpGrowthHotAdapted) -> data.ScenarioDebtStabilizingPrimaryBalanceHotAdapted:
    """Compute the hot-adapted-scenario debt-stabilizing primary balance as a share of nominal GDP in each projection year.

    Derive the primary balance needed to hold the debt-to-GDP ratio steady under the hot-adapted climate scenario, given the weighted average nominal interest rate, the projected debt stock, and nominal GDP growth.

    Args:
        hot_adapted_engine_weighted_interest_rate: Weighted average nominal interest rate on gross government debt in the hot-adapted scenario, in percent; used together with nominal GDP growth to form the automatic debt dynamics.
        hot_adapted_engine_gross_debt_pct_gdp: Gross government debt-to-GDP ratio in the hot-adapted scenario, in percent, lagged one year relative to the year being computed; the first projection year has no prior-year debt.
        scenario_nominal_gdp_growth_hot_adapted: Hot-adapted-scenario nominal GDP growth rate, in percent, approximating the sum of employment growth, productivity growth, and inflation.

    Returns:
        A time series of the debt-stabilizing primary balance in the hot-adapted scenario, expressed as a percent of nominal GDP for each projection year, or None where the required input is unavailable.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(xl_div(xl_sub(hot_adapted_engine_weighted_interest_rate[time_period], scenario_nominal_gdp_growth_hot_adapted[time_period]), 100), xl_add(1, xl_div(scenario_nominal_gdp_growth_hot_adapted[time_period], 100))), hot_adapted_engine_gross_debt_pct_gdp[time_period - 1]))

    return data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_ADAPTED.collect(evaluate(formula, data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_ADAPTED.required))

@publish(data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_UNADAPTED.schema, cells=data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_UNADAPTED.cells)
def scenario_debt_stabilizing_primary_balance_hot_unadapted(*, hot_unadapted_engine_weighted_interest_rate: data.Series[float | str | None], hot_unadapted_engine_gross_debt_pct_gdp: data.Series[float | str | None], scenario_nominal_gdp_growth_hot_unadapted: data.ScenarioNominalGdpGrowthHotUnadapted) -> data.ScenarioDebtStabilizingPrimaryBalanceHotUnadapted:
    """Compute the debt-stabilizing primary balance under the Hot Un-Adapted climate scenario.

    Derive the primary balance needed to hold the gross debt-to-GDP ratio stable each year given scenario interest and growth conditions.

    Args:
        hot_unadapted_engine_weighted_interest_rate: Weighted average nominal interest rate on gross government debt under the Hot Un-Adapted scenario, used as the rate i in the debt dynamics equation.
        hot_unadapted_engine_gross_debt_pct_gdp: Gross government debt as a percent of nominal GDP under the Hot Un-Adapted scenario; the prior-year value provides the initial debt level in the debt dynamics equation.
        scenario_nominal_gdp_growth_hot_unadapted: Nominal GDP growth rate under the Hot Un-Adapted scenario, used as g in the debt dynamics equation.

    Returns:
        A time series of the debt-stabilizing primary balance under the Hot Un-Adapted scenario, in percent of nominal GDP for each projection year.
    """
    def formula(time_period: int) -> float | str | None:
        return as_measure(xl_mul(xl_div(xl_div(xl_sub(hot_unadapted_engine_weighted_interest_rate[time_period], scenario_nominal_gdp_growth_hot_unadapted[time_period]), 100), xl_add(1, xl_div(scenario_nominal_gdp_growth_hot_unadapted[time_period], 100))), hot_unadapted_engine_gross_debt_pct_gdp[time_period - 1]))

    return data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_UNADAPTED.collect(evaluate(formula, data.SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_UNADAPTED.required))

@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_PARIS.schema, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_PARIS.cells)
def scenario_nominal_gdp_growth_paris(*, paris_engine_real_gdp_growth: data.Series[float | str | None], paris_engine_gdp_deflator_growth: data.Series[float | str | None], baseline_nominal_gdp_growth: data.BaselineNominalGdpGrowth) -> data.ScenarioNominalGdpGrowthParis:
    """Compute Paris-scenario nominal GDP growth from real GDP and deflator growth.

    Derive the engine-sheet nominal GDP growth for the Paris climate scenario, holding the baseline through 2029 and compounding real GDP growth with GDP deflator growth thereafter.

    Args:
        paris_engine_real_gdp_growth: Paris-scenario engine-sheet real GDP growth (in percent), reflecting the macroeconomic effect of climate change on economic output over the projection horizon.
        paris_engine_gdp_deflator_growth: Paris-scenario engine-sheet GDP deflator growth (in percent), the inflation measure used to convert real GDP into nominal GDP for the scenario.
        baseline_nominal_gdp_growth: Baseline nominal GDP growth, used unchanged for periods up to and including 2029 before the Paris scenario effects take hold.

    Returns:
        Paris-scenario nominal GDP growth for each projection year: the baseline value through 2029, and thereafter the compounded real GDP and GDP deflator growth rates.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_nominal_gdp_growth[time_period])
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(paris_engine_real_gdp_growth[time_period], 100)), xl_add(1, xl_div(paris_engine_gdp_deflator_growth[time_period], 100))), 100), 100))

    return data.SCENARIO_NOMINAL_GDP_GROWTH_PARIS.collect(evaluate(formula, data.SCENARIO_NOMINAL_GDP_GROWTH_PARIS.required))

@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_MODERATE.schema, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_MODERATE.cells)
def scenario_nominal_gdp_growth_moderate(*, moderate_engine_real_gdp_growth: data.Series[float | str | None], moderate_engine_gdp_deflator_growth: data.Series[float | str | None], baseline_nominal_gdp_growth: data.BaselineNominalGdpGrowth) -> data.ScenarioNominalGdpGrowthModerate:
    """Project nominal GDP growth for the moderate climate scenario.

    Derive scenario nominal GDP growth as the compounded growth in real GDP and the GDP deflator, holding the baseline path through 2029 and applying the moderate scenario's real GDP and GDP deflator growth from 2030 onward.

    Args:
        moderate_engine_real_gdp_growth: Moderate-scenario growth rate of real GDP, expressed in percent per year, used to form the real component of scenario nominal GDP growth.
        moderate_engine_gdp_deflator_growth: Moderate-scenario growth rate of the GDP deflator, expressed in percent per year, used to form the price component of scenario nominal GDP growth.
        baseline_nominal_gdp_growth: Baseline nominal GDP growth used through 2029, before the moderate climate scenario effects are applied from 2030 onward.

    Returns:
        Nominal GDP growth for the moderate climate scenario under the baseline fiscal settings, in percent per year.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_nominal_gdp_growth[time_period])
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(moderate_engine_real_gdp_growth[time_period], 100)), xl_add(1, xl_div(moderate_engine_gdp_deflator_growth[time_period], 100))), 100), 100))

    return data.SCENARIO_NOMINAL_GDP_GROWTH_MODERATE.collect(evaluate(formula, data.SCENARIO_NOMINAL_GDP_GROWTH_MODERATE.required))

@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_HIGH.schema, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_HIGH.cells)
def scenario_nominal_gdp_growth_high(*, high_engine_real_gdp_growth: data.Series[float | str | None], high_engine_gdp_deflator_growth: data.Series[float | str | None], baseline_nominal_gdp_growth: data.BaselineNominalGdpGrowth) -> data.ScenarioNominalGdpGrowthHigh:
    """Project nominal GDP growth under the high climate scenario.

    Extend the baseline nominal GDP growth path into the high-emissions climate scenario by compounding real GDP growth and GDP deflator growth from 2030 onward.

    Args:
        high_engine_real_gdp_growth: Annual real GDP growth (in percent) under the high climate scenario, reflecting the slowdown in productivity growth induced by rising temperatures.
        high_engine_gdp_deflator_growth: Annual GDP deflator growth (in percent) under the high climate scenario, used to convert real GDP growth into nominal GDP growth.
        baseline_nominal_gdp_growth: Baseline nominal GDP growth (in percent) prior to the start of the climate scenario horizon, carried over unchanged through 2029.

    Returns:
        The high climate scenario nominal GDP growth series (in percent), taken from the baseline through 2029 and compounded from real GDP growth and GDP deflator growth thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_nominal_gdp_growth[time_period])
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(high_engine_real_gdp_growth[time_period], 100)), xl_add(1, xl_div(high_engine_gdp_deflator_growth[time_period], 100))), 100), 100))

    return data.SCENARIO_NOMINAL_GDP_GROWTH_HIGH.collect(evaluate(formula, data.SCENARIO_NOMINAL_GDP_GROWTH_HIGH.required))

@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_HOT.schema, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_HOT.cells)
def scenario_nominal_gdp_growth_hot(*, hot_engine_real_gdp_growth: data.Series[float | str | None], hot_engine_gdp_deflator_growth: data.Series[float | str | None], baseline_nominal_gdp_growth: data.BaselineNominalGdpGrowth) -> data.ScenarioNominalGdpGrowthHot:
    """Project nominal GDP growth under the "Hot" climate scenario.

    Combine real GDP growth and GDP deflator growth under the Hot scenario (SSP3-7.0 with 90th-percentile warming) into a nominal GDP growth path, holding the baseline before the projection horizon.

    Args:
        hot_engine_real_gdp_growth: Real GDP growth (percent per year) under the Hot climate scenario, expressed as the climate-change-induced slowdown in productivity growth from 2030 onward.
        hot_engine_gdp_deflator_growth: Growth (percent per year) of the GDP deflator, the broadest measure of the tax base, under the Hot climate scenario.
        baseline_nominal_gdp_growth: Nominal GDP growth from the baseline scenario, equal to the sum of employment growth, productivity growth, and inflation, used for time periods up to 2029.

    Returns:
        Nominal GDP growth under the Hot climate scenario, equal to the baseline value through 2029 and thereafter approximated as the sum of Hot-scenario real GDP growth and GDP deflator growth.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_nominal_gdp_growth[time_period])
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(hot_engine_real_gdp_growth[time_period], 100)), xl_add(1, xl_div(hot_engine_gdp_deflator_growth[time_period], 100))), 100), 100))

    return data.SCENARIO_NOMINAL_GDP_GROWTH_HOT.collect(evaluate(formula, data.SCENARIO_NOMINAL_GDP_GROWTH_HOT.required))

@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_ADAPTED.schema, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_ADAPTED.cells)
def scenario_nominal_gdp_growth_hot_adapted(*, hot_adapted_engine_real_gdp_growth: data.Series[float | str | None], hot_adapted_engine_gdp_deflator_growth: data.Series[float | str | None], baseline_nominal_gdp_growth: data.BaselineNominalGdpGrowth) -> data.ScenarioNominalGdpGrowthHotAdapted:
    """Project nominal GDP growth under the Hot Adapted climate scenario.

    Derive the Hot Adapted scenario's nominal GDP growth path, using the baseline growth rate through the WEO horizon and, from 2030 onwards, compounding the scenario's real GDP growth and GDP deflator growth.

    Args:
        hot_adapted_engine_real_gdp_growth: Hot Adapted scenario real GDP growth rates (in percent), reflecting faster adaptation to higher temperatures.
        hot_adapted_engine_gdp_deflator_growth: Hot Adapted scenario GDP deflator growth rates (in percent) used to convert real GDP growth into nominal GDP growth.
        baseline_nominal_gdp_growth: Baseline nominal GDP growth carried forward through the WEO horizon, before climate change effects apply from 2030.

    Returns:
        The Hot Adapted scenario nominal GDP growth series, in percent.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_nominal_gdp_growth[time_period])
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(hot_adapted_engine_real_gdp_growth[time_period], 100)), xl_add(1, xl_div(hot_adapted_engine_gdp_deflator_growth[time_period], 100))), 100), 100))

    return data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_ADAPTED.collect(evaluate(formula, data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_ADAPTED.required))

@publish(data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_UNADAPTED.schema, cells=data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_UNADAPTED.cells)
def scenario_nominal_gdp_growth_hot_unadapted(*, hot_unadapted_engine_real_gdp_growth: data.Series[float | str | None], hot_unadapted_engine_gdp_deflator_growth: data.Series[float | str | None], baseline_nominal_gdp_growth: data.BaselineNominalGdpGrowth) -> data.ScenarioNominalGdpGrowthHotUnadapted:
    """Compute the Hot Un-Adapted climate scenario's nominal GDP growth path.

    Project nominal GDP growth under the Hot Un-Adapted scenario by compounding the scenario's real GDP growth with its GDP deflator growth, while carrying the baseline nominal GDP growth through 2029.

    Args:
        hot_unadapted_engine_real_gdp_growth: Hot Un-Adapted scenario real GDP growth (in percent), reflecting the severe, slowly-adapted temperature path applied from 2030 onward.
        hot_unadapted_engine_gdp_deflator_growth: Hot Un-Adapted scenario GDP deflator growth (in percent), used as the inflation component when compounding nominal GDP growth.
        baseline_nominal_gdp_growth: Baseline nominal GDP growth, in line with the sum of employment growth, productivity growth, and inflation, carried forward for periods through 2029.

    Returns:
        The Hot Un-Adapted scenario nominal GDP growth series: baseline nominal GDP growth through 2029, then the compounded real GDP growth and GDP deflator growth thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_nominal_gdp_growth[time_period])
        return as_measure(xl_sub(xl_mul(xl_mul(xl_add(1, xl_div(hot_unadapted_engine_real_gdp_growth[time_period], 100)), xl_add(1, xl_div(hot_unadapted_engine_gdp_deflator_growth[time_period], 100))), 100), 100))

    return data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_UNADAPTED.collect(evaluate(formula, data.SCENARIO_NOMINAL_GDP_GROWTH_HOT_UNADAPTED.required))

@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_PARIS.schema, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_PARIS.cells)
def scenario_real_gdp_level_index_paris(*, baseline_engine_real_gdp_lcu: data.Series[float | str | None], paris_engine_real_gdp_growth: data.Series[float | str | None]) -> data.ScenarioRealGdpLevelIndexParis:
    """Compute the Paris-scenario real GDP level index.

    Indexes real GDP under the Paris (SSP1-2.6) scenario, holding the level at the baseline through 2029 and then compounding annual growth thereafter.

    Args:
        baseline_engine_real_gdp_lcu: Baseline real GDP in billions of local currency units, in the same units as that of nominal GDP; provides the level the Paris index is anchored to through 2029.
        paris_engine_real_gdp_growth: Paris scenario real GDP growth rate in percent per year, reflecting the gradual warming impact on GDP per capita growth, used to compound the index from 2030 onwards.

    Returns:
        The Paris scenario real GDP level index for every projected year, in billions of local currency units.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_real_gdp_lcu[time_period])
        return as_measure(xl_mul(scenario_real_gdp_level_index_paris[time_period - 1], xl_add(1, xl_div(paris_engine_real_gdp_growth[time_period], 100))))

    scenario_real_gdp_level_index_paris = CoordinateReader('scenario_real_gdp_level_index_paris', data.SCENARIO_REAL_GDP_LEVEL_INDEX_PARIS.required, formula)
    return data.SCENARIO_REAL_GDP_LEVEL_INDEX_PARIS.collect((coord, scenario_real_gdp_level_index_paris[coord]) for coord in data.SCENARIO_REAL_GDP_LEVEL_INDEX_PARIS.required)

@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_MODERATE.schema, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_MODERATE.cells)
def scenario_real_gdp_level_index_moderate(*, baseline_engine_real_gdp_lcu: data.Series[float | str | None], moderate_engine_real_gdp_growth: data.Series[float | str | None]) -> data.ScenarioRealGdpLevelIndexModerate:
    """Build the real GDP level index for the moderate climate scenario.

    Derives a long-term real GDP level index under the moderate (SSP2-4.5) climate scenario by compounding baseline real GDP with projected climate-induced growth effects from 2030 onward.

    Args:
        baseline_engine_real_gdp_lcu: Baseline real GDP level in billions of local currency units, used to seed the index through 2029 before climate effects are applied.
        moderate_engine_real_gdp_growth: Projected real GDP growth rate, in percent, under the moderate climate scenario, used to grow the index from 2030 onward.

    Returns:
        Real GDP level index series for the moderate scenario, expressed as a local-currency level anchored to the baseline through 2029.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_real_gdp_lcu[time_period])
        return as_measure(xl_mul(scenario_real_gdp_level_index_moderate[time_period - 1], xl_add(1, xl_div(moderate_engine_real_gdp_growth[time_period], 100))))

    scenario_real_gdp_level_index_moderate = CoordinateReader('scenario_real_gdp_level_index_moderate', data.SCENARIO_REAL_GDP_LEVEL_INDEX_MODERATE.required, formula)
    return data.SCENARIO_REAL_GDP_LEVEL_INDEX_MODERATE.collect((coord, scenario_real_gdp_level_index_moderate[coord]) for coord in data.SCENARIO_REAL_GDP_LEVEL_INDEX_MODERATE.required)

@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_HIGH.schema, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_HIGH.cells)
def scenario_real_gdp_level_index_high(*, baseline_engine_real_gdp_lcu: data.Series[float | str | None], high_engine_real_gdp_growth: data.Series[float | str | None]) -> data.ScenarioRealGdpLevelIndexHigh:
    """Derive the high climate scenario real GDP level index from the baseline level and high-scenario growth rates.

    Build a real GDP level index under the high (SSP3-7.0) climate scenario for use in deriving index and deviation measures of climate-related output losses relative to the baseline.

    Args:
        baseline_engine_real_gdp_lcu: Baseline real GDP level in local currency units, held fixed through the WEO horizon and used as the starting point for the index.
        high_engine_real_gdp_growth: Year-on-year real GDP growth rates, in percent, under the high climate scenario, applied from the end of the WEO horizon onward.

    Returns:
        A real GDP level index under the high climate scenario, equal to the baseline level through 2029 and compounded thereafter by the high-scenario growth rates.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_real_gdp_lcu[time_period])
        return as_measure(xl_mul(scenario_real_gdp_level_index_high[time_period - 1], xl_add(1, xl_div(high_engine_real_gdp_growth[time_period], 100))))

    scenario_real_gdp_level_index_high = CoordinateReader('scenario_real_gdp_level_index_high', data.SCENARIO_REAL_GDP_LEVEL_INDEX_HIGH.required, formula)
    return data.SCENARIO_REAL_GDP_LEVEL_INDEX_HIGH.collect((coord, scenario_real_gdp_level_index_high[coord]) for coord in data.SCENARIO_REAL_GDP_LEVEL_INDEX_HIGH.required)

@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT.schema, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT.cells)
def scenario_real_gdp_level_index_hot(*, baseline_engine_real_gdp_lcu: data.Series[float | str | None], hot_engine_real_gdp_growth: data.Series[float | str | None]) -> data.ScenarioRealGdpLevelIndexHot:
    """Builds the Hot scenario real GDP level index by chaining baseline levels into climate-adjusted growth.

    Expresses the Hot scenario's real GDP level as an index that starts from the baseline level and compounds the scenario's annual growth impact from 2030 onward.

    Args:
        baseline_engine_real_gdp_lcu: Baseline real GDP in billions of local currency units, used to anchor the index through the WEO horizon (to 2029).
        hot_engine_real_gdp_growth: Hot scenario growth rate of real GDP, in percent, applied each year from 2030 to compound the index and capture the macroeconomic effect of climate change.

    Returns:
        A scenario real GDP level index for the Hot scenario, indexed to the baseline before 2030 and grown by the Hot scenario's real GDP growth thereafter, supporting index and deviation derivations for fiscal risk analysis.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_real_gdp_lcu[time_period])
        return as_measure(xl_mul(scenario_real_gdp_level_index_hot[time_period - 1], xl_add(1, xl_div(hot_engine_real_gdp_growth[time_period], 100))))

    scenario_real_gdp_level_index_hot = CoordinateReader('scenario_real_gdp_level_index_hot', data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT.required, formula)
    return data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT.collect((coord, scenario_real_gdp_level_index_hot[coord]) for coord in data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT.required)

@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_ADAPTED.schema, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_ADAPTED.cells)
def scenario_real_gdp_level_index_hot_adapted(*, baseline_engine_real_gdp_lcu: data.Series[float | str | None], hot_adapted_engine_real_gdp_growth: data.Series[float | str | None]) -> data.ScenarioRealGdpLevelIndexHotAdapted:
    """Project the real GDP level index under the hot adapted climate scenario.

    Build the long-term real GDP level index for the hot adapted scenario, where countries adapt to higher temperatures more quickly, by carrying forward the baseline level through 2029 and compounding the hot adapted real GDP growth thereafter.

    Args:
        baseline_engine_real_gdp_lcu: Baseline real GDP level in billions of local currency units, used as the starting level for the index through 2029.
        hot_adapted_engine_real_gdp_growth: Real GDP growth rate, in percent, under the hot adapted scenario, used to compound the index from 2030 onward.

    Returns:
        The real GDP level index for the hot adapted climate scenario, aligned to the scenario's required coordinate set.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_real_gdp_lcu[time_period])
        return as_measure(xl_mul(scenario_real_gdp_level_index_hot_adapted[time_period - 1], xl_add(1, xl_div(hot_adapted_engine_real_gdp_growth[time_period], 100))))

    scenario_real_gdp_level_index_hot_adapted = CoordinateReader('scenario_real_gdp_level_index_hot_adapted', data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_ADAPTED.required, formula)
    return data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_ADAPTED.collect((coord, scenario_real_gdp_level_index_hot_adapted[coord]) for coord in data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_ADAPTED.required)

@publish(data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_UNADAPTED.schema, cells=data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_UNADAPTED.cells)
def scenario_real_gdp_level_index_hot_unadapted(*, baseline_engine_real_gdp_lcu: data.Series[float | str | None], hot_unadapted_engine_real_gdp_growth: data.Series[float | str | None]) -> data.ScenarioRealGdpLevelIndexHotUnadapted:
    """Project the real GDP level index under the Hot Un-Adapted climate scenario.

    Chain the baseline real GDP level with Hot Un-Adapted scenario growth rates to yield a long-run level index for fiscal risk analysis.

    Args:
        baseline_engine_real_gdp_lcu: Baseline real GDP in local currency units; supplies the level from which the Hot Un-Adapted scenario level index is anchored through 2029.
        hot_unadapted_engine_real_gdp_growth: Hot Un-Adapted scenario real GDP growth rates (in percent) used to compound the index forward from 2030 onward, reflecting slower adaptation to higher temperatures.

    Returns:
        The real GDP level index series for the Hot Un-Adapted climate scenario, anchored to baseline real GDP through 2029 and compounded by scenario growth thereafter.
    """
    def formula(time_period: int) -> float | str | None:
        if time_period <= 2029:
            return as_measure(baseline_engine_real_gdp_lcu[time_period])
        return as_measure(xl_mul(scenario_real_gdp_level_index_hot_unadapted[time_period - 1], xl_add(1, xl_div(hot_unadapted_engine_real_gdp_growth[time_period], 100))))

    scenario_real_gdp_level_index_hot_unadapted = CoordinateReader('scenario_real_gdp_level_index_hot_unadapted', data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_UNADAPTED.required, formula)
    return data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_UNADAPTED.collect((coord, scenario_real_gdp_level_index_hot_unadapted[coord]) for coord in data.SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_UNADAPTED.required)

@publish(data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2050.schema, cells=data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2050.cells)
def scenario_fiscal_consolidation_gap_milestones_2050(*, output_scenarios_dspb_milestones_paris_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_paris_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_moderate_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_moderate_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_high_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_high_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_adapted_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_adapted_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_unadapted_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_unadapted_pb_star: data.Series[float | str | None]) -> data.ScenarioFiscalConsolidationGapMilestones2050:
    """Compute the 2050 fiscal consolidation gap milestone for each climate scenario.

    Derive, for 2050, the gap between the debt-stabilizing primary balance and the projected primary balance under each climate scenario, keeping the Baseline row internal.

    Args:
        output_scenarios_dspb_milestones_paris_pb: Projected primary balance (PB) milestone for 2050 under the Paris scenario.
        output_scenarios_dspb_milestones_paris_pb_star: Debt-stabilizing primary balance (PB*) milestone for 2050 under the Paris scenario.
        output_scenarios_dspb_milestones_moderate_pb: Projected primary balance (PB) milestone for 2050 under the Moderate scenario.
        output_scenarios_dspb_milestones_moderate_pb_star: Debt-stabilizing primary balance (PB*) milestone for 2050 under the Moderate scenario.
        output_scenarios_dspb_milestones_high_pb: Projected primary balance (PB) milestone for 2050 under the High scenario.
        output_scenarios_dspb_milestones_high_pb_star: Debt-stabilizing primary balance (PB*) milestone for 2050 under the High scenario.
        output_scenarios_dspb_milestones_hot_pb: Projected primary balance (PB) milestone for 2050 under the Hot scenario.
        output_scenarios_dspb_milestones_hot_pb_star: Debt-stabilizing primary balance (PB*) milestone for 2050 under the Hot scenario.
        output_scenarios_dspb_milestones_hot_adapted_pb: Projected primary balance (PB) milestone for 2050 under the Hot adapted scenario.
        output_scenarios_dspb_milestones_hot_adapted_pb_star: Debt-stabilizing primary balance (PB*) milestone for 2050 under the Hot adapted scenario.
        output_scenarios_dspb_milestones_hot_unadapted_pb: Projected primary balance (PB) milestone for 2050 under the Hot un-adapted scenario.
        output_scenarios_dspb_milestones_hot_unadapted_pb_star: Debt-stabilizing primary balance (PB*) milestone for 2050 under the Hot un-adapted scenario.

    Returns:
        A scenario fiscal consolidation gap milestones collection holding the 2050 PB* minus PB gap for each climate scenario.
    """
    def formula(scenario: str, time_period: int) -> float | str | None:
        if scenario == 'Paris':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_paris_pb_star[2050], output_scenarios_dspb_milestones_paris_pb[2050]))
        elif scenario == 'Moderate':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_moderate_pb_star[2050], output_scenarios_dspb_milestones_moderate_pb[2050]))
        elif scenario == 'High':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_high_pb_star[2050], output_scenarios_dspb_milestones_high_pb[2050]))
        elif scenario == 'Hot':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_hot_pb_star[2050], output_scenarios_dspb_milestones_hot_pb[2050]))
        elif scenario == 'Hot adapted':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_hot_adapted_pb_star[2050], output_scenarios_dspb_milestones_hot_adapted_pb[2050]))
        return as_measure(xl_sub(output_scenarios_dspb_milestones_hot_unadapted_pb_star[2050], output_scenarios_dspb_milestones_hot_unadapted_pb[2050]))

    return data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2050.collect(evaluate(formula, data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2050.required))

@publish(data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2075.schema, cells=data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2075.cells)
def scenario_fiscal_consolidation_gap_milestones_2075(*, output_scenarios_dspb_milestones_paris_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_paris_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_moderate_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_moderate_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_high_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_high_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_adapted_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_adapted_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_unadapted_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_unadapted_pb_star: data.Series[float | str | None]) -> data.ScenarioFiscalConsolidationGapMilestones2075:
    """Compute the 2075 PB gap milestone across climate scenarios.

    Provides the 2075 milestone of the fiscal consolidation gap series, spanning the Paris, Moderate, High, Hot, Hot adapted, and Hot unadapted climate scenarios.

    Args:
        output_scenarios_dspb_milestones_paris_pb: Projected primary balance under the Paris scenario.
        output_scenarios_dspb_milestones_paris_pb_star: Debt-stabilizing primary balance under the Paris scenario.
        output_scenarios_dspb_milestones_moderate_pb: Projected primary balance under the Moderate scenario.
        output_scenarios_dspb_milestones_moderate_pb_star: Debt-stabilizing primary balance under the Moderate scenario.
        output_scenarios_dspb_milestones_high_pb: Projected primary balance under the High scenario.
        output_scenarios_dspb_milestones_high_pb_star: Debt-stabilizing primary balance under the High scenario.
        output_scenarios_dspb_milestones_hot_pb: Projected primary balance under the Hot scenario.
        output_scenarios_dspb_milestones_hot_pb_star: Debt-stabilizing primary balance under the Hot scenario.
        output_scenarios_dspb_milestones_hot_adapted_pb: Projected primary balance under the Hot adapted scenario.
        output_scenarios_dspb_milestones_hot_adapted_pb_star: Debt-stabilizing primary balance under the Hot adapted scenario.
        output_scenarios_dspb_milestones_hot_unadapted_pb: Projected primary balance under the Hot unadapted scenario.
        output_scenarios_dspb_milestones_hot_unadapted_pb_star: Debt-stabilizing primary balance under the Hot unadapted scenario.

    Returns:
        A ScenarioFiscalConsolidationGapMilestones2075 carrying the 2075 fiscal consolidation gap milestone by climate scenario.
    """
    def formula(scenario: str, time_period: int) -> float | str | None:
        if scenario == 'Paris':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_paris_pb_star[2075], output_scenarios_dspb_milestones_paris_pb[2075]))
        elif scenario == 'Moderate':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_moderate_pb_star[2075], output_scenarios_dspb_milestones_moderate_pb[2075]))
        elif scenario == 'High':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_high_pb_star[2075], output_scenarios_dspb_milestones_high_pb[2075]))
        elif scenario == 'Hot':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_hot_pb_star[2075], output_scenarios_dspb_milestones_hot_pb[2075]))
        elif scenario == 'Hot adapted':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_hot_adapted_pb_star[2075], output_scenarios_dspb_milestones_hot_adapted_pb[2075]))
        return as_measure(xl_sub(output_scenarios_dspb_milestones_hot_unadapted_pb_star[2075], output_scenarios_dspb_milestones_hot_unadapted_pb[2075]))

    return data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2075.collect(evaluate(formula, data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2075.required))

@publish(data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2099.schema, cells=data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2099.cells)
def scenario_fiscal_consolidation_gap_milestones_2099(*, output_scenarios_dspb_milestones_paris_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_paris_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_moderate_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_moderate_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_high_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_high_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_adapted_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_adapted_pb_star: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_unadapted_pb: data.Series[float | str | None], output_scenarios_dspb_milestones_hot_unadapted_pb_star: data.Series[float | str | None]) -> data.ScenarioFiscalConsolidationGapMilestones2099:
    """Compute the 2099 fiscal consolidation gap milestones across the climate scenarios.

    Derive, for each climate scenario, the 2099 gap between the debt-stabilizing primary balance and the projected primary balance from the Output Scenarios PB milestone columns.

    Args:
        output_scenarios_dspb_milestones_paris_pb: Projected primary balance milestone for 2099 under the Paris scenario.
        output_scenarios_dspb_milestones_paris_pb_star: Debt-stabilizing primary balance milestone for 2099 under the Paris scenario.
        output_scenarios_dspb_milestones_moderate_pb: Projected primary balance milestone for 2099 under the Moderate scenario.
        output_scenarios_dspb_milestones_moderate_pb_star: Debt-stabilizing primary balance milestone for 2099 under the Moderate scenario.
        output_scenarios_dspb_milestones_high_pb: Projected primary balance milestone for 2099 under the High scenario.
        output_scenarios_dspb_milestones_high_pb_star: Debt-stabilizing primary balance milestone for 2099 under the High scenario.
        output_scenarios_dspb_milestones_hot_pb: Projected primary balance milestone for 2099 under the Hot scenario.
        output_scenarios_dspb_milestones_hot_pb_star: Debt-stabilizing primary balance milestone for 2099 under the Hot scenario.
        output_scenarios_dspb_milestones_hot_adapted_pb: Projected primary balance milestone for 2099 under the Hot adapted scenario.
        output_scenarios_dspb_milestones_hot_adapted_pb_star: Debt-stabilizing primary balance milestone for 2099 under the Hot adapted scenario.
        output_scenarios_dspb_milestones_hot_unadapted_pb: Projected primary balance milestone for 2099 under the Hot un-adapted scenario.
        output_scenarios_dspb_milestones_hot_unadapted_pb_star: Debt-stabilizing primary balance milestone for 2099 under the Hot un-adapted scenario.

    Returns:
        ScenarioFiscalConsolidationGapMilestones2099 keyed by climate scenario, each holding the 2099 fiscal consolidation gap as the difference between the debt-stabilizing primary balance and the projected primary balance.
    """
    def formula(scenario: str, time_period: int) -> float | str | None:
        if scenario == 'Paris':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_paris_pb_star[2099], output_scenarios_dspb_milestones_paris_pb[2099]))
        elif scenario == 'Moderate':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_moderate_pb_star[2099], output_scenarios_dspb_milestones_moderate_pb[2099]))
        elif scenario == 'High':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_high_pb_star[2099], output_scenarios_dspb_milestones_high_pb[2099]))
        elif scenario == 'Hot':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_hot_pb_star[2099], output_scenarios_dspb_milestones_hot_pb[2099]))
        elif scenario == 'Hot adapted':
            return as_measure(xl_sub(output_scenarios_dspb_milestones_hot_adapted_pb_star[2099], output_scenarios_dspb_milestones_hot_adapted_pb[2099]))
        return as_measure(xl_sub(output_scenarios_dspb_milestones_hot_unadapted_pb_star[2099], output_scenarios_dspb_milestones_hot_unadapted_pb[2099]))

    return data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2099.collect(evaluate(formula, data.SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2099.required))
