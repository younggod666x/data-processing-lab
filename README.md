# Object-Oriented Data Processing Lab

## Lab overview

This lab refactors the city CSV analysis into an object-oriented design. A data
loader reads CSV rows, and a `Table` object groups those rows with operations
for filtering and aggregating values.

## Project structure

```text
data-processing-lab/
├── README.md
├── Cities.csv
├── data_processing.py
└── test_data_processing.py
```

## Design overview

- `DataLoader` stores a base directory and loads a named CSV file into a list
  of dictionaries. CSV values remain strings so rows retain the source data.
- `Table` stores a name, rows, and their column names. `filter` returns a new
  table containing matching rows. `aggregate` passes the selected column's
  values to a supplied function, converting the whole column to floats when
  every value is numeric. `__str__` displays the table name and rows.

## How to run and test

Run the city analysis from the repository directory:

```bash
python data_processing.py
```

Run the tests with Python's standard library test runner:

```bash
python -m unittest -v
```
