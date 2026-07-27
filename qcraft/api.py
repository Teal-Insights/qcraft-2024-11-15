from __future__ import annotations

import warnings

from ._api_helpers import (
    DataFrameInput,
    EmptyMeasure,
    Record,
    Records,
    _apply_series_records,
    coerce_setter_input,
    _DEMOGRAPHY_SCENARIO_LABELS,
    _INTEREST_RATE_MODE_LABELS,
    require_measure_labels,
    resolve_measure_labels,
)
from ._readers import (
    _LEAF_INDEX_COUNTRY,
    _LEAF_INDEX_DEMOGRAPHY_SCENARIO,
    _LEAF_INDEX_PRODUCTIVITY_START,
    _LEAF_INDEX_PRODUCTIVITY_END,
    _LEAF_INDEX_INFLATION_START,
    _LEAF_INDEX_INFLATION_END,
    _LEAF_INDEX_INTEREST_RATE_MODE,
    _LEAF_INDEX_REAL_INTEREST_RATE,
    _LEAF_INDEX_FISCAL_RULE_ENABLED,
    _LEAF_INDEX_DEBT_TARGET,
    _LEAF_INDEX_EXPENDITURE_RIGIDITY,
    _LEAF_INDEX_DISCRETE_REVENUE_SHOCKS,
    _LEAF_INDEX_DISCRETE_PRIMARY_EXPENDITURE_SHOCKS,
    _LEAF_INDEX_BASELINE_DEBT_DIRECTION_ABOVE_SENTINEL,
    _LEAF_INDEX_BASELINE_DEBT_DIRECTION_BELOW_SENTINEL,
    _LEAF_INDEX_DEMOGRAPHY_VARIANT_LABEL_MEDIUM,
    _LEAF_INDEX_DEMOGRAPHY_VARIANT_LABEL_HIGH,
    _LEAF_INDEX_DEMOGRAPHY_VARIANT_LABEL_LOW,
    _LEAF_INDEX_PRODUCTIVITY_CONVERGENCE_LOGISTIC_STEEPNESS,
    _LEAF_INDEX_PRODUCTIVITY_CONVERGENCE_LOGISTIC_MIDPOINT,
    _LEAF_INDEX_PRODUCTIVITY_CONVERGENCE_PERIOD_INDEX,
    _LEAF_INDEX_INFLATION_CONVERGENCE_LOGISTIC_STEEPNESS,
    _LEAF_INDEX_INFLATION_CONVERGENCE_LOGISTIC_MIDPOINT,
    _LEAF_INDEX_INFLATION_CONVERGENCE_PERIOD_INDEX,
    _LEAF_INDEX_INTEREST_RATE_ASSUMPTION_LABEL_NOMINAL,
    _LEAF_INDEX_INTEREST_RATE_ASSUMPTION_LABEL_DIFFERENTIAL,
    _LEAF_INDEX_INTEREST_RATE_ASSUMPTION_LABEL_REAL,
)
from ._output_leaves import (
    _OUTPUT_LEAVES_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP,
    _OUTPUT_LEAVES_BASELINE_INTEREST_EXPENDITURE_PCT_GDP,
    _OUTPUT_LEAVES_BASELINE_INTEREST_RATE,
    _OUTPUT_LEAVES_BASELINE_PRIMARY_BALANCE_PCT_GDP,
    _OUTPUT_LEAVES_BASELINE_OVERALL_BALANCE_PCT_GDP,
    _OUTPUT_LEAVES_BASELINE_DEBT_TO_GDP,
    _OUTPUT_LEAVES_BASELINE_DEBT_STABILIZING_PRIMARY_BALANCE,
    _OUTPUT_LEAVES_BASELINE_FISCAL_CONSOLIDATION_GAP,
    _OUTPUT_LEAVES_BASELINE_NOMINAL_GDP_GROWTH,
    _OUTPUT_LEAVES_BASELINE_REAL_GDP_GROWTH,
    _OUTPUT_LEAVES_BASELINE_REVENUE_PCT_GDP,
    _OUTPUT_LEAVES_BASELINE_EMPLOYMENT_GROWTH,
    _OUTPUT_LEAVES_BASELINE_LABOUR_PRODUCTIVITY_GROWTH,
    _OUTPUT_LEAVES_BASELINE_GDP_DEFLATOR_GROWTH,
    _OUTPUT_LEAVES_BASELINE_POPULATION_GROWTH,
    _OUTPUT_LEAVES_SCENARIO_PRIMARY_BALANCE_PCT_GDP,
    _OUTPUT_LEAVES_SCENARIO_OVERALL_BALANCE_PCT_GDP,
    _OUTPUT_LEAVES_SCENARIO_DEBT_TO_GDP,
    _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_PARIS,
    _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_MODERATE,
    _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HIGH,
    _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT,
    _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_ADAPTED,
    _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_UNADAPTED,
    _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_PARIS,
    _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_MODERATE,
    _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_HIGH,
    _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_HOT,
    _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_HOT_ADAPTED,
    _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_HOT_UNADAPTED,
    _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_PARIS,
    _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_MODERATE,
    _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HIGH,
    _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT,
    _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_ADAPTED,
    _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_UNADAPTED,
    _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_PARIS,
    _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_MODERATE,
    _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HIGH,
    _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT,
    _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_ADAPTED,
    _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_UNADAPTED,
    _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_PARIS,
    _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_MODERATE,
    _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_HIGH,
    _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_HOT,
    _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_ADAPTED,
    _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_UNADAPTED,
    _OUTPUT_LEAVES_SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2050,
    _OUTPUT_LEAVES_SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2075,
    _OUTPUT_LEAVES_SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2099,
)
from .data import CONSTANTS, DEFAULT_INPUTS
from .internals import (
    _resolve_formula,
    baseline_employment_growth,
    baseline_gdp_deflator_growth,
    baseline_labour_productivity_growth,
    baseline_nominal_gdp_growth,
    baseline_overall_balance_pct_gdp,
    baseline_population_growth,
    baseline_real_gdp_growth,
    baseline_revenue_pct_gdp,
    scenario_debt_stabilizing_primary_balance_high,
    scenario_debt_stabilizing_primary_balance_hot,
    scenario_debt_stabilizing_primary_balance_hot_adapted,
    scenario_debt_stabilizing_primary_balance_hot_unadapted,
    scenario_debt_stabilizing_primary_balance_moderate,
    scenario_debt_stabilizing_primary_balance_paris,
    scenario_debt_to_gdp,
    scenario_nominal_gdp_growth_high,
    scenario_nominal_gdp_growth_hot,
    scenario_nominal_gdp_growth_hot_adapted,
    scenario_nominal_gdp_growth_hot_unadapted,
    scenario_nominal_gdp_growth_moderate,
    scenario_nominal_gdp_growth_paris,
    scenario_overall_balance_pct_gdp,
    scenario_primary_balance_pct_gdp,
    scenario_real_gdp_level_index_high,
    scenario_real_gdp_level_index_hot,
    scenario_real_gdp_level_index_hot_adapted,
    scenario_real_gdp_level_index_hot_unadapted,
    scenario_real_gdp_level_index_moderate,
    scenario_real_gdp_level_index_paris,
)
from .runtime import (
    EvalContext,
    XlErrorException,
    coerce_inputs_dict,
    xl_cell,
    xl_range_rows,
)


def make_context(inputs: dict[str, object] | None = None) -> EvalContext:
    """Create an EvalContext with merged inputs."""
    merged: dict[str, object] = dict(DEFAULT_INPUTS)
    merged.update(CONSTANTS)
    if inputs is not None:
        merged.update(inputs)
    return EvalContext(inputs=coerce_inputs_dict(merged), resolver=_resolve_formula, iterative_enabled=False, iterate_count=100, iterate_delta=0.001)


# --- Series binding setters (Records API) ---

def set_country(
    ctx: EvalContext,
    records: Records | Record | str,
    *,
    strict: bool = True,
) -> None:
    """Set the country for the Q-CRAFT scenario.

    Updates the country selection in the Dashboard worksheet.
    The OBS_VALUE field corresponds to the country name written to the Dashboard cell C12.

    Args:
        records (Records | Record | str): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: Country name to use for the scenario.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C12
        Layout: scalar
        Value type: string

    Examples:
        set_country(ctx, 'Afghanistan')
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='scalar',
            key_fields=(),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            measure_dtype='string',
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_COUNTRY,
        strict=strict,
        fn_name='set_country',
        allow_address=False,
        requires_address=False,
    )

def set_demography_scenario(
    ctx: EvalContext,
    records: Records | Record | str,
    *,
    strict: bool = True,
) -> None:
    """Set the UN demographic variant for the baseline macro-fiscal projection.

    Updates the demographic scenario used by Q-CRAFT to project working-age population and employment growth.
    The single OBS_VALUE string selects one of the available UN demographic scenarios.

    Args:
        records (Records | Record | str): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: The demographic variant (Medium, High, or Low) to apply.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C17
        Layout: scalar
        Value type: string

    Examples:
        set_demography_scenario(ctx, 'Medium')
    """
    _apply_series_records(
        ctx,
        require_measure_labels(
            coerce_setter_input(
                records,
                layout='scalar',
                key_fields=(),
                measure_field='OBS_VALUE',
                key_order=None,
                strict=strict,
                measure_dtype='string',
            ),
            measure_field='OBS_VALUE',
            choices=_DEMOGRAPHY_SCENARIO_LABELS,
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_DEMOGRAPHY_SCENARIO,
        strict=strict,
        fn_name='set_demography_scenario',
        allow_address=False,
        requires_address=False,
    )

def set_productivity_start(
    ctx: EvalContext,
    records: Records | Record | float,
    *,
    strict: bool = True,
) -> None:
    """Set the start productivity growth rate for the baseline scenario.

    Sets the annual labor productivity growth rate projected for the start of the Q-CRAFT projection period.
    The observation value is written directly into the designated scalar cell on the Dashboard sheet.

    Args:
        records (Records | Record | float): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: Annual labor productivity growth rate expressed as a percentage.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C20
        Layout: scalar
        Value type: float

    Examples:
        set_productivity_start(ctx, 5.0)
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='scalar',
            key_fields=(),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            measure_dtype='float',
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_PRODUCTIVITY_START,
        strict=strict,
        fn_name='set_productivity_start',
        allow_address=False,
        requires_address=False,
    )

def set_productivity_end(
    ctx: EvalContext,
    records: Records | Record | float,
    *,
    strict: bool = True,
) -> None:
    """Set the long-run end productivity growth rate assumption for the baseline scenario.

    Updates the end productivity growth rate used to project the long-term productivity trajectory.
    The scalar float value is written to the productivity end cell on the Dashboard sheet.

    Args:
        records (Records | Record | float): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: Long-run structural productivity growth rate at the end of the projection horizon, expressed as a percentage value.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C21
        Layout: scalar
        Value type: float

    Examples:
        set_productivity_end(ctx, 1.2)
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='scalar',
            key_fields=(),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            measure_dtype='float',
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_PRODUCTIVITY_END,
        strict=strict,
        fn_name='set_productivity_end',
        allow_address=False,
        requires_address=False,
    )

def set_inflation_start(
    ctx: EvalContext,
    records: Records | Record | float,
    *,
    strict: bool = True,
) -> None:
    """Set the starting inflation rate assumption for the long-term projections.

    Updates the scalar inflation assumption used as the initial value in the inflation trajectory.
    A single record with an OBS_VALUE field is written directly to cell Dashboard!C24.

    Args:
        records (Records | Record | float): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: The inflation rate (as a percentage) assumed at the start of the projection period.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C24
        Layout: scalar
        Value type: float

    Examples:
        set_inflation_start(ctx, 3.5)
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='scalar',
            key_fields=(),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            measure_dtype='float',
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_INFLATION_START,
        strict=strict,
        fn_name='set_inflation_start',
        allow_address=False,
        requires_address=False,
    )

def set_inflation_end(
    ctx: EvalContext,
    records: Records | Record | float,
    *,
    strict: bool = True,
) -> None:
    """Set the long-run end-period inflation assumption for the baseline scenario.

    Updates the end inflation rate used in the dashboard to project long-term nominal GDP growth.
    The scalar float value in the record maps directly to the single dashboard cell for the end inflation rate.

    Args:
        records (Records | Record | float): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: The constant long-run inflation rate, typically the central bank's target or a regional average.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C25
        Layout: scalar
        Value type: float

    Examples:
        set_inflation_end(ctx, 3.5)
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='scalar',
            key_fields=(),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            measure_dtype='float',
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_INFLATION_END,
        strict=strict,
        fn_name='set_inflation_end',
        allow_address=False,
        requires_address=False,
    )

def set_interest_rate_mode(
    ctx: EvalContext,
    records: Records | Record | str,
    *,
    strict: bool = True,
) -> None:
    """Set the interest rate assumption mode for projecting government interest rates.

    Updates the interest rate mode in the Dashboard worksheet to control how long-term interest rates are projected.
    The scalar OBS_VALUE is written to the interest rate mode cell on the Dashboard sheet.

    Args:
        records (Records | Record | str): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: The interest rate assumption mode, specifying how future nominal interest rates are determined.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C28
        Layout: scalar
        Value type: string

    Examples:
        set_interest_rate_mode(ctx, 'Nominal interest rate')
    """
    _apply_series_records(
        ctx,
        resolve_measure_labels(
            coerce_setter_input(
                records,
                layout='scalar',
                key_fields=(),
                measure_field='OBS_VALUE',
                key_order=None,
                strict=strict,
                measure_dtype='string',
            ),
            measure_field='OBS_VALUE',
            choices=_INTEREST_RATE_MODE_LABELS,
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_INTEREST_RATE_MODE,
        strict=strict,
        fn_name='set_interest_rate_mode',
        allow_address=False,
        requires_address=False,
    )

def set_real_interest_rate(
    ctx: EvalContext,
    records: Records | Record | float,
    *,
    strict: bool = True,
) -> None:
    """Set the real interest rate used in fiscal projections.

    Updates the real interest rate assumption in the Dashboard for generating baseline and climate scenarios.
    A single scalar record is mapped to the specified Dashboard cell.

    Args:
        records (Records | Record | float): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: The real interest rate, typically aligned with the neutral real interest rate (r-star), expressed as a percentage.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C29
        Layout: scalar
        Value type: float

    Examples:
        set_real_interest_rate(ctx, 1.0)
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='scalar',
            key_fields=(),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            measure_dtype='float',
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_REAL_INTEREST_RATE,
        strict=strict,
        fn_name='set_real_interest_rate',
        allow_address=False,
        requires_address=False,
    )

def set_fiscal_rule_enabled(
    ctx: EvalContext,
    records: Records | Record | str,
    *,
    strict: bool = True,
) -> None:
    """Set whether a fiscal rule debt target is applied in the dashboard.

    Update the fiscal rule enabled status in the Dashboard worksheet.
    The record's OBS_VALUE maps directly to the single cell Dashboard!C33.

    Args:
        records (Records | Record | str): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: Indicates whether a fiscal rule debt target is applied.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C33
        Layout: scalar
        Value type: string

    Examples:
        set_fiscal_rule_enabled(ctx, 'Yes')
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='scalar',
            key_fields=(),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            measure_dtype='string',
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_FISCAL_RULE_ENABLED,
        strict=strict,
        fn_name='set_fiscal_rule_enabled',
        allow_address=False,
        requires_address=False,
    )

def set_debt_target(
    ctx: EvalContext,
    records: Records | Record | float,
    *,
    strict: bool = True,
) -> None:
    """Set the debt-to-GDP target for the fiscal rule in the dashboard.

    Updates the debt_target value used when a fiscal rule is active.
    The OBS_VALUE field maps directly to cell C34 of the Dashboard sheet.

    Args:
        records (Records | Record | float): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: Debt-to-GDP ratio target (in percent) that triggers fiscal adjustments when the fiscal rule is enabled.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C34
        Layout: scalar
        Value type: float

    Examples:
        set_debt_target(ctx, 60.0)
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='scalar',
            key_fields=(),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            measure_dtype='float',
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_DEBT_TARGET,
        strict=strict,
        fn_name='set_debt_target',
        allow_address=False,
        requires_address=False,
    )

