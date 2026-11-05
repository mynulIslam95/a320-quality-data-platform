import unittest
from src.generate_demo_data import generate
from src.pipeline import TABLES, read_csv, validate, run

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate()

    def test_demo_data(self):
        data = {name: read_csv(name) for name in TABLES}
        self.assertEqual(validate(data), [])
        self.assertEqual(len(data["aircraft"]), 120)
        self.assertEqual(len(data["inspections"]), 960)

    def test_orphan_detected(self):
        data = {name: read_csv(name) for name in TABLES}
        data["inspections"][0]["aircraft_id"] = "UNKNOWN"
        self.assertTrue(any("orphan" in issue for issue in validate(data)))

    def test_pipeline(self):
        self.assertTrue(run()["passed"])

if __name__ == "__main__":
    unittest.main()
