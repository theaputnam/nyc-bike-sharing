##
# Connect to MySQL server (localhost), query database using 'analysis-rides.sql' file
# and visualize data
##

import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fill in user credentials
config = {"user": "root", "password": "123", "host": "localhost"}

# Connect to MySQL server with user credentials
connection = mysql.connector.connect(**config)

print(connection)

# Create cursor
cursor = connection.cursor(dictionary=True)


def executeSqlFile(path, cursor):
    """Execute a SQL script given a path and a cursor"""
    with open(path, "r") as sql_file:
        result_iterator = cursor.execute(sql_file.read(), multi=True)

    for result in result_iterator:
        print("Running query: ", result)
        print(f"Affected {result.rowcount} rows")

    connection.commit()


def sqlViewAsDataFrame(view, connection):
    """Query a SQL database and stores the output as a pandas DataFrame given a query and a connection"""
    query = f"SELECT * FROM {view}"
    df = pd.read_sql_query(sql=query, con=connection)
    return df


# Run station querys using 'analysis-stations.sql' SQL script
executeSqlFile("analysis-rides.sql", cursor)

# Mean ride count per weekday
ride_count_weekday = sqlViewAsDataFrame("RideCountPerWeekday", connection)
print(ride_count_weekday.head())

# Mean ride duration per weekday
ride_duration_weekday = sqlViewAsDataFrame("RideDurationPerWeekday", connection)
print(ride_duration_weekday.head())

# Mean ride count given precipitation
precipitation_effect = sqlViewAsDataFrame("PrecipitationEffect", connection)
print(precipitation_effect.head())

# Convert weekday numbers to names
WEEK_DAYS = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

ride_count_weekday = ride_count_weekday.sort_values(by="weekday")
ride_count_weekday["weekday"] = ride_count_weekday["weekday"].replace(WEEK_DAYS)
print(ride_count_weekday.head())

ride_duration_weekday = ride_duration_weekday.sort_values(by="weekday")
ride_duration_weekday["weekday"] = ride_duration_weekday["weekday"].replace(WEEK_DAYS)
print(ride_duration_weekday.head())

precipitation_effect = precipitation_effect.sort_values(by="weekday")
precipitation_effect["weekday"] = precipitation_effect["weekday"].replace(WEEK_DAYS)
print(precipitation_effect.head())

# Re-shape precipitation_effect DataFrame to long form
precipitation_effect_long = pd.melt(
    precipitation_effect[["weekday", "mean_ride_count_rain", "mean_ride_count_clear"]],
    id_vars=["weekday"],
    var_name="condition",
    value_name="mean_ride_count",
)
precipitation_effect_long["condition"] = precipitation_effect_long["condition"].replace(
    {"mean_ride_count_rain": "rain", "mean_ride_count_clear": "clear"}
)
print(precipitation_effect_long.head())
print(precipitation_effect_long.tail())

# Set global seaborn styles
sns.set_context("talk")
sns.set_style("white")

# Define color palette as list of hex codes
color_palette = ["#772B58", "#DB6E59"]

# Plot mean ride count per weekday
fig, ax = plt.subplots(figsize=(10, 7))
_ = plt.bar(
    x="weekday",
    height="mean_ride_count",
    data=ride_count_weekday,
    color=color_palette[0],
)
_ = plt.bar(
    x="weekday",
    height="mean_ride_count",
    data=ride_count_weekday[ride_count_weekday["weekday"].isin(["Sat", "Sun"])],
    color=color_palette[1],
)
_ = plt.xlabel("")
_ = plt.ylabel("")
_ = plt.title("Mean Ride Count per Weekday")
plt.savefig("figures/ride_count_weekday.png", dpi=400)
plt.show()

# Plot mean ride duration per weekday
fig, ax = plt.subplots(figsize=(10, 7))
_ = sns.set_color_codes("muted")
_ = plt.bar(
    x="weekday",
    height="mean_duration",
    data=ride_duration_weekday,
    color=color_palette[0],
)
_ = sns.set_color_codes("dark")
_ = plt.bar(
    x="weekday",
    height="mean_duration",
    data=ride_duration_weekday[ride_duration_weekday["weekday"].isin(["Sat", "Sun"])],
    color=color_palette[1],
)
_ = plt.xlabel("")
_ = plt.ylabel("")
_ = plt.title("Mean Ride Duration per Weekday")
plt.savefig("figures/ride_duration_weekday.png", dpi=400)
plt.show()

# Plot mean ride count given precipitation
fig, ax = plt.subplots(figsize=(10, 7))
_ = sns.barplot(
    x="weekday",
    y="mean_ride_count",
    hue="condition",
    hue_order=["clear", "rain"],
    palette="rocket",
    data=precipitation_effect_long,
)
_ = plt.xlabel("")
_ = plt.ylabel("")
_ = plt.title("Mean Ride Count Given Precipitation")
_ = plt.legend(loc="upper left")
plt.savefig("figures/precipitation_effect.png", dpi=400)
plt.show()
