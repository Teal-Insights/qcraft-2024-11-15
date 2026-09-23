"""Pedagogical series-graph API for the docs dependency-graph viz.

Recomputes via the exported ``Model`` (default) or excel-grapher's
``FormulaEvaluator``. JSON shapes match ``assets/graph/app.js``
(flat key→value maps, not tuple coordinates).
"""

from __future__ import annotations

from typing import Any, Mapping

from . import data
from .graph_schema import (
    EDGES,
    INPUT_IDS,
    NODES,
    SERIES_IDS,
    VIZ_INPUT_IDS,
    BackendName,
    axes,
)
from .model import Model
from .tensor import Series

JsonValue = Any
FlatInputs = dict[str, JsonValue]
FlatValues = dict[str, JsonValue]

_ENUM_INPUTS = {
    "country",
    "demography_scenario",
    "interest_rate_mode",
    "fiscal_rule_enabled",
}
_FLOAT_INPUTS = {
    "productivity_start",
    "productivity_end",
    "inflation_start",
    "inflation_end",
    "real_interest_rate",
    "debt_target",
    "expenditure_rigidity",
}


class GraphApiError(Exception):
    """Structured failure for HTTP / callers (validation or missing backend)."""

    def __init__(
        self,
        message: str,
        *,
        status: int = 400,
        errors: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.errors = errors or {}

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"error": self.message}
        if self.errors:
            payload["errors"] = self.errors
        return payload


def _unwrap_key(key: object) -> object:
    if isinstance(key, tuple) and len(key) == 1:
        return key[0]
    if isinstance(key, tuple):
        return "|".join(str(part) for part in key)
    return key


def flatten_series(value: object) -> JsonValue:
    """Series / scalar → JSON-friendly scalar or flat map."""
    if isinstance(value, Series):
        return {_unwrap_key(coord): _json_number(item) for coord, item in value.items()}
    if hasattr(value, "items") and hasattr(value, "domain"):
        return {
            _unwrap_key(coord): _json_number(item)
            for coord, item in value.items()  # type: ignore[union-attr]
        }
    return _json_number(value)


def _json_number(value: object) -> JsonValue:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return float(value)
    try:
        as_float = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return value
    if as_float.is_integer():
        return int(as_float)
    return as_float


def flatten_defaults() -> FlatInputs:
    """Canonical Dashboard defaults for the pedagogical viz.

    Uses France rather than ``data.COUNTRY_DEFAULT`` (Afghanistan): several
    climate / scenario paths are blank for countries without climate coverage,
    which surfaces as ``#VALUE!`` in the graph.
    """
    defaults: FlatInputs = {}
    for name in VIZ_INPUT_IDS:
        defaults[name] = _json_number(getattr(data, f"{name.upper()}_DEFAULT"))
    defaults["country"] = "France"
    return defaults


def normalize_inputs(raw: Mapping[str, Any] | None) -> FlatInputs:
    """Accept JSON inputs; fill missing Dashboard scalars from defaults."""
    base = flatten_defaults()
    if not raw:
        return base
    allowed = set(VIZ_INPUT_IDS)
    unknown = set(raw) - allowed - set(INPUT_IDS)
    if unknown:
        raise GraphApiError(
            f"unknown inputs: {sorted(unknown)}",
            errors={name: "unknown input" for name in sorted(unknown)},
        )
    merged = dict(base)
    for name in VIZ_INPUT_IDS:
        if name not in raw:
            continue
        value = raw[name]
        if name in _ENUM_INPUTS:
            merged[name] = str(value)
        elif name in _FLOAT_INPUTS:
            if isinstance(value, (dict, list)):
                raise GraphApiError(
                    f"{name} must be a number",
                    errors={name: "expected scalar"},
                )
            merged[name] = float(value)
        else:
            merged[name] = value
    return merged


def bind_model_inputs(flat: FlatInputs) -> dict[str, Any]:
    """Flat viz inputs → keyword args for ``Model.from_defaults``."""
    kwargs = {name: flat[name] for name in VIZ_INPUT_IDS}
    # Matrix shocks stay at workbook defaults (not exposed in the pedagogical viz).
    kwargs["discrete_revenue_shocks"] = data.DISCRETE_REVENUE_SHOCKS_DEFAULT
    kwargs["discrete_primary_expenditure_shocks"] = (
        data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT
    )
    return kwargs


def available_backends() -> list[BackendName]:
    backends: list[BackendName] = ["export"]
    try:
        from . import graph_formula_evaluator as _fe

        if _fe.is_available():
            backends.append("formula_evaluator")
    except Exception:
        pass
    return backends


def evaluate_export(inputs: Mapping[str, Any] | None = None) -> FlatValues:
    """Recompute every viz series via the exported ``Model``."""
    flat = normalize_inputs(inputs)
    try:
        model = Model.from_defaults(**bind_model_inputs(flat))
    except (TypeError, ValueError) as exc:
        raise GraphApiError(str(exc), errors={"_model": str(exc)}) from exc

    values: FlatValues = {name: flat[name] for name in VIZ_INPUT_IDS}
    for series_id in SERIES_IDS:
        if series_id in values:
            continue
        values[series_id] = flatten_series(getattr(model, series_id))
    return values


def evaluate_formula_evaluator(inputs: Mapping[str, Any] | None = None) -> FlatValues:
    """Recompute every series via excel-grapher ``FormulaEvaluator``."""
    from . import graph_formula_evaluator as fe

    if not fe.is_available():
        raise GraphApiError(
            "formula_evaluator backend requires excel-grapher and "
            "tests/fixtures/qcraft-toolv10.xlsx",
            status=503,
        )
    flat = normalize_inputs(inputs)
    try:
        return fe.evaluate(flat)
    except GraphApiError:
        raise
    except Exception as exc:
        raise GraphApiError(str(exc), status=503, errors={"_formula_evaluator": str(exc)}) from exc


def evaluate(
    inputs: Mapping[str, Any] | None = None,
    *,
    backend: BackendName = "export",
) -> FlatValues:
    if backend == "export":
        return evaluate_export(inputs)
    if backend == "formula_evaluator":
        return evaluate_formula_evaluator(inputs)
    raise GraphApiError(f"unknown backend: {backend!r}", status=400)


def bootstrap(*, backend: BackendName = "export") -> dict[str, Any]:
    """Schema + defaults + initial values for the viz."""
    defaults = flatten_defaults()
    return {
        "axes": axes(),
        "defaults": defaults,
        "nodes": list(NODES),
        "edges": [list(edge) for edge in EDGES],
        "values": evaluate(defaults, backend=backend),
        "backend": backend,
        "backends": available_backends(),
    }


__all__ = [
    "GraphApiError",
    "available_backends",
    "bind_model_inputs",
    "bootstrap",
    "evaluate",
    "evaluate_export",
    "evaluate_formula_evaluator",
    "flatten_defaults",
    "flatten_series",
    "normalize_inputs",
]
