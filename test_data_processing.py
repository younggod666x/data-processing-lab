import os
import tempfile
import unittest

from data_processing import DataLoader, Table, average_temperature


class TableTests(unittest.TestCase):
    def setUp(self):
        self.table = Table(
            ('country', 'temperature'),
            (
                {'country': 'Germany', 'temperature': '8.5'},
                {'country': 'Spain', 'temperature': '15.0'},
            ),
        )

    def test_filter_returns_matching_rows_and_preserves_columns(self):
        german_cities = self.table.filter(lambda row: row['country'] == 'Germany')

        self.assertEqual(german_cities.columns, ('country', 'temperature'))
        self.assertEqual(len(german_cities), 1)
        self.assertEqual(
            list(german_cities),
            [{'country': 'Germany', 'temperature': '8.5'}],
        )
        self.assertEqual(len(self.table), 2)

    def test_iteration_does_not_expose_internal_rows(self):
        row = next(iter(self.table))
        row['country'] = 'Changed'

        self.assertEqual(
            list(self.table)[0],
            {'country': 'Germany', 'temperature': '8.5'},
        )

    def test_empty_filter_preserves_schema_and_aggregates_empty_values(self):
        empty_table = self.table.filter(lambda row: False)

        self.assertEqual(empty_table.columns, self.table.columns)
        self.assertEqual(len(empty_table), 0)
        self.assertEqual(empty_table.aggregate('country', len), 0)
        with self.assertRaises(ValueError):
            empty_table.aggregate('temperature', average_temperature)

    def test_aggregate_applies_function_to_column_values(self):
        average = self.table.aggregate(
            'temperature',
            lambda values: sum(float(value) for value in values) / len(values),
        )

        self.assertEqual(average, 11.75)

    def test_aggregate_rejects_unknown_columns(self):
        with self.assertRaises(KeyError):
            self.table.aggregate('missing', len)


class DataLoaderTests(unittest.TestCase):
    def test_load_csv_returns_table_with_header_and_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, 'cities.csv')
            with open(filepath, 'w', newline='', encoding='utf-8') as csv_file:
                csv_file.write('city,country\nBerlin,Germany\nMadrid,Spain\n')

            table = DataLoader.load_csv(filepath)

        self.assertEqual(table.columns, ('city', 'country'))
        self.assertEqual(
            list(table),
            [
                {'city': 'Berlin', 'country': 'Germany'},
                {'city': 'Madrid', 'country': 'Spain'},
            ],
        )


if __name__ == '__main__':
    unittest.main()
