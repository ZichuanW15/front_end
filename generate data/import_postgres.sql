-- After creating a database and connecting to it:
-- \i schema_postgres.sql
\copy Users FROM 'Users.csv' WITH (FORMAT csv, HEADER true)
\copy Assets FROM 'Assets.csv' WITH (FORMAT csv, HEADER true)
\copy Fractions FROM 'Fractions.csv' WITH (FORMAT csv, HEADER true)
\copy Ownership FROM 'Ownership.csv' WITH (FORMAT csv, HEADER true)
\copy Transactions FROM 'Transactions.csv' WITH (FORMAT csv, HEADER true)
\copy ValueHistory FROM 'ValueHistory.csv' WITH (FORMAT csv, HEADER true)
