import csv
import os
from typing import Callable, Dict, Iterable, Iterator, List, Mapping, Tuple, TypeVar


Result = TypeVar('Result')


class Table:
    def __init__(self, columns: Iterable[str], rows: Iterable[Mapping[str, str]]):
        self._columns: Tuple[str, ...] = tuple(columns)
        if len(set(self._columns)) != len(self._columns):
            raise ValueError("Table columns must be unique")

        self._rows: List[Dict[str, str]] = []
        expected_columns = set(self._columns)
        for row in rows:
            if set(row) != expected_columns:
                raise ValueError("Each row must contain exactly the table columns")
            self._rows.append({column: row[column] for column in self._columns})

    @property
    def columns(self) -> Tuple[str, ...]:
        return self._columns

    def __iter__(self) -> Iterator[Dict[str, str]]:
        return (dict(row) for row in self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def filter(self, condition: Callable[[Mapping[str, str]], bool]) -> 'Table':
        matching_rows = (
            row for row in self._rows if condition(dict(row))
        )
        return Table(self._columns, matching_rows)

    def aggregate(
        self,
        aggregation_key: str,
        aggregation_function: Callable[[List[str]], Result],
    ) -> Result:
        """Pass column values to the function, including an empty list for empty tables."""
        if aggregation_key not in self._columns:
            raise KeyError("Unknown table column: {}".format(aggregation_key))
        values = [row[aggregation_key] for row in self._rows]
        return aggregation_function(values)


class DataLoader:
    @staticmethod
    def load_csv(filepath: str) -> Table:
        with open(filepath, newline='', encoding='utf-8') as csv_file:
            rows = csv.DictReader(csv_file)
            if rows.fieldnames is None:
                raise ValueError("CSV file must contain a header row")
            return Table(rows.fieldnames, rows)


def average_temperature(values: List[str]) -> float:
    if not values:
        raise ValueError("Cannot average an empty temperature column")
    return sum(float(value) for value in values) / len(values)


def main() -> None:
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Cities.csv')
    cities = DataLoader.load_csv(data_path)

    # Print first 5 cities only
    for city in list(cities)[:5]:
        print(city)

    # Print the average temperature of all the cities
    print("The average temperature of all the cities:")
    print(cities.aggregate('temperature', average_temperature))
    print()

    # Print all cities in Germany
    german_cities = cities.filter(lambda city: city['country'] == 'Germany')
    for city in german_cities:
        print(city)

    # Print all cities in Spain with a temperature above 12°C
    spanish_cities = cities.filter(
        lambda city: city['country'] == 'Spain' and float(city['temperature']) > 12
    )
    for city in spanish_cities:
        print(city)

    # Count the number of unique countries
    unique_country_count = cities.aggregate('country', lambda values: len(set(values)))
    print("The number of unique countries:")
    print(unique_country_count)

    # Print the average temperature for all the cities in Germany
    print("The average temperature for all the cities in Germany:")
    print(german_cities.aggregate('temperature', average_temperature))

    # Print the max temperature for all the cities in Italy
    italian_cities = cities.filter(lambda city: city['country'] == 'Italy')
    print("The max temperature for all the cities in Italy:")
    print(italian_cities.aggregate('temperature', lambda values: max(map(float, values))))


if __name__ == '__main__':
    main()
