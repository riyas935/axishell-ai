"""Production-readiness configuration and session-safe operational helpers."""

APP_VERSION = "1.0.0"
APP_RELEASE = "Phase 10"

SUPPORT_BOUNDARIES = [
    "AxiShell AI analyzes uploaded Excel and CSV tables in the active Streamlit session; it is not a system of record.",
    "The application does not execute spreadsheet formulas or macros and does not persist uploaded data or analytics logs itself.",
    "Outputs are exploratory aids. Users remain responsible for validating decisions, exports, and domain-specific conclusions.",
    "Optional AI analysis sends only bounded computed summaries after the required consent controls; it does not send raw spreadsheet rows.",
]


def build_operational_snapshot(
    dataset_rows,
    dataset_columns,
    source_tables,
    uploaded_files,
    elapsed_seconds,
    focus_mode,
):
    """Return display-safe, non-persistent session telemetry for the UI."""
    dataset_rows = max(0, int(dataset_rows or 0))
    dataset_columns = max(0, int(dataset_columns or 0))
    source_tables = max(0, int(source_tables or 0))
    uploaded_files = max(0, int(uploaded_files or 0))
    elapsed_seconds = max(0.0, float(elapsed_seconds or 0.0))

    state = "Ready" if dataset_rows else "Awaiting data"
    mode = "Focus Mode" if focus_mode else "Guided Mode"
    return [
        {"Area": "Session status", "Status": state, "Detail": f"{mode}; {elapsed_seconds:.1f}s in the current app session."},
        {"Area": "Active scope", "Status": f"{dataset_rows:,} rows", "Detail": f"{dataset_columns:,} columns across {source_tables:,} source table(s)."},
        {"Area": "Upload batch", "Status": f"{uploaded_files:,} file(s)", "Detail": "Limits and validation are enforced before analysis."},
        {"Area": "Observability", "Status": "Session-only", "Detail": "No uploaded data or analytics activity is logged persistently by the application."},
    ]
