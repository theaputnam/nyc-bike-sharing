##
# Connect to MySQL server (localhost), setup database with schema defined in 'database-setup.sql' file,
# read datasets, clean data, and insert the data into MySQL
##

import mysql.connector
import pandas as pd

# Fill in user credentials
config = {"user": "clemensheithecker", "password": "knLJ}tN4", "host": "localhost"}

# Connect to MySQL server with user credentials
connection = mysql.connector.connect(**config)

# Create cursor
cursor = connection.cursor(dictionary=True)

# Setup database and tables using 'database-setup.sql' SQL script
with open("database-setup.sql", "r") as sql_file:
    result_iterator = cursor.execute(sql_file.read(), multi=True)

    for result in result_iterator:
        print("Running query: ", result)
        print(f"Affected {result.rowcount} rows")

    connection.commit()


# Read and clean data

# Read bike data
bike_data = pd.read_csv(
    "data/JC-202110-citibike-tripdata.csv", index_col=False, delimiter=","
)

# Drop rows containing null values
print("Null values in bike_data: ", bike_data.isnull().values.any())
bike_data = bike_data.dropna()

# Clean station data

# Remove duplicate start stations
#
# Some stations have slighly different coordinates. This might be due to data
# inaccuracy. Since the geo-locational difference is neglectable, we take the
# mean of the coordinates for the affected stations.
start_station_data = bike_data[
    ["start_station_id", "start_station_name", "start_lat", "start_lng"]
]
start_station_data.columns = ["station_id", "station_name", "lat", "lng"]
station_data = start_station_data.groupby(
    ["station_id", "station_name"], as_index=False
).mean()

# Remove duplicate end stations
end_station_data = bike_data[
    ["end_station_id", "end_station_name", "end_lat", "end_lng"]
]
end_station_data.columns = ["station_id", "station_name", "lat", "lng"]
station_data = end_station_data.groupby(
    ["station_id", "station_name"], as_index=False
).mean()

# Merge start and end stations
station_data = pd.concat([start_station_data, end_station_data], ignore_index=True)
station_data = station_data.groupby(
    ["station_id", "station_name"], as_index=False
).mean()

print(station_data.head())
print("Number of stations: ", len(station_data))

# Read weather data
weather_data = pd.read_csv("data/2796493.csv", index_col=False, delimiter=",")

# Clean weather data

# Select columns of interest
weather_data = weather_data[["DATE", "TMIN", "TMAX", "PRCP"]]
print(weather_data.head())

# Clean ride data

# Select columns of interest
ride_data = bike_data[
    [
        "ride_id",
        "started_at",
        "ended_at",
        "start_station_id",
        "end_station_id",
        "member_casual",
    ]
]
print(ride_data.head())


# Insert data in database

# Insert station data
for index, row in station_data.iterrows():
    sql = "INSERT INTO station VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, tuple(row))
    print(f"Station record {index} inserted")

    connection.commit()

# Insert weather data
for index, row in weather_data.iterrows():
    sql = "INSERT INTO weather VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, tuple(row))
    print(f"Weather record {index} inserted")

    connection.commit()

# Insert ride data
for index, row in ride_data.iterrows():
    sql = "INSERT INTO ride (ride_id, start_date_time, end_date_time, start_station_id, end_station_id, customer_type) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, tuple(row))
    print(f"Ride record {index} inserted")

    connection.commit()
