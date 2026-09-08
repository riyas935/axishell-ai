# AxiShell AI Project Progress

## Original Project State And Purpose

The original project was a single-file Streamlit application named `Uniexcel.py`.
It was built as a sales analytics dashboard using Python, Streamlit, pandas, and Plotly.

The original dashboard expected Excel files with a fixed sales schema:

- `Product`
- `Units Sold`
- `Revenue`
- `Region`

It calculated sales-focused KPIs and visualizations such as total revenue, total units sold, average selling price, revenue growth, regional contribution, product trends, and product performance summaries.

## Current AxiShell AI Project Goal

**AxiShell AI** is an AI-assisted universal Excel data-analysis application. It began as a sales analytics dashboard and is being transformed into a schema-independent analyzer for arbitrary Excel and CSV datasets.

Its long-term goal is to help users upload structured data from different domains and receive reliable analytics, visualizations, and, eventually, AI-assisted insights. Sales analytics are a compatibility path, not the product's defining schema or destination.

## Completed Phase 1 Changes

Phase 1 has been implemented.

Completed changes:

- Renamed visible app branding to `AxiShell AI`.
- Updated the Streamlit page title to `AxiShell AI - Universal Excel Analyzer`.
- Neutralized public-facing UI copy where possible.
- Reframed the current required columns as a Phase 1 starter format.
- Kept the existing sales-compatible analytics intact for stability.
- Renamed the uploaded-file identity field from `Period` to `Source File`.
- Updated filters, charts, and comparisons to use `Source File`.
- Updated export filenames to use `axishell_ai_*` names.
- Removed visible corrupted/emoji status text from modified UI areas.
- Created a backup before implementation: `Uniexcel_backup_phase1.py`.

Validation completed:

- `python -m py_compile .\Uniexcel.py` passed.
- Python imports for `streamlit`, `pandas`, and `plotly` passed.

## Completed Phase 2 Changes

Phase 2 has been implemented.

Completed changes:

- Replaced fixed sales-only ingestion with universal tabular ingestion.
- Added support for uploaded `.xlsx`, `.xls`, and `.csv` files.
- Excel workbooks are loaded sheet-by-sheet using `sheet_name=None`.
- CSV files are loaded as a single `CSV` source sheet.
- Original dataset columns are preserved instead of forcing every upload into the sales schema.
- Blank rows and blank columns are removed during ingestion.
- Blank or unnamed headers are normalized to stable names such as `Column 1`.
- Duplicate column names are made unique with suffixes.
- Added `Source File` and `Source Sheet` metadata columns.
- Added generic column type inference: numeric, numeric-like, datetime, datetime-like, categorical, boolean, text, and empty.
- Added a universal dataset overview with row count, column count, missing cells, duplicate rows, and detected type counts.
- Added a column profile table with missing values, inferred type, pandas type, unique counts, and numeric summary values.
- Added a loaded-data preview section.
- Added CSV downloads for arbitrary datasets:
  - `axishell_ai_loaded_data.csv`
  - `axishell_ai_column_profile.csv`
- Kept the previous sales-compatible dashboard available only when the loaded dataset contains `Product`, `Units Sold`, `Revenue`, and `Region`.
- Hid starter sales analytics for arbitrary datasets that do not contain the starter schema.
- Added an informational note that dynamic arbitrary-column filters are planned for Phase 3.

Validation completed:

- `python -m py_compile .\Uniexcel.py` passed.
- Dependency import check passed for `streamlit`, `pandas`, `plotly`, and `openpyxl`.
- Validated arbitrary CSV ingestion with an HR-style dataset containing employee, department, salary, and start-date columns.
- Confirmed arbitrary CSV profiling detects numeric, categorical, datetime-like, and source metadata columns.
- Confirmed arbitrary CSV datasets do not trigger the starter sales dashboard.
- Validated sales-compatible `.xlsx` ingestion with a generated workbook containing `Product`, `Units Sold`, `Revenue`, and `Region`.
- Confirmed sales-compatible datasets still produce `Avg Price` and retain the starter analytics path.

