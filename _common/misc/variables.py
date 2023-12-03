from _common.database_communicator.tables import DataMainCols

LOCATION_LIST = [
    "Grunwald",
    "Górczyn",
    "Ławica",
    "Łazarz",
    "Junikowo",
    "Jeżyce",
    "Podolany",
    "Sołacz",
    "Wilda",
    "Dębiec",
    "Nowe Miasto",
    "Łacina",
    "Rataje",
    "Starołęka Mała",
    "Stare Miasto",
    "Naramowice",
    "Piątkowo",
    "Winogrady",
    "Chartowo",
]

FEAT_COLS = [
    DataMainCols.STATUS,
    DataMainCols.SIZE,
    DataMainCols.PROPERTY_TYPE,
    DataMainCols.ROOMS,
    DataMainCols.FLOOR,
    DataMainCols.YEAR_BUILT,
    DataMainCols.PROPERTY_CONDITION,
    DataMainCols.LOCATION,
]

CATEGORICAL_FEATS = [
    DataMainCols.STATUS,
    DataMainCols.PROPERTY_TYPE,
    DataMainCols.FLOOR,
    DataMainCols.YEAR_BUILT,
    DataMainCols.PROPERTY_CONDITION,
    DataMainCols.LOCATION,
]

NUMERIC_FEATS = [DataMainCols.SIZE, DataMainCols.ROOMS]

TARGET_COL = DataMainCols.PRICE
