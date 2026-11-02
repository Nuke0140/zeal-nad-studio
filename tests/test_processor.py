import io
import unittest

import pandas as pd

from core.processor import run_generate_report, run_merge_files


class GenerateReportTests(unittest.TestCase):
    def test_promotion_note_header_whitespace_does_not_blank_result(self):
        source = io.StringIO(
            "Username,Course Code,Course Name,Full Name,Promotion Note \n"
            "241001,BTechCSE,B.Tech CSE,Amit Kumar,sem_all_clear\n"
        )

        result = run_generate_report(source, lambda _: None)

        self.assertTrue(result["ok"])
        generated = pd.read_excel(result["buffer"], engine="openpyxl")
        self.assertEqual(generated.loc[0, "RESULT"], "Pass")


class MergeFilesTests(unittest.TestCase):
    def test_blank_update_values_preserve_master_fields(self):
        master = pd.DataFrame(
            [
                {
                    "REGN_NO": "241001",
                    "RROLL": "241001001",
                    "CNAME": "Amit Kumar",
                    "RESULT": "A. T. K. T",
                    "CGPA": 0.0,
                }
            ]
        )
        update = pd.DataFrame(
            [
                {
                    "REGN_NO": "241001",
                    "RROLL": "241001001",
                    "CNAME": "   ",
                    "RESULT": "",
                    "CGPA": 0.0,
                }
            ]
        )
        master_file = io.BytesIO()
        update_file = io.BytesIO()
        master.to_excel(master_file, index=False)
        update.to_excel(update_file, index=False)
        master_file.seek(0)
        update_file.seek(0)

        result = run_merge_files(master_file, update_file, lambda _: None)

        self.assertTrue(result["ok"])
        merged = pd.read_excel(result["buffer"], engine="openpyxl")
        self.assertEqual(merged.loc[0, "CNAME"], "Amit Kumar")
        self.assertEqual(merged.loc[0, "RESULT"], "A. T. K. T")
        self.assertEqual(merged.loc[0, "CGPA"], 0)


if __name__ == "__main__":
    unittest.main()