Files modified:

- `Uniexcel.py`
- `project_progress.md`

## Completed Phase 3 Changes

Phase 3: Dynamic Filters And Data Explorer has been implemented.

Completed changes:

- Replaced the fixed source, region, and product filter controls with schema-aware dynamic filters.
- Users can choose any loaded field to filter.
- Numeric and numeric-like fields use inclusive range sliders.
- Datetime and datetime-like fields use date-range controls.
- Categorical, boolean, and low-cardinality text fields use multi-select controls.
- High-cardinality text fields use case-insensitive contains search.
- Added a universal Data Explorer for every dataset, including starter sales datasets.
- The explorer searches across all fields, supports column visibility selection, optional sorting, and CSV export of its results.
- Kept starter sales analytics as a compatibility path when the starter schema is available.
- Removed the sales-only raw-data explorer because the universal explorer replaces it.
- Updated Phase 3 user-facing labels and footer copy.

Validation completed:

- `python -m py_compile .\Uniexcel.py` passed.
- Source review confirmed the arbitrary-schema path now renders the same dynamic filters and Data Explorer before starter-schema branching.

Files modified:

- `Uniexcel.py`
- `project_progress.md`

## Completed Phase 4 Changes

Phase 4: Schema-Aware Analytics And Visualization Builder has been implemented.

Completed changes:

- Added a universal analytics builder before the starter sales compatibility branch, so arbitrary datasets receive analytical output.
- Users can choose any inferred numeric or numeric-like field as a measure, or use row count when no numeric measure is available.
- Users can group analysis by detected categorical, boolean, or text fields.
- Users can group analysis by detected date or date-like fields at daily, monthly, quarterly, or yearly granularity.
- Added generic sum, average, median, minimum, maximum, and count aggregations for numeric measures.
- Added reusable aggregation tables and CSV export for the selected analysis.
- Added type-aware visualization recommendations and corresponding charts:
  - line charts for date-grouped analysis;
  - bar charts for categorical comparisons;
  - histograms for ungrouped numeric distributions; and
  - KPI cards for ungrouped row counts.
- Kept the original sales KPIs and charts as a conditional compatibility template only.

Validation completed:

- Direct aggregation checks passed for categorical numeric sums and date-grouped row counts using a representative HR-style dataset.
- `python -m py_compile .\Uniexcel.py` passed.

Files modified:

- `Uniexcel.py`
- `project_progress.md`

## Completed Phase 5 Changes

Phase 5: Domain Semantics And Analysis Templates has been implemented.

Completed changes:

- Added an explainable semantic-role profile for every loaded column.
- The automatic role inference recognizes identifiers, dates, currency/amounts, quantities, percentages/rates, categories, free text, and potential sensitive personal data.
- Each inferred role includes its source, confidence, and plain-language evidence.
- Users can override the role of any column or restore its automatic inference; overrides are retained in the Streamlit session and do not alter uploaded data.
- Added optional, non-destructive domain-template suggestions for Sales, HR, Finance, Operations, and Healthcare.
- Domain suggestions are based on detected column names and semantic roles and are presented as guidance, not as forced schema classification.
- Added template-specific guidance and a list of fields available to the selected template.
- Kept generic analytics available even when no domain template is detected or selected.

Validation completed:

- Semantic-role and domain-template checks passed with representative HR and finance-style datasets.
- Confirmed automatic roles for identifier, currency/amount, and date fields.
- Confirmed user overrides are marked with `User override` provenance.
- `python -m py_compile .\Uniexcel.py` passed.

Files modified:

- `Uniexcel.py`
- `project_progress.md`

## Completed Phase 6 Changes

Phase 6: Security, Data Integrity And Reliability has been implemented.

Completed changes:

