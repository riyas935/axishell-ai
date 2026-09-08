# AxiShell AI

A universal Excel and CSV analysis tool built with Streamlit, pandas, and Plotly.

AxiShell AI helps users upload structured data, understand its shape, explore quality signals, build schema-aware summaries, and review explainable findings. It is designed as an independent portfolio prototype for data analysis and AI-assisted application development.

> **Portfolio note:** Use fictional or non-sensitive data with the public demo. This project is an exploratory analysis tool, not a system of record or an automated decision-maker.

## Contents

- [What it does](#what-it-does)
- [Features](#features)
- [Project structure](#project-structure)
- [Run locally](#run-locally)
- [Run with Docker](#run-with-docker)
- [Run the tests](#run-the-tests)
- [Publish with Git](#publish-with-git)
- [Deploy to Streamlit Community Cloud](#deploy-to-streamlit-community-cloud)
- [Optional AI analysis](#optional-ai-analysis)
- [Data protection](#data-protection)
- [Current limitations](#current-limitations)
- [Future improvements](#future-improvements)

## What it does

AxiShell AI accepts Excel workbooks and CSV files from different domains. It preserves the uploaded schema, profiles columns, applies type-aware filters, and provides analysis tools without requiring a fixed sales dataset.

The original sales dashboard remains available as a compatibility template when the expected sales fields are present.

## Features

### Universal data ingestion

- Supports `.xlsx`, `.xls`, and `.csv` files.
- Supports multiple files and workbook sheets.
- Enforces a 25 MB per-file limit.
- Limits upload batches, workbook sheets, rows, and columns.
- Normalizes blank and duplicate headers.
- Preserves source file and sheet lineage.
- Blocks macro-enabled `.xlsx` workbooks.
- Does not execute spreadsheet formulas or macros.

### Data exploration

- Dataset overview and column profiles.
- Automatic type inference for numeric, date, categorical, boolean, text, and empty fields.
- Dynamic filters for numeric, date, categorical, and text fields.
- Searchable and sortable Data Explorer.
- CSV exports with sensitive-field acknowledgement controls.

### Analysis and insights

- User-selected measures and dimensions.
- Sum, average, median, minimum, maximum, count, and row-count analysis.
- Date grouping by day, month, quarter, or year.
- Recommended charts for dates, categories, and numeric distributions.
- Explainable semantic roles and optional Sales, HR, Finance, Operations, and Healthcare guidance.
- Deterministic quality scorecards and findings for missing values, duplicates, outliers, distributions, trends, and relationships.

### Optional AI assistance

- Uses computed summaries instead of raw spreadsheet rows.
- Requires an explicit acknowledgement for datasets with potential sensitive fields.
- Uses `store=False` for OpenAI Responses API requests.
- Keeps conversation history in the current Streamlit session only.
- Requires an environment or Streamlit secret named `OPENAI_API_KEY`.

## Project structure

```text
.
|-- Uniexcel.py                  # Streamlit application
|-- axishell_runtime.py          # Release metadata and operational helpers
|-- requirements.txt             # Python dependencies
|-- Dockerfile                   # Repeatable container deployment
|-- .streamlit/config.toml       # Streamlit server configuration
|-- test_phase6_regression.py    # Ingestion, safety, privacy, and AI tests
|-- test_phase10_regression.py   # Production-readiness helper tests
|-- PRODUCTION_READINESS.md      # Deployment checklist and support boundary
|-- project_progress.md          # Project roadmap and implementation record
`-- .gitignore                   # Local secrets, data, logs, and generated files
```

## Run locally

### Requirements

- Python 3.12 or newer
- Windows, macOS, or Linux

### Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run Uniexcel.py
```

macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run Uniexcel.py
```

Open the local address shown by Streamlit, usually `http://localhost:8501`.

## Run with Docker

Build and start the application:

```bash
docker build -t axishell-ai .
docker run --rm -p 8501:8501 axishell-ai
```

Then open `http://localhost:8501`.

The container listens on port `8501` and includes a Streamlit health check.

## Run the tests

From the project directory:

```powershell
python -m py_compile .\Uniexcel.py .\axishell_runtime.py .\test_phase6_regression.py .\test_phase10_regression.py
python -m unittest .\test_phase6_regression.py .\test_phase10_regression.py
```

The regression suite covers upload boundaries, workbook safety checks, lineage, integrity warnings, quality scoring, deterministic findings, AI context boundaries, release metadata, and accessibility contracts.

## Publish with Git

The project is published at [github.com/riyas935/axishell-ai](https://github.com/riyas935/axishell-ai).

From the project folder, create a local Git history:

```powershell
git init
git add .
git commit -m "Initial project version"
```

Review the files with `git status` before committing. The `.gitignore` file excludes secrets, uploaded data, logs, Python cache files, and the old backup script.

Connect the project to GitHub and push the `main` branch:

```powershell
git remote add origin https://github.com/riyas935/axishell-ai.git
git branch -M main
git push -u origin main
```

For later changes:

```powershell
git add .
git commit -m "Describe the change"
git push
```

## Deploy to Streamlit Community Cloud

1. Confirm the code is pushed to [github.com/riyas935/axishell-ai](https://github.com/riyas935/axishell-ai).
2. Open [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Choose **Create app** or **Deploy an app**.
4. Select repository `riyas935/axishell-ai`.
5. Select the `main` branch.
6. Set the main file path to `Uniexcel.py`.
7. Click **Deploy** and wait for the app URL.
8. Open the deployed URL and test it with fictional sample data.
9. If optional AI analysis is enabled, add `OPENAI_API_KEY` through the app's secrets settings. Never commit the key to GitHub.

Streamlit Community Cloud provides HTTPS for the deployed app. Do not upload real personal, financial, health, employment, or company-confidential data to a public portfolio demo.

## Optional AI analysis

AI analysis is disabled unless an API key is configured.

PowerShell session example:

```powershell
$env:OPENAI_API_KEY = "your-key-is-set-locally-only"
python -m streamlit run Uniexcel.py
```

Do not place the key in source files, the README, spreadsheets, screenshots, or Git history. For Streamlit deployment, configure it through the platform's secrets interface.

The model can be changed with `AXISHELL_OPENAI_MODEL` when the deployment has access to the selected model.

## Data protection

- Uploaded data is processed in the active Streamlit session.
- Upload ingestion is not globally cached.
- The application does not provide persistent upload storage or analytics logging.
- Formula cells are analyzed as stored values and are not recalculated.
- Macro-bearing `.xlsx` files are blocked.
- Potential sensitive fields are flagged before data-bearing exports.
- AI requests receive bounded computed summaries and not raw spreadsheet rows.

These controls reduce risk but do not replace hosting security, authentication, or organizational privacy requirements.

## Current limitations

- Type and semantic-role inference is heuristic and should be reviewed.
- Legacy `.xls` files cannot receive the same inspection as `.xlsx` files.
- AI analysis requires the OpenAI SDK, API access, network access, and a configured model.
- The app is a large single Streamlit application file.
- Public hosting is appropriate only for fictional or non-sensitive demo data.
- Hosting-level authentication, monitoring, and resource controls depend on the selected platform.

## Future improvements

- Add representative non-sensitive demo files and screenshots.
- Expand focused regression coverage for more workbook edge cases.
- Add broader browser smoke testing across desktop browsers.
- Improve modular separation of ingestion, analysis, and UI components.
- Add deployment-specific authentication and monitoring when moving beyond a portfolio demo.

## License

Add a license before sharing the repository publicly. Choose one that matches how you want others to use the project.
