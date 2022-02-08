/*
New York City Ride Sharing Data Exploration - Ride Analysis

Skills used: Joins, CTE, Aggregate Functions, Views
*/

USE nyc_bike_sharing;

SHOW TABLES;

SELECT *
FROM ride;

SELECT *
FROM weather;

-- DO PEOPLE RENT BIKES MORE OFTEN ON WEEKENDS?

-- Mean ride count per weekday
DROP VIEW IF EXISTS RideCountPerWeekday;

CREATE VIEW RideCountPerWeekday AS
SELECT days.weekday, AVG(ride_count) as mean_ride_count
FROM (
	SELECT start_date, WEEKDAY(start_date) AS weekday, COUNT(ride_id) AS ride_count
	FROM ride
	GROUP BY start_date
) AS days
GROUP BY days.weekday
ORDER BY mean_ride_count DESC;

SELECT *
FROM RideCountPerWeekday;

-- Mean ride count per working day and weekend day
SELECT weekdays.weekend, AVG(weekdays.mean_ride_count) AS mean_ride_count
FROM (
	SELECT days.weekday, IF(weekday<5, 0, 1) AS weekend, AVG(ride_count) as mean_ride_count
	FROM (
		SELECT start_date, WEEKDAY(start_date) AS weekday, COUNT(ride_id) AS ride_count
		FROM ride
		GROUP BY start_date
	) AS days
	GROUP BY days.weekday
) AS weekdays
GROUP BY weekdays.weekend
ORDER BY weekdays.weekend;

-- DO PEOPLE RENT BIKES FOR LONGER ON WEEKENDS?

-- Mean ride duration per weekday
DROP VIEW IF EXISTS RideDurationPerWeekday;

CREATE VIEW RideDurationPerWeekday AS
SELECT WEEKDAY(start_date) AS weekday, AVG(duration) AS mean_duration
FROM ride
GROUP BY weekday
ORDER BY mean_duration DESC;

SELECT *
FROM RideDurationPerWeekday;

-- Mean ride duration per working day and weekend day
SELECT weekdays.weekend, AVG(weekdays.mean_duration) AS mean_duration
FROM (
	SELECT WEEKDAY(start_date) AS weekday, IF(WEEKDAY(start_date)<5, 0, 1) AS weekend, AVG(duration) AS mean_duration
	FROM ride
	GROUP BY weekday
) AS weekdays
GROUP BY weekdays.weekend
ORDER BY weekdays.weekend;

-- DO PEOPLE RENT BIKES LESS OFTEN ON RAINY DAYS?

DROP VIEW IF EXISTS PrecipitationEffect;

CREATE VIEW PrecipitationEffect AS

WITH cte_ride_count_rain AS (
	SELECT days.weekday, AVG(days.ride_count) AS mean_ride_count, 1 AS precipitation
	FROM (
		SELECT ride.start_date, WEEKDAY(ride.start_date) AS weekday, weather.precipitation, COUNT(ride.ride_id) AS ride_count
		FROM ride LEFT JOIN weather ON ride.start_date = weather.date
		GROUP BY ride.start_date
		HAVING weather.precipitation > 0
		) AS days
	GROUP BY days.weekday
), cte_ride_count_clear AS (
	SELECT days.weekday, AVG(days.ride_count) AS mean_ride_count, 0 AS precipitation
	FROM (
		SELECT WEEKDAY(ride.start_date) AS weekday, weather.precipitation, COUNT(ride.ride_id) AS ride_count
		FROM ride LEFT JOIN weather ON ride.start_date = weather.date
		GROUP BY ride.start_date
		HAVING weather.precipitation = 0
		) AS days
	GROUP BY days.weekday
)

SELECT rain.weekday, rain.mean_ride_count AS mean_ride_count_rain, clear.mean_ride_count AS mean_ride_count_clear, rain.mean_ride_count-clear.mean_ride_count AS mean_ride_count_difference
FROM (
		SELECT *
        FROM cte_ride_count_rain) rain
	LEFT JOIN (
		SELECT *
        FROM cte_ride_count_clear) clear
	ON rain.weekday = clear.weekday

UNION ALL

SELECT clear.weekday, rain.mean_ride_count AS mean_ride_count_rain, clear.mean_ride_count AS mean_ride_count_clear, rain.mean_ride_count-clear.mean_ride_count AS mean_ride_count_difference
FROM (
		SELECT *
        FROM cte_ride_count_rain) rain
	RIGHT JOIN (
		SELECT *
        FROM cte_ride_count_clear) clear
	ON rain.weekday = clear.weekday
WHERE rain.weekday IS NULL

ORDER BY weekday;

SELECT *
FROM PrecipitationEffect;
