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
    price FLOAT,
    status VARCHAR(10),
    "size" FLOAT,
    property_type VARCHAR(10),
    rooms INT,
    "floor" INT,
    year_built INT,
    property_condition VARCHAR(30),
    "location" VARCHAR(30),
    "desc" TEXT,
    image_url TEXT,
    CONSTRAINT ck_status CHECK (status IN ('pierwotny', 'wtórny')),
    CONSTRAINT ck_size CHECK ("size" BETWEEN 0 AND 1000),
    CONSTRAINT ck_property_type CHECK (property_type IN ('dom', 'kamienica', 'blok')),
    CONSTRAINT ck_rooms CHECK (rooms BETWEEN 0 AND 20),
    CONSTRAINT ck_floor CHECK ("floor" BETWEEN 0 AND 30),
    CONSTRAINT ck_year_built CHECK (year_built BETWEEN 1000 AND 2050),
    CONSTRAINT ck_property_condition CHECK (property_condition IN ('do zamieszkania', 'do wykończenia', 'do remontu'))
);

GRANT ALL ON data_staging TO "Zosia";
GRANT ALL ON data_staging TO "Artur";
GRANT ALL ON data_staging TO "Dominika";
GRANT ALL ON data_main TO "Zosia";
GRANT ALL ON data_main TO "Artur";
GRANT ALL ON data_main TO "Dominika";