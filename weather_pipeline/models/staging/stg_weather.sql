-- This model takes raw API data and cleans it up

WITH source AS (

    -- Pull everything from the raw table your Python script created
    SELECT * FROM raw_weather

),

cleaned AS (

    SELECT
        -- Identity columns
        id                                    AS weather_id,
        city                                  AS city_name,
        latitude,
        longitude,

        -- Time columns
        timestamp                             AS weather_hour,
        DATE(timestamp)                       AS weather_date,
        EXTRACT(HOUR FROM timestamp)          AS hour_of_day,

        -- Temperature columns (renamed to be more readable)
        temperature_2m                        AS temperature_c,
        apparent_temperature                  AS feels_like_c,

        -- Other weather columns
        relative_humidity_2m                  AS humidity_pct,
        precipitation                         AS rainfall_mm,
        windspeed_10m                         AS windspeed_kmh,
        weathercode,

        -- When was this row loaded into our system
        ingested_at

    FROM source

    -- Filter out any rows where temperature is missing
    WHERE temperature_2m IS NOT NULL

)

SELECT * FROM cleaned