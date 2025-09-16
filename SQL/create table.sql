-- users（保留你图上的列）
CREATE TABLE IF NOT EXISTS users (
  user_id     BIGSERIAL PRIMARY KEY,
  is_manager  BOOLEAN NOT NULL DEFAULT FALSE,
  email       VARCHAR(255) UNIQUE,
  password    VARCHAR(64),
  username    VARCHAR(32) UNIQUE,
  create_time TIMESTAMP NOT NULL DEFAULT NOW()
);

-- assets（保留你图上的列）
CREATE TABLE IF NOT EXISTS assets (
  asset_id                      BIGSERIAL PRIMARY KEY,
  name                          VARCHAR(64) NOT NULL,
  description                   VARCHAR(255),
  max_fractions                 INTEGER NOT NULL CHECK (max_fractions > 0),
  min_fractions                 INTEGER NOT NULL DEFAULT 1,
  available_fractions           INTEGER NOT NULL DEFAULT 0,                 -- 可根据业务维护
  submitted_by_users_user_id    BIGINT REFERENCES users(user_id),
  created_at                    TIMESTAMP NOT NULL DEFAULT NOW(),
  status                        TEXT CHECK (status IN ('draft','pending','approved','rejected','archived')),
  approved_at                   TIMESTAMP,
  approved_by_users_user_id     BIGINT REFERENCES users(user_id)
);

-- 全局唯一 Fractions（只有这一张）
-- 每行代表“当前存在的一块份额块”，用 slices 表示块内的份数
-- 两个关键属性：current_owner_user_id（当前持有人）、owners_history（历史）
CREATE TABLE IF NOT EXISTS fractions (
  fraction_id            BIGSERIAL PRIMARY KEY,
  asset_id               BIGINT  NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
  slices                 INTEGER NOT NULL CHECK (slices > 0),
  current_owner_user_id  BIGINT  NOT NULL REFERENCES users(user_id),
  owners_history         JSONB   NOT NULL DEFAULT '[]'::jsonb,              -- [{"user_id":..., "event":..., "qty":..., "time":...}, ...]
  parent_fraction_id     BIGINT REFERENCES fractions(fraction_id),          -- 拆分来源（可空）
  created_at             TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at             TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fractions_asset  ON fractions(asset_id);
CREATE INDEX IF NOT EXISTS idx_fractions_owner  ON fractions(current_owner_user_id);

-- 交易流水（留痕；可选扩展单价/币种等）
CREATE TABLE IF NOT EXISTS transactions (
  transaction_id        BIGSERIAL PRIMARY KEY,
  asset_id              BIGINT NOT NULL REFERENCES assets(asset_id),
  source_fraction_id    BIGINT NOT NULL REFERENCES fractions(fraction_id),  -- 被拆或被转出的那块
  new_fraction_id       BIGINT REFERENCES fractions(fraction_id),           -- 新生成的 fraction（部分转移时有，全部转移可为 NULL）
  quantity              INTEGER NOT NULL CHECK (quantity > 0),              -- 本次转移的份数
  from_users_user_id    BIGINT NOT NULL REFERENCES users(user_id),
  to_users_user_id      BIGINT NOT NULL REFERENCES users(user_id),
  trade_time            TIMESTAMP NOT NULL DEFAULT NOW(),
  unit_price            NUMERIC(12,2),                                      -- 如需记录价格
  currency              CHAR(3),
  notes                 TEXT
);
-- 资产价值时间序列（只追加，不更新历史）
CREATE TABLE IF NOT EXISTS valuehistory (
  value_id       BIGSERIAL PRIMARY KEY,
  asset_id       BIGINT NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
  value_amount   NUMERIC(18,2) NOT NULL,     -- 价格/估值；可换成 NUMERIC(20,4)
  currency       CHAR(3)      NOT NULL DEFAULT 'USD',
  as_of_time     TIMESTAMP    NOT NULL,      -- 这条记录的时间点（采样时间）
  created_at     TIMESTAMP    NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_asset_time UNIQUE (asset_id, as_of_time)
);