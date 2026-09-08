# AxiShell AI Production Readiness

## Local release checks

Run the following from the project directory before a release:

```powershell
python -m py_compile .\Uniexcel.py .\axishell_runtime.py .\test_phase6_regression.py .\test_phase10_regression.py
python -m unittest .\test_phase6_regression.py .\test_phase10_regression.py
streamlit run .\Uniexcel.py
```

Use the running application to perform the browser smoke checks below.

## Browser smoke checks

- Upload a small CSV and an `.xlsx` workbook; verify the profile, scope selector, filters, exports, and lineage panel.
- Check the upload flow, empty-data state, invalid-file feedback, Focus Mode, and `Show another welcome` in a current Chromium-, Firefox-, and WebKit-based browser.
- Navigate interactive controls by keyboard and confirm the visible focus outline. Enable a reduced-motion preference and confirm nonessential transitions are minimized.
- Verify the layout at narrow and wide desktop widths. This application is designed for desktop data analysis; mobile use is supported only as a constrained viewing experience.
- If AI analysis is enabled in the deployment, test it with a non-sensitive sample and verify consent behavior with a sample that contains a field classified as sensitive.

## Deployment configuration

- Install the dependencies in `requirements.txt` in a supported Python environment.
- Configure `OPENAI_API_KEY` only when optional AI analysis is intended. Do not place keys in source code, spreadsheets, or UI fields.
- Set `AXISHELL_OPENAI_MODEL` only when the deployment has access to the chosen model.
- Put the Streamlit service behind the organization’s normal HTTPS, authentication, network, backup, and monitoring controls when handling non-public data.
- Keep the process and its temporary workspace on infrastructure approved for the uploaded-data classification.

## Operational model and support boundary

The in-app Operational Status panel exposes session-only telemetry. AxiShell AI intentionally does not persist uploaded data or analytics logs itself. Production deployments should therefore collect service health, errors, latency, and resource metrics at the hosting layer, without recording raw upload contents or sensitive computed findings.

The application is an exploratory analysis tool, not a system of record or an automated decision-maker. Users must validate inputs, heuristics, findings, exports, and decisions—especially for financial, health, employment, legal, or other sensitive use cases.

## Scale strategy

The application enforces upload, worksheet, row, and column limits before analysis. Repeated dataset profiles and quality-score calculations are cached in the Streamlit session/runtime. For workloads that exceed the documented limits, use a dedicated data-processing service or pre-aggregate the source rather than increasing limits without load testing and privacy review.

## Continuous improvement

Review anonymized, organization-approved feedback and representative non-sensitive datasets before changing semantic roles, templates, or recommendations. Add a regression case for every confirmed issue before releasing its fix. Do not collect raw uploaded rows through feedback mechanisms.
