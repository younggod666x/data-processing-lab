import csv
import os


def filter_items(condition, dict_list):
    return [item for item in dict_list if condition(item)]


def aggregate(aggregation_key, aggregation_function, dict_list):
    values = [item[aggregation_key] for item in dict_list]
    return aggregation_function(values)

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

cities = []
with open(os.path.join(__location__, 'Cities.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        cities.append(dict(r))

# Print first 5 cities only
for city in cities[:5]:
    print(city)

# Print the average temperature of all the cities
print("The average temperature of all the cities:")
average_temperature = aggregate(
    'temperature',
    lambda values: sum(float(value) for value in values) / len(values),
    cities,
)
print(average_temperature)
print()

# Print all cities in Germany

german_cities = filter_items(lambda city: city['country'] == 'Germany', cities)
for city in german_cities:
    print(city)

# Print all cities in Spain with a temperature above 12°C

spanish_cities = filter_items(
    lambda city: city['country'] == 'Spain' and float(city['temperature']) > 12,
    cities,
)
for city in spanish_cities:
    print(city)

# Count the number of unique countries

unique_country_count = aggregate('country', lambda values: len(set(values)), cities)
print("The number of unique countries:")
print(unique_country_count)

# Print the average temperature for all the cities in Germany

german_average_temperature = aggregate(
    'temperature',
    lambda values: sum(float(value) for value in values) / len(values),
    german_cities,
)
print("The average temperature for all the cities in Germany:")
print(german_average_temperature)

# Print the max temperature for all the cities in Italy

italian_cities = filter_items(lambda city: city['country'] == 'Italy', cities)
italian_max_temperature = aggregate(
    'temperature',
    lambda values: max(float(value) for value in values),
    italian_cities,
)
print("The max temperature for all the cities in Italy:")
print(italian_max_temperature)