def set_expenditure_rigidity(
    ctx: EvalContext,
    records: Records | Record | float,
    *,
    strict: bool = True,
) -> None:
    """Set the expenditure rigidity parameter for climate scenarios.

    Updates the dashboard cell that controls how rigid primary expenditure is under climate change.
    The record's OBS_VALUE is written directly to Dashboard cell C38.

    Args:
        records (Records | Record | float): A bare scalar value, a single record dict, or a list of records.
            Required record fields:
                - OBS_VALUE: Degree of expenditure rigidity: 1 means completely rigid (expenditure unchanged from baseline), 0 means fully flexible (same expenditure-to-GDP ratio as baseline).

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Dashboard!C38
        Layout: scalar
        Value type: float

    Examples:
        set_expenditure_rigidity(ctx, 1.0)
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='scalar',
            key_fields=(),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            measure_dtype='float',
        ),
        key_fields=(),
        allowed_fields=frozenset({'OBS_VALUE', 'PARAMETER'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_EXPENDITURE_RIGIDITY,
        strict=strict,
        fn_name='set_expenditure_rigidity',
        allow_address=False,
        requires_address=False,
    )

def set_discrete_revenue_shocks(
    ctx: EvalContext,
    records: Records | Record | DataFrameInput,
    *,
    strict: bool = True,
    empty_measure: EmptyMeasure = "write",
) -> None:
    """Set revenue shock paths for climate change discrete risk scenarios.

    Updates the revenue-side fiscal impacts of discrete risk materializations across scenarios and time.
    Each record maps to a cell in the worksheet matrix by its SCENARIO row label and TIME_PERIOD column header.

    Args:
        records (Records | Record | DataFrameInput): A list of records, a single record dict, or a tidy pandas/polars DataFrame.
        empty_measure (EmptyMeasure): How to treat rows with missing measure values (`None` or float NaN after DataFrame coercion). "write" (default) passes values through; "skip" drops them; "error" raises. Empty key fields always raise.
            Required record fields:
                - SCENARIO: Climate change scenario identifier.
                - TIME_PERIOD: Projection year for the shock value.
                - OBS_VALUE: Revenue shock as a percentage of GDP.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Discrete Risks!C2:BT13
        Layout: matrix
        Value type: float

    Examples:
        set_discrete_revenue_shocks(ctx, [
            {'SCENARIO': 'Paris', 'TIME_PERIOD': 2030, 'OBS_VALUE': None},
            {'SCENARIO': 'Paris', 'TIME_PERIOD': 2031, 'OBS_VALUE': None},
        ])
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='matrix',
            key_fields=('SCENARIO', 'TIME_PERIOD'),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            empty_measure=empty_measure,
            requires_address=False,
            key_dtypes={'SCENARIO': 'string', 'TIME_PERIOD': 'int'},
            measure_dtype='float',
        ),
        key_fields=('SCENARIO', 'TIME_PERIOD'),
        allowed_fields=frozenset({'OBS_VALUE', 'SCENARIO', 'TIME_PERIOD'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_DISCRETE_REVENUE_SHOCKS,
        strict=strict,
        fn_name='set_discrete_revenue_shocks',
        allow_address=False,
        requires_address=False,
    )

def set_discrete_primary_expenditure_shocks(
    ctx: EvalContext,
    records: Records | Record | DataFrameInput,
    *,
    strict: bool = True,
    empty_measure: EmptyMeasure = "write",
) -> None:
    """Set discrete climate-scenario primary expenditure shock paths as percentage-of-GDP values.

    Updates the Discrete Risks worksheet with primary expenditure shock records for different climate scenarios and time periods.
    Each record corresponds to a cell in the grouped-row matrix layout on the Discrete Risks sheet, keyed by scenario and year.

    Args:
        records (Records | Record | DataFrameInput): A list of records, a single record dict, or a tidy pandas/polars DataFrame.
        empty_measure (EmptyMeasure): How to treat rows with missing measure values (`None` or float NaN after DataFrame coercion). "write" (default) passes values through; "skip" drops them; "error" raises. Empty key fields always raise.
            Required record fields:
                - SCENARIO: Climate scenario to which the shock path applies.
                - TIME_PERIOD: Year during which the shock occurs.
                - OBS_VALUE: Primary expenditure shock expressed as a percentage of GDP.

    Returns:
        None: Applies the input updates to ctx.

    Source binding:
        Workbook range: Discrete Risks!C2:BT13
        Layout: matrix
        Value type: float

    Examples:
        set_discrete_primary_expenditure_shocks(ctx, [
            {'SCENARIO': 'Paris', 'TIME_PERIOD': 2030, 'OBS_VALUE': None},
            {'SCENARIO': 'Paris', 'TIME_PERIOD': 2031, 'OBS_VALUE': None},
        ])
    """
    _apply_series_records(
        ctx,
        coerce_setter_input(
            records,
            layout='matrix',
            key_fields=('SCENARIO', 'TIME_PERIOD'),
            measure_field='OBS_VALUE',
            key_order=None,
            strict=strict,
            empty_measure=empty_measure,
            requires_address=False,
            key_dtypes={'SCENARIO': 'string', 'TIME_PERIOD': 'int'},
            measure_dtype='float',
        ),
        key_fields=('SCENARIO', 'TIME_PERIOD'),
        allowed_fields=frozenset({'OBS_VALUE', 'SCENARIO', 'TIME_PERIOD'}),
        measure_field='OBS_VALUE',
        leaf_index=_LEAF_INDEX_DISCRETE_PRIMARY_EXPENDITURE_SHOCKS,
        strict=strict,
        fn_name='set_discrete_primary_expenditure_shocks',
        allow_address=False,
        requires_address=False,
    )

# --- Series binding output compute (Records API) ---

def compute_baseline_primary_expenditure_pct_gdp(ctx=None, *, inputs=None) -> Records:
    """Retrieve the baseline primary expenditure as a percentage of GDP for each projection year.

    Returns records that map each time period to the primary expenditure-to-GDP ratio from the baseline scenario.
    Each record corresponds to one column in the Baseline sheet, with TIME_PERIOD from the column header and OBS_VALUE from the data cell.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The calendar year for which the primary expenditure ratio is projected.
                - OBS_VALUE: The primary expenditure expressed as a percentage of nominal GDP in the baseline scenario.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D21:CP21
        Layout: series
        Value type: float

    Examples:
        compute_baseline_primary_expenditure_pct_gdp(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_PRIMARY_EXPENDITURE_PCT_GDP:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_interest_expenditure_pct_gdp(ctx=None, *, inputs=None) -> Records:
    """Compute baseline interest expenditure as a percentage of GDP.

    Return records of annual baseline interest expenditure expressed as percent of nominal GDP.
    Each record corresponds to one column from the Baseline sheet range D20:CP20, with the TIME_PERIOD taken from the column header in row 2.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Calendar year of the observation.
                - OBS_VALUE: Interest expenditure value as percent of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D20:CP20
        Layout: series
        Value type: float

    Examples:
        compute_baseline_interest_expenditure_pct_gdp(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_INTEREST_EXPENDITURE_PCT_GDP:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_interest_rate(ctx=None, *, inputs=None) -> Records:
    """Compute the weighted nominal interest rate series from the baseline scenario.

    Returns the projected weighted nominal interest rate for each year in the baseline scenario.
    Each record corresponds to a year column in the `Baseline` worksheet, with `TIME_PERIOD` as the year and `OBS_VALUE` as the interest rate.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year of the projection.
                - OBS_VALUE: Weighted nominal interest rate.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the interest rate. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D33:CP33
        Layout: series
        Value type: float

    Examples:
        compute_baseline_interest_rate(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_INTEREST_RATE:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_primary_balance_pct_gdp(ctx=None, *, inputs=None) -> Records:
    """Compute baseline primary balance as percent of GDP time series.

    Returns a Series of baseline primary balance values expressed as percent of GDP for each year.
    Each record corresponds to a year in the Baseline worksheet row containing primary balance percent of GDP data.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year of the projection or historical data point.
                - OBS_VALUE: Primary balance as percentage of nominal GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D22:CP22
        Layout: series
        Value type: float

    Examples:
        compute_baseline_primary_balance_pct_gdp(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_PRIMARY_BALANCE_PCT_GDP:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_overall_balance_pct_gdp(ctx=None, *, inputs=None) -> Records:
    """Compute the baseline overall balance as a percentage of GDP.

    Return the projected baseline overall balance as a percentage of GDP for each projection year.
    Each record represents a value from the row 'Overall balance' on the Baseline sheet, keyed by projection year (TIME_PERIOD).

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The projection year.
                - OBS_VALUE: The overall balance expressed as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D23:CP23
        Layout: series
        Value type: float

    Examples:
        compute_baseline_overall_balance_pct_gdp(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_OVERALL_BALANCE_PCT_GDP:
        record = dict(static_record)
        try:
            record[measure_field] = baseline_overall_balance_pct_gdp(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_debt_to_gdp(ctx=None, *, inputs=None) -> Records:
    """Compute and return the baseline gross debt-to-GDP ratio series from the Q-CRAFT Baseline worksheet.

    This function returns a sequence of records representing the baseline debt-to-GDP ratio for each projection year.
    Each output record pulls the debt-to-GDP ratio from the corresponding projection year cell in the Baseline worksheet, pairing it with the year taken from column headers.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Calendar year of the projection.
                - OBS_VALUE: Debt-to-GDP ratio expressed as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D36:CP36
        Layout: series
        Value type: float

    Examples:
        compute_baseline_debt_to_gdp(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_DEBT_TO_GDP:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_debt_stabilizing_primary_balance(ctx=None, *, inputs=None) -> Records:
    """Compute the debt-stabilizing primary balance for each year in the baseline scenario.

    Returns the primary balance (as a percent of GDP) required to keep the debt-to-GDP ratio stable over time.
    Each record represents one year; TIME_PERIOD identifies the calendar year column, and OBS_VALUE reads the computed debt-stabilizing primary balance from the corresponding cell.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Calendar year for the projection.
                - OBS_VALUE: Primary balance (percent of GDP) that stabilizes the debt-to-GDP ratio.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!E37:CP37
        Layout: series
        Value type: float

    Examples:
        compute_baseline_debt_stabilizing_primary_balance(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_DEBT_STABILIZING_PRIMARY_BALANCE:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_fiscal_consolidation_gap(ctx=None, *, inputs=None) -> Records:
    """Compute the fiscal consolidation gap series for the baseline scenario.

    Returns the fiscal consolidation gap as a percent of GDP over the projection period.
    Each record corresponds to a cell in the Baseline worksheet row U40:CP40, keyed by TIME_PERIOD.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year of the projection.
                - OBS_VALUE: Fiscal consolidation gap, in percent of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!U40:CP40
        Layout: series
        Value type: float

    Examples:
        compute_baseline_fiscal_consolidation_gap(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_FISCAL_CONSOLIDATION_GAP:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_nominal_gdp_growth(ctx=None, *, inputs=None) -> Records:
    """Compute baseline nominal GDP growth rate projections.

    Return the projected annual nominal GDP growth rate for the baseline scenario.
    Each record corresponds to a year's growth rate value from the Baseline worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year of the projection.
                - OBS_VALUE: Projected annual nominal GDP growth rate.
            Optional record fields:
                - UNIT_MEASURE: Indicates the unit of measure for the projected values. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D15:CP15
        Layout: series
        Value type: float

    Examples:
        compute_baseline_nominal_gdp_growth(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_NOMINAL_GDP_GROWTH:
        record = dict(static_record)
        try:
            record[measure_field] = baseline_nominal_gdp_growth(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_real_gdp_growth(ctx=None, *, inputs=None) -> Records:
    """Compute baseline real GDP growth series from the Q-CRAFT Baseline worksheet.

    Returns the projected real GDP growth rates for each year in the projection horizon.
    Each record corresponds to a single year's real GDP growth rate extracted from the Baseline worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the projection or historical data point.
                - OBS_VALUE: The real GDP growth rate for the given time period, expressed as a percentage.
            Optional record fields:
                - UNIT_MEASURE: The unit of measurement for the growth rate, specified as a percent of GDP. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D13:CP13
        Layout: series
        Value type: float

    Examples:
        compute_baseline_real_gdp_growth(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_REAL_GDP_GROWTH:
        record = dict(static_record)
        try:
            record[measure_field] = baseline_real_gdp_growth(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_revenue_pct_gdp(ctx=None, *, inputs=None) -> Records:
    """Retrieve the baseline projection of general government revenue as a percentage of GDP.

    Returns the baseline revenue-to-GDP ratio series for all projection years.
    Each record corresponds to a cell in the Baseline worksheet range, mapping column headers to TIME_PERIOD and cell values to OBS_VALUE.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The projection year.
                - OBS_VALUE: The projected general government revenue, expressed as a percentage of nominal GDP.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation values. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D18:CP18
        Layout: series
        Value type: float

    Examples:
        compute_baseline_revenue_pct_gdp(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_REVENUE_PCT_GDP:
        record = dict(static_record)
        try:
            record[measure_field] = baseline_revenue_pct_gdp(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_employment_growth(ctx=None, *, inputs=None) -> Records:
    """Computes the baseline employment growth series from demographic projections.

    Returns the projected annual growth rate of employment under the baseline scenario.
    Each record represents a year in the Baseline sheet, with TIME_PERIOD from the column header and OBS_VALUE from the corresponding data cell.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year of the observation.
                - OBS_VALUE: Employment growth rate.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D11:CP11
        Layout: series
        Value type: float

    Examples:
        compute_baseline_employment_growth(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_EMPLOYMENT_GROWTH:
        record = dict(static_record)
        try:
            record[measure_field] = baseline_employment_growth(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_labour_productivity_growth(ctx=None, *, inputs=None) -> Records:
    """Returns the baseline labour productivity growth series.

    Returns the annual growth rate of GDP per employed person for the baseline scenario.
    Each record corresponds to a year in the Baseline worksheet row 12.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the observation.
                - OBS_VALUE: The labour productivity growth rate for the year.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D12:CP12
        Layout: series
        Value type: float

    Examples:
        compute_baseline_labour_productivity_growth(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_LABOUR_PRODUCTIVITY_GROWTH:
        record = dict(static_record)
        try:
            record[measure_field] = baseline_labour_productivity_growth(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_gdp_deflator_growth(ctx=None, *, inputs=None) -> Records:
    """Return projected GDP deflator growth rates for the baseline scenario.

    Compute and return the GDP deflator growth rates used in the baseline macro-fiscal projections.
    Each record corresponds to the GDP deflator growth for a given year, sourced from the Baseline worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the projection.
                - OBS_VALUE: Projected growth rate of the GDP deflator.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D14:CP14
        Layout: series
        Value type: float

    Examples:
        compute_baseline_gdp_deflator_growth(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_GDP_DEFLATOR_GROWTH:
        record = dict(static_record)
        try:
            record[measure_field] = baseline_gdp_deflator_growth(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_baseline_population_growth(ctx=None, *, inputs=None) -> Records:
    """Returns the baseline population growth series from the Q-CRAFT Baseline sheet.

    Provides the projected annual population growth rates under the baseline demographic scenario.
    Each record corresponds to a time period column in the series data range on the Baseline sheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year or time period for which the population growth is projected.
                - OBS_VALUE: The projected population growth rate.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Baseline!D16:CP16
        Layout: series
        Value type: float

    Examples:
        compute_baseline_population_growth(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_BASELINE_POPULATION_GROWTH:
        record = dict(static_record)
        try:
            record[measure_field] = baseline_population_growth(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_primary_balance_pct_gdp(ctx=None, *, inputs=None) -> Records:
    """Returns the primary balance as a percentage of GDP for each climate scenario over the projection horizon.

    Provides scenario primary balance values from the 'Output Scenarios' worksheet.
    Each record corresponds to a cell in the scenario primary balance matrix, identified by scenario row and time-period column.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: Climate scenario identifier (e.g., Paris, Moderate, High, Hot, Hot adapted, Hot un-adapted).
                - TIME_PERIOD: Projection year.
                - OBS_VALUE: Primary balance as a percent of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure indicator; the observation value is expressed as a percentage of GDP. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Output Scenarios!V93:CO98
        Layout: matrix
        Value type: float

    Examples:
        compute_scenario_primary_balance_pct_gdp(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_PRIMARY_BALANCE_PCT_GDP:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_primary_balance_pct_gdp(ctx, scenario=static_record['SCENARIO'], time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_overall_balance_pct_gdp(ctx=None, *, inputs=None) -> Records:
    """Return overall balance as a percentage of GDP for Q-CRAFT climate scenarios.

    Returns projected overall balance as percent of GDP for each climate scenario and time period.
    Each record corresponds to a cell in the Output Scenarios worksheet, with SCENARIO from row labels, TIME_PERIOD from column headers, and OBS_VALUE from the intersecting cell.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: The climate scenario.
                - TIME_PERIOD: The year of the projection.
                - OBS_VALUE: The overall balance as a percentage of GDP for the given scenario and time period.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Output Scenarios!V102:CO107
        Layout: matrix
        Value type: float

    Examples:
        compute_scenario_overall_balance_pct_gdp(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_OVERALL_BALANCE_PCT_GDP:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_overall_balance_pct_gdp(ctx, scenario=static_record['SCENARIO'], time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_debt_to_gdp(ctx=None, *, inputs=None) -> Records:
    """Compute projected debt-to-GDP ratio paths under climate change scenarios.

    Return the projected debt-to-GDP ratio for each climate scenario and year.
    Each record represents a cell in the matrix, with SCENARIO and TIME_PERIOD keys matching the row label and column header.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: Climate scenario path (e.g., Paris, Moderate, High, Hot, Hot Adapted, Hot Un-Adapted).
                - TIME_PERIOD: Projection year.
                - OBS_VALUE: Debt-to-GDP ratio under the scenario.
            Optional record fields:
                - UNIT_MEASURE: Unit of measurement for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Output Scenarios!V111:CO116
        Layout: matrix
        Value type: float

    Examples:
        compute_scenario_debt_to_gdp(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_DEBT_TO_GDP:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_debt_to_gdp(ctx, scenario=static_record['SCENARIO'], time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_debt_stabilizing_primary_balance_paris(ctx=None, *, inputs=None) -> Records:
    """Compute annual debt-stabilizing primary balance under the Paris climate scenario as percent of GDP.

    Returns a series of the debt-stabilizing primary balance values for each year.
    Each record corresponds to a cell in the workbook range Paris!D36:CP36, keyed by year.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the projection.
                - OBS_VALUE: The debt-stabilizing primary balance, expressed as percent of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Paris!D36:CP36
        Layout: series
        Value type: float

    Examples:
        compute_scenario_debt_stabilizing_primary_balance_paris(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_PARIS:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_debt_stabilizing_primary_balance_paris(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_debt_stabilizing_primary_balance_moderate(ctx=None, *, inputs=None) -> Records:
    """Compute the debt-stabilizing primary balance under the Moderate climate scenario.

    Returns an iterator of records for the debt-stabilizing primary balance required to keep the debt-to-GDP ratio stable each year under the Moderate scenario.
    Each record is derived from a cell in the Moderate sheet's D36:CP36 range, with TIME_PERIOD from the column headers and OBS_VALUE from the cell value, accompanied by a constant UNIT_MEASURE attribute.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the projection.
                - OBS_VALUE: The debt-stabilizing primary balance as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the primary balance values. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Moderate!D36:CP36
        Layout: series
        Value type: float

    Examples:
        compute_scenario_debt_stabilizing_primary_balance_moderate(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_MODERATE:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_debt_stabilizing_primary_balance_moderate(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_debt_stabilizing_primary_balance_high(ctx=None, *, inputs=None) -> Records:
    """Compute the annual debt-stabilizing primary balance as a percent of GDP for the High climate scenario.

    Returns the primary balance required each year to stabilize the debt-to-GDP ratio under the High emissions scenario.
    Each record represents a year from the 'High!D36:CP36' range, mapping column headers to TIME_PERIOD and cell values to OBS_VALUE.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Calendar year of the projected observation.
                - OBS_VALUE: Debt-stabilizing primary balance expressed as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: High!D36:CP36
        Layout: series
        Value type: float

    Examples:
        compute_scenario_debt_stabilizing_primary_balance_high(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HIGH:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_debt_stabilizing_primary_balance_high(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_debt_stabilizing_primary_balance_hot(ctx=None, *, inputs=None) -> Records:
    """Compute the debt-stabilizing primary balance trajectory for the Hot climate scenario.

    Return the debt-stabilizing primary balance as a percentage of GDP for each projection year in the Hot scenario.
    Each record corresponds to a year in the Hot sheet's debt-stabilizing primary balance row, with TIME_PERIOD from column headers and OBS_VALUE from data cells.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The projection year.
                - OBS_VALUE: The debt-stabilizing primary balance as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: The unit of measurement for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot!D36:CP36
        Layout: series
        Value type: float

    Examples:
        compute_scenario_debt_stabilizing_primary_balance_hot(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_debt_stabilizing_primary_balance_hot(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_debt_stabilizing_primary_balance_hot_adapted(ctx=None, *, inputs=None) -> Records:
    """Compute the debt-stabilising primary balance series for the hot adapted climate scenario.

    Returns a sequence of records providing the annual debt-stabilising primary balance as a percentage of GDP.
    Each record pairs a cell from the Hot Adapted sheet row with its corresponding year header, mapping the header to the TIME_PERIOD field and the cell value to OBS_VALUE.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year of the projection.
                - OBS_VALUE: Debt-stabilising primary balance expressed as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measurement for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot Adapted!D36:CP36
        Layout: series
        Value type: float

    Examples:
        compute_scenario_debt_stabilizing_primary_balance_hot_adapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_ADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_debt_stabilizing_primary_balance_hot_adapted(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_debt_stabilizing_primary_balance_hot_unadapted(ctx=None, *, inputs=None) -> Records:
    """Compute the debt-stabilizing primary balance (% of GDP) under the Hot Unadapted climate scenario.

    Returns the annual debt-stabilizing primary balance projections for the Hot Unadapted climate scenario.
    Each record corresponds to a projection year, with OBS_VALUE read from the 'Hot Unadapted' sheet row 36 for that year.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The calendar year of the projection.
                - OBS_VALUE: The debt-stabilizing primary balance as percent of GDP in the Hot Unadapted climate scenario.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot Unadapted!D36:CP36
        Layout: series
        Value type: float

    Examples:
        compute_scenario_debt_stabilizing_primary_balance_hot_unadapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_DEBT_STABILIZING_PRIMARY_BALANCE_HOT_UNADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_debt_stabilizing_primary_balance_hot_unadapted(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_nominal_gdp_growth_paris(ctx=None, *, inputs=None) -> Records:
    """Compute the annual nominal GDP growth rate series for the Paris climate change scenario.

    Returns a list of records, each containing the projection year and the corresponding nominal GDP growth rate.
    Each record corresponds to one column in the Paris!D11:CP11 range, with the year taken from the column header in row 2.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The projection year.
                - OBS_VALUE: The nominal GDP growth rate (percent).
            Optional record fields:
                - UNIT_MEASURE: Indicates the unit of measure of the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Paris!D11:CP11
        Layout: series
        Value type: float

    Examples:
        compute_scenario_nominal_gdp_growth_paris(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_PARIS:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_nominal_gdp_growth_paris(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_nominal_gdp_growth_moderate(ctx=None, *, inputs=None) -> Records:
    """Compute projected nominal GDP growth rates for the Moderate climate scenario.

    Returns a sequence of annual nominal GDP growth rates under the Moderate scenario.
    Each record corresponds to a cell in row 11 of the Moderate sheet, with the column header providing the TIME_PERIOD and the cell value providing OBS_VALUE.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The calendar year of the projection.
                - OBS_VALUE: The projected nominal GDP growth rate for the given year.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the growth rate. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Moderate!D11:CP11
        Layout: series
        Value type: float

    Examples:
        compute_scenario_nominal_gdp_growth_moderate(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_MODERATE:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_nominal_gdp_growth_moderate(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_nominal_gdp_growth_high(ctx=None, *, inputs=None) -> Records:
    """Compute the nominal GDP growth rate for the High climate scenario.

    Returns a helper containing nominal GDP growth records for the High scenario, indexed by time period.
    Each record corresponds to a cell in the 'High' worksheet, row 11, columns D to CP, with TIME_PERIOD from the header row.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the observation.
                - OBS_VALUE: The nominal GDP growth rate for the given year under the High scenario.
            Optional record fields:
                - UNIT_MEASURE: Indicates the unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: High!D11:CP11
        Layout: series
        Value type: float

    Examples:
        compute_scenario_nominal_gdp_growth_high(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_HIGH:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_nominal_gdp_growth_high(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_nominal_gdp_growth_hot(ctx=None, *, inputs=None) -> Records:
    """Retrieve projected nominal GDP growth under the Hot climate scenario.

    Return a list of records containing annual nominal GDP growth rates for the Hot scenario.
    Each record corresponds to a yearly value from the Hot scenario nominal GDP growth series.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The projected year.
                - OBS_VALUE: The nominal GDP growth rate.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the growth rate. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot!D11:CP11
        Layout: series
        Value type: float

    Examples:
        compute_scenario_nominal_gdp_growth_hot(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_HOT:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_nominal_gdp_growth_hot(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_nominal_gdp_growth_hot_adapted(ctx=None, *, inputs=None) -> Records:
    """Compute projected nominal GDP growth under the Hot Adapted climate scenario.

    Returns the nominal GDP growth series for the Hot Adapted scenario.
    Each record corresponds to a year in the projection, with the observation value read from the data range 'Hot Adapted!D11:CP11'.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the projection.
                - OBS_VALUE: The projected nominal GDP growth rate.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot Adapted!D11:CP11
        Layout: series
        Value type: float

    Examples:
        compute_scenario_nominal_gdp_growth_hot_adapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_HOT_ADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_nominal_gdp_growth_hot_adapted(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_nominal_gdp_growth_hot_unadapted(ctx=None, *, inputs=None) -> Records:
    """Compute nominal GDP growth rates for the Hot unadapted climate scenario.

    Returns an iterable of records containing the annual nominal GDP growth rate for each projection year in the Hot unadapted scenario.
    Each record corresponds to a year (TIME_PERIOD) from the Hot Unadapted worksheet row, with OBS_VALUE as the associated growth rate.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The projection year.
                - OBS_VALUE: The annual nominal GDP growth rate.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the growth rate. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot Unadapted!D11:CP11
        Layout: series
        Value type: float

    Examples:
        compute_scenario_nominal_gdp_growth_hot_unadapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_NOMINAL_GDP_GROWTH_HOT_UNADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_nominal_gdp_growth_hot_unadapted(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_primary_expenditure_pct_gdp_paris(ctx=None, *, inputs=None) -> Records:
    """Returns the projected primary expenditure as a percentage of GDP under the Paris climate scenario.

    Provides the primary expenditure-to-GDP ratio for each year in the Paris scenario, reflecting fiscal impacts under the SSP1-2.6 climate pathway.
    Each record corresponds to a single year (TIME_PERIOD) and its primary expenditure value (OBS_VALUE) as a percentage of GDP.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The calendar year of the projection.
                - OBS_VALUE: The primary expenditure expressed as a percentage of GDP in that year.
            Optional record fields:
                - UNIT_MEASURE: Indicates the observation is measured as a percentage of GDP. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Paris!D20:CP20
        Layout: series
        Value type: float

    Examples:
        compute_scenario_primary_expenditure_pct_gdp_paris(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_PARIS:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_primary_expenditure_pct_gdp_moderate(ctx=None, *, inputs=None) -> Records:
    """Compute primary expenditure as percent of GDP under the Moderate climate scenario.

    Return primary expenditure-to-GDP ratios for the Moderate scenario projections.
    Each record corresponds to a single time period's primary expenditure as percent of GDP from the Moderate scenario.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The time period (year) of the projection.
                - OBS_VALUE: The primary expenditure as a percentage of GDP for the given period.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Moderate!D20:CP20
        Layout: series
        Value type: float

    Examples:
        compute_scenario_primary_expenditure_pct_gdp_moderate(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_MODERATE:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_primary_expenditure_pct_gdp_high(ctx=None, *, inputs=None) -> Records:
    """Compute primary expenditure as a percentage of GDP under the High climate scenario.

    Returns the projected primary expenditure-to-GDP ratio for the High climate scenario.
    Each record maps one column in the High sheet row 20 to a year (TIME_PERIOD) and the cell value to primary expenditure as percent of GDP (OBS_VALUE).

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the projection.
                - OBS_VALUE: The primary expenditure as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: High!D20:CP20
        Layout: series
        Value type: float

    Examples:
        compute_scenario_primary_expenditure_pct_gdp_high(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HIGH:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_primary_expenditure_pct_gdp_hot(ctx=None, *, inputs=None) -> Records:
    """Retrieve projected primary expenditure as a percentage of GDP under the Hot climate scenario.

    Returns a list of records with annual primary expenditure-to-GDP ratios for the Hot scenario.
    Each record corresponds to a single year's value from the Hot scenario projection row.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Calendar year of the projection.
                - OBS_VALUE: Primary expenditure expressed as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot!D20:CP20
        Layout: series
        Value type: float

    Examples:
        compute_scenario_primary_expenditure_pct_gdp_hot(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_primary_expenditure_pct_gdp_hot_adapted(ctx=None, *, inputs=None) -> Records:
    """Compute primary expenditure as a percentage of GDP for the Hot adapted climate scenario.

    Return the projected primary expenditure-to-GDP ratio under the Hot adapted climate scenario.
    Each record corresponds to a year's projected primary expenditure percentage from the Hot Adapted worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the observation.
                - OBS_VALUE: The projected primary expenditure as a percentage of GDP for the Hot adapted scenario.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the primary expenditure observation. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot Adapted!D20:CP20
        Layout: series
        Value type: float

    Examples:
        compute_scenario_primary_expenditure_pct_gdp_hot_adapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_ADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_primary_expenditure_pct_gdp_hot_unadapted(ctx=None, *, inputs=None) -> Records:
    """Compute primary expenditure as a percentage of GDP under the Hot Unadapted climate scenario.

    Returns a sequence of annual observations for the Hot Unadapted scenario's primary expenditure-to-GDP ratio.
    Each record corresponds to a column in the 'Hot Unadapted' worksheet row 20, with TIME_PERIOD parsed from the column headers.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the observation.
                - OBS_VALUE: Primary expenditure as a percentage of GDP in the Hot Unadapted scenario.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure of the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot Unadapted!D20:CP20
        Layout: series
        Value type: float

    Examples:
        compute_scenario_primary_expenditure_pct_gdp_hot_unadapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_PRIMARY_EXPENDITURE_PCT_GDP_HOT_UNADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_interest_expenditure_pct_gdp_paris(ctx=None, *, inputs=None) -> Records:
    """Compute interest expenditure as a percentage of GDP under the Paris Agreement climate scenario.

    Returns projected interest expenditure-to-GDP ratios for each year in the Paris scenario.
    Each record corresponds to a cell in the Paris worksheet row D19:CP19, with TIME_PERIOD from column headers and OBS_VALUE from the cell value.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The projection year.
                - OBS_VALUE: Interest expenditure as a percentage of GDP under the Paris scenario.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Paris!D19:CP19
        Layout: series
        Value type: float

    Examples:
        compute_scenario_interest_expenditure_pct_gdp_paris(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_PARIS:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_interest_expenditure_pct_gdp_moderate(ctx=None, *, inputs=None) -> Records:
    """Compute interest expenditure as percent of GDP for the Moderate climate scenario.

    Returns the projected interest expenditure-to-GDP ratio for each year under the Moderate climate scenario.
    Each record corresponds to a year; TIME_PERIOD is extracted from column headers, and OBS_VALUE is read from the associated data cell in the Moderate sheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year for the observation.
                - OBS_VALUE: Interest expenditure expressed as a percentage of GDP in the Moderate scenario.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Moderate!D19:CP19
        Layout: series
        Value type: float

    Examples:
        compute_scenario_interest_expenditure_pct_gdp_moderate(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_MODERATE:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_interest_expenditure_pct_gdp_high(ctx=None, *, inputs=None) -> Records:
    """Compute interest expenditure as a percentage of GDP under the High climate scenario.

    Returns time series records for interest expenditure as a percent of GDP for the High scenario.
    Each record corresponds to a cell in the High!D19:CP19 row, with TIME_PERIOD from column headers.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year of the observation.
                - OBS_VALUE: Interest expenditure as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: High!D19:CP19
        Layout: series
        Value type: float

    Examples:
        compute_scenario_interest_expenditure_pct_gdp_high(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HIGH:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_interest_expenditure_pct_gdp_hot(ctx=None, *, inputs=None) -> Records:
    """Compute interest expenditure as a percentage of GDP for the Hot climate scenario.

    Returns a sequence of records with annual interest expenditure as a percentage of GDP under the Hot climate scenario.
    Each record corresponds to a year in the Hot scenario output range, where TIME_PERIOD maps to the column year and OBS_VALUE maps to the interest expenditure value.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year for which the observation is reported.
                - OBS_VALUE: Interest expenditure as a percentage of GDP under the Hot climate scenario.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot!D19:CP19
        Layout: series
        Value type: float

    Examples:
        compute_scenario_interest_expenditure_pct_gdp_hot(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_interest_expenditure_pct_gdp_hot_adapted(ctx=None, *, inputs=None) -> Records:
    """Compute the interest expenditure as a percentage of GDP for the Hot Adapted climate scenario.

    Returns time series records of interest expenditure as a percentage of GDP under the Hot Adapted scenario.
    Each record maps a column header (year) to the corresponding value in row 19 of the Hot Adapted worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Calendar year of the observation.
                - OBS_VALUE: Interest expenditure as a percentage of nominal GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot Adapted!D19:CP19
        Layout: series
        Value type: float

    Examples:
        compute_scenario_interest_expenditure_pct_gdp_hot_adapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_ADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_interest_expenditure_pct_gdp_hot_unadapted(ctx=None, *, inputs=None) -> Records:
    """Compute interest expenditure as a percentage of GDP for the Hot unadapted climate scenario.

    This function returns a list of records containing the computed interest expenditure as a percentage of GDP for each projection year under the Hot unadapted scenario.
    Each record corresponds to one column in the Hot Unadapted sheet, with TIME_PERIOD read from the column header and OBS_VALUE from the data row.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Projection year.
                - OBS_VALUE: Computed interest expenditure as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure indicator for percent of GDP. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Hot Unadapted!D19:CP19
        Layout: series
        Value type: float

    Examples:
        compute_scenario_interest_expenditure_pct_gdp_hot_unadapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_INTEREST_EXPENDITURE_PCT_GDP_HOT_UNADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_real_gdp_level_index_paris(ctx=None, *, inputs=None) -> Records:
    """Compute the real GDP level index for the Paris climate scenario.

    Returns the yearly real GDP level index projection under the Paris scenario.
    Each record maps a year (TIME_PERIOD) from the column headers of the Paris sheet row 14 to the corresponding real GDP level index value (OBS_VALUE).

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the projection.
                - OBS_VALUE: The real GDP level index value for that year.
            Optional record fields:
                - UNIT_MEASURE: Indicates the unit of measurement for OBS_VALUE. If supplied, expected value: "INDEX".

    Source binding:
        Workbook range: Paris!D14:CP14
        Layout: series
        Value type: float

    Examples:
        compute_scenario_real_gdp_level_index_paris(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_PARIS:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_real_gdp_level_index_paris(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_real_gdp_level_index_moderate(ctx=None, *, inputs=None) -> Records:
    """Compute real GDP level index for the Moderate climate scenario.

    Return the real GDP level index series for the Moderate climate scenario.
    Each record corresponds to a cell in the Moderate scenario real GDP level row, pairing year from column headers with the observation value.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year of the observation.
                - OBS_VALUE: Real GDP level index value for the given year under the Moderate scenario.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation. If supplied, expected value: "INDEX".

    Source binding:
        Workbook range: Moderate!D14:CP14
        Layout: series
        Value type: float

    Examples:
        compute_scenario_real_gdp_level_index_moderate(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_MODERATE:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_real_gdp_level_index_moderate(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_real_gdp_level_index_high(ctx=None, *, inputs=None) -> Records:
    """Compute the real GDP level index for the High climate scenario.

    Retrieve the index of real GDP level over time for the High emissions scenario.
    Each record represents one year, with TIME_PERIOD from the column header and OBS_VALUE from the corresponding cell in the 'High' worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year for which the index is reported.
                - OBS_VALUE: Real GDP level index value for the given year.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "INDEX".

    Source binding:
        Workbook range: High!D14:CP14
        Layout: series
        Value type: float

    Examples:
        compute_scenario_real_gdp_level_index_high(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_HIGH:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_real_gdp_level_index_high(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_real_gdp_level_index_hot(ctx=None, *, inputs=None) -> Records:
    """Real GDP level index under the Hot climate scenario.

    Returns the projected real GDP level index for the Hot scenario.
    Each record maps to a column in the Hot sheet (D14:CP14), with TIME_PERIOD from header row 2 and OBS_VALUE from row 14.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The calendar year for the projection.
                - OBS_VALUE: The real GDP level index for the given year under the Hot scenario.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "INDEX".

    Source binding:
        Workbook range: Hot!D14:CP14
        Layout: series
        Value type: float

    Examples:
        compute_scenario_real_gdp_level_index_hot(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_HOT:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_real_gdp_level_index_hot(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_real_gdp_level_index_hot_adapted(ctx=None, *, inputs=None) -> Records:
    """Return the real GDP level index values projected under the Hot Adapted climate scenario.

    Returns a list of records each containing a time period and the associated real GDP level index for the Hot Adapted scenario.
    Each record corresponds to a column in the 'Hot Adapted' sheet, with TIME_PERIOD from the column header row and OBS_VALUE from the data row.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: The year or time period for the projection.
                - OBS_VALUE: The real GDP level index value for the given time period under the Hot Adapted scenario.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure for the observation value. If supplied, expected value: "INDEX".

    Source binding:
        Workbook range: Hot Adapted!D14:CP14
        Layout: series
        Value type: float

    Examples:
        compute_scenario_real_gdp_level_index_hot_adapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_ADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_real_gdp_level_index_hot_adapted(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_real_gdp_level_index_hot_unadapted(ctx=None, *, inputs=None) -> Records:
    """Compute real GDP level index under the Hot Unadapted climate scenario.

    Computes and returns the real GDP level index time series for the Hot Unadapted scenario.
    Each record corresponds to a year in the projection horizon with its real GDP index value.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - TIME_PERIOD: Year of the projection.
                - OBS_VALUE: Real GDP level index value for the Hot Unadapted scenario.
            Optional record fields:
                - UNIT_MEASURE: Unit of measurement for the index values. If supplied, expected value: "INDEX".

    Source binding:
        Workbook range: Hot Unadapted!D14:CP14
        Layout: series
        Value type: float

    Examples:
        compute_scenario_real_gdp_level_index_hot_unadapted(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_REAL_GDP_LEVEL_INDEX_HOT_UNADAPTED:
        record = dict(static_record)
        try:
            record[measure_field] = scenario_real_gdp_level_index_hot_unadapted(ctx, time_period=static_record['TIME_PERIOD'])
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_fiscal_consolidation_gap_milestones_2050(ctx=None, *, inputs=None) -> Records:
    """Returns fiscal consolidation gap milestones for 2050 across climate scenarios.

    Returns the primary balance gap (as percent of GDP) needed to stabilize debt in 2050 under each climate scenario.
    Each record maps a climate scenario and the year 2050 to the corresponding primary balance gap value retrieved from the Output Scenarios worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: The climate scenario (e.g., Paris, Moderate, High, Hot, Hot Adapted, Hot Un-Adapted).
                - TIME_PERIOD: The projection year (2050) for which the fiscal gap is reported.
                - OBS_VALUE: The primary balance gap required to stabilize debt, expressed as a percentage of GDP.
            Optional record fields:
                - UNIT_MEASURE: The unit of measure, indicating that the observation value is a percentage of GDP. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Output Scenarios!H26:H31
        Layout: matrix
        Value type: float

    Examples:
        compute_scenario_fiscal_consolidation_gap_milestones_2050(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2050:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_fiscal_consolidation_gap_milestones_2075(ctx=None, *, inputs=None) -> Records:
    """Retrieve the primary balance gap milestone for 2075 across climate scenarios.

    Returns the computed primary balance gap (as percent of GDP) for the year 2075 under each climate scenario, indicating the fiscal adjustment needed to stabilize debt.
    Each record corresponds to a climate scenario row in the Output Scenarios sheet, with the OBS_VALUE taken from the 2075 column.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: The climate scenario identifier.
                - TIME_PERIOD: The projection year.
                - OBS_VALUE: The primary balance gap as a percentage of GDP; the difference between the projected primary balance and the debt-stabilizing primary balance.
            Optional record fields:
                - UNIT_MEASURE: The unit of measurement for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Output Scenarios!K26:K31
        Layout: matrix
        Value type: float

    Examples:
        compute_scenario_fiscal_consolidation_gap_milestones_2075(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2075:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records

def compute_scenario_fiscal_consolidation_gap_milestones_2099(ctx=None, *, inputs=None) -> Records:
    """Compute the primary balance gap required to stabilize debt at target milestones for 2099 under each climate scenario.

    Returns the debt-stabilizing primary balance gap as a percent of GDP for the year 2099 across climate scenarios.
    Each record corresponds to a climate scenario row and the 2099 column in the Output Scenarios worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: Climate scenario name.
                - TIME_PERIOD: Year of the projection milestone.
                - OBS_VALUE: Primary balance gap as a percent of GDP needed to stabilize debt at the target.
            Optional record fields:
                - UNIT_MEASURE: Unit of measure for the observation value. If supplied, expected value: "PC_GDP".

    Source binding:
        Workbook range: Output Scenarios!N26:N31
        Layout: matrix
        Value type: float

    Examples:
        compute_scenario_fiscal_consolidation_gap_milestones_2099(ctx=ctx)
    """
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn("inputs will be ignored because ctx was provided", UserWarning, stacklevel=2)
    measure_field = 'OBS_VALUE'
    include_address = False
    records: Records = []
    for address, static_record in _OUTPUT_LEAVES_SCENARIO_FISCAL_CONSOLIDATION_GAP_MILESTONES_2099:
        record = dict(static_record)
        try:
            record[measure_field] = xl_cell(ctx, address)
        except XlErrorException as err:
            record[measure_field] = err.code
        if include_address:
            record["address"] = address
        records.append(record)
    return records


def list_setters() -> list[str]:
    """Return generated series-binding setter function names."""
    return ['set_country', 'set_demography_scenario', 'set_productivity_start', 'set_productivity_end', 'set_inflation_start', 'set_inflation_end', 'set_interest_rate_mode', 'set_real_interest_rate', 'set_fiscal_rule_enabled', 'set_debt_target', 'set_expenditure_rigidity', 'set_discrete_revenue_shocks', 'set_discrete_primary_expenditure_shocks']


def list_readers() -> list[str]:
    """Return generated series-binding reader function names."""
    return ['read_country', 'read_demography_scenario', 'read_productivity_start', 'read_productivity_end', 'read_inflation_start', 'read_inflation_end', 'read_interest_rate_mode', 'read_real_interest_rate', 'read_fiscal_rule_enabled', 'read_debt_target', 'read_expenditure_rigidity', 'read_discrete_revenue_shocks', 'read_discrete_primary_expenditure_shocks', 'read_baseline_debt_direction_above_sentinel', 'read_baseline_debt_direction_below_sentinel', 'read_demography_variant_label_medium', 'read_demography_variant_label_high', 'read_demography_variant_label_low', 'read_productivity_convergence_logistic_steepness', 'read_productivity_convergence_logistic_midpoint', 'read_productivity_convergence_period_index', 'read_inflation_convergence_logistic_steepness', 'read_inflation_convergence_logistic_midpoint', 'read_inflation_convergence_period_index', 'read_interest_rate_assumption_label_nominal', 'read_interest_rate_assumption_label_differential', 'read_interest_rate_assumption_label_real']


def list_computes() -> list[str]:
    """Return generated series-binding compute function names."""
    return ['compute_baseline_primary_expenditure_pct_gdp', 'compute_baseline_interest_expenditure_pct_gdp', 'compute_baseline_interest_rate', 'compute_baseline_primary_balance_pct_gdp', 'compute_baseline_overall_balance_pct_gdp', 'compute_baseline_debt_to_gdp', 'compute_baseline_debt_stabilizing_primary_balance', 'compute_baseline_fiscal_consolidation_gap', 'compute_baseline_nominal_gdp_growth', 'compute_baseline_real_gdp_growth', 'compute_baseline_revenue_pct_gdp', 'compute_baseline_employment_growth', 'compute_baseline_labour_productivity_growth', 'compute_baseline_gdp_deflator_growth', 'compute_baseline_population_growth', 'compute_scenario_primary_balance_pct_gdp', 'compute_scenario_overall_balance_pct_gdp', 'compute_scenario_debt_to_gdp', 'compute_scenario_debt_stabilizing_primary_balance_paris', 'compute_scenario_debt_stabilizing_primary_balance_moderate', 'compute_scenario_debt_stabilizing_primary_balance_high', 'compute_scenario_debt_stabilizing_primary_balance_hot', 'compute_scenario_debt_stabilizing_primary_balance_hot_adapted', 'compute_scenario_debt_stabilizing_primary_balance_hot_unadapted', 'compute_scenario_nominal_gdp_growth_paris', 'compute_scenario_nominal_gdp_growth_moderate', 'compute_scenario_nominal_gdp_growth_high', 'compute_scenario_nominal_gdp_growth_hot', 'compute_scenario_nominal_gdp_growth_hot_adapted', 'compute_scenario_nominal_gdp_growth_hot_unadapted', 'compute_scenario_primary_expenditure_pct_gdp_paris', 'compute_scenario_primary_expenditure_pct_gdp_moderate', 'compute_scenario_primary_expenditure_pct_gdp_high', 'compute_scenario_primary_expenditure_pct_gdp_hot', 'compute_scenario_primary_expenditure_pct_gdp_hot_adapted', 'compute_scenario_primary_expenditure_pct_gdp_hot_unadapted', 'compute_scenario_interest_expenditure_pct_gdp_paris', 'compute_scenario_interest_expenditure_pct_gdp_moderate', 'compute_scenario_interest_expenditure_pct_gdp_high', 'compute_scenario_interest_expenditure_pct_gdp_hot', 'compute_scenario_interest_expenditure_pct_gdp_hot_adapted', 'compute_scenario_interest_expenditure_pct_gdp_hot_unadapted', 'compute_scenario_real_gdp_level_index_paris', 'compute_scenario_real_gdp_level_index_moderate', 'compute_scenario_real_gdp_level_index_high', 'compute_scenario_real_gdp_level_index_hot', 'compute_scenario_real_gdp_level_index_hot_adapted', 'compute_scenario_real_gdp_level_index_hot_unadapted', 'compute_scenario_fiscal_consolidation_gap_milestones_2050', 'compute_scenario_fiscal_consolidation_gap_milestones_2075', 'compute_scenario_fiscal_consolidation_gap_milestones_2099']


def list_reader_leaves() -> dict[str, dict[str, object]]:
    """Return address → semantic reader call metadata."""
    return {"'Discrete Risks'!AA10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2054)"}, "'Discrete Risks'!AA11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2054)"}, "'Discrete Risks'!AA12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2054)"}, "'Discrete Risks'!AA13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2054)"}, "'Discrete Risks'!AA2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Paris', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2054)"}, "'Discrete Risks'!AA3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Paris', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2054)"}, "'Discrete Risks'!AA4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2054)"}, "'Discrete Risks'!AA5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2054)"}, "'Discrete Risks'!AA6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'High', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2054)"}, "'Discrete Risks'!AA7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'High', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2054)"}, "'Discrete Risks'!AA8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Hot', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2054)"}, "'Discrete Risks'!AA9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2054}, 'kwargs': {'scenario': 'Hot', 'time_period': 2054}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2054)"}, "'Discrete Risks'!AB10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2055)"}, "'Discrete Risks'!AB11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2055)"}, "'Discrete Risks'!AB12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2055)"}, "'Discrete Risks'!AB13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2055)"}, "'Discrete Risks'!AB2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Paris', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2055)"}, "'Discrete Risks'!AB3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Paris', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2055)"}, "'Discrete Risks'!AB4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2055)"}, "'Discrete Risks'!AB5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2055)"}, "'Discrete Risks'!AB6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'High', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2055)"}, "'Discrete Risks'!AB7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'High', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2055)"}, "'Discrete Risks'!AB8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Hot', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2055)"}, "'Discrete Risks'!AB9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2055}, 'kwargs': {'scenario': 'Hot', 'time_period': 2055}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2055)"}, "'Discrete Risks'!AC10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2056)"}, "'Discrete Risks'!AC11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2056)"}, "'Discrete Risks'!AC12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2056)"}, "'Discrete Risks'!AC13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2056)"}, "'Discrete Risks'!AC2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Paris', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2056)"}, "'Discrete Risks'!AC3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Paris', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2056)"}, "'Discrete Risks'!AC4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2056)"}, "'Discrete Risks'!AC5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2056)"}, "'Discrete Risks'!AC6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'High', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2056)"}, "'Discrete Risks'!AC7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'High', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2056)"}, "'Discrete Risks'!AC8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Hot', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2056)"}, "'Discrete Risks'!AC9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2056}, 'kwargs': {'scenario': 'Hot', 'time_period': 2056}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2056)"}, "'Discrete Risks'!AD10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2057)"}, "'Discrete Risks'!AD11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2057)"}, "'Discrete Risks'!AD12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2057)"}, "'Discrete Risks'!AD13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2057)"}, "'Discrete Risks'!AD2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Paris', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2057)"}, "'Discrete Risks'!AD3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Paris', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2057)"}, "'Discrete Risks'!AD4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2057)"}, "'Discrete Risks'!AD5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2057)"}, "'Discrete Risks'!AD6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'High', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2057)"}, "'Discrete Risks'!AD7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'High', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2057)"}, "'Discrete Risks'!AD8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Hot', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2057)"}, "'Discrete Risks'!AD9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2057}, 'kwargs': {'scenario': 'Hot', 'time_period': 2057}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2057)"}, "'Discrete Risks'!AE10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2058)"}, "'Discrete Risks'!AE11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2058)"}, "'Discrete Risks'!AE12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2058)"}, "'Discrete Risks'!AE13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2058)"}, "'Discrete Risks'!AE2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Paris', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2058)"}, "'Discrete Risks'!AE3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Paris', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2058)"}, "'Discrete Risks'!AE4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2058)"}, "'Discrete Risks'!AE5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2058)"}, "'Discrete Risks'!AE6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'High', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2058)"}, "'Discrete Risks'!AE7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'High', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2058)"}, "'Discrete Risks'!AE8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Hot', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2058)"}, "'Discrete Risks'!AE9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2058}, 'kwargs': {'scenario': 'Hot', 'time_period': 2058}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2058)"}, "'Discrete Risks'!AF10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2059)"}, "'Discrete Risks'!AF11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2059)"}, "'Discrete Risks'!AF12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2059)"}, "'Discrete Risks'!AF13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2059)"}, "'Discrete Risks'!AF2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Paris', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2059)"}, "'Discrete Risks'!AF3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Paris', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2059)"}, "'Discrete Risks'!AF4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2059)"}, "'Discrete Risks'!AF5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2059)"}, "'Discrete Risks'!AF6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'High', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2059)"}, "'Discrete Risks'!AF7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'High', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2059)"}, "'Discrete Risks'!AF8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Hot', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2059)"}, "'Discrete Risks'!AF9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2059}, 'kwargs': {'scenario': 'Hot', 'time_period': 2059}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2059)"}, "'Discrete Risks'!AG10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2060)"}, "'Discrete Risks'!AG11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2060)"}, "'Discrete Risks'!AG12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2060)"}, "'Discrete Risks'!AG13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2060)"}, "'Discrete Risks'!AG2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Paris', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2060)"}, "'Discrete Risks'!AG3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Paris', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2060)"}, "'Discrete Risks'!AG4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2060)"}, "'Discrete Risks'!AG5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2060)"}, "'Discrete Risks'!AG6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'High', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2060)"}, "'Discrete Risks'!AG7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'High', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2060)"}, "'Discrete Risks'!AG8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Hot', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2060)"}, "'Discrete Risks'!AG9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2060}, 'kwargs': {'scenario': 'Hot', 'time_period': 2060}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2060)"}, "'Discrete Risks'!AH10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2061)"}, "'Discrete Risks'!AH11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2061)"}, "'Discrete Risks'!AH12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2061)"}, "'Discrete Risks'!AH13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2061)"}, "'Discrete Risks'!AH2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Paris', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2061)"}, "'Discrete Risks'!AH3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Paris', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2061)"}, "'Discrete Risks'!AH4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2061)"}, "'Discrete Risks'!AH5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2061)"}, "'Discrete Risks'!AH6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'High', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2061)"}, "'Discrete Risks'!AH7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'High', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2061)"}, "'Discrete Risks'!AH8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Hot', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2061)"}, "'Discrete Risks'!AH9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2061}, 'kwargs': {'scenario': 'Hot', 'time_period': 2061}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2061)"}, "'Discrete Risks'!AI10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2062)"}, "'Discrete Risks'!AI11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2062)"}, "'Discrete Risks'!AI12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2062)"}, "'Discrete Risks'!AI13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2062)"}, "'Discrete Risks'!AI2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Paris', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2062)"}, "'Discrete Risks'!AI3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Paris', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2062)"}, "'Discrete Risks'!AI4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2062)"}, "'Discrete Risks'!AI5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2062)"}, "'Discrete Risks'!AI6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'High', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2062)"}, "'Discrete Risks'!AI7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'High', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2062)"}, "'Discrete Risks'!AI8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Hot', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2062)"}, "'Discrete Risks'!AI9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2062}, 'kwargs': {'scenario': 'Hot', 'time_period': 2062}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2062)"}, "'Discrete Risks'!AJ10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2063)"}, "'Discrete Risks'!AJ11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2063)"}, "'Discrete Risks'!AJ12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2063)"}, "'Discrete Risks'!AJ13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2063)"}, "'Discrete Risks'!AJ2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Paris', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2063)"}, "'Discrete Risks'!AJ3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Paris', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2063)"}, "'Discrete Risks'!AJ4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2063)"}, "'Discrete Risks'!AJ5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2063)"}, "'Discrete Risks'!AJ6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'High', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2063)"}, "'Discrete Risks'!AJ7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'High', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2063)"}, "'Discrete Risks'!AJ8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Hot', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2063)"}, "'Discrete Risks'!AJ9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2063}, 'kwargs': {'scenario': 'Hot', 'time_period': 2063}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2063)"}, "'Discrete Risks'!AK10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2064)"}, "'Discrete Risks'!AK11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2064)"}, "'Discrete Risks'!AK12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2064)"}, "'Discrete Risks'!AK13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2064)"}, "'Discrete Risks'!AK2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Paris', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2064)"}, "'Discrete Risks'!AK3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Paris', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2064)"}, "'Discrete Risks'!AK4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2064)"}, "'Discrete Risks'!AK5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2064)"}, "'Discrete Risks'!AK6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'High', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2064)"}, "'Discrete Risks'!AK7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'High', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2064)"}, "'Discrete Risks'!AK8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Hot', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2064)"}, "'Discrete Risks'!AK9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2064}, 'kwargs': {'scenario': 'Hot', 'time_period': 2064}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2064)"}, "'Discrete Risks'!AL10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2065)"}, "'Discrete Risks'!AL11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2065)"}, "'Discrete Risks'!AL12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2065)"}, "'Discrete Risks'!AL13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2065)"}, "'Discrete Risks'!AL2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Paris', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2065)"}, "'Discrete Risks'!AL3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Paris', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2065)"}, "'Discrete Risks'!AL4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2065)"}, "'Discrete Risks'!AL5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2065)"}, "'Discrete Risks'!AL6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'High', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2065)"}, "'Discrete Risks'!AL7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'High', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2065)"}, "'Discrete Risks'!AL8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Hot', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2065)"}, "'Discrete Risks'!AL9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2065}, 'kwargs': {'scenario': 'Hot', 'time_period': 2065}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2065)"}, "'Discrete Risks'!AM10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2066)"}, "'Discrete Risks'!AM11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2066)"}, "'Discrete Risks'!AM12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2066)"}, "'Discrete Risks'!AM13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2066)"}, "'Discrete Risks'!AM2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Paris', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2066)"}, "'Discrete Risks'!AM3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Paris', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2066)"}, "'Discrete Risks'!AM4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2066)"}, "'Discrete Risks'!AM5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2066)"}, "'Discrete Risks'!AM6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'High', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2066)"}, "'Discrete Risks'!AM7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'High', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2066)"}, "'Discrete Risks'!AM8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Hot', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2066)"}, "'Discrete Risks'!AM9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2066}, 'kwargs': {'scenario': 'Hot', 'time_period': 2066}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2066)"}, "'Discrete Risks'!AN10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2067)"}, "'Discrete Risks'!AN11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2067)"}, "'Discrete Risks'!AN12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2067)"}, "'Discrete Risks'!AN13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2067)"}, "'Discrete Risks'!AN2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Paris', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2067)"}, "'Discrete Risks'!AN3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Paris', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2067)"}, "'Discrete Risks'!AN4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2067)"}, "'Discrete Risks'!AN5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2067)"}, "'Discrete Risks'!AN6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'High', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2067)"}, "'Discrete Risks'!AN7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'High', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2067)"}, "'Discrete Risks'!AN8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Hot', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2067)"}, "'Discrete Risks'!AN9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2067}, 'kwargs': {'scenario': 'Hot', 'time_period': 2067}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2067)"}, "'Discrete Risks'!AO10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2068)"}, "'Discrete Risks'!AO11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2068)"}, "'Discrete Risks'!AO12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2068)"}, "'Discrete Risks'!AO13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2068)"}, "'Discrete Risks'!AO2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Paris', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2068)"}, "'Discrete Risks'!AO3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Paris', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2068)"}, "'Discrete Risks'!AO4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2068)"}, "'Discrete Risks'!AO5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2068)"}, "'Discrete Risks'!AO6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'High', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2068)"}, "'Discrete Risks'!AO7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'High', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2068)"}, "'Discrete Risks'!AO8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Hot', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2068)"}, "'Discrete Risks'!AO9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2068}, 'kwargs': {'scenario': 'Hot', 'time_period': 2068}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2068)"}, "'Discrete Risks'!AP10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2069)"}, "'Discrete Risks'!AP11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2069)"}, "'Discrete Risks'!AP12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2069)"}, "'Discrete Risks'!AP13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2069)"}, "'Discrete Risks'!AP2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Paris', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2069)"}, "'Discrete Risks'!AP3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Paris', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2069)"}, "'Discrete Risks'!AP4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2069)"}, "'Discrete Risks'!AP5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2069)"}, "'Discrete Risks'!AP6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'High', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2069)"}, "'Discrete Risks'!AP7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'High', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2069)"}, "'Discrete Risks'!AP8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Hot', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2069)"}, "'Discrete Risks'!AP9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2069}, 'kwargs': {'scenario': 'Hot', 'time_period': 2069}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2069)"}, "'Discrete Risks'!AQ10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2070)"}, "'Discrete Risks'!AQ11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2070)"}, "'Discrete Risks'!AQ12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2070)"}, "'Discrete Risks'!AQ13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2070)"}, "'Discrete Risks'!AQ2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Paris', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2070)"}, "'Discrete Risks'!AQ3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Paris', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2070)"}, "'Discrete Risks'!AQ4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2070)"}, "'Discrete Risks'!AQ5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2070)"}, "'Discrete Risks'!AQ6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'High', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2070)"}, "'Discrete Risks'!AQ7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'High', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2070)"}, "'Discrete Risks'!AQ8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Hot', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2070)"}, "'Discrete Risks'!AQ9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2070}, 'kwargs': {'scenario': 'Hot', 'time_period': 2070}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2070)"}, "'Discrete Risks'!AR10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2071)"}, "'Discrete Risks'!AR11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2071)"}, "'Discrete Risks'!AR12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2071)"}, "'Discrete Risks'!AR13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2071)"}, "'Discrete Risks'!AR2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Paris', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2071)"}, "'Discrete Risks'!AR3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Paris', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2071)"}, "'Discrete Risks'!AR4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2071)"}, "'Discrete Risks'!AR5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2071)"}, "'Discrete Risks'!AR6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'High', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2071)"}, "'Discrete Risks'!AR7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'High', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2071)"}, "'Discrete Risks'!AR8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Hot', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2071)"}, "'Discrete Risks'!AR9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2071}, 'kwargs': {'scenario': 'Hot', 'time_period': 2071}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2071)"}, "'Discrete Risks'!AS10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2072)"}, "'Discrete Risks'!AS11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2072)"}, "'Discrete Risks'!AS12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2072)"}, "'Discrete Risks'!AS13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2072)"}, "'Discrete Risks'!AS2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Paris', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2072)"}, "'Discrete Risks'!AS3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Paris', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2072)"}, "'Discrete Risks'!AS4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2072)"}, "'Discrete Risks'!AS5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2072)"}, "'Discrete Risks'!AS6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'High', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2072)"}, "'Discrete Risks'!AS7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'High', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2072)"}, "'Discrete Risks'!AS8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Hot', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2072)"}, "'Discrete Risks'!AS9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2072}, 'kwargs': {'scenario': 'Hot', 'time_period': 2072}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2072)"}, "'Discrete Risks'!AT10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2073)"}, "'Discrete Risks'!AT11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2073)"}, "'Discrete Risks'!AT12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2073)"}, "'Discrete Risks'!AT13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2073)"}, "'Discrete Risks'!AT2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Paris', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2073)"}, "'Discrete Risks'!AT3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Paris', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2073)"}, "'Discrete Risks'!AT4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2073)"}, "'Discrete Risks'!AT5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2073)"}, "'Discrete Risks'!AT6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'High', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2073)"}, "'Discrete Risks'!AT7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'High', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2073)"}, "'Discrete Risks'!AT8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Hot', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2073)"}, "'Discrete Risks'!AT9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2073}, 'kwargs': {'scenario': 'Hot', 'time_period': 2073}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2073)"}, "'Discrete Risks'!AU10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2074)"}, "'Discrete Risks'!AU11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2074)"}, "'Discrete Risks'!AU12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2074)"}, "'Discrete Risks'!AU13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2074)"}, "'Discrete Risks'!AU2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Paris', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2074)"}, "'Discrete Risks'!AU3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Paris', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2074)"}, "'Discrete Risks'!AU4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2074)"}, "'Discrete Risks'!AU5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2074)"}, "'Discrete Risks'!AU6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'High', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2074)"}, "'Discrete Risks'!AU7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'High', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2074)"}, "'Discrete Risks'!AU8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Hot', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2074)"}, "'Discrete Risks'!AU9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2074}, 'kwargs': {'scenario': 'Hot', 'time_period': 2074}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2074)"}, "'Discrete Risks'!AV10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2075)"}, "'Discrete Risks'!AV11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2075)"}, "'Discrete Risks'!AV12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2075)"}, "'Discrete Risks'!AV13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2075)"}, "'Discrete Risks'!AV2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Paris', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2075)"}, "'Discrete Risks'!AV3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Paris', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2075)"}, "'Discrete Risks'!AV4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2075)"}, "'Discrete Risks'!AV5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2075)"}, "'Discrete Risks'!AV6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'High', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2075)"}, "'Discrete Risks'!AV7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'High', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2075)"}, "'Discrete Risks'!AV8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Hot', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2075)"}, "'Discrete Risks'!AV9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2075}, 'kwargs': {'scenario': 'Hot', 'time_period': 2075}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2075)"}, "'Discrete Risks'!AW10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2076)"}, "'Discrete Risks'!AW11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2076)"}, "'Discrete Risks'!AW12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2076)"}, "'Discrete Risks'!AW13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2076)"}, "'Discrete Risks'!AW2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Paris', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2076)"}, "'Discrete Risks'!AW3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Paris', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2076)"}, "'Discrete Risks'!AW4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2076)"}, "'Discrete Risks'!AW5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2076)"}, "'Discrete Risks'!AW6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'High', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2076)"}, "'Discrete Risks'!AW7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'High', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2076)"}, "'Discrete Risks'!AW8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Hot', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2076)"}, "'Discrete Risks'!AW9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2076}, 'kwargs': {'scenario': 'Hot', 'time_period': 2076}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2076)"}, "'Discrete Risks'!AX10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2077)"}, "'Discrete Risks'!AX11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2077)"}, "'Discrete Risks'!AX12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2077)"}, "'Discrete Risks'!AX13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2077)"}, "'Discrete Risks'!AX2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Paris', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2077)"}, "'Discrete Risks'!AX3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Paris', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2077)"}, "'Discrete Risks'!AX4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2077)"}, "'Discrete Risks'!AX5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2077)"}, "'Discrete Risks'!AX6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'High', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2077)"}, "'Discrete Risks'!AX7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'High', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2077)"}, "'Discrete Risks'!AX8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Hot', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2077)"}, "'Discrete Risks'!AX9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2077}, 'kwargs': {'scenario': 'Hot', 'time_period': 2077}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2077)"}, "'Discrete Risks'!AY10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2078)"}, "'Discrete Risks'!AY11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2078)"}, "'Discrete Risks'!AY12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2078)"}, "'Discrete Risks'!AY13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2078)"}, "'Discrete Risks'!AY2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Paris', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2078)"}, "'Discrete Risks'!AY3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Paris', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2078)"}, "'Discrete Risks'!AY4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2078)"}, "'Discrete Risks'!AY5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2078)"}, "'Discrete Risks'!AY6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'High', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2078)"}, "'Discrete Risks'!AY7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'High', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2078)"}, "'Discrete Risks'!AY8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Hot', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2078)"}, "'Discrete Risks'!AY9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2078}, 'kwargs': {'scenario': 'Hot', 'time_period': 2078}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2078)"}, "'Discrete Risks'!AZ10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2079)"}, "'Discrete Risks'!AZ11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2079)"}, "'Discrete Risks'!AZ12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2079)"}, "'Discrete Risks'!AZ13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2079)"}, "'Discrete Risks'!AZ2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Paris', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2079)"}, "'Discrete Risks'!AZ3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Paris', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2079)"}, "'Discrete Risks'!AZ4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2079)"}, "'Discrete Risks'!AZ5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2079)"}, "'Discrete Risks'!AZ6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'High', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2079)"}, "'Discrete Risks'!AZ7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'High', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2079)"}, "'Discrete Risks'!AZ8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Hot', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2079)"}, "'Discrete Risks'!AZ9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2079}, 'kwargs': {'scenario': 'Hot', 'time_period': 2079}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2079)"}, "'Discrete Risks'!BA10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2080)"}, "'Discrete Risks'!BA11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2080)"}, "'Discrete Risks'!BA12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2080)"}, "'Discrete Risks'!BA13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2080)"}, "'Discrete Risks'!BA2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Paris', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2080)"}, "'Discrete Risks'!BA3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Paris', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2080)"}, "'Discrete Risks'!BA4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2080)"}, "'Discrete Risks'!BA5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2080)"}, "'Discrete Risks'!BA6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'High', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2080)"}, "'Discrete Risks'!BA7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'High', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2080)"}, "'Discrete Risks'!BA8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Hot', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2080)"}, "'Discrete Risks'!BA9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2080}, 'kwargs': {'scenario': 'Hot', 'time_period': 2080}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2080)"}, "'Discrete Risks'!BB10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2081)"}, "'Discrete Risks'!BB11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2081)"}, "'Discrete Risks'!BB12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2081)"}, "'Discrete Risks'!BB13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2081)"}, "'Discrete Risks'!BB2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Paris', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2081)"}, "'Discrete Risks'!BB3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Paris', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2081)"}, "'Discrete Risks'!BB4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2081)"}, "'Discrete Risks'!BB5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2081)"}, "'Discrete Risks'!BB6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'High', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2081)"}, "'Discrete Risks'!BB7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'High', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2081)"}, "'Discrete Risks'!BB8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Hot', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2081)"}, "'Discrete Risks'!BB9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2081}, 'kwargs': {'scenario': 'Hot', 'time_period': 2081}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2081)"}, "'Discrete Risks'!BC10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2082)"}, "'Discrete Risks'!BC11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2082)"}, "'Discrete Risks'!BC12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2082)"}, "'Discrete Risks'!BC13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2082)"}, "'Discrete Risks'!BC2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Paris', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2082)"}, "'Discrete Risks'!BC3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Paris', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2082)"}, "'Discrete Risks'!BC4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2082)"}, "'Discrete Risks'!BC5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2082)"}, "'Discrete Risks'!BC6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'High', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2082)"}, "'Discrete Risks'!BC7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'High', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2082)"}, "'Discrete Risks'!BC8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Hot', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2082)"}, "'Discrete Risks'!BC9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2082}, 'kwargs': {'scenario': 'Hot', 'time_period': 2082}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2082)"}, "'Discrete Risks'!BD10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2083)"}, "'Discrete Risks'!BD11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2083)"}, "'Discrete Risks'!BD12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2083)"}, "'Discrete Risks'!BD13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2083)"}, "'Discrete Risks'!BD2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Paris', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2083)"}, "'Discrete Risks'!BD3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Paris', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2083)"}, "'Discrete Risks'!BD4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2083)"}, "'Discrete Risks'!BD5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2083)"}, "'Discrete Risks'!BD6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'High', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2083)"}, "'Discrete Risks'!BD7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'High', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2083)"}, "'Discrete Risks'!BD8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Hot', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2083)"}, "'Discrete Risks'!BD9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2083}, 'kwargs': {'scenario': 'Hot', 'time_period': 2083}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2083)"}, "'Discrete Risks'!BE10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2084)"}, "'Discrete Risks'!BE11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2084)"}, "'Discrete Risks'!BE12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2084)"}, "'Discrete Risks'!BE13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2084)"}, "'Discrete Risks'!BE2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Paris', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2084)"}, "'Discrete Risks'!BE3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Paris', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2084)"}, "'Discrete Risks'!BE4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2084)"}, "'Discrete Risks'!BE5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2084)"}, "'Discrete Risks'!BE6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'High', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2084)"}, "'Discrete Risks'!BE7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'High', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2084)"}, "'Discrete Risks'!BE8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Hot', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2084)"}, "'Discrete Risks'!BE9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2084}, 'kwargs': {'scenario': 'Hot', 'time_period': 2084}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2084)"}, "'Discrete Risks'!BF10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2085)"}, "'Discrete Risks'!BF11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2085)"}, "'Discrete Risks'!BF12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2085)"}, "'Discrete Risks'!BF13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2085)"}, "'Discrete Risks'!BF2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Paris', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2085)"}, "'Discrete Risks'!BF3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Paris', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2085)"}, "'Discrete Risks'!BF4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2085)"}, "'Discrete Risks'!BF5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2085)"}, "'Discrete Risks'!BF6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'High', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2085)"}, "'Discrete Risks'!BF7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'High', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2085)"}, "'Discrete Risks'!BF8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Hot', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2085)"}, "'Discrete Risks'!BF9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2085}, 'kwargs': {'scenario': 'Hot', 'time_period': 2085}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2085)"}, "'Discrete Risks'!BG10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2086)"}, "'Discrete Risks'!BG11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2086)"}, "'Discrete Risks'!BG12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2086)"}, "'Discrete Risks'!BG13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2086)"}, "'Discrete Risks'!BG2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Paris', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2086)"}, "'Discrete Risks'!BG3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Paris', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2086)"}, "'Discrete Risks'!BG4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2086)"}, "'Discrete Risks'!BG5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2086)"}, "'Discrete Risks'!BG6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'High', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2086)"}, "'Discrete Risks'!BG7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'High', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2086)"}, "'Discrete Risks'!BG8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Hot', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2086)"}, "'Discrete Risks'!BG9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2086}, 'kwargs': {'scenario': 'Hot', 'time_period': 2086}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2086)"}, "'Discrete Risks'!BH10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2087)"}, "'Discrete Risks'!BH11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2087)"}, "'Discrete Risks'!BH12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2087)"}, "'Discrete Risks'!BH13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2087)"}, "'Discrete Risks'!BH2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Paris', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2087)"}, "'Discrete Risks'!BH3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Paris', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2087)"}, "'Discrete Risks'!BH4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2087)"}, "'Discrete Risks'!BH5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2087)"}, "'Discrete Risks'!BH6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'High', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2087)"}, "'Discrete Risks'!BH7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'High', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2087)"}, "'Discrete Risks'!BH8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Hot', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2087)"}, "'Discrete Risks'!BH9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2087}, 'kwargs': {'scenario': 'Hot', 'time_period': 2087}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2087)"}, "'Discrete Risks'!BI10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2088)"}, "'Discrete Risks'!BI11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2088)"}, "'Discrete Risks'!BI12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2088)"}, "'Discrete Risks'!BI13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2088)"}, "'Discrete Risks'!BI2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Paris', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2088)"}, "'Discrete Risks'!BI3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Paris', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2088)"}, "'Discrete Risks'!BI4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2088)"}, "'Discrete Risks'!BI5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2088)"}, "'Discrete Risks'!BI6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'High', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2088)"}, "'Discrete Risks'!BI7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'High', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2088)"}, "'Discrete Risks'!BI8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Hot', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2088)"}, "'Discrete Risks'!BI9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2088}, 'kwargs': {'scenario': 'Hot', 'time_period': 2088}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2088)"}, "'Discrete Risks'!BJ10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2089)"}, "'Discrete Risks'!BJ11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2089)"}, "'Discrete Risks'!BJ12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2089)"}, "'Discrete Risks'!BJ13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2089)"}, "'Discrete Risks'!BJ2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Paris', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2089)"}, "'Discrete Risks'!BJ3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Paris', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2089)"}, "'Discrete Risks'!BJ4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2089)"}, "'Discrete Risks'!BJ5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2089)"}, "'Discrete Risks'!BJ6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'High', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2089)"}, "'Discrete Risks'!BJ7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'High', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2089)"}, "'Discrete Risks'!BJ8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Hot', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2089)"}, "'Discrete Risks'!BJ9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2089}, 'kwargs': {'scenario': 'Hot', 'time_period': 2089}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2089)"}, "'Discrete Risks'!BK10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2090)"}, "'Discrete Risks'!BK11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2090)"}, "'Discrete Risks'!BK12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2090)"}, "'Discrete Risks'!BK13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2090)"}, "'Discrete Risks'!BK2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Paris', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2090)"}, "'Discrete Risks'!BK3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Paris', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2090)"}, "'Discrete Risks'!BK4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2090)"}, "'Discrete Risks'!BK5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2090)"}, "'Discrete Risks'!BK6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'High', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2090)"}, "'Discrete Risks'!BK7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'High', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2090)"}, "'Discrete Risks'!BK8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Hot', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2090)"}, "'Discrete Risks'!BK9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2090}, 'kwargs': {'scenario': 'Hot', 'time_period': 2090}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2090)"}, "'Discrete Risks'!BL10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2091)"}, "'Discrete Risks'!BL11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2091)"}, "'Discrete Risks'!BL12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2091)"}, "'Discrete Risks'!BL13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2091)"}, "'Discrete Risks'!BL2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Paris', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2091)"}, "'Discrete Risks'!BL3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Paris', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2091)"}, "'Discrete Risks'!BL4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2091)"}, "'Discrete Risks'!BL5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2091)"}, "'Discrete Risks'!BL6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'High', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2091)"}, "'Discrete Risks'!BL7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'High', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2091)"}, "'Discrete Risks'!BL8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Hot', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2091)"}, "'Discrete Risks'!BL9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2091}, 'kwargs': {'scenario': 'Hot', 'time_period': 2091}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2091)"}, "'Discrete Risks'!BM10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2092)"}, "'Discrete Risks'!BM11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2092)"}, "'Discrete Risks'!BM12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2092)"}, "'Discrete Risks'!BM13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2092)"}, "'Discrete Risks'!BM2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Paris', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2092)"}, "'Discrete Risks'!BM3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Paris', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2092)"}, "'Discrete Risks'!BM4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2092)"}, "'Discrete Risks'!BM5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2092)"}, "'Discrete Risks'!BM6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'High', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2092)"}, "'Discrete Risks'!BM7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'High', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2092)"}, "'Discrete Risks'!BM8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Hot', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2092)"}, "'Discrete Risks'!BM9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2092}, 'kwargs': {'scenario': 'Hot', 'time_period': 2092}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2092)"}, "'Discrete Risks'!BN10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2093)"}, "'Discrete Risks'!BN11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2093)"}, "'Discrete Risks'!BN12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2093)"}, "'Discrete Risks'!BN13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2093)"}, "'Discrete Risks'!BN2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Paris', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2093)"}, "'Discrete Risks'!BN3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Paris', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2093)"}, "'Discrete Risks'!BN4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2093)"}, "'Discrete Risks'!BN5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2093)"}, "'Discrete Risks'!BN6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'High', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2093)"}, "'Discrete Risks'!BN7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'High', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2093)"}, "'Discrete Risks'!BN8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Hot', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2093)"}, "'Discrete Risks'!BN9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2093}, 'kwargs': {'scenario': 'Hot', 'time_period': 2093}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2093)"}, "'Discrete Risks'!BO10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2094)"}, "'Discrete Risks'!BO11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2094)"}, "'Discrete Risks'!BO12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2094)"}, "'Discrete Risks'!BO13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2094)"}, "'Discrete Risks'!BO2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Paris', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2094)"}, "'Discrete Risks'!BO3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Paris', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2094)"}, "'Discrete Risks'!BO4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2094)"}, "'Discrete Risks'!BO5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2094)"}, "'Discrete Risks'!BO6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'High', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2094)"}, "'Discrete Risks'!BO7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'High', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2094)"}, "'Discrete Risks'!BO8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Hot', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2094)"}, "'Discrete Risks'!BO9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2094}, 'kwargs': {'scenario': 'Hot', 'time_period': 2094}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2094)"}, "'Discrete Risks'!BP10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2095)"}, "'Discrete Risks'!BP11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2095)"}, "'Discrete Risks'!BP12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2095)"}, "'Discrete Risks'!BP13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2095)"}, "'Discrete Risks'!BP2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Paris', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2095)"}, "'Discrete Risks'!BP3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Paris', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2095)"}, "'Discrete Risks'!BP4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2095)"}, "'Discrete Risks'!BP5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2095)"}, "'Discrete Risks'!BP6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'High', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2095)"}, "'Discrete Risks'!BP7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'High', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2095)"}, "'Discrete Risks'!BP8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Hot', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2095)"}, "'Discrete Risks'!BP9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2095}, 'kwargs': {'scenario': 'Hot', 'time_period': 2095}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2095)"}, "'Discrete Risks'!BQ10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2096)"}, "'Discrete Risks'!BQ11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2096)"}, "'Discrete Risks'!BQ12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2096)"}, "'Discrete Risks'!BQ13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2096)"}, "'Discrete Risks'!BQ2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Paris', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2096)"}, "'Discrete Risks'!BQ3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Paris', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2096)"}, "'Discrete Risks'!BQ4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2096)"}, "'Discrete Risks'!BQ5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2096)"}, "'Discrete Risks'!BQ6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'High', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2096)"}, "'Discrete Risks'!BQ7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'High', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2096)"}, "'Discrete Risks'!BQ8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Hot', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2096)"}, "'Discrete Risks'!BQ9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2096}, 'kwargs': {'scenario': 'Hot', 'time_period': 2096}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2096)"}, "'Discrete Risks'!BR10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2097)"}, "'Discrete Risks'!BR11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2097)"}, "'Discrete Risks'!BR12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2097)"}, "'Discrete Risks'!BR13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2097)"}, "'Discrete Risks'!BR2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Paris', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2097)"}, "'Discrete Risks'!BR3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Paris', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2097)"}, "'Discrete Risks'!BR4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2097)"}, "'Discrete Risks'!BR5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2097)"}, "'Discrete Risks'!BR6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'High', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2097)"}, "'Discrete Risks'!BR7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'High', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2097)"}, "'Discrete Risks'!BR8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Hot', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2097)"}, "'Discrete Risks'!BR9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2097}, 'kwargs': {'scenario': 'Hot', 'time_period': 2097}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2097)"}, "'Discrete Risks'!BS10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2098)"}, "'Discrete Risks'!BS11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2098)"}, "'Discrete Risks'!BS12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2098)"}, "'Discrete Risks'!BS13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2098)"}, "'Discrete Risks'!BS2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Paris', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2098)"}, "'Discrete Risks'!BS3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Paris', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2098)"}, "'Discrete Risks'!BS4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2098)"}, "'Discrete Risks'!BS5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2098)"}, "'Discrete Risks'!BS6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'High', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2098)"}, "'Discrete Risks'!BS7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'High', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2098)"}, "'Discrete Risks'!BS8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Hot', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2098)"}, "'Discrete Risks'!BS9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2098}, 'kwargs': {'scenario': 'Hot', 'time_period': 2098}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2098)"}, "'Discrete Risks'!BT10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2099)"}, "'Discrete Risks'!BT11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2099)"}, "'Discrete Risks'!BT12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2099)"}, "'Discrete Risks'!BT13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2099)"}, "'Discrete Risks'!BT2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Paris', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2099)"}, "'Discrete Risks'!BT3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Paris', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2099)"}, "'Discrete Risks'!BT4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2099)"}, "'Discrete Risks'!BT5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2099)"}, "'Discrete Risks'!BT6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'High', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2099)"}, "'Discrete Risks'!BT7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'High', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2099)"}, "'Discrete Risks'!BT8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Hot', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2099)"}, "'Discrete Risks'!BT9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2099}, 'kwargs': {'scenario': 'Hot', 'time_period': 2099}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2099)"}, "'Discrete Risks'!C10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2030)"}, "'Discrete Risks'!C11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2030)"}, "'Discrete Risks'!C12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2030)"}, "'Discrete Risks'!C13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2030)"}, "'Discrete Risks'!C2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Paris', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2030)"}, "'Discrete Risks'!C3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Paris', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2030)"}, "'Discrete Risks'!C4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2030)"}, "'Discrete Risks'!C5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2030)"}, "'Discrete Risks'!C6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'High', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2030)"}, "'Discrete Risks'!C7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'High', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2030)"}, "'Discrete Risks'!C8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Hot', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2030)"}, "'Discrete Risks'!C9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2030}, 'kwargs': {'scenario': 'Hot', 'time_period': 2030}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2030)"}, "'Discrete Risks'!D10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2031)"}, "'Discrete Risks'!D11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2031)"}, "'Discrete Risks'!D12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2031)"}, "'Discrete Risks'!D13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2031)"}, "'Discrete Risks'!D2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Paris', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2031)"}, "'Discrete Risks'!D3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Paris', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2031)"}, "'Discrete Risks'!D4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2031)"}, "'Discrete Risks'!D5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2031)"}, "'Discrete Risks'!D6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'High', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2031)"}, "'Discrete Risks'!D7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'High', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2031)"}, "'Discrete Risks'!D8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Hot', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2031)"}, "'Discrete Risks'!D9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2031}, 'kwargs': {'scenario': 'Hot', 'time_period': 2031}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2031)"}, "'Discrete Risks'!E10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2032)"}, "'Discrete Risks'!E11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2032)"}, "'Discrete Risks'!E12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2032)"}, "'Discrete Risks'!E13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2032)"}, "'Discrete Risks'!E2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Paris', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2032)"}, "'Discrete Risks'!E3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Paris', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2032)"}, "'Discrete Risks'!E4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2032)"}, "'Discrete Risks'!E5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2032)"}, "'Discrete Risks'!E6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'High', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2032)"}, "'Discrete Risks'!E7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'High', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2032)"}, "'Discrete Risks'!E8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Hot', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2032)"}, "'Discrete Risks'!E9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2032}, 'kwargs': {'scenario': 'Hot', 'time_period': 2032}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2032)"}, "'Discrete Risks'!F10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2033)"}, "'Discrete Risks'!F11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2033)"}, "'Discrete Risks'!F12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2033)"}, "'Discrete Risks'!F13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2033)"}, "'Discrete Risks'!F2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Paris', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2033)"}, "'Discrete Risks'!F3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Paris', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2033)"}, "'Discrete Risks'!F4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2033)"}, "'Discrete Risks'!F5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2033)"}, "'Discrete Risks'!F6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'High', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2033)"}, "'Discrete Risks'!F7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'High', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2033)"}, "'Discrete Risks'!F8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Hot', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2033)"}, "'Discrete Risks'!F9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2033}, 'kwargs': {'scenario': 'Hot', 'time_period': 2033}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2033)"}, "'Discrete Risks'!G10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2034)"}, "'Discrete Risks'!G11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2034)"}, "'Discrete Risks'!G12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2034)"}, "'Discrete Risks'!G13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2034)"}, "'Discrete Risks'!G2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Paris', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2034)"}, "'Discrete Risks'!G3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Paris', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2034)"}, "'Discrete Risks'!G4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2034)"}, "'Discrete Risks'!G5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2034)"}, "'Discrete Risks'!G6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'High', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2034)"}, "'Discrete Risks'!G7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'High', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2034)"}, "'Discrete Risks'!G8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Hot', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2034)"}, "'Discrete Risks'!G9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2034}, 'kwargs': {'scenario': 'Hot', 'time_period': 2034}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2034)"}, "'Discrete Risks'!H10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2035)"}, "'Discrete Risks'!H11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2035)"}, "'Discrete Risks'!H12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2035)"}, "'Discrete Risks'!H13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2035)"}, "'Discrete Risks'!H2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Paris', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2035)"}, "'Discrete Risks'!H3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Paris', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2035)"}, "'Discrete Risks'!H4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2035)"}, "'Discrete Risks'!H5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2035)"}, "'Discrete Risks'!H6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'High', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2035)"}, "'Discrete Risks'!H7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'High', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2035)"}, "'Discrete Risks'!H8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Hot', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2035)"}, "'Discrete Risks'!H9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2035}, 'kwargs': {'scenario': 'Hot', 'time_period': 2035}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2035)"}, "'Discrete Risks'!I10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2036)"}, "'Discrete Risks'!I11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2036)"}, "'Discrete Risks'!I12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2036)"}, "'Discrete Risks'!I13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2036)"}, "'Discrete Risks'!I2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Paris', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2036)"}, "'Discrete Risks'!I3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Paris', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2036)"}, "'Discrete Risks'!I4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2036)"}, "'Discrete Risks'!I5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2036)"}, "'Discrete Risks'!I6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'High', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2036)"}, "'Discrete Risks'!I7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'High', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2036)"}, "'Discrete Risks'!I8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Hot', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2036)"}, "'Discrete Risks'!I9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2036}, 'kwargs': {'scenario': 'Hot', 'time_period': 2036}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2036)"}, "'Discrete Risks'!J10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2037)"}, "'Discrete Risks'!J11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2037)"}, "'Discrete Risks'!J12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2037)"}, "'Discrete Risks'!J13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2037)"}, "'Discrete Risks'!J2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Paris', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2037)"}, "'Discrete Risks'!J3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Paris', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2037)"}, "'Discrete Risks'!J4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2037)"}, "'Discrete Risks'!J5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2037)"}, "'Discrete Risks'!J6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'High', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2037)"}, "'Discrete Risks'!J7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'High', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2037)"}, "'Discrete Risks'!J8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Hot', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2037)"}, "'Discrete Risks'!J9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2037}, 'kwargs': {'scenario': 'Hot', 'time_period': 2037}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2037)"}, "'Discrete Risks'!K10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2038)"}, "'Discrete Risks'!K11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2038)"}, "'Discrete Risks'!K12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2038)"}, "'Discrete Risks'!K13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2038)"}, "'Discrete Risks'!K2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Paris', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2038)"}, "'Discrete Risks'!K3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Paris', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2038)"}, "'Discrete Risks'!K4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2038)"}, "'Discrete Risks'!K5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2038)"}, "'Discrete Risks'!K6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'High', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2038)"}, "'Discrete Risks'!K7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'High', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2038)"}, "'Discrete Risks'!K8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Hot', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2038)"}, "'Discrete Risks'!K9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2038}, 'kwargs': {'scenario': 'Hot', 'time_period': 2038}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2038)"}, "'Discrete Risks'!L10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2039)"}, "'Discrete Risks'!L11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2039)"}, "'Discrete Risks'!L12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2039)"}, "'Discrete Risks'!L13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2039)"}, "'Discrete Risks'!L2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Paris', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2039)"}, "'Discrete Risks'!L3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Paris', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2039)"}, "'Discrete Risks'!L4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2039)"}, "'Discrete Risks'!L5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2039)"}, "'Discrete Risks'!L6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'High', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2039)"}, "'Discrete Risks'!L7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'High', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2039)"}, "'Discrete Risks'!L8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Hot', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2039)"}, "'Discrete Risks'!L9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2039}, 'kwargs': {'scenario': 'Hot', 'time_period': 2039}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2039)"}, "'Discrete Risks'!M10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2040)"}, "'Discrete Risks'!M11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2040)"}, "'Discrete Risks'!M12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2040)"}, "'Discrete Risks'!M13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2040)"}, "'Discrete Risks'!M2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Paris', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2040)"}, "'Discrete Risks'!M3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Paris', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2040)"}, "'Discrete Risks'!M4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2040)"}, "'Discrete Risks'!M5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2040)"}, "'Discrete Risks'!M6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'High', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2040)"}, "'Discrete Risks'!M7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'High', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2040)"}, "'Discrete Risks'!M8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Hot', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2040)"}, "'Discrete Risks'!M9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2040}, 'kwargs': {'scenario': 'Hot', 'time_period': 2040}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2040)"}, "'Discrete Risks'!N10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2041)"}, "'Discrete Risks'!N11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2041)"}, "'Discrete Risks'!N12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2041)"}, "'Discrete Risks'!N13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2041)"}, "'Discrete Risks'!N2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Paris', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2041)"}, "'Discrete Risks'!N3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Paris', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2041)"}, "'Discrete Risks'!N4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2041)"}, "'Discrete Risks'!N5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2041)"}, "'Discrete Risks'!N6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'High', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2041)"}, "'Discrete Risks'!N7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'High', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2041)"}, "'Discrete Risks'!N8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Hot', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2041)"}, "'Discrete Risks'!N9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2041}, 'kwargs': {'scenario': 'Hot', 'time_period': 2041}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2041)"}, "'Discrete Risks'!O10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2042)"}, "'Discrete Risks'!O11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2042)"}, "'Discrete Risks'!O12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2042)"}, "'Discrete Risks'!O13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2042)"}, "'Discrete Risks'!O2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Paris', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2042)"}, "'Discrete Risks'!O3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Paris', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2042)"}, "'Discrete Risks'!O4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2042)"}, "'Discrete Risks'!O5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2042)"}, "'Discrete Risks'!O6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'High', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2042)"}, "'Discrete Risks'!O7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'High', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2042)"}, "'Discrete Risks'!O8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Hot', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2042)"}, "'Discrete Risks'!O9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2042}, 'kwargs': {'scenario': 'Hot', 'time_period': 2042}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2042)"}, "'Discrete Risks'!P10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2043)"}, "'Discrete Risks'!P11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2043)"}, "'Discrete Risks'!P12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2043)"}, "'Discrete Risks'!P13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2043)"}, "'Discrete Risks'!P2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Paris', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2043)"}, "'Discrete Risks'!P3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Paris', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2043)"}, "'Discrete Risks'!P4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2043)"}, "'Discrete Risks'!P5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2043)"}, "'Discrete Risks'!P6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'High', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2043)"}, "'Discrete Risks'!P7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'High', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2043)"}, "'Discrete Risks'!P8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Hot', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2043)"}, "'Discrete Risks'!P9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2043}, 'kwargs': {'scenario': 'Hot', 'time_period': 2043}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2043)"}, "'Discrete Risks'!Q10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2044)"}, "'Discrete Risks'!Q11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2044)"}, "'Discrete Risks'!Q12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2044)"}, "'Discrete Risks'!Q13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2044)"}, "'Discrete Risks'!Q2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Paris', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2044)"}, "'Discrete Risks'!Q3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Paris', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2044)"}, "'Discrete Risks'!Q4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2044)"}, "'Discrete Risks'!Q5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2044)"}, "'Discrete Risks'!Q6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'High', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2044)"}, "'Discrete Risks'!Q7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'High', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2044)"}, "'Discrete Risks'!Q8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Hot', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2044)"}, "'Discrete Risks'!Q9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2044}, 'kwargs': {'scenario': 'Hot', 'time_period': 2044}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2044)"}, "'Discrete Risks'!R10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2045)"}, "'Discrete Risks'!R11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2045)"}, "'Discrete Risks'!R12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2045)"}, "'Discrete Risks'!R13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2045)"}, "'Discrete Risks'!R2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Paris', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2045)"}, "'Discrete Risks'!R3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Paris', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2045)"}, "'Discrete Risks'!R4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2045)"}, "'Discrete Risks'!R5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2045)"}, "'Discrete Risks'!R6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'High', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2045)"}, "'Discrete Risks'!R7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'High', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2045)"}, "'Discrete Risks'!R8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Hot', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2045)"}, "'Discrete Risks'!R9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2045}, 'kwargs': {'scenario': 'Hot', 'time_period': 2045}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2045)"}, "'Discrete Risks'!S10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2046)"}, "'Discrete Risks'!S11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2046)"}, "'Discrete Risks'!S12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2046)"}, "'Discrete Risks'!S13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2046)"}, "'Discrete Risks'!S2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Paris', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2046)"}, "'Discrete Risks'!S3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Paris', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2046)"}, "'Discrete Risks'!S4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2046)"}, "'Discrete Risks'!S5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2046)"}, "'Discrete Risks'!S6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'High', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2046)"}, "'Discrete Risks'!S7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'High', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2046)"}, "'Discrete Risks'!S8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Hot', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2046)"}, "'Discrete Risks'!S9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2046}, 'kwargs': {'scenario': 'Hot', 'time_period': 2046}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2046)"}, "'Discrete Risks'!T10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2047)"}, "'Discrete Risks'!T11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2047)"}, "'Discrete Risks'!T12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2047)"}, "'Discrete Risks'!T13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2047)"}, "'Discrete Risks'!T2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Paris', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2047)"}, "'Discrete Risks'!T3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Paris', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2047)"}, "'Discrete Risks'!T4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2047)"}, "'Discrete Risks'!T5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2047)"}, "'Discrete Risks'!T6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'High', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2047)"}, "'Discrete Risks'!T7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'High', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2047)"}, "'Discrete Risks'!T8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Hot', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2047)"}, "'Discrete Risks'!T9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2047}, 'kwargs': {'scenario': 'Hot', 'time_period': 2047}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2047)"}, "'Discrete Risks'!U10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2048)"}, "'Discrete Risks'!U11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2048)"}, "'Discrete Risks'!U12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2048)"}, "'Discrete Risks'!U13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2048)"}, "'Discrete Risks'!U2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Paris', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2048)"}, "'Discrete Risks'!U3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Paris', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2048)"}, "'Discrete Risks'!U4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2048)"}, "'Discrete Risks'!U5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2048)"}, "'Discrete Risks'!U6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'High', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2048)"}, "'Discrete Risks'!U7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'High', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2048)"}, "'Discrete Risks'!U8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Hot', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2048)"}, "'Discrete Risks'!U9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2048}, 'kwargs': {'scenario': 'Hot', 'time_period': 2048}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2048)"}, "'Discrete Risks'!V10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2049)"}, "'Discrete Risks'!V11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2049)"}, "'Discrete Risks'!V12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2049)"}, "'Discrete Risks'!V13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2049)"}, "'Discrete Risks'!V2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Paris', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2049)"}, "'Discrete Risks'!V3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Paris', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2049)"}, "'Discrete Risks'!V4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2049)"}, "'Discrete Risks'!V5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2049)"}, "'Discrete Risks'!V6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'High', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2049)"}, "'Discrete Risks'!V7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'High', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2049)"}, "'Discrete Risks'!V8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Hot', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2049)"}, "'Discrete Risks'!V9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2049}, 'kwargs': {'scenario': 'Hot', 'time_period': 2049}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2049)"}, "'Discrete Risks'!W10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2050)"}, "'Discrete Risks'!W11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2050)"}, "'Discrete Risks'!W12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2050)"}, "'Discrete Risks'!W13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2050)"}, "'Discrete Risks'!W2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Paris', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2050)"}, "'Discrete Risks'!W3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Paris', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2050)"}, "'Discrete Risks'!W4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2050)"}, "'Discrete Risks'!W5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2050)"}, "'Discrete Risks'!W6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'High', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2050)"}, "'Discrete Risks'!W7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'High', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2050)"}, "'Discrete Risks'!W8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Hot', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2050)"}, "'Discrete Risks'!W9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2050}, 'kwargs': {'scenario': 'Hot', 'time_period': 2050}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2050)"}, "'Discrete Risks'!X10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2051)"}, "'Discrete Risks'!X11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2051)"}, "'Discrete Risks'!X12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2051)"}, "'Discrete Risks'!X13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2051)"}, "'Discrete Risks'!X2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Paris', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2051)"}, "'Discrete Risks'!X3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Paris', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2051)"}, "'Discrete Risks'!X4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2051)"}, "'Discrete Risks'!X5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2051)"}, "'Discrete Risks'!X6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'High', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2051)"}, "'Discrete Risks'!X7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'High', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2051)"}, "'Discrete Risks'!X8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Hot', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2051)"}, "'Discrete Risks'!X9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2051}, 'kwargs': {'scenario': 'Hot', 'time_period': 2051}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2051)"}, "'Discrete Risks'!Y10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2052)"}, "'Discrete Risks'!Y11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2052)"}, "'Discrete Risks'!Y12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2052)"}, "'Discrete Risks'!Y13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2052)"}, "'Discrete Risks'!Y2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Paris', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2052)"}, "'Discrete Risks'!Y3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Paris', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2052)"}, "'Discrete Risks'!Y4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2052)"}, "'Discrete Risks'!Y5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2052)"}, "'Discrete Risks'!Y6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'High', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2052)"}, "'Discrete Risks'!Y7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'High', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2052)"}, "'Discrete Risks'!Y8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Hot', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2052)"}, "'Discrete Risks'!Y9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2052}, 'kwargs': {'scenario': 'Hot', 'time_period': 2052}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2052)"}, "'Discrete Risks'!Z10": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot adapted', time_period=2053)"}, "'Discrete Risks'!Z11": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot adapted', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Hot adapted', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot adapted', time_period=2053)"}, "'Discrete Risks'!Z12": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot unadapted', time_period=2053)"}, "'Discrete Risks'!Z13": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot unadapted', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Hot unadapted', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot unadapted', time_period=2053)"}, "'Discrete Risks'!Z2": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Paris', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Paris', time_period=2053)"}, "'Discrete Risks'!Z3": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Paris', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Paris', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Paris', time_period=2053)"}, "'Discrete Risks'!Z4": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Moderate', time_period=2053)"}, "'Discrete Risks'!Z5": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Moderate', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Moderate', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Moderate', time_period=2053)"}, "'Discrete Risks'!Z6": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'High', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='High', time_period=2053)"}, "'Discrete Risks'!Z7": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'High', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'High', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='High', time_period=2053)"}, "'Discrete Risks'!Z8": {'series_id': 'discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Hot', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_revenue_shocks(ctx, scenario='Hot', time_period=2053)"}, "'Discrete Risks'!Z9": {'series_id': 'discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'keys': {'SCENARIO': 'Hot', 'TIME_PERIOD': 2053}, 'kwargs': {'scenario': 'Hot', 'time_period': 2053}, 'kind': 'keyed', 'call_form': "read_discrete_primary_expenditure_shocks(ctx, scenario='Hot', time_period=2053)"}, "'Interest Rate'!A17": {'series_id': 'interest_rate_assumption_label_nominal', 'reader': 'read_interest_rate_assumption_label_nominal', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_interest_rate_assumption_label_nominal(ctx)'}, "'Interest Rate'!A18": {'series_id': 'interest_rate_assumption_label_differential', 'reader': 'read_interest_rate_assumption_label_differential', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_interest_rate_assumption_label_differential(ctx)'}, "'Interest Rate'!A19": {'series_id': 'interest_rate_assumption_label_real', 'reader': 'read_interest_rate_assumption_label_real', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_interest_rate_assumption_label_real(ctx)'}, 'Baseline!B47': {'series_id': 'baseline_debt_direction_above_sentinel', 'reader': 'read_baseline_debt_direction_above_sentinel', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_baseline_debt_direction_above_sentinel(ctx)'}, 'Baseline!B48': {'series_id': 'baseline_debt_direction_below_sentinel', 'reader': 'read_baseline_debt_direction_below_sentinel', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_baseline_debt_direction_below_sentinel(ctx)'}, 'Dashboard!C12': {'series_id': 'country', 'reader': 'read_country', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_country(ctx)'}, 'Dashboard!C17': {'series_id': 'demography_scenario', 'reader': 'read_demography_scenario', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_demography_scenario(ctx)'}, 'Dashboard!C20': {'series_id': 'productivity_start', 'reader': 'read_productivity_start', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_productivity_start(ctx)'}, 'Dashboard!C21': {'series_id': 'productivity_end', 'reader': 'read_productivity_end', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_productivity_end(ctx)'}, 'Dashboard!C24': {'series_id': 'inflation_start', 'reader': 'read_inflation_start', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_inflation_start(ctx)'}, 'Dashboard!C25': {'series_id': 'inflation_end', 'reader': 'read_inflation_end', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_inflation_end(ctx)'}, 'Dashboard!C28': {'series_id': 'interest_rate_mode', 'reader': 'read_interest_rate_mode', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_interest_rate_mode(ctx)'}, 'Dashboard!C29': {'series_id': 'real_interest_rate', 'reader': 'read_real_interest_rate', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_real_interest_rate(ctx)'}, 'Dashboard!C33': {'series_id': 'fiscal_rule_enabled', 'reader': 'read_fiscal_rule_enabled', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_fiscal_rule_enabled(ctx)'}, 'Dashboard!C34': {'series_id': 'debt_target', 'reader': 'read_debt_target', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_debt_target(ctx)'}, 'Dashboard!C38': {'series_id': 'expenditure_rigidity', 'reader': 'read_expenditure_rigidity', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_expenditure_rigidity(ctx)'}, 'Demography!B10': {'series_id': 'demography_variant_label_low', 'reader': 'read_demography_variant_label_low', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_demography_variant_label_low(ctx)'}, 'Demography!B8': {'series_id': 'demography_variant_label_medium', 'reader': 'read_demography_variant_label_medium', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_demography_variant_label_medium(ctx)'}, 'Demography!B9': {'series_id': 'demography_variant_label_high', 'reader': 'read_demography_variant_label_high', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_demography_variant_label_high(ctx)'}, 'Inflation!AA8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2027}, 'kwargs': {'time_period': 2027}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2027)'}, 'Inflation!AB8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2028}, 'kwargs': {'time_period': 2028}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2028)'}, 'Inflation!AC8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2029}, 'kwargs': {'time_period': 2029}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2029)'}, 'Inflation!AD8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2030}, 'kwargs': {'time_period': 2030}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2030)'}, 'Inflation!AE8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2031}, 'kwargs': {'time_period': 2031}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2031)'}, 'Inflation!AF8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2032}, 'kwargs': {'time_period': 2032}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2032)'}, 'Inflation!AG8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2033}, 'kwargs': {'time_period': 2033}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2033)'}, 'Inflation!AH8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2034}, 'kwargs': {'time_period': 2034}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2034)'}, 'Inflation!AI8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2035}, 'kwargs': {'time_period': 2035}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2035)'}, 'Inflation!AJ8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2036}, 'kwargs': {'time_period': 2036}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2036)'}, 'Inflation!AK8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2037}, 'kwargs': {'time_period': 2037}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2037)'}, 'Inflation!AL8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2038}, 'kwargs': {'time_period': 2038}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2038)'}, 'Inflation!AM8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2039}, 'kwargs': {'time_period': 2039}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2039)'}, 'Inflation!AN8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2040}, 'kwargs': {'time_period': 2040}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2040)'}, 'Inflation!AO8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2041}, 'kwargs': {'time_period': 2041}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2041)'}, 'Inflation!AP8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2042}, 'kwargs': {'time_period': 2042}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2042)'}, 'Inflation!AQ8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2043}, 'kwargs': {'time_period': 2043}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2043)'}, 'Inflation!AR8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2044}, 'kwargs': {'time_period': 2044}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2044)'}, 'Inflation!AS8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2045}, 'kwargs': {'time_period': 2045}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2045)'}, 'Inflation!AT8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2046}, 'kwargs': {'time_period': 2046}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2046)'}, 'Inflation!AU8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2047}, 'kwargs': {'time_period': 2047}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2047)'}, 'Inflation!AV8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2048}, 'kwargs': {'time_period': 2048}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2048)'}, 'Inflation!AW8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2049}, 'kwargs': {'time_period': 2049}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2049)'}, 'Inflation!AX8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2050}, 'kwargs': {'time_period': 2050}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2050)'}, 'Inflation!AY8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2051}, 'kwargs': {'time_period': 2051}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2051)'}, 'Inflation!AZ8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2052}, 'kwargs': {'time_period': 2052}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2052)'}, 'Inflation!B8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2002}, 'kwargs': {'time_period': 2002}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2002)'}, 'Inflation!BA8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2053}, 'kwargs': {'time_period': 2053}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2053)'}, 'Inflation!BB8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2054}, 'kwargs': {'time_period': 2054}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2054)'}, 'Inflation!BC8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2055}, 'kwargs': {'time_period': 2055}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2055)'}, 'Inflation!BD8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2056}, 'kwargs': {'time_period': 2056}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2056)'}, 'Inflation!BE8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2057}, 'kwargs': {'time_period': 2057}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2057)'}, 'Inflation!BF8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2058}, 'kwargs': {'time_period': 2058}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2058)'}, 'Inflation!BG8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2059}, 'kwargs': {'time_period': 2059}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2059)'}, 'Inflation!BH8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2060}, 'kwargs': {'time_period': 2060}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2060)'}, 'Inflation!BI8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2061}, 'kwargs': {'time_period': 2061}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2061)'}, 'Inflation!BJ8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2062}, 'kwargs': {'time_period': 2062}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2062)'}, 'Inflation!BK8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2063}, 'kwargs': {'time_period': 2063}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2063)'}, 'Inflation!BL8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2064}, 'kwargs': {'time_period': 2064}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2064)'}, 'Inflation!BM8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2065}, 'kwargs': {'time_period': 2065}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2065)'}, 'Inflation!BN8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2066}, 'kwargs': {'time_period': 2066}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2066)'}, 'Inflation!BO8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2067}, 'kwargs': {'time_period': 2067}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2067)'}, 'Inflation!BP8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2068}, 'kwargs': {'time_period': 2068}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2068)'}, 'Inflation!BQ8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2069}, 'kwargs': {'time_period': 2069}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2069)'}, 'Inflation!BR8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2070}, 'kwargs': {'time_period': 2070}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2070)'}, 'Inflation!BS8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2071}, 'kwargs': {'time_period': 2071}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2071)'}, 'Inflation!C8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2003}, 'kwargs': {'time_period': 2003}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2003)'}, 'Inflation!D8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2004}, 'kwargs': {'time_period': 2004}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2004)'}, 'Inflation!E8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2005}, 'kwargs': {'time_period': 2005}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2005)'}, 'Inflation!F8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2006}, 'kwargs': {'time_period': 2006}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2006)'}, 'Inflation!G6': {'series_id': 'inflation_convergence_logistic_steepness', 'reader': 'read_inflation_convergence_logistic_steepness', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_inflation_convergence_logistic_steepness(ctx)'}, 'Inflation!G8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2007}, 'kwargs': {'time_period': 2007}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2007)'}, 'Inflation!H8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2008}, 'kwargs': {'time_period': 2008}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2008)'}, 'Inflation!I8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2009}, 'kwargs': {'time_period': 2009}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2009)'}, 'Inflation!J6': {'series_id': 'inflation_convergence_logistic_midpoint', 'reader': 'read_inflation_convergence_logistic_midpoint', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_inflation_convergence_logistic_midpoint(ctx)'}, 'Inflation!J8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2010}, 'kwargs': {'time_period': 2010}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2010)'}, 'Inflation!K8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2011}, 'kwargs': {'time_period': 2011}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2011)'}, 'Inflation!L8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2012}, 'kwargs': {'time_period': 2012}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2012)'}, 'Inflation!M8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2013}, 'kwargs': {'time_period': 2013}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2013)'}, 'Inflation!N8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2014}, 'kwargs': {'time_period': 2014}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2014)'}, 'Inflation!O8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2015}, 'kwargs': {'time_period': 2015}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2015)'}, 'Inflation!P8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2016}, 'kwargs': {'time_period': 2016}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2016)'}, 'Inflation!Q8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2017}, 'kwargs': {'time_period': 2017}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2017)'}, 'Inflation!R8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2018}, 'kwargs': {'time_period': 2018}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2018)'}, 'Inflation!S8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2019}, 'kwargs': {'time_period': 2019}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2019)'}, 'Inflation!T8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2020}, 'kwargs': {'time_period': 2020}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2020)'}, 'Inflation!U8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2021}, 'kwargs': {'time_period': 2021}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2021)'}, 'Inflation!V8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2022}, 'kwargs': {'time_period': 2022}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2022)'}, 'Inflation!W8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2023}, 'kwargs': {'time_period': 2023}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2023)'}, 'Inflation!X8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2024}, 'kwargs': {'time_period': 2024}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2024)'}, 'Inflation!Y8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2025}, 'kwargs': {'time_period': 2025}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2025)'}, 'Inflation!Z8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index', 'keys': {'TIME_PERIOD': 2026}, 'kwargs': {'time_period': 2026}, 'kind': 'keyed', 'call_form': 'read_inflation_convergence_period_index(ctx, time_period=2026)'}, 'Productivity!AA23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2026}, 'kwargs': {'time_period': 2026}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2026)'}, 'Productivity!AB23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2027}, 'kwargs': {'time_period': 2027}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2027)'}, 'Productivity!AC23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2028}, 'kwargs': {'time_period': 2028}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2028)'}, 'Productivity!AD23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2029}, 'kwargs': {'time_period': 2029}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2029)'}, 'Productivity!AE23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2030}, 'kwargs': {'time_period': 2030}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2030)'}, 'Productivity!AF23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2031}, 'kwargs': {'time_period': 2031}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2031)'}, 'Productivity!AG23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2032}, 'kwargs': {'time_period': 2032}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2032)'}, 'Productivity!AH23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2033}, 'kwargs': {'time_period': 2033}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2033)'}, 'Productivity!AI23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2034}, 'kwargs': {'time_period': 2034}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2034)'}, 'Productivity!AJ23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2035}, 'kwargs': {'time_period': 2035}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2035)'}, 'Productivity!AK23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2036}, 'kwargs': {'time_period': 2036}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2036)'}, 'Productivity!AL23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2037}, 'kwargs': {'time_period': 2037}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2037)'}, 'Productivity!AM23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2038}, 'kwargs': {'time_period': 2038}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2038)'}, 'Productivity!AN23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2039}, 'kwargs': {'time_period': 2039}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2039)'}, 'Productivity!AO23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2040}, 'kwargs': {'time_period': 2040}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2040)'}, 'Productivity!AP23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2041}, 'kwargs': {'time_period': 2041}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2041)'}, 'Productivity!AQ23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2042}, 'kwargs': {'time_period': 2042}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2042)'}, 'Productivity!AR23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2043}, 'kwargs': {'time_period': 2043}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2043)'}, 'Productivity!AS23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2044}, 'kwargs': {'time_period': 2044}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2044)'}, 'Productivity!AT23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2045}, 'kwargs': {'time_period': 2045}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2045)'}, 'Productivity!AU23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2046}, 'kwargs': {'time_period': 2046}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2046)'}, 'Productivity!AV23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2047}, 'kwargs': {'time_period': 2047}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2047)'}, 'Productivity!AW23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2048}, 'kwargs': {'time_period': 2048}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2048)'}, 'Productivity!AX23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2049}, 'kwargs': {'time_period': 2049}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2049)'}, 'Productivity!AY23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2050}, 'kwargs': {'time_period': 2050}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2050)'}, 'Productivity!AZ23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2051}, 'kwargs': {'time_period': 2051}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2051)'}, 'Productivity!B23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2001}, 'kwargs': {'time_period': 2001}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2001)'}, 'Productivity!BA23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2052}, 'kwargs': {'time_period': 2052}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2052)'}, 'Productivity!BB23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2053}, 'kwargs': {'time_period': 2053}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2053)'}, 'Productivity!BC23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2054}, 'kwargs': {'time_period': 2054}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2054)'}, 'Productivity!BD23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2055}, 'kwargs': {'time_period': 2055}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2055)'}, 'Productivity!BE23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2056}, 'kwargs': {'time_period': 2056}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2056)'}, 'Productivity!BF23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2057}, 'kwargs': {'time_period': 2057}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2057)'}, 'Productivity!BG23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2058}, 'kwargs': {'time_period': 2058}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2058)'}, 'Productivity!BH23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2059}, 'kwargs': {'time_period': 2059}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2059)'}, 'Productivity!BI23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2060}, 'kwargs': {'time_period': 2060}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2060)'}, 'Productivity!BJ23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2061}, 'kwargs': {'time_period': 2061}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2061)'}, 'Productivity!BK23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2062}, 'kwargs': {'time_period': 2062}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2062)'}, 'Productivity!BL23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2063}, 'kwargs': {'time_period': 2063}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2063)'}, 'Productivity!BM23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2064}, 'kwargs': {'time_period': 2064}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2064)'}, 'Productivity!BN23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2065}, 'kwargs': {'time_period': 2065}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2065)'}, 'Productivity!BO23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2066}, 'kwargs': {'time_period': 2066}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2066)'}, 'Productivity!BP23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2067}, 'kwargs': {'time_period': 2067}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2067)'}, 'Productivity!BQ23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2068}, 'kwargs': {'time_period': 2068}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2068)'}, 'Productivity!BR23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2069}, 'kwargs': {'time_period': 2069}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2069)'}, 'Productivity!BS23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2070}, 'kwargs': {'time_period': 2070}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2070)'}, 'Productivity!C23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2002}, 'kwargs': {'time_period': 2002}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2002)'}, 'Productivity!D23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2003}, 'kwargs': {'time_period': 2003}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2003)'}, 'Productivity!E23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2004}, 'kwargs': {'time_period': 2004}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2004)'}, 'Productivity!F23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2005}, 'kwargs': {'time_period': 2005}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2005)'}, 'Productivity!G21': {'series_id': 'productivity_convergence_logistic_steepness', 'reader': 'read_productivity_convergence_logistic_steepness', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_productivity_convergence_logistic_steepness(ctx)'}, 'Productivity!G23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2006}, 'kwargs': {'time_period': 2006}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2006)'}, 'Productivity!H23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2007}, 'kwargs': {'time_period': 2007}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2007)'}, 'Productivity!I23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2008}, 'kwargs': {'time_period': 2008}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2008)'}, 'Productivity!J21': {'series_id': 'productivity_convergence_logistic_midpoint', 'reader': 'read_productivity_convergence_logistic_midpoint', 'keys': {}, 'kwargs': {}, 'kind': 'scalar', 'call_form': 'read_productivity_convergence_logistic_midpoint(ctx)'}, 'Productivity!J23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2009}, 'kwargs': {'time_period': 2009}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2009)'}, 'Productivity!K23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2010}, 'kwargs': {'time_period': 2010}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2010)'}, 'Productivity!L23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2011}, 'kwargs': {'time_period': 2011}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2011)'}, 'Productivity!M23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2012}, 'kwargs': {'time_period': 2012}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2012)'}, 'Productivity!N23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2013}, 'kwargs': {'time_period': 2013}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2013)'}, 'Productivity!O23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2014}, 'kwargs': {'time_period': 2014}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2014)'}, 'Productivity!P23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2015}, 'kwargs': {'time_period': 2015}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2015)'}, 'Productivity!Q23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2016}, 'kwargs': {'time_period': 2016}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2016)'}, 'Productivity!R23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2017}, 'kwargs': {'time_period': 2017}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2017)'}, 'Productivity!S23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2018}, 'kwargs': {'time_period': 2018}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2018)'}, 'Productivity!T23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2019}, 'kwargs': {'time_period': 2019}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2019)'}, 'Productivity!U23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2020}, 'kwargs': {'time_period': 2020}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2020)'}, 'Productivity!V23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2021}, 'kwargs': {'time_period': 2021}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2021)'}, 'Productivity!W23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2022}, 'kwargs': {'time_period': 2022}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2022)'}, 'Productivity!X23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2023}, 'kwargs': {'time_period': 2023}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2023)'}, 'Productivity!Y23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2024}, 'kwargs': {'time_period': 2024}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2024)'}, 'Productivity!Z23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index', 'keys': {'TIME_PERIOD': 2025}, 'kwargs': {'time_period': 2025}, 'kind': 'keyed', 'call_form': 'read_productivity_convergence_period_index(ctx, time_period=2025)'}}


