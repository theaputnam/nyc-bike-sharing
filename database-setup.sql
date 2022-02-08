/*
New York City Ride Sharing Data Exploration - Database setup
*/

-- Comment out this line to prevent overwriting the database with every run of this script
DROP DATABASE IF EXISTS nyc_bike_sharing;

CREATE DATABASE nyc_bike_sharing;

USE nyc_bike_sharing;

-- Table setups
CREATE TABLE station (
  station_id VARCHAR(7),
  station_name VARCHAR(50),
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  PRIMARY KEY (station_id)
);

CREATE TABLE weather (
  date DATE,
  min_air_temperature DOUBLE,
  max_air_temperature DOUBLE,
  precipitation DOUBLE,
  PRIMARY KEY (date)
);

CREATE TABLE ride (
  ride_id CHAR(16),
  start_date_time DATETIME NOT NULL,
  end_date_time DATETIME NOT NULL,
  start_date DATE GENERATED ALWAYS AS (DATE(start_date_time)) STORED,
  start_station_id VARCHAR(7) NOT NULL,
  end_station_id VARCHAR(7) NOT NULL,
  customer_type CHAR(6),
  duration DOUBLE GENERATED ALWAYS AS (
    TIMESTAMPDIFF(SECOND, start_date_time, end_date_time)
  ),
  PRIMARY KEY (ride_id),
  FOREIGN KEY (start_date) REFERENCES weather(date),
  FOREIGN KEY (start_station_id) REFERENCES station(station_id),
  FOREIGN KEY (end_station_id) REFERENCES station(station_id),
  CHECK (end_date_time >= start_date_time)
);