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

    def __iter__(self) -> Iterator[Row]:
        return (dict(row) for row in self.table)

    def __len__(self) -> int:
        return len(self.table)

    def __str__(self) -> str:
        return self.table_name + ':' + str(self.table)


def main() -> None:
    loader = DataLoader()
    cities = loader.load_csv('Cities.csv')
    cities_table = Table('cities', cities)

    print(cities_table.aggregate(lambda values: sum(values) / len(values), 'temperature'))
    print()

    german_cities = cities_table.filter(lambda city: city['country'] == 'Germany')
    print("All the cities in Germany:")
    for city in german_cities.table:
        print([city['city'], city['country']])
    print()

    spanish_cities = cities_table.filter(
        lambda city: city['country'] == 'Spain' and float(city['temperature']) > 12.0
    )
    print("All the cities in Spain with temperature above 12 C:")
    for city in spanish_cities.table:
        print([city['city'], city['country'], city['temperature']])
    print()

    print("The number of unique countries is:")
    print(cities_table.aggregate(lambda values: len(set(values)), 'country'))
    print()

    german_average = german_cities.aggregate(
        lambda values: sum(values) / len(values), 'temperature'
    )
    print("The average temperature of all the cities in Germany:")
    print(german_average)
    print()

    italian_maximum = cities_table.filter(
        lambda city: city['country'] == 'Italy'
    ).aggregate(lambda values: max(values), 'temperature')
    print("The max temperature of all the cities in Italy:")
    print(italian_maximum)
    print()


if __name__ == '__main__':
    main()
