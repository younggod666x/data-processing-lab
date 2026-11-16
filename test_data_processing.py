import tempfile
import unittest
from pathlib import Path

from data_processing import DataLoader, Table


class TableTests(unittest.TestCase):
    def setUp(self):
        self.table = Table(
            'cities',
            [
                {'country': 'Germany', 'temperature': '8.5'},
                {'country': 'Spain', 'temperature': '15.0'},
            ],
        )

    def test_filter_returns_named_table_with_matching_rows(self):
        filtered = self.table.filter(lambda row: row['country'] == 'Germany')

        self.assertEqual(filtered.table_name, 'cities_filtered')
        self.assertEqual(
            filtered.table,
            [{'country': 'Germany', 'temperature': '8.5'}],
        )
        self.assertEqual(self.table.table[0]['country'], 'Germany')

    def test_filter_preserves_columns_for_empty_result(self):
        filtered = self.table.filter(lambda row: False)

        self.assertEqual(filtered.columns, self.table.columns)
        self.assertEqual(filtered.table, [])
        self.assertEqual(filtered.aggregate(lambda values: len(values), 'country'), 0)

    def test_aggregate_converts_numeric_strings_for_numeric_operations(self):
        average = self.table.aggregate(
            lambda values: sum(values) / len(values),
            'temperature',
        )

        self.assertEqual(average, 11.75)

    def test_aggregate_preserves_text_values(self):
        countries = self.table.aggregate(lambda values: sorted(set(values)), 'country')

        self.assertEqual(countries, ['Germany', 'Spain'])

    def test_aggregate_rejects_unknown_columns(self):
        with self.assertRaises(KeyError):
            self.table.aggregate(len, 'missing')

    def test_string_representation_includes_name_and_rows(self):
        self.assertEqual(
            str(self.table),
            "cities:[{'country': 'Germany', 'temperature': '8.5'}, "
            "{'country': 'Spain', 'temperature': '15.0'}]",
        )


class DataLoaderTests(unittest.TestCase):
    def test_load_csv_returns_list_of_dictionary_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / 'cities.csv'
            filepath.write_text('city,country\nBerlin,Germany\nMadrid,Spain\n', encoding='utf-8')

            rows = DataLoader(temp_dir).load_csv('cities.csv')

        self.assertEqual(
            rows,
            [
                {'city': 'Berlin', 'country': 'Germany'},
                {'city': 'Madrid', 'country': 'Spain'},
            ],
        )


if __name__ == '__main__':
    unittest.main()
