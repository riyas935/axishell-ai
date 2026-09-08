"""Regression checks for Phase 6 helpers without starting the Streamlit UI."""
import ast
import json
import unittest
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pandas as pd


APP_PATH = Path(__file__).with_name("Uniexcel.py")
REQUIRED_FUNCTIONS = {
    "clean_column_headers",
    "normalize_starter_schema",
    "clean_universal_df",
    "infer_column_type",
    "build_dataset_profile",
    "scan_xlsx_safety",
    "build_integrity_summary",
    "build_quality_scorecard",
    "build_deterministic_findings",
    "build_ai_analysis_context",
    "request_ai_analysis",
    "process_data_sources",
}


def load_phase6_helpers():
    tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
    namespace = {
        "os": __import__("os"),
        "pd": pd,
        "warnings": __import__("warnings"),
        "BytesIO": BytesIO,
        "ZipFile": ZipFile,
        "BadZipFile": __import__("zipfile").BadZipFile,
        "STARTER_SCHEMA_COLUMNS": ["Product", "Units Sold", "Revenue", "Region"],
        "SOURCE_COLUMNS": ["Source File", "Source Sheet"],
        "MAX_UPLOAD_FILES": 10,
        "MAX_FILE_SIZE_BYTES": 25 * 1024 * 1024,
        "MAX_SHEETS_PER_WORKBOOK": 25,
        "MAX_ROWS_PER_TABLE": 250_000,
        "MAX_COLUMNS_PER_TABLE": 250,
        "MAX_TOTAL_ROWS": 500_000,
        "DEFAULT_OPENAI_MODEL": "gpt-5.6-sol",
        "MAX_AI_CONTEXT_CHARS": 12_000,
        "json": json,
    }
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in REQUIRED_FUNCTIONS:
            node.decorator_list = []
            module = ast.Module(body=[node], type_ignores=[])
            exec(compile(module, str(APP_PATH), "exec"), namespace)
    return namespace


class FakeUpload:
    def __init__(self, name, data, size=None):
        self.name = name
        self._data = data
        self.size = len(data) if size is None else size

    def getvalue(self):
        return self._data


class FakeResponses:
    def __init__(self):
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        return type("Response", (), {"output_text": "Grounded answer from the supplied context."})()


class FakeOpenAIClient:
    def __init__(self):
        self.responses = FakeResponses()


