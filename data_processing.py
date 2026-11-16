import csv
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, TypeVar


Result = TypeVar('Result')
Row = Dict[str, str]


class DataLoader:
    """Load CSV files as lists of dictionaries."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = Path(base_path) if base_path is not None else Path(__file__).parent.resolve()

    def load_csv(self, filename: str) -> List[Row]:
        filepath = self.base_path / filename
        with filepath.open(newline='', encoding='utf-8') as csv_file:
            rows = csv.DictReader(csv_file)
            if rows.fieldnames is None:
                raise ValueError("CSV file must contain a header row")
            return [dict(row) for row in rows]


class Table:
    """A named collection of dictionary rows with filtering and aggregation."""

    def __init__(
        self,
        table_name: str,
        table: Iterable[Mapping[str, str]],
        columns: Optional[Sequence[str]] = None,
    ):
        self.table_name = table_name
        self.table = [dict(row) for row in table]
        self.columns = tuple(columns) if columns is not None else (
            tuple(self.table[0]) if self.table else tuple()
        )
        if len(set(self.columns)) != len(self.columns):
            raise ValueError("Table columns must be unique")
        expected_columns = set(self.columns)
        if any(set(row) != expected_columns for row in self.table):
            raise ValueError("Each row must contain exactly the table columns")

    def filter(self, condition: Callable[[Mapping[str, str]], bool]) -> 'Table':
        filtered_rows = [row for row in self.table if condition(dict(row))]
        return Table(self.table_name + '_filtered', filtered_rows, self.columns)

    def aggregate(
        self,
        aggregation_function: Callable[[List[object]], Result],
        aggregation_key: str,
    ) -> Result:
        if aggregation_key not in self.columns:
            raise KeyError("Unknown table column: {}".format(aggregation_key))
        values: List[object] = [row[aggregation_key] for row in self.table]
        if values:
            try:
                values = [float(value) for value in values]
            except (TypeError, ValueError):
                pass
        return aggregation_function(values)

    def join(self, other: 'Table', key: str) -> 'Table':
        if key not in self.columns or key not in other.columns:
            raise KeyError("Join key must exist in both tables: {}".format(key))

        overlapping_columns = (set(self.columns) & set(other.columns)) - {key}
        if overlapping_columns:
            raise ValueError(
                "Tables have ambiguous non-key columns: {}".format(
                    ', '.join(sorted(overlapping_columns))
                )
            )

        joined_columns = self.columns + tuple(
            column for column in other.columns if column != key
        )
        joined_rows = []
        right_rows_by_key = {}
        for right_row in other.table:
            right_rows_by_key.setdefault(right_row[key], []).append(right_row)

        for left_row in self.table:
            for right_row in right_rows_by_key.get(left_row[key], []):
                joined_row = dict(left_row)
                joined_row.update(
                    (column, value)
                    for column, value in right_row.items()
                    if column != key
                )
                joined_rows.append(joined_row)

        return Table(
            '{}_{}_joined'.format(self.table_name, other.table_name),
            joined_rows,
            joined_columns,
        )

    def __iter__(self) -> Iterator[Row]:
        return (dict(row) for row in self.table)

    def __len__(self) -> int:
        return len(self.table)

    def __str__(self) -> str:
        return self.table_name + ':' + str(self.table)


class DB:
    """An in-memory collection of named tables."""

    def __init__(self):
        self.tables: List[Table] = []

    def insert(self, table: Table) -> None:
        if any(existing.table_name == table.table_name for existing in self.tables):
            raise ValueError("A table named {!r} is already in the database".format(
                table.table_name
            ))
        self.tables.append(table)

    def search(self, table_name: str) -> Table:
        for table in self.tables:
            if table.table_name == table_name:
                return table
        raise KeyError("No table named {!r} is in the database".format(table_name))


def main() -> None:
    loader = DataLoader()
    cities = loader.load_csv('Cities.csv')
    cities_table = Table('cities', cities)
    countries = loader.load_csv('Countries.csv')
    countries_table = Table('countries', countries)

    database = DB()
    database.insert(cities_table)
    database.insert(countries_table)

    cities_table = database.search('cities')
    print("List all cities in Italy:")
    italian_cities = cities_table.filter(lambda city: city['country'] == 'Italy')
    print(italian_cities)
    print()

    print("Average temperature for all cities in Italy:")
    print(italian_cities.aggregate(lambda values: sum(values) / len(values), 'temperature'))
    print()

    countries_table = database.search('countries')
    print("List all non-EU countries:")
    non_eu_countries = countries_table.filter(lambda country: country['EU'] == 'no')
    print(non_eu_countries)
    print()

    print("Number of countries that have coastline:")
    coastal_countries = countries_table.filter(
        lambda country: country['coastline'] == 'yes'
    )
    print(coastal_countries.aggregate(lambda values: len(values), 'coastline'))
    print()

    joined_table = cities_table.join(countries_table, 'country')
    print("First 5 entries of the joined table (cities and countries):")
    for row in joined_table.table[:5]:
        print(row)
    print()

    print("Cities whose temperatures are below 5.0 in non-EU countries:")
    cold_non_eu_cities = joined_table.filter(lambda row: row['EU'] == 'no').filter(
        lambda row: float(row['temperature']) < 5.0
    )
    print(cold_non_eu_cities.table)
    print()

    print("The min and max temperatures for cities in EU countries that do not have coastlines")
    eu_without_coastline = joined_table.filter(lambda row: row['EU'] == 'yes').filter(
        lambda row: row['coastline'] == 'no'
    )
    print("Min temp:", eu_without_coastline.aggregate(lambda values: min(values), 'temperature'))
    print("Max temp:", eu_without_coastline.aggregate(lambda values: max(values), 'temperature'))
    print()


if __name__ == '__main__':
    main()
