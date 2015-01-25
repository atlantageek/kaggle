SELECT trip_id, MAX(ABS(omega)), MAX(alpha), MIN(ALPHA), AVG(r), MAX(r), MAX(omega / r)
FROM trips WHERE driver_id = 1 AND r BETWEEN 4 AND 40
GROUP BY trip_id

UNION ALL

SELECT trip_id, MAX(ABS(omega)), MAX(alpha), MIN(ALPHA), AVG(r), MAX(r), MAX(omega / r + 1E-9)
FROM trips WHERE driver_id = 1 AND r BETWEEN 4 AND 40
GROUP BY trip_id HAVING MAX(r) < 4 OR MIN(r) > 40

ORDER BY trip_id ASC



CREATE TABLE feature_set1 AS
SELECT
  driver_id, trip_id, MAX(ABS(omega)) AS max_omega,
  MAX(alpha) AS max_alpha, MIN(alpha) AS min_alpha,
  AVG(r) AS avg_speed, MAX(r) AS max_speed,
  MAX(omega / (r + 1e-9)) AS turning_ratio
FROM trips
GROUP BY driver_id, trip_id
ORDER BY driver_id ASC, trip_id ASC;
