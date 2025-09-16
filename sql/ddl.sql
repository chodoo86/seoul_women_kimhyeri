
-- SQLite DDL for IVD lead scoring demo

CREATE TABLE IF NOT EXISTS ingest_log(
  file_path TEXT PRIMARY KEY,
  table_name TEXT,
  row_count INTEGER,
  sha256 TEXT,
  loaded_at TEXT
);

CREATE TABLE IF NOT EXISTS accounts(
  account_id INTEGER PRIMARY KEY,
  account_name TEXT,
  account_type TEXT,
  bed_count INTEGER,
  annual_test_volume INTEGER,
  city TEXT,
  state_region TEXT,
  country TEXT,
  ownership_type TEXT,
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS contacts(
  contact_id INTEGER PRIMARY KEY,
  account_id INTEGER,
  title TEXT,
  seniority TEXT,
  email TEXT,
  phone TEXT,
  is_decision_maker INTEGER,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS products(
  product_id INTEGER PRIMARY KEY,
  product_name TEXT,
  product_type TEXT,
  brand TEXT,
  requires_install INTEGER,
  list_price REAL
);

CREATE TABLE IF NOT EXISTS install_base(
  install_id INTEGER PRIMARY KEY,
  account_id INTEGER,
  product_id INTEGER,
  install_date TEXT,
  warranty_end TEXT,
  status TEXT
);

CREATE TABLE IF NOT EXISTS opportunities(
  opportunity_id INTEGER PRIMARY KEY,
  account_id INTEGER,
  stage TEXT,
  expected_close_date TEXT,
  amount_expected REAL,
  source TEXT,
  created_at TEXT,
  closed_at TEXT
);

CREATE TABLE IF NOT EXISTS opportunity_line_items(
  op_line_id INTEGER PRIMARY KEY,
  opportunity_id INTEGER,
  product_id INTEGER,
  qty REAL,
  unit_price REAL
);

CREATE TABLE IF NOT EXISTS bids(
  bid_id INTEGER PRIMARY KEY,
  account_id INTEGER,
  bid_due_date TEXT,
  bid_status TEXT,
  est_amount REAL,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS quotes(
  quote_id INTEGER PRIMARY KEY,
  account_id INTEGER,
  opportunity_id INTEGER,
  quote_date TEXT,
  valid_until TEXT,
  quote_amount REAL,
  quote_status TEXT
);

CREATE TABLE IF NOT EXISTS orders(
  order_id INTEGER PRIMARY KEY,
  account_id INTEGER,
  order_date TEXT,
  total_amount REAL
);

CREATE TABLE IF NOT EXISTS shipments(
  shipment_id INTEGER PRIMARY KEY,
  order_id INTEGER,
  product_id INTEGER,
  qty REAL,
  ship_date TEXT
);

CREATE TABLE IF NOT EXISTS interactions(
  interaction_id INTEGER PRIMARY KEY,
  account_id INTEGER,
  contact_id INTEGER,
  channel TEXT,
  outcome TEXT,
  occurred_at TEXT
);

CREATE TABLE IF NOT EXISTS web_events(
  web_event_id INTEGER PRIMARY KEY,
  account_id INTEGER,
  event_type TEXT,
  url TEXT,
  occurred_at TEXT
);

CREATE TABLE IF NOT EXISTS service_tickets(
  ticket_id INTEGER PRIMARY KEY,
  account_id INTEGER,
  product_id INTEGER,
  opened_at TEXT,
  closed_at TEXT,
  severity TEXT,
  issue_type TEXT
);

CREATE TABLE IF NOT EXISTS campaigns(
  campaign_id INTEGER PRIMARY KEY,
  campaign_name TEXT,
  channel TEXT,
  start_date TEXT,
  end_date TEXT
);

CREATE TABLE IF NOT EXISTS campaign_members(
  campaign_member_id INTEGER PRIMARY KEY,
  campaign_id INTEGER,
  account_id INTEGER,
  contact_id INTEGER,
  member_status TEXT,
  occurred_at TEXT
);

CREATE TABLE IF NOT EXISTS marketing_costs(
  cost_id INTEGER PRIMARY KEY,
  campaign_id INTEGER,
  spend_date TEXT,
  amount REAL
);

-- BI tables
CREATE TABLE IF NOT EXISTS bi_scores_daily(
  run_date TEXT,
  account_id INTEGER,
  t0_date TEXT,
  p_win_90d REAL,
  expected_amount_180d REAL,
  expected_value REAL,
  is_priority INTEGER
);

CREATE TABLE IF NOT EXISTS bi_opportunities AS SELECT * FROM opportunities WHERE 0;
CREATE TABLE IF NOT EXISTS bi_orders AS SELECT * FROM orders WHERE 0;
