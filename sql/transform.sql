
-- transform.sql: create feature view for scoring (uses current date as t0)
-- For demo simplicity, we compute features with rolling windows relative to 'now'.
DROP VIEW IF EXISTS feature_view;
CREATE VIEW feature_view AS
WITH t AS (
  SELECT date('now') AS t0
),
orders_agg AS (
  SELECT account_id,
         COUNT(*) FILTER (WHERE order_date >= date((SELECT t0 FROM t), '-180 day')) AS orders_cnt_180d,
         SUM(total_amount) FILTER (WHERE order_date >= date((SELECT t0 FROM t), '-180 day')) AS monetary_180d,
         CAST(julianday((SELECT t0 FROM t)) - julianday(MAX(order_date)) AS INT) AS order_recency_days
  FROM orders
  GROUP BY account_id
),
interact_agg AS (
  SELECT account_id,
         COUNT(*) FILTER (WHERE occurred_at >= date((SELECT t0 FROM t), '-90 day')) AS interactions_90d,
         COUNT(*) FILTER (WHERE channel='demo' AND occurred_at >= date((SELECT t0 FROM t), '-180 day')) AS demo_180d,
         AVG(CASE WHEN outcome='positive' THEN 1.0 ELSE 0.0 END) AS outcome_pos_ratio,
         CAST(julianday((SELECT t0 FROM t)) - julianday(MAX(occurred_at)) AS INT) AS last_interact_recency_days
  FROM interactions
  GROUP BY account_id
),
bid_agg AS (
  SELECT account_id,
         MAX(CASE WHEN bid_due_date BETWEEN date((SELECT t0 FROM t)) AND date((SELECT t0 FROM t), '+30 day') THEN 1 ELSE 0 END) AS has_active_bid_due_30d,
         COUNT(*) FILTER (WHERE created_at >= date((SELECT t0 FROM t), '-90 day')) AS bids_submitted_90d
  FROM bids
  GROUP BY account_id
),
ticket_agg AS (
  SELECT account_id,
         COUNT(*) FILTER (WHERE opened_at >= date((SELECT t0 FROM t), '-180 day')) AS tickets_180d,
         AVG(CASE WHEN severity='P1' THEN 1.0 ELSE 0.0 END) AS p1_ratio
  FROM service_tickets
  GROUP BY account_id
),
install_agg AS (
  SELECT account_id,
         COUNT(*) FILTER (WHERE status='active') AS install_equipment_count_active,
         AVG((julianday((SELECT t0 FROM t)) - julianday(install_date))/365.25) AS avg_equipment_age_years
  FROM install_base
  GROUP BY account_id
)
SELECT a.account_id,
       (SELECT t0 FROM t) AS t0_date,
       a.bed_count, a.annual_test_volume, a.account_type, a.state_region,
       COALESCE(oa.orders_cnt_180d,0) AS orders_cnt_180d,
       COALESCE(oa.monetary_180d,0.0) AS monetary_180d,
       COALESCE(oa.order_recency_days,9999) AS order_recency_days,
       COALESCE(ia.interactions_90d,0) AS interactions_90d,
       COALESCE(ia.demo_180d,0) AS demo_180d,
       COALESCE(ia.outcome_pos_ratio,0.0) AS outcome_pos_ratio,
       COALESCE(ia.last_interact_recency_days,9999) AS last_interact_recency_days,
       COALESCE(ba.has_active_bid_due_30d,0) AS has_active_bid_due_30d,
       COALESCE(ba.bids_submitted_90d,0) AS bids_submitted_90d,
       COALESCE(ta.tickets_180d,0) AS tickets_180d,
       COALESCE(ta.p1_ratio,0.0) AS p1_ratio,
       COALESCE(ins.install_equipment_count_active,0) AS install_equipment_count_active,
       COALESCE(ins.avg_equipment_age_years,0.0) AS avg_equipment_age_years
FROM accounts a
LEFT JOIN orders_agg oa ON oa.account_id = a.account_id
LEFT JOIN interact_agg ia ON ia.account_id = a.account_id
LEFT JOIN bid_agg ba ON ba.account_id = a.account_id
LEFT JOIN ticket_agg ta ON ta.account_id = a.account_id
LEFT JOIN install_agg ins ON ins.account_id = a.account_id
;
