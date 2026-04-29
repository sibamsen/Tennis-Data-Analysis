TOTAL_PLAYERS = """
SELECT COUNT(DISTINCT competitor_id) as total FROM Competitors
"""

TOTAL_COUNTRIES = """
SELECT COUNT(DISTINCT country) as total FROM Competitors
"""

MAX_POINTS = """
SELECT MAX(points) as max_points FROM Rankings
"""

ALL_PLAYERS = """
SELECT 
    c.competitor_id,
    c.name,
    c.country,
    MAX(r.rank_position) as rank_position,
    MAX(r.points) as points,
    MAX(r.movement) as movement
FROM Competitors c
JOIN Rankings r ON c.competitor_id = r.competitor_id
GROUP BY c.competitor_id, c.name, c.country
"""

COUNTRY_STATS = """
SELECT 
    c.country,
    COUNT(DISTINCT c.competitor_id) as players,
    AVG(r.points) as avg_points
FROM Competitors c
JOIN Rankings r ON c.competitor_id = r.competitor_id
GROUP BY c.country
"""

TOP_PLAYERS = """
SELECT 
    c.name,
    MAX(r.points) as points,
    MIN(r.rank_position) as rank_position
FROM Competitors c
JOIN Rankings r ON c.competitor_id = r.competitor_id
GROUP BY c.competitor_id, c.name
ORDER BY rank_position ASC
LIMIT 10
"""