- Added explicit upload boundaries: a maximum of 10 files per batch, 25 MB per file, 25 sheets per workbook, 250,000 rows per table, 250 columns per table, and 500,000 loaded rows per batch.
- Added structured validation outcomes for unsupported types, size or scope limits, invalid data, parsing failures, and macro-bearing workbooks.
- Added safe spreadsheet handling: `.xlsx` workbooks are inspected without execution before parsing; macro payloads are blocked; formula cells are disclosed and analyzed only as stored values; and legacy `.xls` uploads display a reliability note because they cannot receive the same inspection.
- Added CSV parsing safeguards, including malformed-row failure and a disclosed latin-1 fallback when UTF-8 decoding fails.
- Added a Dataset Scope control so users can analyze all loaded sources together or select one source sheet, avoiding accidental aggregation of unrelated tables.
- Added a Reliability, Lineage & Data Protection panel that shows per-sheet dimensions before and after cleaning, transformations applied, formula presence, and reproducible integrity checks.
- Added integrity checks for missing cells, duplicate rows, identifier-like fields, and formula sources.
- Added privacy-conscious export controls: potential sensitive-personal-data fields are highlighted, and data-bearing exports require an explicit authorization acknowledgement when those fields are detected.
- Documented the in-app processing boundary: uploaded data is not modified, formulas/macros are not executed, and the application does not implement persistent upload storage or analytics logging.
- Added `test_phase6_regression.py` with regression checks for formula detection, upload-size rejection, source lineage, and integrity warnings.

Validation completed:

- `python -m py_compile .\Uniexcel.py .\test_phase6_regression.py` passed.
- `python .\test_phase6_regression.py` passed: 4 tests.
- Dependency import check passed for `streamlit`, `pandas`, `plotly`, and `openpyxl`.

Files modified:

- `Uniexcel.py`
- `test_phase6_regression.py`
- `project_progress.md`

## Completed Phase 7 Changes

Phase 7: Deterministic Insight And Data-Quality Engine has been implemented.

Completed changes:

- Added an explainable 0–100 Data Quality Scorecard for the active dataset scope and filters.
- The score is reproducibly calculated from capped deductions for missing data, exact duplicate rows, numeric/date-like parse failures, and sparse columns; each scorecard row exposes its method and deduction.
- Added deterministic findings for missingness, exact duplicates, IQR-based numeric outliers, categorical concentration, monthly endpoint trends, and strong Pearson correlations.
- Findings exclude source metadata and avoid identifier/sensitive-personal-data fields for numeric outlier and relationship checks.
- Each finding records its fields, severity, calculation, active scope/filter context, and a clear limitation. Findings are explicitly presented as rule-based calculations, not AI-generated interpretations.
- Added CSV export for deterministic findings, using the existing sensitive-data export acknowledgement safeguard.
- Expanded `test_phase6_regression.py` to validate scorecard deductions and the provenance fields of deterministic findings.

Validation completed:

- `python -m py_compile .\Uniexcel.py .\test_phase6_regression.py` passed.
- `python .\test_phase6_regression.py` passed: 6 tests.

Files modified:

- `Uniexcel.py`
- `test_phase6_regression.py`
- `project_progress.md`

## Completed Phase 8 Changes

Phase 8: AI-Assisted Analysis has been implemented as an optional, OpenAI-backed feature.

Completed changes:

- Added an optional AI-Assisted Analysis interface for natural-language questions about the active dataset scope and filters.
- Integrated the OpenAI Responses API with `store=False` so API response storage is disabled for each request.
- Uses `gpt-5.6-sol` by default, with an `AXISHELL_OPENAI_MODEL` environment override for deployments that need a different permitted model.
- API credentials are accepted only from `OPENAI_API_KEY` in the environment or Streamlit secrets. The UI never asks users to enter or stores an API key.
- AI requests receive a bounded computed context: active scope/filter context, column and semantic profiles, the Phase 7 scorecard, and deterministic findings. Raw spreadsheet rows are not transmitted.
- Added a grounding instruction that requires the response to distinguish computed evidence from generated interpretation, disclose limitations, avoid causal claims, and avoid sensitive-data reconstruction.
- Added explicit consent before sending computed summaries for datasets containing potential sensitive personal-data fields.
- Added current-session AI response history with a clear control; the app does not persist conversation history itself.
- Added clear configuration and runtime failure messages without exposing credentials or internal exceptions.
- Added `requirements.txt` with the OpenAI SDK and existing runtime dependencies. Legacy `.xls` support is conditional below Python 3.14 because `xlrd` is not available for the active Python 3.14 environment.
- Expanded `test_phase6_regression.py` with mocked OpenAI checks proving raw rows are excluded from AI context and API calls set `store=False`.

