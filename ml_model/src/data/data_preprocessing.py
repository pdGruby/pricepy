import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import DataMainCols
from _common.misc.variables import (
    CATEGORICAL_FEATS,
    FEAT_COLS,
    NUMERIC_FEATS,
    TARGET_COL,
)


class DataPreprocessor(DBConnector):
    def __init__(self, main: bool = True) -> None:
        """Initialize DataPreprocessor class and load data from database"""
        super().__init__()
        engine = self.create_sql_engine()

        self.df = (
            pd.read_sql_query("SELECT * FROM data_main", con=engine)
            if main
            else pd.read_sql_query("SELECT * FROM data_staging", con=engine)
        )

    def _process_price(self, filter_price: float = 0.0):
        """Process price column and filter out prices higher than filter_price"""

        mask = pd.to_numeric(self.df[DataMainCols.PRICE], errors="coerce").notna()
        self.df = self.df[mask]

        self.df[DataMainCols.PRICE] = self.df[DataMainCols.PRICE].astype(float)

        if filter_price > 0.0:
            self.df = self.df[self.df[DataMainCols.PRICE] < filter_price]

    def _process_size(self, filter_size: float = 0.0):
        """Process size column"""

        # self.df["size"] = self.df["size"].fillna(self.df["size"].median())

        if filter_size > 0.0:
            self.df = self.df[self.df[DataMainCols.SIZE] < filter_size]

    def _process_floor(self, filter_floor: float = 0.0):
        """Process floor column"""

        if filter_floor > 0.0:
            self.df = self.df[self.df[DataMainCols.FLOOR] < filter_floor]

    def _cast_types(self):
        numerical_col = NUMERIC_FEATS
        categorical_col = CATEGORICAL_FEATS

        for col in numerical_col:
            self.df[col] = self.df[col].astype(float)

        for col in categorical_col:
            self.df[col] = self.df[col].astype("category")

    @staticmethod
    def static_cast_types(df):
        numerical_col = NUMERIC_FEATS
        categorical_col = CATEGORICAL_FEATS

        for col in numerical_col:
            df[col] = df[col].astype(float)

        for col in categorical_col:
            df[col] = df[col].astype("category")

        return df

    def _select_features(self):
        """Select features to be used in the model"""
        self.df = self.df[FEAT_COLS + [TARGET_COL]]

    def _standardize(self, save_scaler: bool = True):
        """Standardize numerical features"""
        scaler = StandardScaler().fit(self.df[NUMERIC_FEATS])
        self.df[NUMERIC_FEATS] = scaler.transform(self.df[NUMERIC_FEATS])
        if save_scaler:
            with open("scaler.pkl", "wb") as file:
                pickle.dump(scaler, file)

    def run_preprocessing_pipeline(
        self,
        cast_types: bool = True,
        standardize: bool = True,
        save_scaler: bool = True,
    ):
        """Run preprocessing pipeline"""

        if cast_types:
            self._cast_types()
        self._process_price(filter_price=17500000.0)
        self._process_size(filter_size=1000.0)
        self._process_floor(filter_floor=30.0)
        if standardize:
            self._standardize(save_scaler)
        self._select_features()

    def train_test_split(
        self,
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
