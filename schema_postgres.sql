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

-- Function to enforce manager approval constraint
CREATE OR REPLACE FUNCTION check_manager_approval()
RETURNS TRIGGER AS $$
BEGIN
    -- If approved_by_Users_user_id is not NULL, check if the user is a manager
    IF NEW.approved_by_Users_user_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = NEW.approved_by_Users_user_id AND is_manager = TRUE) THEN
            RAISE EXCEPTION 'Only managers can approve assets. User % is not a manager.', NEW.approved_by_Users_user_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for manager approval constraint
CREATE TRIGGER trigger_check_manager_approval
    BEFORE INSERT OR UPDATE ON Assets
    FOR EACH ROW
    EXECUTE FUNCTION check_manager_approval();

-- Function to calculate fraction value based on latest asset value and available fractions
CREATE OR REPLACE FUNCTION calculate_fraction_value(p_asset_id INTEGER)
RETURNS NUMERIC(12,2) AS $$
DECLARE
    latest_value INTEGER;
    available_fractions INTEGER;
BEGIN
    -- Get the latest asset value from ValueHistory
    SELECT vh.asset_value INTO latest_value
    FROM ValueHistory vh 
    WHERE vh.Assets_asset_id = p_asset_id 
    ORDER BY vh.update_time DESC 
    LIMIT 1;
    
    -- Get available fractions from Assets (total fractions per asset)
    SELECT a.available_fractions INTO available_fractions
    FROM Assets a 
    WHERE a.asset_id = p_asset_id;
    
    -- Return calculated value or 0 if no data
    IF latest_value IS NOT NULL AND available_fractions IS NOT NULL AND available_fractions > 0 THEN
        RETURN (latest_value::NUMERIC(12,2) / available_fractions);
    ELSE
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Trigger function to update fraction values when ValueHistory changes
CREATE OR REPLACE FUNCTION update_fraction_values()
RETURNS TRIGGER AS $$
BEGIN
    -- Update all fractions for the affected asset
    UPDATE Fractions 
    SET fraction_value = calculate_fraction_value(NEW.Assets_asset_id)
    WHERE Assets_asset_id = NEW.Assets_asset_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger will be created after ValueHistory table is created

-- Procedure to initialize fraction values for existing data
CREATE OR REPLACE FUNCTION initialize_fraction_values()
RETURNS VOID AS $$
DECLARE
    asset_record RECORD;
    latest_value INTEGER;
    available_fractions INTEGER;
    calculated_value NUMERIC(12,2);
BEGIN
    -- Process each asset individually for better performance
    FOR asset_record IN SELECT DISTINCT Assets_asset_id FROM Fractions WHERE Assets_asset_id IS NOT NULL LOOP
        -- Get the latest asset value from ValueHistory
        SELECT vh.asset_value INTO latest_value
        FROM ValueHistory vh 
        WHERE vh.Assets_asset_id = asset_record.Assets_asset_id 
        ORDER BY vh.update_time DESC 
        LIMIT 1;
        
        -- Get available fractions from Assets (total fractions per asset)
        SELECT a.available_fractions INTO available_fractions
        FROM Assets a 
        WHERE a.asset_id = asset_record.Assets_asset_id;
        
        -- Calculate fraction value
        IF latest_value IS NOT NULL AND available_fractions IS NOT NULL AND available_fractions > 0 THEN
            calculated_value := (latest_value::NUMERIC(12,2) / available_fractions);
        ELSE
            calculated_value := 0;
        END IF;
        
        -- Update all fractions for this asset
        UPDATE Fractions 
        SET fraction_value = calculated_value
        WHERE Assets_asset_id = asset_record.Assets_asset_id;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

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

-- Create trigger for ValueHistory updates (after table creation)
CREATE TRIGGER trigger_update_fraction_values
    AFTER INSERT OR UPDATE ON ValueHistory
    FOR EACH ROW
    EXECUTE FUNCTION update_fraction_values();

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_assets_submitter ON Assets(submitted_by_Users_user_id);
CREATE INDEX IF NOT EXISTS idx_assets_status ON Assets(status);
CREATE INDEX IF NOT EXISTS idx_fracs_asset ON Fractions(Assets_asset_id, fraction_no);
CREATE INDEX IF NOT EXISTS idx_owner_user ON Ownership(Users_user_id);
CREATE INDEX IF NOT EXISTS idx_tx_time ON Transactions(trade_time);
CREATE INDEX IF NOT EXISTS idx_vh_asset_time ON ValueHistory(Assets_asset_id, update_time);
