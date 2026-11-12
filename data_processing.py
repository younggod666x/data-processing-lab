import csv, os

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
temps = []
for city in cities:
    temps.append(float(city['temperature']))
print(sum(temps)/len(temps))
print()

# Print the average temperature of all the cities
print("The average temperature of all the cities:")
temps = [float(city['temperature']) for city in cities]
print(sum(temps)/len(temps))
print()

# Print all cities in Germany

for city in cities:
    if city['country'] == 'Germany':
        print(city)

# Print all cities in Spain with a temperature above 12°C

for city in cities:
    if city['country'] == 'Spain' and float(city['temperature']) > 12:
        print(city)

# Count the number of unique countries

countries = set()
for city in cities:
    countries.add(city['country'])
print("The number of unique countries:")
print(len(countries))

# Print the average temperature for all the cities in Germany

german_temps = []
for city in cities:
    if city['country'] == 'Germany':
        german_temps.append(float(city['temperature']))
print("The average temperature for all the cities in Germany:")
print(sum(german_temps) / len(german_temps))

# Print the max temperature for all the cities in Italy

italian_temps = []
for city in cities:
    if city['country'] == 'Italy':
        italian_temps.append(float(city['temperature']))
print("The max temperature for all the cities in Italy:")
print(max(italian_temps))
