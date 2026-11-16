# Object-Oriented Data Processing and Joins Lab

## Lab overview

This lab models CSV datasets as named tables, refactors city analysis into an
object-oriented design, and combines related city and country data with an
inner join on a shared key.

## Project structure

```text
data-processing-lab/
|-- README.md
|-- Countries.csv
|-- Cities.csv
|-- data_processing.py
\-- test_data_processing.py
```

## Design overview

- `DataLoader` stores a base directory and loads a CSV file into a list of
  dictionaries. CSV fields remain strings in the source rows.
- `Table` stores a `table_name`, rows in `table`, and the table's column names.
  `filter(condition)` creates a new named table with the matching rows.
  `aggregate(function, key)` applies a function to one column; if every value
  in that column is numeric, values are passed as floats. An empty table passes
  an empty list to the aggregation function. `join(other, key)` performs an
  inner join, preserving left-table row order and omitting the repeated key
  column. Joins reject a missing key or ambiguous duplicate non-key columns.
  `__str__` displays the table name and rows.
- `DB` is an in-memory list of tables. `insert(table)` adds a uniquely named
  table, and `search(table_name)` returns it. Duplicate names are rejected and
  searching for a missing name raises `KeyError`.

## How to run and test

Run the city and country analysis from the repository directory:

```bash
python data_processing.py
```

Run the tests with Python's standard library test runner:

```bash
python -m unittest -v
```
