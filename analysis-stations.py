##
# Connect to MySQL server (localhost), query database using 'analysis-stations.sql' file,
# convert DataFrames to GeoDataFrames, and visualize data
##

import mysql.connector
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

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
executeSqlFile("analysis-stations.sql", cursor)

# Most popular start stations
top_start_stations = sqlViewAsDataFrame("TopStartStations", connection)
print(top_start_stations.head())

# Most popular destination stations
top_end_stations = sqlViewAsDataFrame("TopEndStations", connection)
print(top_end_stations.head())

# Mean ride count given precipitation
top_stations = sqlViewAsDataFrame("TopStations", connection)
print(top_stations.head())


# Convert DataFrames to GeoDataFrames


def dataFrameToGeoDataFrame(df, long_column, lat_column):
    """Convert the DataFrame to a GeoDataFrame"""
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[long_column], df[lat_column]),
        crs="EPSG:4326",
    )
    # Change crf (coordinate reference system) to match contextily basemap
    gdf = gdf.to_crs(epsg=3857)

    return gdf


geo_top_start_stations = dataFrameToGeoDataFrame(
    top_start_stations, "longitude", "latitude"
)
geo_top_end_stations = dataFrameToGeoDataFrame(
    top_end_stations, "longitude", "latitude"
)
geo_top_stations = dataFrameToGeoDataFrame(top_stations, "longitude", "latitude")

## Set global seaborn styles
sns.set_context("talk")
sns.set_style("white")

# Plot most popular start stations
ax = geo_top_start_stations.plot(
    figsize=(9, 10),
    alpha=1,
    edgecolor="k",
    markersize=60,
    c="ride_count",
    cmap="rocket",
)
geo_top_stations.plot(ax=ax, alpha=0, markersize=60)
cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, zoom=12)
plt.title("Most Popular Start Stations")
ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)

# Add colorbar
vmin, vmax = 0, 8240
fig = ax.get_figure()
sm = plt.cm.ScalarMappable(cmap="rocket_r", norm=plt.Normalize(vmin=vmin, vmax=vmax))
divider = make_axes_locatable(ax)
cax = inset_axes(ax, width="5%", height="50%", loc="right", borderpad=-2)
fig.colorbar(sm, cax=cax)

plt.savefig("figures/most_popular_start_stations.png", dpi=400)
plt.show()

# Plot most popular destination stations

ax = geo_top_end_stations.plot(
    figsize=(9, 10),
    alpha=1,
    edgecolor="k",
    markersize=60,
    c="ride_count",
    cmap="rocket",
)
cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, zoom=12)
_ = plt.title("Most Popular Destination Stations")
ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)

# Add colorbar
vmin, vmax = 0, 8240
fig = ax.get_figure()
sm = plt.cm.ScalarMappable(cmap="rocket_r", norm=plt.Normalize(vmin=vmin, vmax=vmax))
divider = make_axes_locatable(ax)
cax = inset_axes(ax, width="5%", height="50%", loc="right", borderpad=-2)
fig.colorbar(sm, cax=cax)

plt.savefig("figures/most_popular_end_stations.png", dpi=400)
plt.show()

# Plot most popular stations

ax = geo_top_stations.plot(
    figsize=(9, 10),
    alpha=1,
    edgecolor="k",
    markersize=60,
    c="ride_count",
    cmap="rocket",
)
cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, zoom=12)
_ = plt.title("Most Popular Stations")
ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)

# Add colorbar
vmin, vmax = 0, 8240
fig = ax.get_figure()
sm = plt.cm.ScalarMappable(cmap="rocket_r", norm=plt.Normalize(vmin=vmin, vmax=vmax))
divider = make_axes_locatable(ax)
cax = inset_axes(ax, width="5%", height="50%", loc="right", borderpad=-2)
fig.colorbar(sm, cax=cax)

plt.savefig("figures/most_popular_stations.png", dpi=400)
plt.show()
