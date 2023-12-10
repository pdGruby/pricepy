from _common.database_communicator.tables import DataMainCols

# Please, do not reorder offhandedly the list below. It should be ordered from the most detailed locations, to the most
# general
LOCATION_LIST = [
    "Łazarz",
    "Ławica",
    "Górczyn",
    "Junikowo",
    "Grunwald",
    "Podolany",
    "Sołacz",
    "Jeżyce",
    "Wilda",
    "Dębiec",
    "Łacina",
    "Starołęka",
    "Naramowice",
    "Piątkowo",
    "Winogrady",
    "Chartowo",
    "Rataje",
    "Antoninek",
    "Ogrody",
    "Stare Miasto",
    "Nowe Miasto",
    "Szczytniki",
    "Komorniki",
    "Tarnowo Podgórne",
    "Skórzewo",
    "Szczepankowo",
    "Swarzędz",
    "Luboń",
    "Mosina",
    "Suchy Las",
    "Rokietnica"
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

PROPERTY_CONDITION_LIST = ['do remontu', 'do wykończenia', 'do zamieszkania']

STATUS_LIST = ['wtórny', 'pierwotny']

PROPERTY_TYPE_LIST = ['kamienica', 'blok', 'apartamentowiec', 'dom wolnostojący', 'bliźniak', 'szeregowiec']