class Phase6RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_phase6_helpers()

    def test_formula_detection_never_executes_workbook_content(self):
        buffer = BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr("xl/worksheets/sheet1.xml", "<worksheet><f>SUM(A1:A2)</f></worksheet>")
        has_macros, has_formulas, error = self.helpers["scan_xlsx_safety"](buffer.getvalue())
        self.assertFalse(has_macros)
        self.assertTrue(has_formulas)
        self.assertEqual(error, "")

    def test_oversized_upload_is_rejected_before_parsing(self):
        upload = FakeUpload("too_large.csv", b"name,value\nA,1\n", size=26 * 1024 * 1024)
        dataframe, reports, lineage = self.helpers["process_data_sources"]([upload])
        self.assertTrue(dataframe.empty)
        self.assertTrue(lineage.empty)
        self.assertEqual(reports[0]["status"], "Limit Exceeded")

    def test_csv_ingestion_records_lineage_and_source_metadata(self):
        upload = FakeUpload("people.csv", b"Employee,Salary\nAda,100\nBen,200\n")
        dataframe, reports, lineage = self.helpers["process_data_sources"]([upload])
        self.assertEqual(reports[0]["status"], "Valid")
        self.assertEqual(len(dataframe), 2)
        self.assertEqual(dataframe["Source File"].iloc[0], "people")
        self.assertEqual(lineage.loc[0, "Loaded Rows"], 2)
        self.assertIn("Normalized headers", lineage.loc[0, "Transformations"])

    def test_integrity_summary_reports_formula_and_missing_value_risks(self):
        dataframe = pd.DataFrame({"Record ID": ["1", "2"], "Amount": [10, None]})
        profile = self.helpers["build_dataset_profile"](dataframe)
        lineage = pd.DataFrame([{"Source": "test", "Formulas Detected": True}])
        summary, warnings_list = self.helpers["build_integrity_summary"](dataframe, profile, lineage)
        self.assertIn("Formula sources", summary["Check"].tolist())
        self.assertTrue(any("missing" in warning.lower() for warning in warnings_list))
        self.assertTrue(any("Formula" in warning for warning in warnings_list))

    def test_quality_scorecard_uses_documented_deductions(self):
        dataframe = pd.DataFrame({"Value": [1, 1, None], "Category": ["A", "A", "A"]})
        profile = self.helpers["build_dataset_profile"](dataframe)
        score, rating, scorecard = self.helpers["build_quality_scorecard"](dataframe, profile)
        self.assertLess(score, 100)
        self.assertIn(rating, {"Good", "Needs review", "High risk"})
        self.assertIn("Quality score", scorecard["Metric"].tolist())

    def test_deterministic_findings_include_methods_and_context(self):
        dataframe = pd.DataFrame({
            "Date": ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01", "2026-05-01"],
            "Amount": [1, 2, 3, 4, 100],
            "Amount Copy": [1, 2, 3, 4, 100],
            "Segment": ["Core", "Core", "Core", "Core", "Other"],
        })
        profile = self.helpers["build_dataset_profile"](dataframe)
        semantic = pd.DataFrame({
            "Column": dataframe.columns,
            "Applied Role": ["Date", "Currency / Amount", "Currency / Amount", "Category"],
        })
        findings = self.helpers["build_deterministic_findings"](
            dataframe, profile, semantic, "Scope: test. No field filters applied."
        )
        self.assertIn("Calculation", findings.columns)
        self.assertIn("Active Context", findings.columns)
        self.assertIn("Limitation", findings.columns)
        self.assertTrue({"Outliers", "Relationship", "Distribution"}.intersection(findings["Finding Type"]))

    def test_ai_context_excludes_raw_rows_and_keeps_provenance(self):
        dataframe = pd.DataFrame({"Private Note": ["secret-value"], "Amount": [42]})
        profile = self.helpers["build_dataset_profile"](dataframe)
        semantic = pd.DataFrame({
            "Column": ["Private Note", "Amount"],
            "Inferred Type": ["text", "numeric"],
            "Applied Role": ["Sensitive Personal Data", "Currency / Amount"],
            "Source": ["Automatic", "Automatic"],
            "Confidence": ["High", "High"],
            "Evidence": ["Sensitive field", "Amount field"],
        })
        score, _, scorecard = self.helpers["build_quality_scorecard"](dataframe, profile)
        findings = pd.DataFrame([{
            "Finding Type": "Coverage", "Severity": "Info", "Fields": "Amount",
            "Observation": "No alert.", "Calculation": "Rule check.",
            "Active Context": "Scope: test.", "Limitation": "Review manually.",
        }])
        context = self.helpers["build_ai_analysis_context"](profile, semantic, scorecard, findings, "Scope: test.")
        self.assertIn("computed summaries", context)
        self.assertIn("Quality score", context)
        self.assertNotIn("secret-value", context)
        self.assertGreaterEqual(score, 0)

    def test_ai_request_disables_storage_and_uses_supplied_context(self):
        client = FakeOpenAIClient()
        answer = self.helpers["request_ai_analysis"](
            "test-key", "What should I review?", "computed context", client=client
        )
        self.assertEqual(answer, "Grounded answer from the supplied context.")
        self.assertFalse(client.responses.request["store"])
        self.assertEqual(client.responses.request["model"], "gpt-5.6-sol")
        self.assertIn("computed context", client.responses.request["input"])


if __name__ == "__main__":
    unittest.main()
