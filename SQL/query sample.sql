--search fractions owned by user 202
SELECT
  f.current_owner_user_id AS user_id,
  f.asset_id,
  a.name AS asset_name,
  SUM(f.slices) AS total_slices,           
  COUNT(*) AS fraction_count               
FROM fractions f
JOIN assets a ON a.asset_id = f.asset_id
WHERE f.current_owner_user_id = 203
GROUP BY f.current_owner_user_id, f.asset_id, a.name
ORDER BY f.asset_id;

--detail of fractions owned by user 203
SELECT
  f.fraction_id,
  f.asset_id,
  a.name AS asset_name,
  f.slices,
  f.created_at,
  f.updated_at
FROM fractions f
JOIN assets a ON a.asset_id = f.asset_id
WHERE f.current_owner_user_id = 203
ORDER BY f.asset_id, f.fraction_id;

--transaction history of fraction 39
SELECT
  t.transaction_id,
  t.trade_time,
  a.name AS asset_name,
  t.source_fraction_id,
  t.new_fraction_id,
  CASE
    WHEN t.source_fraction_id = 41 THEN 'OUT'   -- 从 39 这条转出
    WHEN t.new_fraction_id    = 41 THEN 'IN'    -- 转入到 39 这条
  END AS direction,
  t.quantity,
  t.from_users_user_id,
  t.to_users_user_id,
  t.unit_price,
  t.currency,
  t.notes
FROM transactions t
LEFT JOIN assets a ON a.asset_id = t.asset_id
WHERE t.source_fraction_id = 41
   OR t.new_fraction_id    = 41
ORDER BY t.trade_time, t.transaction_id;

--past owners of fration 39
WITH hist AS (                      -- 从 owners_history(JSONB) 里抽取 user_id
  SELECT DISTINCT (e->>'user_id')::bigint AS user_id
  FROM fractions f
  CROSS JOIN LATERAL jsonb_array_elements(f.owners_history) AS e
  WHERE f.fraction_id = 39
),
tx AS (                             -- 从交易两侧抽取：作为源 或 新生成的目标
  SELECT DISTINCT from_users_user_id AS user_id
  FROM transactions
  WHERE source_fraction_id = 39
  UNION
  SELECT DISTINCT to_users_user_id
  FROM transactions
  WHERE new_fraction_id = 39
),
curr AS (                           -- 当前持有人
  SELECT current_owner_user_id AS user_id
  FROM fractions
  WHERE fraction_id = 39
)
SELECT u.user_id, u.username, u.email
FROM (
  SELECT user_id FROM hist
  UNION
  SELECT user_id FROM tx
  UNION
  SELECT user_id FROM curr
) AS x
JOIN users u USING (user_id)
ORDER BY u.user_id;

SELECT (e->>'user_id')::int AS past_owner, e->>'event' AS event, e->>'time' AS time
FROM fractions f
CROSS JOIN LATERAL jsonb_array_elements(f.owners_history) e
WHERE f.fraction_id = 39;

-- search transaction history of fraction 41;
SELECT (e->>'user_id')::int AS past_owner, e->>'event' AS event, e->>'time' AS time
FROM fractions f
CROSS JOIN LATERAL jsonb_array_elements(f.owners_history) e
WHERE f.fraction_id = 41;





--