Validation completed:

- `python -m py_compile .\Uniexcel.py .\test_phase6_regression.py` passed.
- `python .\test_phase6_regression.py` passed: 8 tests, including mocked AI context and Responses API behavior.
- Core dependency import check passed for `streamlit`, `pandas`, `plotly`, and `openpyxl`.

Validation limitation:

- The local `openai` SDK could not be installed in this environment: the first full dependency install was blocked by unavailable `xlrd` for Python 3.14, and the OpenAI-only installation stalled at the package source and was stopped. No live OpenAI request was made because no API credential was supplied. The app handles a missing SDK with a clear setup message.

Files modified:

- `Uniexcel.py`
- `test_phase6_regression.py`
- `requirements.txt`
- `project_progress.md`

## Completed Phase 9 Changes

Phase 9: Personality And Experience Layer has been implemented.

Completed changes:

- Added an optional personality layer with rotating welcome and loading messages.
- Added a lightweight original in-app guide, Axi, rendered as a code-native interface element rather than as a data-processing feature.
- Added a `Show another welcome` control so users can rotate the welcome message without affecting their data or analysis.
- Added friendly, action-oriented copy for the no-data, no-filter-results, demo, and file-validation states.
- Added Focus Mode in the sidebar. Focus Mode replaces personality copy with concise neutral language while preserving the same data, analytical, privacy, and safety behavior.
- Updated footer references to Phase 9.

Validation completed:

- `python -m py_compile .\Uniexcel.py .\test_phase6_regression.py` passed.
- `python .\test_phase6_regression.py` passed: 8 tests.
- Verified that personality state is isolated to Streamlit session/UI state and is not used by ingestion, filtering, analysis, exports, deterministic findings, or AI context construction.

Files modified:

- `Uniexcel.py`
- `project_progress.md`

## Completed Phase 10 Changes

Phase 10: Production Readiness, Scale And Continuous Improvement has been implemented for the current local Streamlit deployment model.

Completed changes:

- Added `axishell_runtime.py` to separate release metadata, support boundaries, and session-safe operational snapshot construction from the Streamlit interface.
- Added a session-only Operational Status & Support Boundary panel with active-scope information, upload-batch status, release metadata, and clear non-persistent observability disclosure.
- Added caching for repeat dataset-profile and data-quality-score calculations to reduce redundant work during Streamlit reruns.
- Added keyboard-visible focus styling and a reduced-motion media query for accessibility preferences.
- Added `PRODUCTION_READINESS.md` with release checks, browser smoke-test coverage, deployment configuration, support boundaries, scale guidance, monitoring boundaries, and a safe continuous-improvement workflow.
- Added `test_phase10_regression.py` covering production helper behavior, release metadata, support boundaries, Focus Mode, operational-panel presence, and accessibility CSS contracts.

Validation completed:

- `python -m py_compile .\Uniexcel.py .\axishell_runtime.py .\test_phase6_regression.py .\test_phase10_regression.py` passed.
- `python -m unittest .\test_phase6_regression.py .\test_phase10_regression.py` passed: 12 tests.
- Browser smoke checks and hosting-layer monitoring remain deployment responsibilities and are explicitly documented in `PRODUCTION_READINESS.md`; no live deployment or browser automation was available in this workspace.

Files modified:

