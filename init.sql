--- DATA TABLES ---
CREATE TABLE IF NOT EXISTS data_staging
(
    url TEXT,
    price TEXT,
    status TEXT,
    "size" TEXT,
    property_type TEXT,
    rooms TEXT,
    "floor" TEXT,
    year_built TEXT,
    property_condition TEXT,
    "location" TEXT,
    "desc" TEXT,
    image_url TEXT
);


CREATE TABLE IF NOT EXISTS data_main
(
    url TEXT PRIMARY KEY,
    price DECIMAL,
    currency VARCHAR(10),
    status VARCHAR(30),
    "size" DECIMAL,
    property_type VARCHAR(30),
    rooms INT,
    "floor" INT,
    year_built INT,
    property_condition VARCHAR(30),
    "location" VARCHAR(30),
    "desc" TEXT,
    image_url TEXT,
    insert_date DATE,
    last_time_seen DATE,
    row_hash VARCHAR(64),
    run_id TEXT

    CONSTRAINT ck_status CHECK (status IN ('pierwotny', 'wtórny')),
    CONSTRAINT ck_property_type CHECK (property_type IN ('dom', 'kamienica', 'blok', 'apartamentowiec', 'inne')),
    CONSTRAINT ck_property_condition CHECK (property_condition IN ('do zamieszkania', 'do wykończenia', 'do remontu', 'stan surowy zamknięty', 'stan surowy otwarty'))
);

CREATE TABLE IF NOT EXISTS temp_table
(
    url TEXT PRIMARY KEY,
    price TEXT,
    "location" TEXT,
    image_url TEXT
);

CREATE TABLE IF NOT EXISTS models
(
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(50),
    model_date TIMESTAMP(0),
    model_mae FLOAT,
    model_rmse FLOAT,
    model_r2 FLOAT,
    model_binary BYTEA,
    hparams JSON
);

CREATE TABLE IF NOT EXISTS opportunities
(
    url TEXT PRIMARY KEY,
    predicted_price DECIMAL,
    potential_gain DECIMAL,
    FOREIGN KEY (url) REFERENCES data_main(url) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bargainletter_emails
(
    id SERIAL PRIMARY KEY,
    email TEXT,
    max_real_price DECIMAL,
    min_potential_gain DECIMAL,
    "location" VARCHAR(30)
);

GRANT ALL ON models TO "Zosia";
GRANT ALL ON models TO "Kamil";
GRANT ALL ON models TO "Dominika";
GRANT ALL ON models TO "Artur";

GRANT ALL ON data_staging TO "Kamil";
GRANT ALL ON data_staging TO "Zosia";
GRANT ALL ON data_staging TO "Artur";
GRANT ALL ON data_staging TO "Dominika";

GRANT ALL ON data_main TO "Kamil";
GRANT ALL ON data_main TO "Zosia";
GRANT ALL ON data_main TO "Artur";
GRANT ALL ON data_main TO "Dominika";

GRANT ALL ON temp_table TO "Kamil";
GRANT ALL ON temp_table TO "Zosia";
GRANT ALL ON temp_table TO "Artur";
GRANT ALL ON temp_table TO "Kamil";

GRANT ALL ON opportunities TO "Zosia";
GRANT ALL ON opportunities TO "Kamil";
GRANT ALL ON opportunities TO "Dominika";
GRANT ALL ON opportunities TO "Artur";

GRANT ALL ON bargainletter_emails TO "Zosia";
GRANT ALL ON bargainletter_emails TO "Kamil";
GRANT ALL ON bargainletter_emails TO "Dominika";
GRANT ALL ON bargainletter_emails TO "Artur";