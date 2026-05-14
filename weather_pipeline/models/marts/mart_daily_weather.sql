-- This model summarises weather by city by day
-- Think of this as the final report your boss asked for

WITH staging AS (

    -- We build ON TOP of the staging model we just created
    -- dbt automatically knows stg_weather is a dependency
    SELECT * FROM {{ ref('stg_weather') }} -- dbt's smart reference

),

daily_summary AS (

    SELECT
        city_name,
        weather_date,

        -- Temperature stats for the day
        ROUND(AVG(temperature_c)::NUMERIC, 2)    AS avg_temp_c,
        ROUND(MAX(temperature_c)::NUMERIC, 2)    AS max_temp_c,
        ROUND(MIN(temperature_c)::NUMERIC, 2)    AS min_temp_c,
        ROUND(AVG(feels_like_c)::NUMERIC, 2)     AS avg_feels_like_c,

        -- Rainfall total for the day
        ROUND(SUM(rainfall_mm)::NUMERIC, 2)      AS total_rainfall_mm,

        -- Wind stats
        ROUND(AVG(windspeed_kmh)::NUMERIC, 2)    AS avg_windspeed_kmh,
        ROUND(MAX(windspeed_kmh)::NUMERIC, 2)    AS max_windspeed_kmh,

        -- Humidity
        ROUND(AVG(humidity_pct)::NUMERIC, 2)     AS avg_humidity_pct,

        -- How many hours of data do we have for this day
        COUNT(*)                                  AS hours_of_data

    FROM staging
    GROUP BY city_name, weather_date

)

SELECT * FROM daily_summary
ORDER BY city_name, weather_date