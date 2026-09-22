"""Exported-library differential test harness.

Compare the generated standalone package against the extraction graph evaluated
with ``FormulaEvaluator``. Workbook-specific scenario definitions live in the
``Workbook-specific hooks`` section at the bottom of this module.

Run from the extraction repo after export::

    uv run python -m tests.differential.differential_test_exported_library

From the exported ``dist/`` project (graph cache + ``excel-grapher`` required)::

    uv run --project dist python -m tests.differential.differential_test_exported_library --layout exported
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import logging
import platform
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

from .comparison_utils import classify_comparison
from .differential_excel import (
    coerce_excel_error,
    matched_error_values,
    parity_exit_code,
)
from .differential_scenario_inputs import collect_scenario_input_addresses
from .differential_types import ATOL, RTOL, Axis, AxisPoint, Scenario

logger = logging.getLogger(__name__)

LayoutName = Literal["repo", "exported"]

GraphOracle = Callable[[Scenario, tuple[str, ...]], dict[str, Any]]
MvpOracle = Callable[[Scenario], dict[str, Any]]


@dataclass(frozen=True)
class DifferentialConfig:
    """Runtime paths and import settings for one differential run."""

    workbook_path: Path
    package_dir: Path
    package_name: str
    import_root: Path
    report_dir: Path
    library_name: str
    atol: float = ATOL
    rtol: float = RTOL
    allow_matched_errors: bool = False
    targets: tuple[str, ...] = ()
    bindings_path: Path | None = None
    blank_ranges: tuple[str, ...] = ()


@dataclass(frozen=True)
class Comparison:
    scenario_id: str
    cell_address: str
    cell_label: str
    graph_value: Any
    mvp_value: Any
    abs_diff: float | None
    rel_diff: float | None
    passed: bool
    matched_error: bool = False
    flagged_matched_error: bool = False
    note: str = ""


CSV_COLUMNS: tuple[str, ...] = (
    "scenario_id",
    "cell_address",
    "cell_label",
    "graph_value",
    "mvp_value",
    "abs_diff",
    "rel_diff",
    "passed",
    "matched_error",
    "flagged_matched_error",
    "note",
)

_REQUIRED_WORKBOOK_HOOKS: tuple[str, ...] = (
    "build_scenarios",
    "output_cell_labels",
    "inputs_for_excel",
    "mvp_outputs_for_scenario",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Differential test for the exported standalone library.",
    )
    parser.add_argument(
        "--layout",
        choices=("repo", "exported"),
        default="repo",
        help="Path preset: extraction repo (default) or exported dist/tests copy.",
    )
    parser.add_argument(
        "--workbook-path",
        type=Path,
        default=None,
        help="Override workbook path (defaults depend on --layout).",
    )
    parser.add_argument(
        "--package-name",
        default=None,
        help="Override import module for the MVP oracle (defaults depend on --layout).",
    )
    parser.add_argument(
        "--import-root",
        type=Path,
        default=None,
        help="Directory added to sys.path before importing the MVP oracle.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Directory for parity_report.{csv,txt} output.",
    )
    parser.add_argument(
        "--allow-matched-errors",
        action="store_true",
        help=(
            "Triage escape hatch: do not fail the run when both oracles return "
            "the same Excel error on a scenario without expects_error_values=True. "
            "Flagged comparisons are still listed in the report."
        ),
    )
    return parser.parse_args(argv)


def _project_root_from_module(module_path: Path) -> Path:
    """Return repo or dist root from ``tests/differential/<module>.py``."""
    return module_path.resolve().parents[2]


def _tests_root_from_module(module_path: Path) -> Path:
    return module_path.resolve().parents[1]


def resolve_config(
    *,
    module_path: Path,
    layout: LayoutName,
    workbook_path: Path | None = None,
    package_name: str | None = None,
    import_root: Path | None = None,
    report_dir: Path | None = None,
    allow_matched_errors: bool = False,
) -> DifferentialConfig:
    """Resolve paths from ``workbook_config.py`` and the selected layout."""
    module_path = module_path.resolve()
    project_root = _project_root_from_module(module_path)

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.pipeline_config import load_pipeline_config

    pipeline = load_pipeline_config(repo_root=project_root)
    package_dir = pipeline.package_root
    package_slug = pipeline.dist_metadata.package_name
    library_name = pipeline.dist_metadata.library_name

    if layout == "exported":
        tests_root = _tests_root_from_module(module_path)
        dist_root = project_root
        defaults = DifferentialConfig(
            workbook_path=tests_root / "fixtures" / pipeline.workbook_path.name,
            package_dir=dist_root / package_slug,
            package_name=f"{package_slug}.api",
            import_root=dist_root,
            report_dir=tests_root / "results" / "local",
            library_name=library_name,
            targets=pipeline.targets,
            bindings_path=pipeline.bindings_path,
            blank_ranges=pipeline.blank_ranges,
        )
    else:
        defaults = DifferentialConfig(
            workbook_path=pipeline.workbook_path,
            package_dir=package_dir,
            package_name=f"dist.{package_slug}.api",
            import_root=project_root,
            report_dir=project_root / pipeline.differential_report_dir_rel,
            library_name=library_name,
            targets=pipeline.targets,
            bindings_path=pipeline.bindings_path,
            blank_ranges=pipeline.blank_ranges,
        )

    return DifferentialConfig(
        workbook_path=(workbook_path or defaults.workbook_path).resolve(),
        package_dir=defaults.package_dir.resolve(),
        package_name=package_name or defaults.package_name,
        import_root=(import_root or defaults.import_root).resolve(),
        report_dir=(report_dir or defaults.report_dir).resolve(),
        library_name=library_name,
        atol=ATOL,
        rtol=RTOL,
        allow_matched_errors=allow_matched_errors,
        targets=defaults.targets,
        bindings_path=defaults.bindings_path,
        blank_ranges=defaults.blank_ranges,
    )


def config_from_args(module_path: Path, args: argparse.Namespace) -> DifferentialConfig:
    return resolve_config(
        module_path=module_path,
        layout=args.layout,
        workbook_path=args.workbook_path,
        package_name=args.package_name,
        import_root=args.import_root,
        report_dir=args.report_dir,
        allow_matched_errors=args.allow_matched_errors,
    )


def compare_cell(
    scenario_id: str,
    cell_address: str,
    cell_label: str,
    graph: Any,
    mvp: Any,
    *,
    atol: float,
    rtol: float,
    expects_error_values: bool = False,
) -> Comparison:
    passed, _healthy, _outcome, abs_diff, rel_diff, _note = classify_comparison(
        graph, mvp, atol=atol, rtol=rtol
    )
    graph_c = coerce_excel_error(graph)
    mvp_c = coerce_excel_error(mvp)
    matched_error = matched_error_values(graph, mvp) and passed

    graph_out: Any = graph_c
    mvp_out: Any = mvp_c
    if (
        abs_diff is not None
        and isinstance(graph_c, int | float)
        and isinstance(mvp_c, int | float)
        and not isinstance(graph_c, bool)
        and not isinstance(mvp_c, bool)
    ):
        graph_out = float(graph_c)
        mvp_out = float(mvp_c)
    elif (
        isinstance(graph_c, int | float)
        and isinstance(mvp_c, int | float)
        and not isinstance(graph_c, bool)
        and not isinstance(mvp_c, bool)
    ):
        try:
            graph_out = float(graph_c)
            mvp_out = float(mvp_c)
        except OverflowError:
            pass

    return Comparison(
        scenario_id,
        cell_address,
        cell_label,
        graph_out,
        mvp_out,
        abs_diff,
        rel_diff,
        passed,
        matched_error=matched_error,
        flagged_matched_error=matched_error and not expects_error_values,
    )


def compare_scenario(
    scenario: Scenario,
    graph_outputs: dict[str, Any],
    mvp_outputs: dict[str, Any],
    cell_labels: tuple[tuple[str, str], ...],
    *,
    atol: float,
    rtol: float,
) -> list[Comparison]:
    return [
        compare_cell(
            scenario.id,
            cell_address,
            cell_label,
            graph_outputs.get(cell_address),
            mvp_outputs.get(cell_label),
            atol=atol,
            rtol=rtol,
            expects_error_values=scenario.expects_error_values,
        )
        for cell_label, cell_address in cell_labels
    ]


def crash_comparisons(
    scenario: Scenario,
    cell_labels: tuple[tuple[str, str], ...],
    exc: BaseException,
    *,
    crashed_oracle: str = "unknown",
    graph_outputs: Mapping[str, Any] | None = None,
    mvp_outputs: Mapping[str, Any] | None = None,
) -> list[Comparison]:
    err_repr = f"<exception: {type(exc).__name__}: {exc}>"
    note = f"{crashed_oracle} oracle crashed"
    return [
        Comparison(
            scenario_id=scenario.id,
            cell_address=cell_address,
            cell_label=cell_label,
            graph_value=(
                err_repr
                if crashed_oracle == "graph"
                else (graph_outputs or {}).get(cell_address)
            ),
            mvp_value=(
                err_repr
                if crashed_oracle == "mvp"
                else (mvp_outputs or {}).get(cell_label)
            ),
            abs_diff=None,
            rel_diff=None,
            passed=False,
            note=note,
        )
        for cell_label, cell_address in cell_labels
    ]


def write_csv_report(comparisons: list[Comparison], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_COLUMNS)
        for comparison in comparisons:
            writer.writerow(
                [
                    comparison.scenario_id,
                    comparison.cell_address,
                    comparison.cell_label,
                    comparison.graph_value,
                    comparison.mvp_value,
                    comparison.abs_diff,
                    comparison.rel_diff,
                    comparison.passed,
                    comparison.matched_error,
                    comparison.flagged_matched_error,
                    comparison.note,
                ]
            )


def _environment_info() -> dict[str, str]:
    try:
        excel_grapher_version = version("excel-grapher")
    except Exception:  # noqa: BLE001
        excel_grapher_version = "unavailable"
    return {
        "python": sys.version.split()[0],
        "os": platform.platform(),
        "excel_grapher": excel_grapher_version,
    }


def write_txt_summary(
    comparisons: list[Comparison],
    path: Path,
    *,
    config: DifferentialConfig,
    environment: Mapping[str, str],
    workbook_sha256: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    total = len(comparisons)
    failures = [comparison for comparison in comparisons if not comparison.passed]
    passed = total - len(failures)
    pass_rate = (100.0 * passed / total) if total else 0.0
    flagged = [
        comparison for comparison in comparisons if comparison.flagged_matched_error
    ]
    failing_run = bool(failures) or bool(flagged and not config.allow_matched_errors)
    result = "FAIL" if failing_run else "PASS"
    first = failures[0] if failures else None

    with path.open("w", encoding="utf-8") as handle:
        handle.write(
            f"Parity report: exported {config.library_name} standalone library vs FormulaEvaluator\n"
        )
        handle.write(f"Generated: {datetime.now(UTC).isoformat(timespec='seconds')}\n")
        handle.write(f"Workbook:  {config.workbook_path}\n")
        handle.write(
            f"Package:   {config.package_dir} (imported as {config.package_name})\n"
        )
        handle.write(
            "Oracles:   excel-grapher graph + FormulaEvaluator [golden] vs "
            "exported package compute_* [mvp]\n"
        )
        handle.write(f"Tolerance: atol = {config.atol}, rtol = {config.rtol}\n\n")
        handle.write(f"Workbook SHA-256: {workbook_sha256}\n\n")
        handle.write("ENVIRONMENT\n")
        handle.write(f"  Python:  {environment['python']}\n")
        handle.write(f"  OS:      {environment['os']}\n")
        handle.write(f"  excel-grapher: {environment['excel_grapher']}\n\n")
        handle.write(f"Total comparisons: {total}\n")
        handle.write(f"Passed:            {passed}\n")
        handle.write(f"Failed:            {len(failures)}\n")
        if flagged:
            allowed_note = (
                " (allowed by --allow-matched-errors)"
                if config.allow_matched_errors
                else " (fails the run)"
            )
            handle.write(f"Matched errors:    {len(flagged)} flagged{allowed_note}\n")
        handle.write(f"Pass rate:         {pass_rate:.2f}%\n")
        handle.write("Acceptance bar:    100.00%\n")
        handle.write(f"Result:            {result}\n")
        if first is not None:
            handle.write("\nFirst divergence:\n")
            handle.write(f"  scenario:  {first.scenario_id}\n")
            handle.write(f"  cell:      {first.cell_address}  ({first.cell_label})\n")
            handle.write(f"  graph:     {first.graph_value!r}\n")
            handle.write(f"  mvp:       {first.mvp_value!r}\n")
            handle.write(f"  abs_diff:  {first.abs_diff!r}\n")
            handle.write(f"  rel_diff:  {first.rel_diff!r}\n")
        if failures:
            handle.write(f"\nFAILING COMPARISONS ({len(failures)}):\n")
            for comparison in failures:
                handle.write(
                    f"  {comparison.scenario_id} :: {comparison.cell_address} "
                    f"({comparison.cell_label}) graph={comparison.graph_value!r} "
                    f"mvp={comparison.mvp_value!r} abs_diff={comparison.abs_diff!r}\n"
                )
        if flagged:
            handle.write(
                "\nMATCHED ERROR VALUES (both oracles returned the same Excel "
                "error; fails the run unless the scenario sets "
                "expects_error_values=True or --allow-matched-errors is passed):\n"
            )
            for comparison in flagged:
                handle.write(f"  {comparison.scenario_id} :: ")
                handle.write(f"{comparison.cell_address} ({comparison.cell_label})\n")
                handle.write(f"    graph: {comparison.graph_value!r}\n")
                handle.write(f"    mvp:   {comparison.mvp_value!r}\n")


def load_exported_library(import_root: Path, package_name: str) -> ModuleType:
    root_str = str(import_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return importlib.import_module(package_name)


class FormulaEvaluatorGraphOracle:
    """Golden oracle: ``FormulaEvaluator`` over the extraction dependency graph."""

    def __init__(self, config: DifferentialConfig) -> None:
        if not config.targets:
            raise RuntimeError(
                "DifferentialConfig.targets is empty; cannot build the graph oracle."
            )
        if config.bindings_path is None:
            raise RuntimeError(
                "DifferentialConfig.bindings_path is missing; cannot build the graph oracle."
            )
        from tests.differential.differential_test_graph import MvpGraphDriver

        self._driver = MvpGraphDriver(
            config.workbook_path,
            targets=config.targets,
            bindings_path=config.bindings_path,
        )
        self._baselines_recorded = False
        self._baseline_cells: frozenset[str] = frozenset()

    def record_baselines(self, cells: frozenset[str]) -> None:
        self._driver.record_input_baselines(cells)
        self._baseline_cells = cells
        self._baselines_recorded = True

    def __call__(
        self, scenario: Scenario, output_addresses: tuple[str, ...]
    ) -> dict[str, Any]:
        if not self._baselines_recorded:
            raise RuntimeError(
                "Graph oracle baselines were not recorded before the sweep."
            )
        logger.info("Graph oracle: %s", scenario.id)
        self._driver.reset_inputs(self._baseline_cells)
        self._driver.set_inputs(inputs_for_excel(scenario))
        return {address: self._driver.read(address) for address in output_addresses}


def _verify_paths(config: DifferentialConfig) -> None:
    if not config.workbook_path.is_file():
        raise FileNotFoundError(
            f"Workbook not found: {config.workbook_path}. "
            "Populate data/ and workbook_config.py before running parity tests."
        )
    if (
        not (config.package_dir / "__init__.py").is_file()
        or not (config.package_dir / "api.py").is_file()
    ):
        raise FileNotFoundError(
            f"Exported package incomplete at {config.package_dir} "
            "(expected __init__.py and api.py). "
            "Run 'uv run python -m src.extraction_pipeline' to regenerate."
        )


def _workbook_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_input_symmetry(scenarios: tuple[Scenario, ...]) -> None:
    """Every graph write must be expressible as a ``compute_*`` argument when configured."""
    expressible = expressible_input_cells()
    if expressible is None:
        return

    offenders: dict[str, list[str]] = {}
    for scenario in scenarios:
        rogue = sorted(set(inputs_for_excel(scenario)) - expressible)
        if rogue:
            offenders[scenario.id] = rogue
    if offenders:
        details = "; ".join(
            f"{scenario_id}: {cells}" for scenario_id, cells in offenders.items()
        )
        raise RuntimeError(
            "Input-symmetry pre-flight failed — these graph writes have no "
            f"compute_* counterpart in the exported API: {details}. "
            "Either bind them as inputs (and re-export) or remove them from "
            "the scenario's graph writes."
        )


def _check_staleness(config: DifferentialConfig) -> None:
    fixture = (
        config.package_dir.parent / "tests" / "fixtures" / config.workbook_path.name
    )
    if fixture.is_file():
        current = _workbook_sha256(config.workbook_path)
        exported = _workbook_sha256(fixture)
        if current != exported:
            raise RuntimeError(
                "Workbook SHA-256 mismatch: the workbook has changed since the "
                f"package was exported (current {current[:12]}…, export-time "
                f"{exported[:12]}…). Re-run the extraction pipeline before "
                "trusting parity results."
            )
        return
    data_path = config.package_dir / "data.py"
    if not data_path.is_file():
        return
    if config.workbook_path.stat().st_mtime > data_path.stat().st_mtime:
        logger.warning(
            "Workbook is newer than exported data.py; regenerate dist/ if constants changed."
        )


def _validate_workbook_hooks() -> None:
    hooks = {
        "build_scenarios": build_scenarios,
        "output_cell_labels": output_cell_labels,
        "inputs_for_excel": inputs_for_excel,
        "mvp_outputs_for_scenario": mvp_outputs_for_scenario,
    }
    missing = [name for name in _REQUIRED_WORKBOOK_HOOKS if not callable(hooks[name])]
    if missing:
        raise RuntimeError(
            "Missing workbook-specific hook(s): "
            f"{', '.join(missing)}. Author them in "
            "tests/differential/differential_test_exported_library.py."
        )
    if not build_scenarios():
        raise RuntimeError(
            "No differential scenarios configured. Author build_scenarios(), "
            "output_cell_labels(), inputs_for_excel(), and "
            "mvp_outputs_for_scenario() in "
            "tests/differential/differential_test_exported_library.py."
        )
    if not output_cell_labels():
        raise RuntimeError(
            "output_cell_labels() returned no cells. Mirror your output bindings "
            "as (label, address) pairs, typically via specs_from_output_series()."
        )


def run_differential_test(
    config: DifferentialConfig,
    *,
    graph_oracle: GraphOracle | None = None,
    mvp_oracle: MvpOracle | None = None,
) -> int:
    _verify_paths(config)
    _validate_workbook_hooks()
    _check_staleness(config)

    api = load_exported_library(config.import_root, config.package_name)
    scenarios = build_scenarios()
    _verify_input_symmetry(scenarios)
    cell_labels = output_cell_labels()
    output_addresses = tuple(address for _, address in cell_labels)

    if graph_oracle is None:
        graph_driver = FormulaEvaluatorGraphOracle(config)
        axes = (
            Axis(
                name="scenarios",
                points=tuple(
                    AxisPoint(label=scenario.id, scenario=scenario)
                    for scenario in scenarios
                ),
            ),
        )
        graph_driver.record_baselines(
            collect_scenario_input_addresses(axes, inputs_for_excel)
        )
        graph_oracle = graph_driver
    if mvp_oracle is None:

        def mvp_oracle(scenario: Scenario) -> dict[str, Any]:
            return mvp_outputs_for_scenario(api, scenario)

    comparisons: list[Comparison] = []
    for scenario in scenarios:
        try:
            graph_outputs = graph_oracle(scenario, output_addresses)
        except Exception as exc:
            logger.exception("Graph oracle crashed on %s.", scenario.id)
            comparisons.extend(
                crash_comparisons(scenario, cell_labels, exc, crashed_oracle="graph")
            )
            continue
        try:
            mvp_outputs = mvp_oracle(scenario)
        except Exception as exc:
            logger.exception("MVP oracle crashed on %s.", scenario.id)
            comparisons.extend(
                crash_comparisons(
                    scenario,
                    cell_labels,
                    exc,
                    crashed_oracle="mvp",
                    graph_outputs=graph_outputs,
                )
            )
            continue
        try:
            comparisons.extend(
                compare_scenario(
                    scenario,
                    graph_outputs,
                    mvp_outputs,
                    cell_labels,
                    atol=config.atol,
                    rtol=config.rtol,
                )
            )
        except Exception as exc:
            logger.exception(
                "Comparison stage crashed on %s; recording as failure.", scenario.id
            )
            comparisons.extend(
                crash_comparisons(
                    scenario,
                    cell_labels,
                    exc,
                    crashed_oracle="comparison",
                    graph_outputs=graph_outputs,
                    mvp_outputs=mvp_outputs,
                )
            )
            continue

    workbook_sha256 = _workbook_sha256(config.workbook_path)
    environment = _environment_info()

    config.report_dir.mkdir(parents=True, exist_ok=True)
    write_csv_report(comparisons, config.report_dir / "parity_report.csv")
    write_txt_summary(
        comparisons,
        config.report_dir / "parity_report.txt",
        config=config,
        environment=environment,
        workbook_sha256=workbook_sha256,
    )

    failed = sum(1 for comparison in comparisons if not comparison.passed)
    flagged = sum(1 for comparison in comparisons if comparison.flagged_matched_error)
    logger.info("Done. Failures: %d / %d", failed, len(comparisons))
    if flagged:
        log = logger.warning if config.allow_matched_errors else logger.error
        log(
            "Matched error values in %d comparison(s); see MATCHED ERROR VALUES in %s "
            "(set Scenario.expects_error_values=True when intentional)",
            flagged,
            config.report_dir / "parity_report.txt",
        )
    return parity_exit_code(
        failed=failed,
        flagged_matched_errors=flagged,
        allow_matched_errors=config.allow_matched_errors,
    )


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        args = parse_args(argv)
        config = config_from_args(Path(__file__).resolve(), args)
        return run_differential_test(config)
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 2
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 2
    except Exception:
        logger.exception("Differential test failed with an unhandled exception.")
        return 2


# --------------------------------------------------------------------------
# Workbook-specific hooks — Q-CRAFT scenario matrix (see artifacts/differential_scenario_spec.md).
# --------------------------------------------------------------------------

from tests.differential.qcraft_scenario_matrix import (  # noqa: I001
    build_library_scenarios as build_scenarios,
    expressible_input_cells,
    inputs_for_excel,
    mvp_outputs_for_scenario,
    output_cell_labels,
)


if __name__ == "__main__":
    sys.exit(main())
