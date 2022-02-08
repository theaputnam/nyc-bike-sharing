/*
New York City Ride Sharing Data Exploration - Station Analysis

Skills used: Joins, CTE, Aggregate Functions, Views
*/

USE nyc_bike_sharing;

SHOW TABLES;

SELECT *
FROM ride;

SELECT *
FROM station;

-- WHAT ARE THE MOST POPULAR STATIONS?

-- Most popular start stations
DROP VIEW IF EXISTS TopStartStations;

CREATE VIEW TopStartStations AS

WITH cte_start_station_ride_count AS (
	SELECT start_station_id, COUNT(ride_id) AS ride_count
	FROM ride
	GROUP BY start_station_id
)

SELECT station_id, station_name, latitude, longitude, ride_count
FROM (
	station AS s
	JOIN cte_start_station_ride_count AS c
    ON s.station_id = c.start_station_id
)
ORDER BY ride_count DESC;

SELECT *
FROM TopStartStations;

-- Most popular destination stations
DROP VIEW IF EXISTS TopEndStations;

CREATE VIEW TopEndStations AS

WITH cte_end_station_ride_count AS (
	SELECT end_station_id, COUNT(ride_id) AS ride_count
	FROM ride
	GROUP BY end_station_id
)

SELECT station_id, station_name, latitude, longitude, ride_count
FROM (
	station AS s
	JOIN cte_end_station_ride_count AS c
    ON s.station_id = c.end_station_id
)
ORDER BY ride_count DESC;

SELECT *
FROM TopEndStations;

-- Most popular stations
DROP VIEW IF EXISTS TopStations;

CREATE VIEW TopStations AS

WITH cte_start_station_ride_count AS (
	SELECT start_station_id, COUNT(ride_id) AS ride_count
	FROM ride
	GROUP BY start_station_id
), cte_end_station_ride_count AS (
	SELECT end_station_id, COUNT(ride_id) AS ride_count
    FROM ride
    GROUP BY end_station_id
), cte_total_station_ride_count AS (
	SELECT s.start_station_id AS station_id, s.ride_count+e.ride_count AS ride_count
	FROM (
			SELECT *
			FROM cte_start_station_ride_count) s
		LEFT JOIN (
			SELECT *
			FROM cte_end_station_ride_count) e
		ON s.start_station_id = e.end_station_id
	
	UNION ALL
    
    SELECT e.end_station_id AS station_id, e.ride_count
	FROM (
			SELECT *
			FROM cte_start_station_ride_count) s
		RIGHT JOIN (
			SELECT *
			FROM cte_end_station_ride_count) e
		ON s.start_station_id = e.end_station_id
	WHERE s.start_station_id IS NULL
)

SELECT s.station_id, s.station_name, s.latitude, s.longitude, c.ride_count
FROM (
	station AS s
	JOIN cte_total_station_ride_count AS c
    ON s.station_id = c.station_id
)
ORDER BY c.ride_count DESC;

SELECT *
FROM TopStations;
