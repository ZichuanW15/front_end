-- PostgreSQL schema derived from the EER diagram
CREATE TABLE IF NOT EXISTS Users (
  user_id INTEGER PRIMARY KEY,
  is_manager BOOLEAN NOT NULL DEFAULT FALSE,
  email VARCHAR(255) UNIQUE,
  password VARCHAR(64),
  username VARCHAR(32) UNIQUE,
  create_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Assets (
  asset_id INTEGER PRIMARY KEY,
  name VARCHAR(64),
  description VARCHAR(255),
  max_fractions INTEGER,
  min_fractions INTEGER,
  available_fractions INTEGER,
  submitted_by_Users_user_id INTEGER REFERENCES Users(user_id),
  created_at TIMESTAMP,
  status TEXT CHECK (status IN ('draft','pending','approved','rejected','archived')),
  approved_at TIMESTAMP,
  approved_by_Users_user_id INTEGER REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Fractions (
  fraction_id INTEGER PRIMARY KEY,
  Assets_asset_id INTEGER REFERENCES Assets(asset_id),
  fraction_no INTEGER,
  fraction_value NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS Ownership (
  Users_user_id INTEGER REFERENCES Users(user_id),
  Fractions_fraction_id INTEGER REFERENCES Fractions(fraction_id),
  Fractions_Assets_asset_id INTEGER REFERENCES Assets(asset_id),
  acquired_at TIMESTAMP,
  PRIMARY KEY (Users_user_id, Fractions_fraction_id)
);

CREATE TABLE IF NOT EXISTS Transactions (
  transaction_id INTEGER PRIMARY KEY,
  quantity INTEGER NOT NULL,
  unit_price NUMERIC(12,2),
  currency CHAR(3),
  trade_time TIMESTAMP,
  notes VARCHAR(500),
  from_Users_user_id INTEGER REFERENCES Users(user_id),
  to_Users_user_id INTEGER REFERENCES Users(user_id),
  Fractions_fraction_id INTEGER REFERENCES Fractions(fraction_id),
  Fractions_Assets_asset_id INTEGER REFERENCES Assets(asset_id)
);

CREATE TABLE IF NOT EXISTS ValueHistory (
  value_id VARCHAR(45) PRIMARY KEY,
  Assets_asset_id INTEGER REFERENCES Assets(asset_id),
  asset_value INTEGER,
  update_time TIMESTAMP,
  end_time TIMESTAMP
);

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_assets_submitter ON Assets(submitted_by_Users_user_id);
CREATE INDEX IF NOT EXISTS idx_assets_status ON Assets(status);
CREATE INDEX IF NOT EXISTS idx_fracs_asset ON Fractions(Assets_asset_id, fraction_no);
CREATE INDEX IF NOT EXISTS idx_owner_user ON Ownership(Users_user_id);
CREATE INDEX IF NOT EXISTS idx_tx_time ON Transactions(trade_time);
CREATE INDEX IF NOT EXISTS idx_vh_asset_time ON ValueHistory(Assets_asset_id, update_time);
