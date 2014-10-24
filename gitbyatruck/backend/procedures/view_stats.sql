-- Only run CREATE EXTENSION the first time you need stats
-- CREATE EXTENSION pg_stat_statements;
\x -- Extended display

-- Get the five functions the most time is spent on
SELECT query, calls, total_time, rows, 100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
    FROM pg_stat_statements 
    ORDER BY total_time
    DESC LIMIT 5;
