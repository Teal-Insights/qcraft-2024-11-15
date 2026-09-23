"""FormulaEvaluator backend for the series-graph API.

Builds an excel-grapher dependency graph over the Q-CRAFT workbook fixture
and evaluates series cells after writing input leaves. Optional: requires
``excel-grapher`` and ``tests/fixtures/qcraft-toolv10.xlsx``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from .graph_schema import (
    NODES_BY_ID,
    SERIES_IDS,
    VIZ_INPUT_IDS,
    all_cell_addresses,
    input_cell_writes,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKBOOK = _REPO_ROOT / "tests" / "fixtures" / "qcraft-toolv10.xlsx"
DEFAULT_BINDINGS = _REPO_ROOT / "bindings"

# Fallback dynamic-ref domains when series bindings cannot be loaded.
_CONSTRAINTS_SCHEMA: dict[str, Any] = {
    "Dashboard!C17": Literal["High", "Low", "Medium"],
    "Dashboard!C28": Literal[
        "Interest-growth differential",
        "Nominal interest rate",
        "Real interest rate (a)",
    ],
    "Dashboard!C33": Literal["No", "Yes"],
}

_driver: _FormulaEvaluatorDriver | None = None
_driver_workbook: Path | None = None


def is_available(*, workbook: Path | None = None) -> bool:
    path = workbook or DEFAULT_WORKBOOK
    if not path.is_file():
        return False
    try:
        import excel_grapher  # noqa: F401
        from excel_grapher.grapher import DynamicRefConfig, create_dependency_graph  # noqa: F401
        import fastpyxl
        import inspect

        # excel-grapher may require a newer fastpyxl than is installed.
        if "keep_formula_cache" not in inspect.signature(fastpyxl.load_workbook).parameters:
            return False
    except ImportError:
        return False
    return True


def _as_json_number(value: object) -> Any:
    if hasattr(value, "value") and type(value).__name__ in {"FormulaValue", "XlError"}:
        value = getattr(value, "value", value)
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


def _build_dynamic_refs(workbook: Path) -> Any:
    from excel_grapher.grapher import DynamicRefConfig

    if DEFAULT_BINDINGS.is_dir():
        try:
            from excel_grapher.series_bindings import load_series_bindings

            bindings = load_series_bindings(DEFAULT_BINDINGS)
            return DynamicRefConfig.from_bindings(
                bindings, workbook, bindings_path=DEFAULT_BINDINGS
            )
        except Exception:
            pass
    return DynamicRefConfig.from_constraints(_CONSTRAINTS_SCHEMA)


class _FormulaEvaluatorDriver:
    """Hold one DependencyGraph + FormulaEvaluator for repeated evaluates."""

    def __init__(self, workbook: Path) -> None:
        from excel_grapher import FormulaEvaluator
        from excel_grapher.grapher import create_dependency_graph

        self.workbook = workbook
        self.graph = create_dependency_graph(
            workbook,
            list(all_cell_addresses()),
            load_values=True,
            dynamic_refs=_build_dynamic_refs(workbook),
        )
        self.evaluator = FormulaEvaluator(self.graph)
        self._baselines: dict[str, object] = {}
        for address in self._input_addresses():
            node = self.graph.get_node(address)
            if node is not None and getattr(node, "is_leaf", False):
                self._baselines[address] = node.value

    @staticmethod
    def _input_addresses() -> list[str]:
        addresses: list[str] = []
        for series_id in VIZ_INPUT_IDS:
            node = NODES_BY_ID[series_id]
            if "address" in node:
                addresses.append(node["address"])
            addresses.extend(node.get("addresses", {}).values())
        return addresses

    def reset_inputs(self) -> None:
        for address, value in self._baselines.items():
            self.graph.set_node_value(address, value)

    def apply_inputs(self, flat_inputs: dict[str, Any]) -> None:
        self.reset_inputs()
        for address, value in input_cell_writes(flat_inputs).items():
            self.graph.set_node_value(address, value)

    def read_series_values(self, flat_inputs: dict[str, Any]) -> dict[str, Any]:
        values: dict[str, Any] = {name: flat_inputs[name] for name in VIZ_INPUT_IDS}
        for series_id in SERIES_IDS:
            if series_id in values:
                continue
            node = NODES_BY_ID[series_id]
            if "address" in node:
                values[series_id] = _as_json_number(
                    self.evaluator.evaluate(node["address"])
                )
                continue
            series_map: dict[Any, Any] = {}
            for key, address in node["addresses"].items():
                series_map[key] = _as_json_number(self.evaluator.evaluate(address))
            values[series_id] = series_map
        return values


def _get_driver(workbook: Path | None = None) -> _FormulaEvaluatorDriver:
    global _driver, _driver_workbook
    path = (workbook or DEFAULT_WORKBOOK).resolve()
    if _driver is None or _driver_workbook != path:
        if not is_available(workbook=path):
            raise RuntimeError(
                "formula_evaluator backend requires excel-grapher and "
                f"workbook at {path}"
            )
        _driver = _FormulaEvaluatorDriver(path)
        _driver_workbook = path
    return _driver


def evaluate(flat_inputs: dict[str, Any], *, workbook: Path | None = None) -> dict[str, Any]:
    """Write flat inputs onto the graph and return full series value maps."""
    driver = _get_driver(workbook)
    driver.apply_inputs(flat_inputs)
    return driver.read_series_values(flat_inputs)


def reset_driver() -> None:
    """Drop the cached graph (tests / workbook swap)."""
    global _driver, _driver_workbook
    _driver = None
    _driver_workbook = None


__all__ = [
    "DEFAULT_WORKBOOK",
    "evaluate",
    "is_available",
    "reset_driver",
]
