-- After creating a database and connecting to it:
-- \i schema_postgres.sql

-- Import data in optimal order
\copy Users FROM 'Users.csv' WITH (FORMAT csv, HEADER true)
\copy Assets FROM 'Assets.csv' WITH (FORMAT csv, HEADER true)
\copy Fractions FROM 'Fractions.csv' WITH (FORMAT csv, HEADER true)
\copy Ownership FROM 'Ownership.csv' WITH (FORMAT csv, HEADER true)
\copy Transactions FROM 'Transactions.csv' WITH (FORMAT csv, HEADER true)

-- Disable trigger before importing ValueHistory to avoid performance issues
ALTER TABLE ValueHistory DISABLE TRIGGER trigger_update_fraction_values;

-- Import ValueHistory data
\copy ValueHistory FROM 'ValueHistory.csv' WITH (FORMAT csv, HEADER true)

-- Re-enable trigger after ValueHistory import
ALTER TABLE ValueHistory ENABLE TRIGGER trigger_update_fraction_values;

-- Initialize fraction values after importing all data
SELECT initialize_fraction_values();
