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

TARGET_COL = DataMainCols.PRICE

PROPERTY_CONDITION_LIST = ['do remontu', 'do wykończenia', 'do zamieszkania']

STATUS_LIST = ['wtórny', 'pierwotny']

PROPERTY_TYPE_LIST = ['kamienica', 'blok', 'apartamentowiec', 'dom wolnostojący', 'bliźniak', 'szeregowiec']

