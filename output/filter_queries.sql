-- filter_queries.sql
-- Join origins with fork enrichment, compute derived columns, apply constraints.
-- Edit threshold values to taste — no recompilation needed.

-- Constants
-- LLM baseline (2022-11-01 00:00 UTC): 1667260800
-- Seconds per calendar month (365.25 / 12 * 86400): 2629800

COPY (
  WITH enriched AS (
    SELECT
      o.*,
      COALESCE(f.fork_count, 0)   AS fork_count,
      COALESCE(f.is_fork,  false) AS is_fork,
      -- Derived: frequency and age are NOT stored in Parquet — computed here.
      o.total_commits
        / NULLIF(o.latest_ts - o.creation_ts, 0) * 2629800.0  AS commit_freq_per_month,
      (o.latest_ts - o.creation_ts) / 2629800.0               AS age_months
    FROM  read_parquet('origins.parquet')           o
    LEFT  JOIN read_parquet('fork_enrichment.parquet') f ON o.swhid = f.swhid
  )
  SELECT *
  FROM   enriched
  WHERE
    -- Activity
    creation_ts           < 1667260800   -- exists before LLM baseline
    AND recent_commits    >= 100
    AND total_commits     >= 10000
    AND unique_authors    >= 60
    AND core_authors      >= 15
 
    -- Codebase
    AND file_count        >= 100
    AND estimated_size_bytes >= 1000
    AND estimated_size_bytes <  2000000000
    AND has_ci
    AND has_license
    -- Intent
    AND has_readme
) TO 'passing_origins.parquet' (FORMAT PARQUET, COMPRESSION 'zstd');

SELECT COUNT(*) AS passing_origins FROM read_parquet('passing_origins.parquet');
