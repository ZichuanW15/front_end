# Generate PostgreSQL schema + CSVs following the EER diagram the user shared.
# Assumptions (documented below in the chat message):
# - 20 users
# - 10 assets
# - For each asset: 10,000 fractions (100,000 total)
# - Ownership: assign each fraction to a random user with acquired_at timestamp
# - Transactions: generate ~50,000 transactions between users moving fractions
# - ValueHistory: daily asset values for the past 120 days per asset (1,200 rows total)
# - Types adapted for PostgreSQL: boolean, timestamptz, numeric for money-like fields, text for notes/description.
#
# All outputs written to C:\works\S3_2\it project\database for download. No internet access required.

import csv, os, random
from datetime import datetime, timedelta
from faker import Faker

random.seed(7)
Faker.seed(7)
fake = Faker()

out_dir = "C:\works\S3_2\it project\database"
os.makedirs(out_dir, exist_ok=True)

N_USERS = 1000
N_ASSETS = 100
FRACTIONS_PER_ASSET = 10_000           # 100k fractions total
TRANSACTIONS_TOTAL = 50_000
VALUE_DAYS = 120

status_choices = ["draft", "pending", "approved", "rejected", "archived"]
currencies = ["USD","EUR","CNY","JPY","AUD"]
asset_names = ["Office", "Warehouse", "ETF", "Bond", "Stock", "Crypto", "Art", "Land", "REIT", "Fund"]

def rand_past(days):
    return datetime.now() - timedelta(days=random.randint(0, days), hours=random.randint(0,23), minutes=random.randint(0,59))

# 1) Users
users = []
for i in range(1, N_USERS+1):
    users.append({
        "user_id": i,
        "is_manager": 1 if random.random() < 0.2 else 0,
        "email": f"user{i}@example.com",
        "password": fake.password(length=12, special_chars=True, upper_case=True, lower_case=True, digits=True),
        "username": f"user{i}",
        "create_time": rand_past(365).strftime("%Y-%m-%d %H:%M:%S"),
    })

# 2) Assets
assets = []
for aid in range(1, N_ASSETS+1):
    max_fr = FRACTIONS_PER_ASSET
    min_fr = 1
    available = max_fr  # will be adjusted by ownership later
    submitter = random.randint(1, N_USERS)
    approver = random.randint(1, N_USERS)
    created_at = rand_past(365)
    approved_at = created_at + timedelta(days=random.randint(1,30))
    status = random.choices(["approved","pending","rejected","draft","archived"], weights=[70,15,5,5,5])[0]
    assets.append({
        "asset_id": aid,
        "name": f"{random.choice(asset_names)} {aid}",
        "description": fake.sentence(nb_words=6),
        "max_fractions": max_fr,
        "min_fractions": min_fr,
        "available_fractions": available,  # temporary; will update later
        "submitted_by_Users_user_id": submitter,
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "approved_at": approved_at.strftime("%Y-%m-%d %H:%M:%S"),
        "approved_by_Users_user_id": approver
    })

# 3) Fractions
fractions = []
fid = 0
for a in assets:
    for n in range(1, FRACTIONS_PER_ASSET+1):
        fid += 1
        fractions.append({
            "fraction_id": fid,
            "Assets_asset_id": a["asset_id"],
            "fraction_no": n,
            "fraction_value": f"{random.uniform(1.0, 100.0):.2f}"
        })
# 4) Ownership (each fraction assigned to one user)
ownerships = []
for fr in fractions:
    uid = random.randint(1, N_USERS)
    acquired_at = rand_past(200).strftime("%Y-%m-%d %H:%M:%S")
    ownerships.append({
        "Users_user_id": uid,
        "Fractions_fraction_id": fr["fraction_id"],
        "Fractions_Assets_asset_id": fr["Assets_asset_id"],
        "acquired_at": acquired_at
    })

# Update available_fractions per asset (all owned -> 0 available)
for a in assets:
    a["available_fractions"] = 0

