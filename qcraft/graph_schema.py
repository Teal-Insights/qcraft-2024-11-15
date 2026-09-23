"""Series topology for the interactive dependency-graph viz.

Author ``NODES`` / ``EDGES`` for this workbook after export. Prefer cell
addresses from ``data`` (``.cells`` / ``*_CELLS``) so provenance stays
single-sourced with bindings.

Repeatable pieces (do not invent):

- **Axes / defaults / addresses** — from ``data`` and ``Model._INPUT_IDS``
- **Recompute** — ``Model`` (export) or excel-grapher ``FormulaEvaluator``
  via ``graph_formula_evaluator``
- **Edges** — authored series DAG (producer → consumer), matching how
  formulas depend on bound series

See the extraction-pipeline-template reference:
``templates/series-graph/examples/tiny_dsa_graph_schema.py``.
"""

from __future__ import annotations

from typing import Any, Literal, Mapping

from . import data
from .model import Model

BackendName = Literal["export", "formula_evaluator"]

INPUT_IDS: tuple[str, ...] = tuple(Model._INPUT_IDS)

# Author: every series id the viz should show (inputs + internals + outputs).
SERIES_IDS: tuple[str, ...] = INPUT_IDS

# Author: producer → consumer edges for the series DAG.
EDGES: tuple[tuple[str, str], ...] = ()

# Author: one node dict per series id (role, kind, keys, address/addresses, …).
# Start from Tiny DSA reference or build with `_node` helpers below.
NODES: tuple[dict[str, Any], ...] = ()

NODES_BY_ID: dict[str, dict[str, Any]] = {node["id"]: node for node in NODES}


def axes() -> dict[str, list[Any]]:
    """Optional viz axes; override when your workbook has year/country domains."""
    years = list(getattr(getattr(data, "TIME_PERIOD_AXIS", None), "keys", ()) or ())
    countries = list(getattr(getattr(data, "COUNTRY_AXIS", None), "keys", ()) or ())
    shock_params = list(
        getattr(getattr(data, "SHOCK_PARAMETER_AXIS", None), "keys", ()) or ()
    )
    return {
        "years": years,
        "countries": countries,
        "shock_params": shock_params,
    }


def _flat_addresses(cells: Mapping[Any, str]) -> dict[Any, str]:
    out: dict[Any, str] = {}
    for coord, address in cells.items():
        if isinstance(coord, tuple) and len(coord) == 1:
            out[coord[0]] = address
        elif coord == ():
            continue
        else:
            out[coord] = address
    return out


def _scalar_address(cells: Mapping[Any, str]) -> str:
    return cells[()]


def _sheet_of(address: str) -> str:
    return address.split("!", 1)[0]


def _node(
    *,
    series_id: str,
    role: str,
    kind: str,
    keys: list[Any],
    address: str | None = None,
    addresses: dict[Any, str] | None = None,
    domain: dict[str, float] | None = None,
    options: list[Any] | None = None,
    option_labels: dict[Any, str] | None = None,
) -> dict[str, Any]:
    if address is not None:
        sample = address
    elif addresses:
        sample = next(iter(addresses.values()))
    else:
        raise ValueError(f"{series_id} needs address or addresses")
    node: dict[str, Any] = {
        "id": series_id,
        "role": role,
        "label": series_id,
        "sheet": _sheet_of(sample),
        "kind": kind,
        "keys": keys,
    }
    if address is not None:
        node["address"] = address
    if addresses is not None:
        node["addresses"] = addresses
    if domain is not None:
        node["domain"] = domain
    if options is not None:
        node["options"] = options
    if option_labels is not None:
        node["optionLabels"] = option_labels
    return node


def all_cell_addresses() -> tuple[str, ...]:
    addresses: list[str] = []
    for node in NODES:
        if "address" in node:
            addresses.append(node["address"])
        for address in node.get("addresses", {}).values():
            addresses.append(address)
    return tuple(dict.fromkeys(addresses))


def input_cell_writes(flat_inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Map flat viz inputs to sheet-qualified leaf cells for FormulaEvaluator."""
    writes: dict[str, Any] = {}
    for series_id in INPUT_IDS:
        node = NODES_BY_ID.get(series_id)
        if node is None:
            continue
        if "address" in node:
            writes[node["address"]] = flat_inputs[series_id]
            continue
        for key, address in node.get("addresses", {}).items():
            writes[address] = flat_inputs[series_id][key]
    return writes


__all__ = [
    "INPUT_IDS",
    "SERIES_IDS",
    "EDGES",
    "NODES",
    "NODES_BY_ID",
    "BackendName",
    "axes",
    "all_cell_addresses",
    "input_cell_writes",
    "_node",
    "_flat_addresses",
    "_scalar_address",
]