- `Uniexcel.py`
- `axishell_runtime.py`
- `test_phase10_regression.py`
- `PRODUCTION_READINESS.md`
- `project_progress.md`

## Completed Phase 11 UX Consolidation

The user approved implementation of the visual-improvement recommendations one at a time before treating the full UX consolidation as complete.

Completed Phase 11 items:

- Added a compact, keyboard-accessible in-page workspace navigation strip that links to Overview, Insights, AI analysis, Data Explorer, schema-aware analytics, and the conditional sales template.
- Replaced the previously forced dark-mode state with a session-scoped Dark/Light theme selector in the sidebar. Theme changes affect presentation only; uploaded data, filters, and analysis are unchanged.
- Added a responsive dataset-health summary made of visual cards for quality score, deterministic findings, integrity-review items, and sensitive-field flags. Detailed lineage, integrity, scorecard, findings, and operational tables remain available in expanders for traceability.
- Added a responsive active-context bar beneath workspace navigation showing the selected data scope, active versus scoped row count, active-filter count, and data-protection state.
- Reorganized the sidebar so upload/status remains the primary panel, dataset scope is grouped with controls, type-aware filters are collapsed by default, and visual preferences are tucked into a separate lower expander.
- Added a shared Plotly chart-theme helper and applied it to generic and sales-template visualizations, giving them consistent palette, typography, transparent surfaces, axes, grids, hover labels, and theme-aware rendering without changing the underlying analyses.
- Replaced the sales-template regional contribution donut with a sorted horizontal bar chart that displays the same grouped revenue and contribution percentages more clearly at higher category counts. No source data, aggregation, filtering, export, or analytical calculation was changed.
- Added responsive, code-native visual empty states for no-data, no-filter-results, and insufficient-analysis-value conditions. The existing messages and application behavior remain intact.
- Corrected current release presentation by sourcing both application footers from the runtime release metadata and standardizing the operational-status separator to an ASCII-safe vertical bar. Historical roadmap references remain unchanged.
- Clarified action hierarchy without changing behavior: analysis generation, applying semantic-role settings, and the primary full-data export use primary actions; conversation clearing and secondary exports remain visually secondary.

Validation completed:

- `python -m py_compile .\Uniexcel.py .\axishell_runtime.py .\test_phase6_regression.py .\test_phase10_regression.py` passed.
- `python -m unittest .\test_phase6_regression.py .\test_phase10_regression.py` passed: 12 tests.

All ten Phase 11 UX recommendations are complete for the current local application scope.

## Important Architectural Decisions So Far

- The Streamlit UI remains in `Uniexcel.py`, while production runtime metadata and operational helpers are separated into `axishell_runtime.py`.
- Phase 1 intentionally preserved the existing analytics behavior.
- Phase 2 added universal ingestion and profiling without splitting the code into modules.
- Arbitrary datasets can now be loaded and profiled without `Product`, `Units Sold`, `Revenue`, and `Region`.
- The starter sales analytics remain as a conditional compatibility path.
- Phase 3 applies filters according to detected column type, without changing the original uploaded data.
- The universal Data Explorer is shared by arbitrary and starter-schema datasets.
- Phase 4 generic analytics are rendered before the starter-sales branch; the sales dashboard is retained only as a compatibility template.
- Phase 5 semantic roles and domain templates are advisory, explainable, and user-overridable; they do not modify raw data or force a dataset into a domain.
- Phase 6 blocks detected macro payloads and never executes formulas or spreadsheet macros.
- Users can scope analysis to an individual source sheet before applying filters, reducing the risk of combining unrelated tables.
- Dataset lineage records source/sheet identity, before-and-after dimensions, transformations, and formula detection; integrity findings are displayed alongside the active filtered scope.
- Potential sensitive data does not block analysis, but users must explicitly acknowledge responsibility before data-bearing exports are enabled.
- Phase 7 findings are deterministic and rule-based. They expose their calculations, active data context, and limitations; they do not infer causes or use an AI model.
- Phase 8 is optional and does not replace deterministic findings. It receives bounded computed context from the active filtered dataset rather than raw spreadsheet rows, uses an API-key environment/secret boundary, disables API response storage, and requires an additional acknowledgement for sensitive datasets.
- Phase 9 personality/experience features are optional UI state only. Focus Mode provides neutral presentation without changing analytical logic.
- Serious analytical findings, especially healthcare or financial insights, must keep a clear and professional tone.

