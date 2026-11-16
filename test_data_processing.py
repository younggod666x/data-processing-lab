import tempfile
import unittest
from pathlib import Path

from data_processing import DB, DataLoader, Table


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

    def test_join_combines_matching_rows_and_omits_duplicate_key(self):
        country_table = Table(
            'countries',
            [
                {'country': 'Germany', 'EU': 'yes'},
                {'country': 'France', 'EU': 'yes'},
            ],
        )

        joined = self.table.join(country_table, 'country')

        self.assertEqual(joined.table_name, 'cities_countries_joined')
        self.assertEqual(
            joined.table,
            [{'country': 'Germany', 'temperature': '8.5', 'EU': 'yes'}],
        )
        self.assertEqual(
            joined.columns,
            ('country', 'temperature', 'EU'),
        )

    def test_join_rejects_missing_key_and_ambiguous_columns(self):
        other = Table('other', [{'country': 'Germany', 'temperature': '9.0'}])

        with self.assertRaises(KeyError):
            self.table.join(other, 'missing')
        with self.assertRaises(ValueError):
            self.table.join(other, 'country')


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

    def test_countries_dataset_supports_expected_join_results(self):
        loader = DataLoader()
        cities = Table('cities', loader.load_csv('Cities.csv'))
        countries = Table('countries', loader.load_csv('Countries.csv'))
        joined = cities.join(countries, 'country')
        eu_landlocked = joined.filter(
            lambda row: row['EU'] == 'yes' and row['coastline'] == 'no'
        )

        self.assertEqual(
            countries.filter(lambda row: row['coastline'] == 'yes').aggregate(
                lambda values: len(values), 'coastline'
            ),
            29,
        )
        self.assertEqual(len(joined), len(cities))
        self.assertEqual(
            eu_landlocked.aggregate(lambda values: min(values), 'temperature'),
            4.54,
        )
        self.assertEqual(
            eu_landlocked.aggregate(lambda values: max(values), 'temperature'),
            10.34,
        )


class DBTests(unittest.TestCase):
    def test_insert_and_search_named_table(self):
        table = Table('cities', [{'city': 'Augsburg'}])
        database = DB()
        database.insert(table)

        self.assertIs(database.search('cities'), table)
        self.assertEqual(database.tables, [table])

    def test_insert_rejects_duplicate_names_and_search_missing_table(self):
        database = DB()
        database.insert(Table('cities', [{'city': 'Augsburg'}]))

        with self.assertRaises(ValueError):
            database.insert(Table('cities', [{'city': 'Berlin'}]))
        with self.assertRaises(KeyError):
            database.search('countries')


if __name__ == '__main__':
    unittest.main()
