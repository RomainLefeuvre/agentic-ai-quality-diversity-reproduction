-- fork_queries.sql
-- Derives fork_count and is_fork from root_edges.parquet via a self-join.
-- Run once after extraction.  Works with DuckDB >= 0.10.

COPY (
  WITH fork_groups AS (
    SELECT
      a.origin_swhid                              AS swhid,
      COUNT(DISTINCT b.origin_swhid)              AS fork_count,
      (MAX(CASE WHEN b.total_commits > a.total_commits
                THEN 1 ELSE 0 END))::BOOLEAN      AS is_fork
    FROM   read_parquet('root_edges.parquet') a
    JOIN   read_parquet('root_edges.parquet') b
           ON  a.root_commit_node_id = b.root_commit_node_id
           AND a.origin_swhid        <> b.origin_swhid
    GROUP  BY a.origin_swhid, a.total_commits
  ),
  solo AS (
    SELECT DISTINCT origin_swhid AS swhid
    FROM   read_parquet('root_edges.parquet')
    WHERE  origin_swhid NOT IN (SELECT swhid FROM fork_groups)
  )
  SELECT swhid, fork_count, is_fork FROM fork_groups
  UNION ALL
  SELECT swhid, 0 AS fork_count, false AS is_fork FROM solo
) TO 'fork_enrichment.parquet' (FORMAT PARQUET, COMPRESSION 'zstd');
