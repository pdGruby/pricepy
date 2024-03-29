from _common.database_communicator.tables import DataMainCols

# Please, do not reorder offhandedly the dictionary below. It should be ordered from the most detailed locations, to the
# most general
LOCATION_MAP = {
    "Naramowice": ["Naramowice"],
    "Winogrady": ["Winogrady"],
    "Ławica": ["Ławica"],
    "Górczyn": ["Górczyn", "Łazarz"],
    "Grunwald": ["Grunwald", "Junikowo"],
    "Piątkowo": ["Piątkowo", "Podolany"],
    "Jeżyce": ["Jeżyce", "Sołacz", "Ogrody"],
    "Wilda": ["Wilda", "Dębiec"],
    "Rataje": ["Rataje", "Łacina", "Chartowo", "Nowe Miasto", "Starołęka"],
    "Stare Miasto": ["Stare Miasto"],
    "przedmieścia": ["Antoninek", "Komorniki", "Luboń", "Mosina", "Tarnowo Podgórne", "Rokietnica",
                     "Skórzewo", "Szczepankowo", "Swarzędz", "Suchy Las", "Szczytniki"]
}

LOCATION_LIST = [
    "Górczyn",
    "Grunwald",
    "Jeżyce",
    "Ławica",
    "Naramowice",
    "Piątkowo",
    "Rataje",
    "Stare Miasto",
    "Wilda",
    "Winogrady",
    "przedmieścia"
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
    DataMainCols.PROPERTY_CONDITION,
    DataMainCols.LOCATION,
]

NUMERIC_FEATS = [
    DataMainCols.SIZE,
    DataMainCols.ROOMS,
    DataMainCols.FLOOR,
    DataMainCols.YEAR_BUILT,
]

TARGET_COL = DataMainCols.PRICE

PROPERTY_CONDITION_LIST = ["do remontu", "do wykończenia", "do zamieszkania"]

STATUS_LIST = ["wtórny", "pierwotny"]

PROPERTY_TYPE_LIST = [
    "kamienica",
    "blok",
    "apartamentowiec",
    "dom wolnostojący",
    "bliźniak",
    "szeregowiec",
]