# 5) Transactions (simulate transfers of fractions and quantities)
transactions = []
tid = 0
for _ in range(TRANSACTIONS_TOTAL):
    tid += 1
    from_user = random.randint(1, N_USERS)
    to_user = random.randint(1, N_USERS)
    while to_user == from_user:
        to_user = random.randint(1, N_USERS)
    fr = random.choice(fractions)
    qty = 1  # fraction-based transfer; one unit per transaction
    unit_price = f"{random.uniform(10, 500):.2f}"
    currency = random.choice(currencies)
    trade_time = rand_past(120).strftime("%Y-%m-%d %H:%M:%S")
    note = "" if random.random() < 0.9 else fake.sentence(nb_words=8)
    transactions.append({
        "transaction_id": tid,
        "quantity": qty,
        "unit_price": unit_price,
        "currency": currency,
        "trade_time": trade_time,
        "notes": note,
        "from_Users_user_id": from_user,
        "to_Users_user_id": to_user,
        "Fractions_fraction_id": fr["fraction_id"],
        "Fractions_Assets_asset_id": fr["Assets_asset_id"]
    })

# 6) ValueHistory (daily values per asset)
value_hist = []
for a in assets:
    base = random.randint(50_000, 2_000_000)
    day0 = datetime.now() - timedelta(days=VALUE_DAYS)
    value_id_counter = 0
    for d in range(VALUE_DAYS):
        value_id_counter += 1
        t = day0 + timedelta(days=d)
        # random walk
        delta = random.randint(-int(base*0.01), int(base*0.01))
        base = max(10_000, base + delta)
        end_t = t + timedelta(days=1)
        value_hist.append({
            "value_id": f"{a['asset_id']}-{value_id_counter}",
            "Assets_asset_id": a["asset_id"],
            "asset_value": base,
            "update_time": t.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_t.strftime("%Y-%m-%d %H:%M:%S"),
        })

# Write CSVs
def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([r[h] for h in header])

write_csv(os.path.join(out_dir, "Users.csv"),
          ["user_id","is_manager","email","password","username","create_time"],
          users)

write_csv(os.path.join(out_dir, "Assets.csv"),
          ["asset_id","name","description","max_fractions","min_fractions","available_fractions",
           "submitted_by_Users_user_id","created_at","status","approved_at","approved_by_Users_user_id"],
          assets)

write_csv(os.path.join(out_dir, "Fractions.csv"),
          ["fraction_id","Assets_asset_id","fraction_no","fraction_value"],
          fractions)

write_csv(os.path.join(out_dir, "Ownership.csv"),
          ["Users_user_id","Fractions_fraction_id","Fractions_Assets_asset_id","acquired_at"],
          ownerships)

write_csv(os.path.join(out_dir, "Transactions.csv"),
          ["transaction_id","quantity","unit_price","currency","trade_time","notes",
           "from_Users_user_id","to_Users_user_id","Fractions_fraction_id","Fractions_Assets_asset_id"],
          transactions)

write_csv(os.path.join(out_dir, "ValueHistory.csv"),
          ["value_id","Assets_asset_id","asset_value","update_time","end_time"],
          value_hist)

# PostgreSQL schema translated from the EER with reasonable type mappings
schema = """\
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
"""
schema_path = os.path.join(out_dir, "schema_postgres.sql")
with open(schema_path, "w", encoding="utf-8") as f:
    f.write(schema)

# Helper .sql to COPY data
copy_sql = """\
-- After creating a database and connecting to it:
-- \i schema_postgres.sql
\\copy Users FROM 'Users.csv' WITH (FORMAT csv, HEADER true)
\\copy Assets FROM 'Assets.csv' WITH (FORMAT csv, HEADER true)
\\copy Fractions FROM 'Fractions.csv' WITH (FORMAT csv, HEADER true)
\\copy Ownership FROM 'Ownership.csv' WITH (FORMAT csv, HEADER true)
\\copy Transactions FROM 'Transactions.csv' WITH (FORMAT csv, HEADER true)
\\copy ValueHistory FROM 'ValueHistory.csv' WITH (FORMAT csv, HEADER true)
"""
with open(os.path.join(out_dir, "import_postgres.sql"), "w", encoding="utf-8") as f:
    f.write(copy_sql)

# Return the list of generated files
sorted([os.path.join(out_dir, x) for x in os.listdir(out_dir)])