## Eleven-Phase Product Roadmap

This is the authoritative roadmap for evolving AxiShell AI into a universal Excel analyzer. Defining a phase does not approve its implementation; Phases 1–9 are complete.

### Phase 1 — Product Foundation And Sales Compatibility

- **Objective:** Establish the AxiShell AI identity while keeping the original sales experience stable.
- **Dependencies:** None; this is the starting point.
- **Outcome:** AxiShell AI branding, source-file terminology, exports, and a preserved sales analytics compatibility path. **Complete.**

### Phase 2 — Universal Ingestion And Dataset Profiling

- **Objective:** Accept arbitrary tabular Excel and CSV data without requiring a sales schema.
- **Dependencies:** Phase 1 branding and compatibility baseline.
- **Outcome:** Multi-file and multi-sheet ingestion, normalized headers, source metadata, inferred types, dataset overview, column profiles, previews, and generic exports. **Complete.**

### Phase 3 — Dynamic Filters And Data Explorer

- **Objective:** Let users inspect any loaded schema through type-aware controls instead of fixed sales filters.
- **Dependencies:** Phase 2's normalized dataset and type profile.
- **Outcome:** Numeric ranges, date ranges, categorical selection, high-cardinality text search, universal table search/sort/column selection, and filtered CSV export. **Complete.**

### Phase 4 — Schema-Aware Analytics And Visualization Builder

- **Objective:** Replace sales-only analytical views with reusable analytics for arbitrary measures, dimensions, and dates.
- **Dependencies:** Phases 2–3; reliable type inference and filtered data.
- **Outcome:** User-selectable measures and groupings, generic aggregation and comparison tables, and chart recommendations based on selected fields and detected types. The existing sales charts remain an optional compatibility template. **Complete.**

### Phase 5 — Domain Semantics And Analysis Templates

- **Objective:** Recognize common business meanings without making the product depend on any one domain.
- **Dependencies:** Phase 4's generic analytics model and Phase 2 profiling metadata.
- **Outcome:** Explainable detection of likely identifiers, dates, currencies, amounts, categories, and domain signals; optional templates for domains such as sales, HR, finance, operations, and healthcare; and a user override for every inference. **Complete.**

### Phase 6 — Security, Data Integrity And Reliability

- **Objective:** Make uploaded-data analysis safe, traceable, resilient, and trustworthy before any AI-assisted insights are introduced.
- **Dependencies:** Phases 2–5, because protections must cover ingestion, profiling, filtering, templates, and visualization outputs.
- **Outcome:** File-size and format limits; secure parsing policy for spreadsheets; explicit handling of formulas, macros, malformed files, and unsupported readers; input validation and error taxonomy; dataset lineage and transformation summaries; integrity checks; privacy-conscious retention and logging rules; regression tests; and clear reliability warnings. **Complete.**

### Phase 7 — Deterministic Insight And Data-Quality Engine

- **Objective:** Produce reproducible, non-AI findings from the user's selected data and clearly expose data-quality risks.
- **Dependencies:** Phases 4–6, especially the security, lineage, and integrity baseline.
- **Outcome:** Rule-based trend, outlier, distribution, missingness, duplicate, and relationship findings; data-quality scorecards; and each finding linked to its fields, filters, calculations, and limitations. **Complete.**

### Phase 8 — AI-Assisted Analysis