def list_reader_ranges() -> dict[str, dict[str, object]]:
    """Return binding-aligned data_range → range-reader metadata."""
    return {'Inflation!B8:BS8': {'series_id': 'inflation_convergence_period_index', 'reader': 'read_inflation_convergence_period_index_range', 'data_range': 'Inflation!B8:BS8', 'call_form': 'read_inflation_convergence_period_index_range(ctx)'}, 'Productivity!B23:BS23': {'series_id': 'productivity_convergence_period_index', 'reader': 'read_productivity_convergence_period_index_range', 'data_range': 'Productivity!B23:BS23', 'call_form': 'read_productivity_convergence_period_index_range(ctx)'}}


def list_groups() -> dict[str, object]:
    """Return the view-level group manifest for the generated API."""
    return {'groups': [{'label': 'setup', 'path': ['setup'], 'slug': 'setup', 'members': [{'id': 'country', 'setter': 'set_country', 'reader': 'read_country', 'compute': None, 'order': 1}, {'id': 'demography_scenario', 'setter': 'set_demography_scenario', 'reader': 'read_demography_scenario', 'compute': None, 'order': 2}, {'id': 'productivity_start', 'setter': 'set_productivity_start', 'reader': 'read_productivity_start', 'compute': None, 'order': 3}, {'id': 'productivity_end', 'setter': 'set_productivity_end', 'reader': 'read_productivity_end', 'compute': None, 'order': 4}, {'id': 'inflation_start', 'setter': 'set_inflation_start', 'reader': 'read_inflation_start', 'compute': None, 'order': 5}, {'id': 'inflation_end', 'setter': 'set_inflation_end', 'reader': 'read_inflation_end', 'compute': None, 'order': 6}, {'id': 'interest_rate_mode', 'setter': 'set_interest_rate_mode', 'reader': 'read_interest_rate_mode', 'compute': None, 'order': 7}, {'id': 'real_interest_rate', 'setter': 'set_real_interest_rate', 'reader': 'read_real_interest_rate', 'compute': None, 'order': 8}, {'id': 'fiscal_rule_enabled', 'setter': 'set_fiscal_rule_enabled', 'reader': 'read_fiscal_rule_enabled', 'compute': None, 'order': 9}, {'id': 'debt_target', 'setter': 'set_debt_target', 'reader': 'read_debt_target', 'compute': None, 'order': 10}], 'children': []}, {'label': 'climate', 'path': ['climate'], 'slug': 'climate', 'members': [{'id': 'expenditure_rigidity', 'setter': 'set_expenditure_rigidity', 'reader': 'read_expenditure_rigidity', 'compute': None, 'order': 1}], 'children': []}, {'label': 'discrete_risks', 'path': ['discrete_risks'], 'slug': 'discrete_risks', 'members': [{'id': 'discrete_revenue_shocks', 'setter': 'set_discrete_revenue_shocks', 'reader': 'read_discrete_revenue_shocks', 'compute': None, 'order': 1}, {'id': 'discrete_primary_expenditure_shocks', 'setter': 'set_discrete_primary_expenditure_shocks', 'reader': 'read_discrete_primary_expenditure_shocks', 'compute': None, 'order': 2}], 'children': []}, {'label': 'baseline_outputs', 'path': ['baseline_outputs'], 'slug': 'baseline_outputs', 'members': [{'id': 'baseline_primary_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': 'compute_baseline_primary_expenditure_pct_gdp', 'order': 1}, {'id': 'baseline_interest_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': 'compute_baseline_interest_expenditure_pct_gdp', 'order': 2}, {'id': 'baseline_interest_rate', 'setter': None, 'reader': None, 'compute': 'compute_baseline_interest_rate', 'order': 3}, {'id': 'baseline_primary_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': 'compute_baseline_primary_balance_pct_gdp', 'order': 4}, {'id': 'baseline_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': 'compute_baseline_overall_balance_pct_gdp', 'order': 5}, {'id': 'baseline_debt_to_gdp', 'setter': None, 'reader': None, 'compute': 'compute_baseline_debt_to_gdp', 'order': 6}, {'id': 'baseline_debt_stabilizing_primary_balance', 'setter': None, 'reader': None, 'compute': 'compute_baseline_debt_stabilizing_primary_balance', 'order': 7}, {'id': 'baseline_fiscal_consolidation_gap', 'setter': None, 'reader': None, 'compute': 'compute_baseline_fiscal_consolidation_gap', 'order': 8}, {'id': 'baseline_nominal_gdp_growth', 'setter': None, 'reader': None, 'compute': 'compute_baseline_nominal_gdp_growth', 'order': 9}, {'id': 'baseline_real_gdp_growth', 'setter': None, 'reader': None, 'compute': 'compute_baseline_real_gdp_growth', 'order': 10}, {'id': 'baseline_revenue_pct_gdp', 'setter': None, 'reader': None, 'compute': 'compute_baseline_revenue_pct_gdp', 'order': 11}, {'id': 'baseline_employment_growth', 'setter': None, 'reader': None, 'compute': 'compute_baseline_employment_growth', 'order': 12}, {'id': 'baseline_labour_productivity_growth', 'setter': None, 'reader': None, 'compute': 'compute_baseline_labour_productivity_growth', 'order': 13}, {'id': 'baseline_gdp_deflator_growth', 'setter': None, 'reader': None, 'compute': 'compute_baseline_gdp_deflator_growth', 'order': 14}, {'id': 'baseline_population_growth', 'setter': None, 'reader': None, 'compute': 'compute_baseline_population_growth', 'order': 15}], 'children': []}, {'label': 'scenario_outputs', 'path': ['scenario_outputs'], 'slug': 'scenario_outputs', 'members': [{'id': 'scenario_primary_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': 'compute_scenario_primary_balance_pct_gdp', 'order': 1}, {'id': 'scenario_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': 'compute_scenario_overall_balance_pct_gdp', 'order': 2}, {'id': 'scenario_debt_to_gdp', 'setter': None, 'reader': None, 'compute': 'compute_scenario_debt_to_gdp', 'order': 3}, {'id': 'scenario_debt_stabilizing_primary_balance_paris', 'setter': None, 'reader': None, 'compute': 'compute_scenario_debt_stabilizing_primary_balance_paris', 'order': 4}, {'id': 'scenario_debt_stabilizing_primary_balance_moderate', 'setter': None, 'reader': None, 'compute': 'compute_scenario_debt_stabilizing_primary_balance_moderate', 'order': 5}, {'id': 'scenario_debt_stabilizing_primary_balance_high', 'setter': None, 'reader': None, 'compute': 'compute_scenario_debt_stabilizing_primary_balance_high', 'order': 6}, {'id': 'scenario_debt_stabilizing_primary_balance_hot', 'setter': None, 'reader': None, 'compute': 'compute_scenario_debt_stabilizing_primary_balance_hot', 'order': 7}, {'id': 'scenario_debt_stabilizing_primary_balance_hot_adapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_debt_stabilizing_primary_balance_hot_adapted', 'order': 8}, {'id': 'scenario_debt_stabilizing_primary_balance_hot_unadapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_debt_stabilizing_primary_balance_hot_unadapted', 'order': 9}, {'id': 'scenario_nominal_gdp_growth_paris', 'setter': None, 'reader': None, 'compute': 'compute_scenario_nominal_gdp_growth_paris', 'order': 10}, {'id': 'scenario_nominal_gdp_growth_moderate', 'setter': None, 'reader': None, 'compute': 'compute_scenario_nominal_gdp_growth_moderate', 'order': 11}, {'id': 'scenario_nominal_gdp_growth_high', 'setter': None, 'reader': None, 'compute': 'compute_scenario_nominal_gdp_growth_high', 'order': 12}, {'id': 'scenario_nominal_gdp_growth_hot', 'setter': None, 'reader': None, 'compute': 'compute_scenario_nominal_gdp_growth_hot', 'order': 13}, {'id': 'scenario_nominal_gdp_growth_hot_adapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_nominal_gdp_growth_hot_adapted', 'order': 14}, {'id': 'scenario_nominal_gdp_growth_hot_unadapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_nominal_gdp_growth_hot_unadapted', 'order': 15}, {'id': 'scenario_primary_expenditure_pct_gdp_paris', 'setter': None, 'reader': None, 'compute': 'compute_scenario_primary_expenditure_pct_gdp_paris', 'order': 16}, {'id': 'scenario_primary_expenditure_pct_gdp_moderate', 'setter': None, 'reader': None, 'compute': 'compute_scenario_primary_expenditure_pct_gdp_moderate', 'order': 17}, {'id': 'scenario_primary_expenditure_pct_gdp_high', 'setter': None, 'reader': None, 'compute': 'compute_scenario_primary_expenditure_pct_gdp_high', 'order': 18}, {'id': 'scenario_primary_expenditure_pct_gdp_hot', 'setter': None, 'reader': None, 'compute': 'compute_scenario_primary_expenditure_pct_gdp_hot', 'order': 19}, {'id': 'scenario_primary_expenditure_pct_gdp_hot_adapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_primary_expenditure_pct_gdp_hot_adapted', 'order': 20}, {'id': 'scenario_primary_expenditure_pct_gdp_hot_unadapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_primary_expenditure_pct_gdp_hot_unadapted', 'order': 21}, {'id': 'scenario_interest_expenditure_pct_gdp_paris', 'setter': None, 'reader': None, 'compute': 'compute_scenario_interest_expenditure_pct_gdp_paris', 'order': 22}, {'id': 'scenario_interest_expenditure_pct_gdp_moderate', 'setter': None, 'reader': None, 'compute': 'compute_scenario_interest_expenditure_pct_gdp_moderate', 'order': 23}, {'id': 'scenario_interest_expenditure_pct_gdp_high', 'setter': None, 'reader': None, 'compute': 'compute_scenario_interest_expenditure_pct_gdp_high', 'order': 24}, {'id': 'scenario_interest_expenditure_pct_gdp_hot', 'setter': None, 'reader': None, 'compute': 'compute_scenario_interest_expenditure_pct_gdp_hot', 'order': 25}, {'id': 'scenario_interest_expenditure_pct_gdp_hot_adapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_interest_expenditure_pct_gdp_hot_adapted', 'order': 26}, {'id': 'scenario_interest_expenditure_pct_gdp_hot_unadapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_interest_expenditure_pct_gdp_hot_unadapted', 'order': 27}, {'id': 'scenario_real_gdp_level_index_paris', 'setter': None, 'reader': None, 'compute': 'compute_scenario_real_gdp_level_index_paris', 'order': 28}, {'id': 'scenario_real_gdp_level_index_moderate', 'setter': None, 'reader': None, 'compute': 'compute_scenario_real_gdp_level_index_moderate', 'order': 29}, {'id': 'scenario_real_gdp_level_index_high', 'setter': None, 'reader': None, 'compute': 'compute_scenario_real_gdp_level_index_high', 'order': 30}, {'id': 'scenario_real_gdp_level_index_hot', 'setter': None, 'reader': None, 'compute': 'compute_scenario_real_gdp_level_index_hot', 'order': 31}, {'id': 'scenario_real_gdp_level_index_hot_adapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_real_gdp_level_index_hot_adapted', 'order': 32}, {'id': 'scenario_real_gdp_level_index_hot_unadapted', 'setter': None, 'reader': None, 'compute': 'compute_scenario_real_gdp_level_index_hot_unadapted', 'order': 33}, {'id': 'scenario_fiscal_consolidation_gap_milestones_2050', 'setter': None, 'reader': None, 'compute': 'compute_scenario_fiscal_consolidation_gap_milestones_2050', 'order': 34}, {'id': 'scenario_fiscal_consolidation_gap_milestones_2075', 'setter': None, 'reader': None, 'compute': 'compute_scenario_fiscal_consolidation_gap_milestones_2075', 'order': 35}, {'id': 'scenario_fiscal_consolidation_gap_milestones_2099', 'setter': None, 'reader': None, 'compute': 'compute_scenario_fiscal_consolidation_gap_milestones_2099', 'order': 36}], 'children': []}], 'ungrouped': [{'id': 'baseline_engine_working_age_population', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_engine_total_population', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_engine_real_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_engine_nominal_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_engine_revenue_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_engine_primary_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_engine_overall_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_engine_interest_expenditure_pct_revenue', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_engine_indicators', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_fiscal_rule_flag', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_debt_target_above', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_debt_target_below', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'baseline_debt_direction_above_sentinel', 'setter': None, 'reader': 'read_baseline_debt_direction_above_sentinel', 'compute': None, 'order': None}, {'id': 'baseline_debt_direction_below_sentinel', 'setter': None, 'reader': 'read_baseline_debt_direction_below_sentinel', 'compute': None, 'order': None}, {'id': 'paris_engine_employment_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_labour_productivity_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_real_gdp_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_gdp_deflator_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_nominal_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_revenue_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_revenue_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_primary_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_overall_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_weighted_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_interest_expenditure_pct_revenue', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_discrete_risk_revenue_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_discrete_risk_expenditure_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_memo_interest_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_memo_primary_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_memo_primary_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_memo_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_memo_gross_debt_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_baseline_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_primary_expenditure_baseline_share_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_recalibration_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'paris_engine_indicators', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_employment_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_labour_productivity_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_real_gdp_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_gdp_deflator_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_nominal_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_revenue_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_revenue_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_primary_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_overall_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_weighted_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_interest_expenditure_pct_revenue', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_discrete_risk_revenue_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_discrete_risk_expenditure_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_memo_interest_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_memo_primary_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_memo_primary_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_memo_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_memo_gross_debt_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_baseline_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_primary_expenditure_baseline_share_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_recalibration_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'moderate_engine_indicators', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_employment_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_labour_productivity_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_real_gdp_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_gdp_deflator_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_nominal_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_revenue_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_revenue_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_primary_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_overall_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_weighted_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_interest_expenditure_pct_revenue', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_discrete_risk_revenue_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_discrete_risk_expenditure_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_memo_interest_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_memo_primary_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_memo_primary_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_memo_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_memo_gross_debt_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_baseline_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_primary_expenditure_baseline_share_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_recalibration_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'high_engine_indicators', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_employment_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_labour_productivity_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_real_gdp_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_gdp_deflator_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_nominal_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_revenue_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_revenue_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_primary_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_overall_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_weighted_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_interest_expenditure_pct_revenue', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_discrete_risk_revenue_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_discrete_risk_expenditure_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_memo_interest_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_memo_primary_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_memo_primary_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_memo_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_memo_gross_debt_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_baseline_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_primary_expenditure_baseline_share_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_recalibration_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_engine_indicators', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_employment_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_labour_productivity_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_real_gdp_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_gdp_deflator_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_nominal_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_revenue_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_revenue_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_primary_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_overall_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_weighted_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_interest_expenditure_pct_revenue', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_discrete_risk_revenue_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_discrete_risk_expenditure_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_memo_interest_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_memo_primary_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_memo_primary_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_memo_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_memo_gross_debt_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_baseline_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_primary_expenditure_baseline_share_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_recalibration_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_adapted_engine_indicators', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_employment_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_labour_productivity_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_real_gdp_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_gdp_deflator_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_nominal_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_revenue_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_revenue_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_primary_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_overall_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_weighted_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_interest_expenditure_pct_revenue', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_discrete_risk_revenue_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_discrete_risk_expenditure_shock', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_memo_interest_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_memo_primary_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_memo_primary_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_memo_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_memo_gross_debt_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_baseline_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_primary_expenditure_baseline_share_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_recalibration_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'hot_unadapted_engine_indicators', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_primary_expenditure_pct_gdp_summary', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_interest_expenditure_pct_gdp_summary', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_interest_rate_summary', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_primary_balance_pct_gdp_summary', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_overall_balance_pct_gdp_summary', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_debt_to_gdp_summary', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_dspb_milestones', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_primary_expenditure_pct_gdp_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_interest_expenditure_pct_gdp_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_interest_rate_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_primary_balance_pct_gdp_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_overall_balance_pct_gdp_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_baseline_debt_to_gdp_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_primary_balance_pct_gdp_summary_baseline', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_primary_balance_pct_gdp_summary_paris', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_primary_balance_pct_gdp_summary_moderate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_primary_balance_pct_gdp_summary_high', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_primary_balance_pct_gdp_summary_hot', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_primary_balance_pct_gdp_summary_hot_adapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_primary_balance_pct_gdp_summary_hot_unadapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_debt_to_gdp_summary_baseline', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_debt_to_gdp_summary_paris', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_debt_to_gdp_summary_moderate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_debt_to_gdp_summary_high', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_debt_to_gdp_summary_hot', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_debt_to_gdp_summary_hot_adapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_debt_to_gdp_summary_hot_unadapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_dspb_milestones_baseline', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_dspb_milestones_paris', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_dspb_milestones_moderate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_dspb_milestones_high', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_dspb_milestones_hot', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_dspb_milestones_hot_adapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_dspb_milestones_hot_unadapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_primary_balance_pct_gdp_baseline_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_overall_balance_pct_gdp_baseline_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'output_scenarios_debt_to_gdp_baseline_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_country', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_real_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_nominal_gdp_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_gdp_deflator', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_revenue_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_overall_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_primary_balance_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_debt_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_interest_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_primary_expenditure_lcu', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_real_gdp_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_nominal_gdp_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_gdp_deflator_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_revenue_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_primary_expenditure_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_debt_to_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_overall_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_primary_balance_pct_gdp', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'macrofiscal_interest_growth_differential', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_country', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_scenario_flag', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_variant_label_medium', 'setter': None, 'reader': 'read_demography_variant_label_medium', 'compute': None, 'order': None}, {'id': 'demography_variant_label_high', 'setter': None, 'reader': 'read_demography_variant_label_high', 'compute': None, 'order': None}, {'id': 'demography_variant_label_low', 'setter': None, 'reader': 'read_demography_variant_label_low', 'compute': None, 'order': None}, {'id': 'demography_working_age_population', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_total_population', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_working_age_population_medium', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_working_age_population_high', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_working_age_population_low', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_total_population_medium', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_total_population_high', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'demography_total_population_low', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'productivity_country', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'productivity_start_flag', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'productivity_end_flag', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'productivity_convergence_logistic_steepness', 'setter': None, 'reader': 'read_productivity_convergence_logistic_steepness', 'compute': None, 'order': None}, {'id': 'productivity_convergence_logistic_midpoint', 'setter': None, 'reader': 'read_productivity_convergence_logistic_midpoint', 'compute': None, 'order': None}, {'id': 'productivity_convergence_period_index', 'setter': None, 'reader': 'read_productivity_convergence_period_index', 'compute': None, 'order': None}, {'id': 'productivity_level', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'productivity_growth', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'productivity_convergence_trajectory', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'inflation_start_flag', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'inflation_end_flag', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'inflation_convergence_logistic_steepness', 'setter': None, 'reader': 'read_inflation_convergence_logistic_steepness', 'compute': None, 'order': None}, {'id': 'inflation_convergence_logistic_midpoint', 'setter': None, 'reader': 'read_inflation_convergence_logistic_midpoint', 'compute': None, 'order': None}, {'id': 'inflation_convergence_period_index', 'setter': None, 'reader': 'read_inflation_convergence_period_index', 'compute': None, 'order': None}, {'id': 'inflation_path', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'inflation_convergence_trajectory', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_mode_flag', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_end_of_mtff', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_growth_differential_end_of_mtff', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_long_run_real_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_assumption_label_nominal', 'setter': None, 'reader': 'read_interest_rate_assumption_label_nominal', 'compute': None, 'order': None}, {'id': 'interest_rate_assumption_label_differential', 'setter': None, 'reader': 'read_interest_rate_assumption_label_differential', 'compute': None, 'order': None}, {'id': 'interest_rate_assumption_label_real', 'setter': None, 'reader': 'read_interest_rate_assumption_label_real', 'compute': None, 'order': None}, {'id': 'interest_rate_nominal_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_nominal_gdp_growth_baseline', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_inflation_baseline', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_long_run_assumption', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_long_run_nominal_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_long_run_interest_growth_differential', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'interest_rate_long_run_real_interest_rate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_country', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_loss_pct_paris', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_loss_pct_moderate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_loss_pct_high', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_loss_pct_hot', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_loss_pct_hot_adapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_loss_pct_hot_unadapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_index_paris', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_index_moderate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_index_high', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_index_hot', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_index_hot_adapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_gdp_index_hot_unadapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_labour_productivity_growth_variation_paris', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_labour_productivity_growth_variation_moderate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_labour_productivity_growth_variation_high', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_labour_productivity_growth_variation_hot', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_labour_productivity_growth_variation_hot_adapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_database_labour_productivity_growth_variation_hot_unadapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_data_labour_productivity_growth_variation_paris', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_data_labour_productivity_growth_variation_moderate', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_data_labour_productivity_growth_variation_high', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_data_labour_productivity_growth_variation_hot', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_data_labour_productivity_growth_variation_hot_adapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}, {'id': 'climate_data_labour_productivity_growth_variation_hot_unadapted', 'setter': None, 'reader': None, 'compute': None, 'order': None}]}


TARGETS = {
    "'Discrete Risks'!C10:BT10": xl_range_rows,
    "'Discrete Risks'!C11:BT11": xl_range_rows,
    "'Discrete Risks'!C12:BT12": xl_range_rows,
    "'Discrete Risks'!C13:BT13": xl_range_rows,
    "'Discrete Risks'!C2:BT2": xl_range_rows,
    "'Discrete Risks'!C3:BT3": xl_range_rows,
    "'Discrete Risks'!C4:BT4": xl_range_rows,
    "'Discrete Risks'!C5:BT5": xl_range_rows,
    "'Discrete Risks'!C6:BT6": xl_range_rows,
    "'Discrete Risks'!C7:BT7": xl_range_rows,
    "'Discrete Risks'!C8:BT8": xl_range_rows,
    "'Discrete Risks'!C9:BT9": xl_range_rows,
    "'Hot Adapted'!D11:CP11": xl_range_rows,
    "'Hot Adapted'!D12:CP12": xl_range_rows,
    "'Hot Adapted'!D13:CP13": xl_range_rows,
    "'Hot Adapted'!D14:CP14": xl_range_rows,
    "'Hot Adapted'!D15:CP15": xl_range_rows,
    "'Hot Adapted'!D16:CP16": xl_range_rows,
    "'Hot Adapted'!D17:CP17": xl_range_rows,
    "'Hot Adapted'!D18:CP18": xl_range_rows,
    "'Hot Adapted'!D19:CP19": xl_range_rows,
    "'Hot Adapted'!D20:CP20": xl_range_rows,
    "'Hot Adapted'!D21:CP21": xl_range_rows,
    "'Hot Adapted'!D22:CP22": xl_range_rows,
    "'Hot Adapted'!D23:CP23": xl_range_rows,
    "'Hot Adapted'!D24:CP24": xl_range_rows,
    "'Hot Adapted'!D25:CP25": xl_range_rows,
    "'Hot Adapted'!D26:CP26": xl_range_rows,
    "'Hot Adapted'!D27:CP27": xl_range_rows,
    "'Hot Adapted'!D28:CP28": xl_range_rows,
    "'Hot Adapted'!D29:CP29": xl_range_rows,
    "'Hot Adapted'!D30:CP30": xl_range_rows,
    "'Hot Adapted'!D31:CP31": xl_range_rows,
    "'Hot Adapted'!D32:CP32": xl_range_rows,
    "'Hot Adapted'!D33:CP33": xl_range_rows,
    "'Hot Adapted'!D34:CP34": xl_range_rows,
    "'Hot Adapted'!D35:CP35": xl_range_rows,
    "'Hot Adapted'!D36:CP36": xl_range_rows,
    "'Hot Adapted'!D37:CP37": xl_range_rows,
    "'Hot Adapted'!D38:CP38": xl_range_rows,
    "'Hot Adapted'!D39:CP39": xl_range_rows,
    "'Hot Adapted'!D40:CP40": xl_range_rows,
    "'Hot Adapted'!D41:CP41": xl_range_rows,
    "'Hot Adapted'!D42:CP42": xl_range_rows,
    "'Hot Adapted'!D43:CP43": xl_range_rows,
    "'Hot Adapted'!D44:CP44": xl_range_rows,
    "'Hot Adapted'!D45:CP45": xl_range_rows,
    "'Hot Adapted'!D46:CP46": xl_range_rows,
    "'Hot Adapted'!D47:CP47": xl_range_rows,
    "'Hot Unadapted'!D11:CP11": xl_range_rows,
    "'Hot Unadapted'!D12:CP12": xl_range_rows,
    "'Hot Unadapted'!D13:CP13": xl_range_rows,
    "'Hot Unadapted'!D14:CP14": xl_range_rows,
    "'Hot Unadapted'!D15:CP15": xl_range_rows,
    "'Hot Unadapted'!D16:CP16": xl_range_rows,
    "'Hot Unadapted'!D17:CP17": xl_range_rows,
    "'Hot Unadapted'!D18:CP18": xl_range_rows,
    "'Hot Unadapted'!D19:CP19": xl_range_rows,
    "'Hot Unadapted'!D20:CP20": xl_range_rows,
    "'Hot Unadapted'!D21:CP21": xl_range_rows,
    "'Hot Unadapted'!D22:CP22": xl_range_rows,
    "'Hot Unadapted'!D23:CP23": xl_range_rows,
    "'Hot Unadapted'!D24:CP24": xl_range_rows,
    "'Hot Unadapted'!D25:CP25": xl_range_rows,
    "'Hot Unadapted'!D26:CP26": xl_range_rows,
    "'Hot Unadapted'!D27:CP27": xl_range_rows,
    "'Hot Unadapted'!D28:CP28": xl_range_rows,
    "'Hot Unadapted'!D29:CP29": xl_range_rows,
    "'Hot Unadapted'!D30:CP30": xl_range_rows,
    "'Hot Unadapted'!D31:CP31": xl_range_rows,
    "'Hot Unadapted'!D32:CP32": xl_range_rows,
    "'Hot Unadapted'!D33:CP33": xl_range_rows,
    "'Hot Unadapted'!D34:CP34": xl_range_rows,
    "'Hot Unadapted'!D35:CP35": xl_range_rows,
    "'Hot Unadapted'!D36:CP36": xl_range_rows,
    "'Hot Unadapted'!D37:CP37": xl_range_rows,
    "'Hot Unadapted'!D38:CP38": xl_range_rows,
    "'Hot Unadapted'!D39:CP39": xl_range_rows,
    "'Hot Unadapted'!D40:CP40": xl_range_rows,
    "'Hot Unadapted'!D41:CP41": xl_range_rows,
    "'Hot Unadapted'!D42:CP42": xl_range_rows,
    "'Hot Unadapted'!D43:CP43": xl_range_rows,
    "'Hot Unadapted'!D44:CP44": xl_range_rows,
    "'Hot Unadapted'!D45:CP45": xl_range_rows,
    "'Hot Unadapted'!D46:CP46": xl_range_rows,
    "'Hot Unadapted'!D47:CP47": xl_range_rows,
    "'Output Baseline'!C10:F10": xl_range_rows,
    "'Output Baseline'!C16:H16": xl_range_rows,
    "'Output Baseline'!C5:F5": xl_range_rows,
    "'Output Baseline'!C6:F6": xl_range_rows,
    "'Output Baseline'!C7:F7": xl_range_rows,
    "'Output Baseline'!C8:F8": xl_range_rows,
    "'Output Baseline'!C9:F9": xl_range_rows,
    "'Output Scenarios'!C10:F10": xl_range_rows,
    "'Output Scenarios'!C11:F11": xl_range_rows,
    "'Output Scenarios'!C14:F14": xl_range_rows,
    "'Output Scenarios'!C15:F15": xl_range_rows,
    "'Output Scenarios'!C16:F16": xl_range_rows,
    "'Output Scenarios'!C17:F17": xl_range_rows,
    "'Output Scenarios'!C18:F18": xl_range_rows,
    "'Output Scenarios'!C19:F19": xl_range_rows,
    "'Output Scenarios'!C20:F20": xl_range_rows,
    "'Output Scenarios'!C25:N25": xl_range_rows,
    "'Output Scenarios'!C26:N26": xl_range_rows,
    "'Output Scenarios'!C27:N27": xl_range_rows,
    "'Output Scenarios'!C28:N28": xl_range_rows,
    "'Output Scenarios'!C29:N29": xl_range_rows,
    "'Output Scenarios'!C30:N30": xl_range_rows,
    "'Output Scenarios'!C31:N31": xl_range_rows,
    "'Output Scenarios'!C5:F5": xl_range_rows,
    "'Output Scenarios'!C6:F6": xl_range_rows,
    "'Output Scenarios'!C7:F7": xl_range_rows,
    "'Output Scenarios'!C8:F8": xl_range_rows,
    "'Output Scenarios'!C9:F9": xl_range_rows,
    "'Output Scenarios'!V100:CO100": xl_range_rows,
    "'Output Scenarios'!V101:CO101": xl_range_rows,
    "'Output Scenarios'!V102:CO102": xl_range_rows,
    "'Output Scenarios'!V103:CO103": xl_range_rows,
    "'Output Scenarios'!V104:CO104": xl_range_rows,
    "'Output Scenarios'!V105:CO105": xl_range_rows,
    "'Output Scenarios'!V106:CO106": xl_range_rows,
    "'Output Scenarios'!V107:CO107": xl_range_rows,
    "'Output Scenarios'!V108:CO108": xl_range_rows,
    "'Output Scenarios'!V109:CO109": xl_range_rows,
    "'Output Scenarios'!V110:CO110": xl_range_rows,
    "'Output Scenarios'!V111:CO111": xl_range_rows,
    "'Output Scenarios'!V112:CO112": xl_range_rows,
    "'Output Scenarios'!V113:CO113": xl_range_rows,
    "'Output Scenarios'!V114:CO114": xl_range_rows,
    "'Output Scenarios'!V115:CO115": xl_range_rows,
    "'Output Scenarios'!V116:CO116": xl_range_rows,
    "'Output Scenarios'!V93:CO93": xl_range_rows,
    "'Output Scenarios'!V94:CO94": xl_range_rows,
    "'Output Scenarios'!V95:CO95": xl_range_rows,
    "'Output Scenarios'!V96:CO96": xl_range_rows,
    "'Output Scenarios'!V97:CO97": xl_range_rows,
    "'Output Scenarios'!V98:CO98": xl_range_rows,
    "'Output Scenarios'!V99:CO99": xl_range_rows,
    'Baseline!D11:CP11': xl_range_rows,
    'Baseline!D12:CP12': xl_range_rows,
    'Baseline!D13:CP13': xl_range_rows,
    'Baseline!D14:CP14': xl_range_rows,
    'Baseline!D15:CP15': xl_range_rows,
    'Baseline!D16:CP16': xl_range_rows,
    'Baseline!D17:CP17': xl_range_rows,
    'Baseline!D18:CP18': xl_range_rows,
    'Baseline!D19:CP19': xl_range_rows,
    'Baseline!D20:CP20': xl_range_rows,
    'Baseline!D21:CP21': xl_range_rows,
    'Baseline!D22:CP22': xl_range_rows,
    'Baseline!D23:CP23': xl_range_rows,
    'Baseline!D24:CP24': xl_range_rows,
    'Baseline!D25:CP25': xl_range_rows,
    'Baseline!D26:CP26': xl_range_rows,
    'Baseline!D27:CP27': xl_range_rows,
    'Baseline!D28:CP28': xl_range_rows,
    'Baseline!D29:CP29': xl_range_rows,
    'Baseline!D30:CP30': xl_range_rows,
    'Baseline!D31:CP31': xl_range_rows,
    'Baseline!D32:CP32': xl_range_rows,
    'Baseline!D33:CP33': xl_range_rows,
    'Baseline!D34:CP34': xl_range_rows,
    'Baseline!D35:CP35': xl_range_rows,
    'Baseline!D36:CP36': xl_range_rows,
    'Baseline!D37:CP37': xl_range_rows,
    'Baseline!D38:CP38': xl_range_rows,
    'Baseline!D39:CP39': xl_range_rows,
    'Baseline!D40:CP40': xl_range_rows,
    'Dashboard!C12': xl_cell,
    'Dashboard!C17': xl_cell,
    'Dashboard!C20:C21': xl_range_rows,
    'Dashboard!C24:C25': xl_range_rows,
    'Dashboard!C28:C29': xl_range_rows,
    'Dashboard!C33:C34': xl_range_rows,
    'Dashboard!C38': xl_cell,
    'High!D11:CP11': xl_range_rows,
    'High!D12:CP12': xl_range_rows,
    'High!D13:CP13': xl_range_rows,
    'High!D14:CP14': xl_range_rows,
    'High!D15:CP15': xl_range_rows,
    'High!D16:CP16': xl_range_rows,
    'High!D17:CP17': xl_range_rows,
    'High!D18:CP18': xl_range_rows,
    'High!D19:CP19': xl_range_rows,
    'High!D20:CP20': xl_range_rows,
    'High!D21:CP21': xl_range_rows,
    'High!D22:CP22': xl_range_rows,
    'High!D23:CP23': xl_range_rows,
    'High!D24:CP24': xl_range_rows,
    'High!D25:CP25': xl_range_rows,
    'High!D26:CP26': xl_range_rows,
    'High!D27:CP27': xl_range_rows,
    'High!D28:CP28': xl_range_rows,
    'High!D29:CP29': xl_range_rows,
    'High!D30:CP30': xl_range_rows,
    'High!D31:CP31': xl_range_rows,
    'High!D32:CP32': xl_range_rows,
    'High!D33:CP33': xl_range_rows,
    'High!D34:CP34': xl_range_rows,
    'High!D35:CP35': xl_range_rows,
    'High!D36:CP36': xl_range_rows,
    'High!D37:CP37': xl_range_rows,
    'High!D38:CP38': xl_range_rows,
    'High!D39:CP39': xl_range_rows,
    'High!D40:CP40': xl_range_rows,
    'High!D41:CP41': xl_range_rows,
    'High!D42:CP42': xl_range_rows,
    'High!D43:CP43': xl_range_rows,
    'High!D44:CP44': xl_range_rows,
    'High!D45:CP45': xl_range_rows,
    'High!D46:CP46': xl_range_rows,
    'High!D47:CP47': xl_range_rows,
    'Hot!D11:CP11': xl_range_rows,
    'Hot!D12:CP12': xl_range_rows,
    'Hot!D13:CP13': xl_range_rows,
    'Hot!D14:CP14': xl_range_rows,
    'Hot!D15:CP15': xl_range_rows,
    'Hot!D16:CP16': xl_range_rows,
    'Hot!D17:CP17': xl_range_rows,
    'Hot!D18:CP18': xl_range_rows,
    'Hot!D19:CP19': xl_range_rows,
    'Hot!D20:CP20': xl_range_rows,
    'Hot!D21:CP21': xl_range_rows,
    'Hot!D22:CP22': xl_range_rows,
    'Hot!D23:CP23': xl_range_rows,
    'Hot!D24:CP24': xl_range_rows,
    'Hot!D25:CP25': xl_range_rows,
    'Hot!D26:CP26': xl_range_rows,
    'Hot!D27:CP27': xl_range_rows,
    'Hot!D28:CP28': xl_range_rows,
    'Hot!D29:CP29': xl_range_rows,
    'Hot!D30:CP30': xl_range_rows,
    'Hot!D31:CP31': xl_range_rows,
    'Hot!D32:CP32': xl_range_rows,
    'Hot!D33:CP33': xl_range_rows,
    'Hot!D34:CP34': xl_range_rows,
    'Hot!D35:CP35': xl_range_rows,
    'Hot!D36:CP36': xl_range_rows,
    'Hot!D37:CP37': xl_range_rows,
    'Hot!D38:CP38': xl_range_rows,
    'Hot!D39:CP39': xl_range_rows,
    'Hot!D40:CP40': xl_range_rows,
    'Hot!D41:CP41': xl_range_rows,
    'Hot!D42:CP42': xl_range_rows,
    'Hot!D43:CP43': xl_range_rows,
    'Hot!D44:CP44': xl_range_rows,
    'Hot!D45:CP45': xl_range_rows,
    'Hot!D46:CP46': xl_range_rows,
    'Hot!D47:CP47': xl_range_rows,
    'Moderate!D11:CP11': xl_range_rows,
    'Moderate!D12:CP12': xl_range_rows,
    'Moderate!D13:CP13': xl_range_rows,
    'Moderate!D14:CP14': xl_range_rows,
    'Moderate!D15:CP15': xl_range_rows,
    'Moderate!D16:CP16': xl_range_rows,
    'Moderate!D17:CP17': xl_range_rows,
    'Moderate!D18:CP18': xl_range_rows,
    'Moderate!D19:CP19': xl_range_rows,
    'Moderate!D20:CP20': xl_range_rows,
    'Moderate!D21:CP21': xl_range_rows,
    'Moderate!D22:CP22': xl_range_rows,
    'Moderate!D23:CP23': xl_range_rows,
    'Moderate!D24:CP24': xl_range_rows,
    'Moderate!D25:CP25': xl_range_rows,
    'Moderate!D26:CP26': xl_range_rows,
    'Moderate!D27:CP27': xl_range_rows,
    'Moderate!D28:CP28': xl_range_rows,
    'Moderate!D29:CP29': xl_range_rows,
    'Moderate!D30:CP30': xl_range_rows,
    'Moderate!D31:CP31': xl_range_rows,
    'Moderate!D32:CP32': xl_range_rows,
    'Moderate!D33:CP33': xl_range_rows,
    'Moderate!D34:CP34': xl_range_rows,
    'Moderate!D35:CP35': xl_range_rows,
    'Moderate!D36:CP36': xl_range_rows,
    'Moderate!D37:CP37': xl_range_rows,
    'Moderate!D38:CP38': xl_range_rows,
    'Moderate!D39:CP39': xl_range_rows,
    'Moderate!D40:CP40': xl_range_rows,
    'Moderate!D41:CP41': xl_range_rows,
    'Moderate!D42:CP42': xl_range_rows,
    'Moderate!D43:CP43': xl_range_rows,
    'Moderate!D44:CP44': xl_range_rows,
    'Moderate!D45:CP45': xl_range_rows,
    'Moderate!D46:CP46': xl_range_rows,
    'Moderate!D47:CP47': xl_range_rows,
    'Paris!D11:CP11': xl_range_rows,
    'Paris!D12:CP12': xl_range_rows,
    'Paris!D13:CP13': xl_range_rows,
    'Paris!D14:CP14': xl_range_rows,
    'Paris!D15:CP15': xl_range_rows,
    'Paris!D16:CP16': xl_range_rows,
    'Paris!D17:CP17': xl_range_rows,
    'Paris!D18:CP18': xl_range_rows,
    'Paris!D19:CP19': xl_range_rows,
    'Paris!D20:CP20': xl_range_rows,
    'Paris!D21:CP21': xl_range_rows,
    'Paris!D22:CP22': xl_range_rows,
    'Paris!D23:CP23': xl_range_rows,
    'Paris!D24:CP24': xl_range_rows,
    'Paris!D25:CP25': xl_range_rows,
    'Paris!D26:CP26': xl_range_rows,
    'Paris!D27:CP27': xl_range_rows,
    'Paris!D28:CP28': xl_range_rows,
    'Paris!D29:CP29': xl_range_rows,
    'Paris!D30:CP30': xl_range_rows,
    'Paris!D31:CP31': xl_range_rows,
    'Paris!D32:CP32': xl_range_rows,
    'Paris!D33:CP33': xl_range_rows,
    'Paris!D34:CP34': xl_range_rows,
    'Paris!D35:CP35': xl_range_rows,
    'Paris!D36:CP36': xl_range_rows,
    'Paris!D37:CP37': xl_range_rows,
    'Paris!D38:CP38': xl_range_rows,
    'Paris!D39:CP39': xl_range_rows,
    'Paris!D40:CP40': xl_range_rows,
    'Paris!D41:CP41': xl_range_rows,
    'Paris!D42:CP42': xl_range_rows,
    'Paris!D43:CP43': xl_range_rows,
    'Paris!D44:CP44': xl_range_rows,
    'Paris!D45:CP45': xl_range_rows,
    'Paris!D46:CP46': xl_range_rows,
    'Paris!D47:CP47': xl_range_rows,
}


def compute_all(ctx: EvalContext | None = None, *, inputs: dict[str, object] | None = None) -> dict[str, object]:
    """Compute all target cells and return results."""
    if ctx is None:
        ctx = make_context(inputs)
    elif inputs is not None:
        warnings.warn(
            "inputs will be ignored because ctx was provided",
            UserWarning,
            stacklevel=2,
        )
    return {target: handler(ctx, target) for target, handler in TARGETS.items()}
