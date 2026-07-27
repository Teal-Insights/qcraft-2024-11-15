"""Exported-library differential test harness.

Compare the generated standalone package against Microsoft Excel via xlwings.
Workbook-specific scenario definitions live in
``tests/differential/qcraft_scenario_matrix.py`` (see ``artifacts/differential_scenario_spec.md``).

Run from the extraction repo after export::

    uv run python -m tests.differential.differential_test_exported_library

From the exported ``dist/`` project (Windows + Excel)::

    uv run --project dist --group validation python -m tests.differential.differential_test_exported_library --layout exported
"""

from __future__ import annotations

import argparse
import csv
import importlib
import logging
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from excel_grapher.core.address_keys import normalize_key, parse_address

from tests.differential.comparison_utils import (
    apply_health_expectation,
    classify_comparison,
)
from tests.differential.differential_excel import parity_exit_code
from tests.differential.differential_types import ATOL, RTOL, Scenario

logger = logging.getLogger(__name__)

LayoutName = Literal["repo", "exported"]


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


@dataclass(frozen=True)
class Comparison:
    scenario_id: str
    cell_address: str
    cell_label: str
    excel_value: Any
    mvp_value: Any
    abs_diff: float | None
    rel_diff: float | None
    passed: bool
    healthy: bool = False
    outcome: str = "mismatched"
    note: str = ""
    flagged_matched_error: bool = False