- **Objective:** Add optional natural-language exploration and explanations that build on verified deterministic analysis rather than replace it.
- **Dependencies:** Phase 6 must be complete; Phase 7 provides grounded findings, provenance, and quality context.
- **Outcome:** Natural-language questions, guided follow-up analysis, plain-language chart and finding explanations, and AI responses that disclose assumptions, use the active filtered dataset, distinguish generated interpretation from computed facts, and preserve professional tone for sensitive domains. **Complete.**

### Phase 9 — Personality And Experience Layer

- **Objective:** Make the application welcoming and approachable without changing analytical logic or compromising clarity.
- **Dependencies:** Phases 4–8 interfaces and safety conventions.
- **Outcome:** Friendly upload, empty-state, and error copy; rotating welcome and loading messages; an optional original in-app guide; and Focus Mode for neutral presentation. Personality remains separate from data processing and serious findings remain professional. **Complete.**

### Phase 10 — Production Readiness, Scale And Continuous Improvement

- **Objective:** Prepare AxiShell AI for dependable real-world use across varied datasets and evolving user needs.
- **Dependencies:** Phases 4–9, including the security and AI safeguards.
- **Outcome:** Initial modular runtime boundary, performance and large-file strategy, accessibility safeguards, documented browser smoke testing, session-safe operational visibility, documented deployment/support boundaries, and ongoing regression coverage. Hosting-level monitoring, browser execution, and feedback review are documented deployment operations. **Complete for the current local application scope.**

### Phase 11 â€” UX Consolidation

- **Objective:** Improve visual hierarchy, scanability, consistency, and action clarity without changing analytical behavior.
- **Dependencies:** Phases 1â€“10 and user approval of the scoped visual recommendations.
- **Outcome:** Workspace navigation, selectable themes, context and health cards, sidebar grouping, shared chart styling, clearer contribution visualization, visual empty states, current release-label consistency, and primary/secondary action hierarchy. **Complete for the current local application scope.**

## Current Known Limitations

- The app can load and profile arbitrary schemas, but it is not yet a full universal analyzer.
- Starter sales analytics still require `Product`, `Units Sold`, `Revenue`, and `Region`.
- `.xls` support depends on the local Python environment having the required Excel reader dependency available.
- Legacy `.xls` files cannot receive the same macro/formula inspection as `.xlsx` files; the app clearly warns users to review their source.
- AI-assisted analysis requires a separately configured OpenAI API key, installed `openai` SDK, network access, and access to the configured model. Live API behavior has not been validated in this workspace because no credential was supplied and the SDK package source was unavailable.
- The Streamlit UI remains a large single file; only production runtime helpers have been modularized so far.
- A live Streamlit browser layout verification has not yet been performed in this workspace; the required smoke checks are documented for deployment.
- If users intentionally select `All loaded sources`, unrelated schemas can still be combined; the Dataset Scope selector provides a single-sheet alternative.
- Current type inference is heuristic and may misclassify ambiguous text, IDs, or date-like strings.
- Semantic roles and domain templates are heuristic guidance; users should review the displayed evidence and apply overrides when needed.
- Hosting-level monitoring, browser smoke-test execution, and organization-approved feedback review require deployment access and remain operational follow-through items.

## Current Project Status

The project is currently at the end of Phase 11 for the current local application scope.

`Uniexcel.py` is still the active application file.
`Uniexcel_backup_phase1.py` is the backup created before Phase 1 modifications.
`project_progress.md` is the persistent project context file.

Phases 2–10 now provide universal ingestion and profiling, dynamic filtering and exploration, schema-aware aggregation and visualization, explainable semantic and optional domain guidance, safety limits, integrity checks, source lineage, privacy-aware exports, regression coverage, reproducible data-quality findings, optional grounded AI explanations, a presentation-only personality layer with Focus Mode, and local production-readiness safeguards and documentation.

## Next Phase Approval Status

All eleven roadmap phases are implemented for the current local application scope. The next work should be deployment-specific operational follow-through: browser smoke testing, hosting-layer monitoring, load testing, and organization-approved feedback review.

## Mandatory Phase Completion Rule

After every implemented phase, `project_progress.md` must be updated before beginning the next phase.
