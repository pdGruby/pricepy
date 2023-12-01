from _common.misc.variables import LOCATION_LIST, FEAT_COLS, TARGET_COL
from _common.database_communicator.db_connector import DBConnector
import pandas as pd
import re
from sklearn.model_selection import train_test_split


class DataPreprocessor(DBConnector):
    def __init__(self) -> None:
        """Initialize DataPreprocessor class and load data from database"""
        super().__init__()
        engine = self.create_sql_engine()

        self.df = pd.read_sql_query("SELECT * FROM data_staging", con=engine)

    def _handle_missing_and_duplicated_values(self):
        """Handle missing and duplicated values in the dataset"""
        self.df["floor"].fillna("brak informacji", inplace=True)
        self.df["status"].fillna("brak informacji", inplace=True)
        self.df["property_type"].fillna("brak informacji", inplace=True)
        self.df["rooms"].fillna(1, inplace=True)
        self.df["year_built"].fillna("brak informacji", inplace=True)
        self.df["property_condition"].fillna("brak informacji", inplace=True)

        self.df.drop_duplicates(inplace=True)

        self.df = self.df[self.df["price"].notna()]
        self.df = self.df[self.df["size"].notna()]

    def _process_price(self, filter_price: float = 0.0):
        """Process price column and filter out prices higher than filter_price"""
        self.df["price"] = (
            self.df["price"]
            .str.replace("zł", "")
            .str.replace(" ", "")
            .replace(",", ".", regex=True)
            .replace("Zapytajocenę", None, regex=True)
        )

        mask = pd.to_numeric(self.df["price"], errors="coerce").notna()
        self.df = self.df[mask]

        if filter_price > 0.0:
            self.df = self.df[self.df["price"] < filter_price]

        self.df["price"] = self.df["price"].astype(float)

    def _process_size(self):
        """Process size column"""
        self.df["size"] = self.df["size"].str.replace(",", ".").astype(float)

    def _process_location(self):
        """Process location column"""

        self.df["location"] = self.df["location"].apply(
            lambda x: next(
                (loc for loc in LOCATION_LIST if bool(re.search(loc, x))), "Poznań"
            )
        )

    def _process_floor(self):
        """Process floor column"""

        self.df["floor"] = self.df["floor"].apply(
            lambda x: x.split("/")[0] if type(x) == str else x
        )

        def extract_numbers(s):
            return "".join(filter(str.isdigit, s)) if any(map(str.isdigit, s)) else s

        self.df["floor"] = (
            self.df["floor"]
            .str.replace("parter", "0")
            .str.replace("poddasze", "10")
            .apply(extract_numbers)
        )
        self.df["floor"] = (
            self.df["floor"]
            .str.replace("zapytaj", "brak informacji")
            .str.replace("suterena", "-1")
        )

    def _process_property_type(self):
        """Process property_type column"""

        self.df["property_type"] = (
            self.df["property_type"]
            .str.replace("plomba", "pozostałe")
            .str.replace("bliźniak", "wolnostojący")
            .str.replace("dom wolnostojący", "wolnostojący")
        )

    def _process_property_condition(self):
        """Process property_condition column"""

        self.df["property_condition"] = self.df["property_condition"].str.replace(
            "zapytaj", "brak informacji"
        )

    def _cast_types(self):
        numerical_col = ["size", "rooms"]
        categorical_col = [
            "status",
            "property_type",
            "floor",
            "year_built",
            "property_condition",
            "location",
        ]

        for col in numerical_col:
            self.df[col] = self.df[col].astype(float)

        for col in categorical_col:
            self.df[col] = self.df[col].astype("category")

    def _select_features(self):
        """Select features to be used in the model"""
        self.df = self.df[FEAT_COLS + [TARGET_COL]]

    def run_preprocessing_pipeline(self):
        """Run preprocessing pipeline"""

        self._process_price()
        self._handle_missing_and_duplicated_values()
        self._process_size()
        self._process_location()
        self._process_floor()
        self._process_property_type()
        self._process_property_condition()
        self._cast_types()
        self._select_features()

    def train_test_split(
        self
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split data into train and test set

        Returns:
            tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series] : train and test set
        """
        X_train, X_test, y_train, y_test = train_test_split(
            self.df[FEAT_COLS],
            self.df[TARGET_COL],
            test_size=0.2,
            random_state=42,
            shuffle=True,
        )
        return X_train, X_test, y_train, y_test

    def get(self):
        """Return data

        Returns:
            pd.DataFrame : data
        """
        return self.df


if __name__ == "__main__":
    preprocessor = DataPreprocessor()

    preprocessor.run_preprocessing_pipeline()
    X_train, X_test, y_train, y_test = preprocessor.train_test_split()
    df = preprocessor.get()