CSV_COLUMNS: tuple[str, ...] = (
    "scenario_id",
    "cell_address",
    "cell_label",
    "excel_value",
    "mvp_value",
    "passed",
    "healthy",
    "outcome",
    "abs_diff",
    "rel_diff",
    "note",
    "flagged_matched_error",
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


def _project_root_from_module(module_path: Path, layout: LayoutName) -> Path:
    return module_path.resolve().parents[2]


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
    repo_root = _project_root_from_module(module_path, layout)

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from src.pipeline_config import load_pipeline_config

    pipeline = load_pipeline_config(repo_root=repo_root)
    package_dir = pipeline.package_root
    package_slug = pipeline.dist_metadata.package_name
    library_name = pipeline.dist_metadata.library_name

    if layout == "exported":
        tests_root = module_path.parent
        dist_root = repo_root
        defaults = DifferentialConfig(
            workbook_path=tests_root / "fixtures" / pipeline.workbook_path.name,
            package_dir=dist_root / package_slug,
            package_name=f"{package_slug}.api",
            import_root=dist_root,
            report_dir=tests_root / "results" / "local",
            library_name=library_name,
        )
    else:
        defaults = DifferentialConfig(
            workbook_path=pipeline.workbook_path,
            package_dir=package_dir,
            package_name=f"dist.{package_slug}.api",
            import_root=repo_root,
            report_dir=repo_root / pipeline.differential_report_dir_rel,
            library_name=library_name,
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
    excel: Any,
    mvp: Any,
    *,
    atol: float,
    rtol: float,
    expects_error_values: bool = False,
) -> Comparison:
    passed, healthy, outcome, abs_diff, rel_diff, note = classify_comparison(
        excel, mvp, atol=atol, rtol=rtol
    )
    healthy = apply_health_expectation(
        expects_error_values=expects_error_values,
        parity_match=passed,
        healthy=healthy,
        outcome=outcome,
    )
    flagged_matched_error = (
        passed and outcome == "matched_error" and not expects_error_values
    )
    return Comparison(
        scenario_id=scenario_id,
        cell_address=cell_address,
        cell_label=cell_label,
        excel_value=excel,
        mvp_value=mvp,
        abs_diff=abs_diff,
        rel_diff=rel_diff,
        passed=passed,
        healthy=healthy,
        outcome=outcome,
        note=note,
        flagged_matched_error=flagged_matched_error,
    )


def compare_scenario(
    scenario: Scenario,
    excel_outputs: dict[str, Any],
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
            excel_outputs.get(cell_address),
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
    excel_outputs: Mapping[str, Any] | None = None,
    mvp_outputs: Mapping[str, Any] | None = None,
) -> list[Comparison]:
    err_repr = f"<exception: {type(exc).__name__}: {exc}>"
    if crashed_oracle in ("excel", "mvp"):
        note = f"{crashed_oracle} oracle crashed"
    else:
        note = f"{crashed_oracle} stage crashed ({err_repr})"
    return [
        Comparison(
            scenario_id=scenario.id,
            cell_address=cell_address,
            cell_label=cell_label,
            excel_value=(
                err_repr
                if crashed_oracle == "excel"
                else (excel_outputs or {}).get(cell_address)
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
                    comparison.excel_value,
                    comparison.mvp_value,
                    comparison.passed,
                    comparison.healthy,
                    comparison.outcome,
                    comparison.abs_diff,
                    comparison.rel_diff,
                    comparison.note,
                    comparison.flagged_matched_error,
                ]
            )


def _environment_info(excel_version: str | None) -> dict[str, str]:
    import platform
    import sys

    try:
        import xlwings

        xlwings_version = xlwings.__version__
    except Exception:  # pragma: no cover - xlwings always present in this repo
        xlwings_version = "unavailable"
    return {
        "python": sys.version.split()[0],
        "os": platform.platform(),
        "xlwings": xlwings_version,
        "excel": excel_version or "not launched",
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
    healthy = sum(1 for comparison in comparisons if comparison.healthy)
    matched_errors = sum(
        1 for comparison in comparisons if comparison.outcome == "matched_error"
    )
    health_rate = (100.0 * healthy / total) if total else 0.0
    flagged = [
        comparison for comparison in comparisons if comparison.flagged_matched_error
    ]
    failing_run = bool(failures) or bool(flagged and not config.allow_matched_errors)
    result = "FAIL" if failing_run else "PASS"
    health_result = "OK" if healthy == total else "WARN"
    first = failures[0] if failures else None

    with path.open("w", encoding="utf-8") as handle:
        handle.write(
            f"Parity report: exported {config.library_name} standalone library vs Excel\n"
        )
        handle.write(
            f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
        )
        handle.write(f"Workbook:  {config.workbook_path}\n")
        handle.write(
            f"Package:   {config.package_dir} (imported as {config.package_name})\n"
        )
        handle.write(f"Tolerance: atol = {config.atol}, rtol = {config.rtol}\n\n")
        handle.write(f"Workbook SHA-256: {workbook_sha256}\n\n")
        handle.write("ENVIRONMENT\n")
        handle.write(f"  Python:  {environment['python']}\n")
        handle.write(f"  OS:      {environment['os']}\n")
        handle.write(f"  xlwings: {environment['xlwings']}\n")
        handle.write(f"  Excel:   {environment['excel']}\n\n")
        handle.write(
            "PARITY (extraction agreement with Excel, including matched errors)\n"
        )
        handle.write(f"Total comparisons: {total}\n")
        handle.write(f"Passed:            {passed}\n")
        handle.write(f"Failed:            {len(failures)}\n")
        handle.write(f"Pass rate:         {pass_rate:.2f}%\n")
        handle.write("Acceptance bar:    100.00%\n")
        handle.write(f"Result:            {result}\n\n")
        handle.write("HEALTH (both sides numeric; matched errors excluded)\n")
        handle.write(f"Healthy:           {healthy}\n")
        handle.write(f"Matched errors:    {matched_errors}\n")
        if flagged:
            allowed_note = (
                " (allowed by --allow-matched-errors)"
                if config.allow_matched_errors
                else " (fails the run)"
            )
            handle.write(f"Flagged errors:    {len(flagged)} flagged{allowed_note}\n")
        handle.write(f"Health rate:       {health_rate:.2f}%\n")
        handle.write(f"Health result:     {health_result}\n")
        if first is not None:
            handle.write("\nFirst divergence:\n")
            handle.write(f"  scenario:  {first.scenario_id}\n")
            handle.write(f"  cell:      {first.cell_address}  ({first.cell_label})\n")
            handle.write(f"  excel:     {first.excel_value!r}\n")
            handle.write(f"  mvp:       {first.mvp_value!r}\n")
            handle.write(f"  abs_diff:  {first.abs_diff!r}\n")
            handle.write(f"  rel_diff:  {first.rel_diff!r}\n")
        if failures:
            handle.write(f"\nFAILING COMPARISONS ({len(failures)}):\n")
            for comparison in failures:
                handle.write(
                    f"  {comparison.scenario_id} :: {comparison.cell_address} "
                    f"({comparison.cell_label}) excel={comparison.excel_value!r} "
                    f"mvp={comparison.mvp_value!r} abs_diff={comparison.abs_diff!r} "
                    f"rel_diff={comparison.rel_diff!r}\n"
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
                handle.write(f"    excel: {comparison.excel_value!r}\n")
                handle.write(f"    mvp:   {comparison.mvp_value!r}\n")


def load_exported_library(import_root: Path, package_name: str) -> ModuleType:
    root_str = str(import_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return importlib.import_module(package_name)


def read_cells_batched(sheets: Any, addresses: Sequence[str]) -> dict[str, Any]:
    """Read cells with one COM span-read per (sheet, row) instead of per cell."""
    import re

    from fastpyxl.utils.cell import column_index_from_string, get_column_letter

    parsed: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for address in addresses:
        sheet, cell = parse_address(normalize_key(address))
        match = re.match(r"([A-Z]+)(\d+)", cell)
        if match is None:
            raise ValueError(f"Cannot parse cell reference {cell!r} from {address!r}")
        column, row = match.groups()
        parsed.setdefault((sheet, row), []).append((column, address))

    values: dict[str, Any] = {}
    for (sheet, row), columns in parsed.items():
        indices = sorted(column_index_from_string(c) for c, _ in columns)
        first, last = indices[0], indices[-1]
        span = (
            f"{get_column_letter(first)}{row}"
            if first == last
            else f"{get_column_letter(first)}{row}:{get_column_letter(last)}{row}"
        )
        raw = sheets[sheet].range(span).options(err_to_str=True).value
        row_values = [raw] if first == last else list(raw)
        for column, address in columns:
            values[address] = row_values[column_index_from_string(column) - first]
    return values


class XlwingsExcelOracle:
    """Golden-master oracle: fresh isolated Excel instance per scenario."""

    def __init__(self, workbook_path: Path) -> None:
        self.workbook_path = workbook_path
        self.excel_version: str | None = None

    def __call__(
        self, scenario: Scenario, output_addresses: tuple[str, ...]
    ) -> dict[str, Any]:
        import xlwings as xw

        logger.info("Excel oracle: %s", scenario.id)
        app = xw.App(visible=False, add_book=False)
        try:
            self.excel_version = str(app.version)
            workbook = app.books.open(str(self.workbook_path))
            try:
                app.calculation = "manual"
                for address, value in inputs_for_excel(scenario).items():
                    sheet, cell = parse_address(normalize_key(address))
                    workbook.sheets[sheet].range(cell).value = value
                workbook.app.calculate()
                return read_cells_batched(workbook.sheets, output_addresses)
            finally:
                workbook.close()
        finally:
            app.quit()


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
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_input_symmetry(scenarios: tuple[Scenario, ...]) -> None:
    """Standard §4.3: every Excel write must be expressible via a public setter.

    A cell outside EXPRESSIBLE_INPUT_CELLS would make the two oracles receive
    different inputs — an unsatisfiable comparison, not a parity failure.
    """
    from tests.differential.qcraft_scenario_matrix import EXPRESSIBLE_INPUT_CELLS

    offenders: dict[str, list[str]] = {}
    for scenario in scenarios:
        rogue = sorted(set(inputs_for_excel(scenario)) - EXPRESSIBLE_INPUT_CELLS)
        if rogue:
            offenders[scenario.id] = rogue
    if offenders:
        details = "; ".join(
            f"{scenario_id}: {cells}" for scenario_id, cells in offenders.items()
        )
        raise RuntimeError(
            "Input-symmetry pre-flight failed — these Excel writes have no "
            f"public-setter counterpart in the exported API: {details}. "
            "Either bind them as inputs (and re-export) or remove them from "
            "the scenario's Excel writes."
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


_REQUIRED_WORKBOOK_HOOKS: tuple[str, ...] = (
    "build_scenarios",
    "output_cell_labels",
    "inputs_for_excel",
    "apply_inputs_to_mvp",
    "mvp_outputs_for_scenario",
)


def _validate_workbook_hooks() -> None:
    hooks = {
        "build_scenarios": build_scenarios,
        "output_cell_labels": output_cell_labels,
        "inputs_for_excel": inputs_for_excel,
        "apply_inputs_to_mvp": apply_inputs_to_mvp,
        "mvp_outputs_for_scenario": mvp_outputs_for_scenario,
    }
    missing = [name for name in _REQUIRED_WORKBOOK_HOOKS if not callable(hooks[name])]
    if missing:
        raise RuntimeError(
            "Missing workbook-specific hook(s): "
            f"{', '.join(missing)}. Author them in "
            "tests/differential/qcraft_scenario_matrix.py."
        )
    if not build_scenarios():
        raise RuntimeError(
            "No differential scenarios configured. build_scenarios() returned none."
        )
    if not output_cell_labels():
        raise RuntimeError(
            "output_cell_labels() returned no cells. Mirror your output bindings "
            "as (label, address) pairs."
        )


def run_differential_test(
    config: DifferentialConfig,
    *,
    excel_oracle: Any = None,
    mvp_oracle: Any = None,
) -> int:
    _verify_paths(config)
    _validate_workbook_hooks()
    _check_staleness(config)

    scenarios = build_scenarios()
    _verify_input_symmetry(scenarios)

    if excel_oracle is None:
        excel_oracle = XlwingsExcelOracle(config.workbook_path)
    if mvp_oracle is None:
        api = load_exported_library(config.import_root, config.package_name)
        mvp_oracle = lambda scenario: mvp_outputs_for_scenario(api, scenario)  # noqa: E731

    cell_labels = output_cell_labels()
    output_addresses = tuple(address for _, address in cell_labels)

    comparisons: list[Comparison] = []
    for scenario in scenarios:
        try:
            excel_outputs = excel_oracle(scenario, output_addresses)
        except Exception as exc:
            logger.exception("Excel oracle crashed on %s.", scenario.id)
            comparisons.extend(
                crash_comparisons(scenario, cell_labels, exc, crashed_oracle="excel")
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
                    excel_outputs=excel_outputs,
                )
            )
            continue
        try:
            scenario_comparisons = compare_scenario(
                scenario,
                excel_outputs,
                mvp_outputs,
                cell_labels,
                atol=config.atol,
                rtol=config.rtol,
            )
        except Exception as exc:
            logger.exception("Comparison stage crashed on %s.", scenario.id)
            comparisons.extend(
                crash_comparisons(
                    scenario,
                    cell_labels,
                    exc,
                    crashed_oracle="comparison",
                    excel_outputs=excel_outputs,
                    mvp_outputs=mvp_outputs,
                )
            )
            continue
        comparisons.extend(scenario_comparisons)

    workbook_sha256 = _workbook_sha256(config.workbook_path)
    environment = _environment_info(getattr(excel_oracle, "excel_version", None))

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

from tests.differential.qcraft_scenario_matrix import (  # noqa: E402
    apply_inputs_to_mvp,
    build_scenarios,
    inputs_for_excel,
    mvp_outputs_for_scenario,
    output_cell_labels,
)


if __name__ == "__main__":
    sys.exit(main())
