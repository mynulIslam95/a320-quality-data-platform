import json
import unittest
from pathlib import Path
from src.generate_demo_data import generate
from src.pipeline import read_csv, TABLES, validate

ROOT = Path(__file__).resolve().parents[1]

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate()

    def test_contract_keys(self):
        contract = json.loads((ROOT / 'contracts/data_contract.json').read_text())
        self.assertEqual(contract['contract_version'], '1.0.0')
        self.assertEqual(set(contract['tables']), set(TABLES))

    def test_aircraft_id_format(self):
        import re
        contract = json.loads((ROOT / 'contracts/data_contract.json').read_text())
        self.assertTrue(all(re.fullmatch(contract['aircraft_id_pattern'], row['aircraft_id'])
                            for row in read_csv('aircraft')))

    def test_repeatable_generation(self):
        before = (ROOT / 'data/raw/aircraft.csv').read_bytes()
        generate()
        self.assertEqual(before, (ROOT / 'data/raw/aircraft.csv').read_bytes())

    def test_missing_reference_rejected(self):
        data = {name: read_csv(name) for name in TABLES}
        data['actions'][0]['finding_id'] = 'FND-99999'
        self.assertTrue(any('orphan actions' in issue for issue in validate(data)))

if __name__ == '__main__':
    unittest.main()
