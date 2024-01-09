import pickle
from datetime import datetime

import numpy as np
import pandas as pd
import randomname
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV, KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy import desc
from sqlalchemy.sql import null

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import (
    DataMain,
    DataMainCols,
    Models,
    ModelsCols,
)
from _common.misc.variables import CATEGORICAL_FEATS, FEAT_COLS, NUMERIC_FEATS


class PricepyModel(DBConnector):
    """ElasticNet regression model with GridSearchCV, cross-validation and evaluation methods."""

    def __init__(self):
        super().__init__()

        self.session = self.create_session()
        self.engine = self.create_sql_engine()

        self.data = None
        self.X = None
        self.y = None
        self.X_preprocessor = None
        self.model = None
        self.mae = None
        self.rmse = None
        self.r2 = None
        self.best_params = None

    def get_data(self):
        query = self.session.query(DataMain).statement
        data = pd.read_sql(query, self.engine)
        self.data = data

        print("Data successfully downloaded from the database!")

    def preprocess_data(self):
        data = self.data
        data = data.dropna()

        X = data[FEAT_COLS].copy()
        y = data[[DataMainCols.PRICE]].copy()

        categorical_transformer = Pipeline(
            steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))]
        )
        numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])
        X_preprocessor = ColumnTransformer(
            transformers=[
                ("cat", categorical_transformer, CATEGORICAL_FEATS),
                ("num", numeric_transformer, NUMERIC_FEATS),
            ]
        )

        X_encoded = X_preprocessor.fit_transform(X)
        y_encoded = y

        self.X = X_encoded
        self.y = y_encoded
        self.X_preprocessor = X_preprocessor

        print("Data successfully preprocessed!")

    def hyperparameter_tuning(self):
        print("Hyperparameter tuning...")
        random_cv = GridSearchCV(
            estimator=ElasticNet(positive=False, fit_intercept=True, copy_X=True),
            param_grid={
                "alpha": [0.1, 0.5, 1.0, 2.0, 5.0],
                "l1_ratio": [0.1, 0.3, 0.5, 0.7, 0.9],
                "positive": [False, True],
                "fit_intercept": [True, False],
                "copy_X": [True, False],
            },
            cv=5,
            scoring="neg_mean_absolute_error",
            n_jobs=-1,
            verbose=1,
        )
        random_cv.fit(self.X, self.y)
        self.best_params = random_cv.best_params_
        print("Found best params: ", self.best_params)

    def fit(self):
        if self.best_params is None:
            model = ElasticNet(
                alpha=0.1, l1_ratio=0.1, positive=False, fit_intercept=True, copy_X=True
            )
        else:
            model = ElasticNet(
                **self.best_params,
            )
        model.fit(self.X, self.y)
        model.X_preprocessor = self.X_preprocessor

        self.model = model

        print("Model successfully created!")

    def train_model(self):
        self.get_data()
        self.preprocess_data()
        self.hyperparameter_tuning()
        self.fit()
        self.evaluate()

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Predict the price of the given data.

        Args:
            data (pd.DataFrame): Data to predict on.

        Returns:
            np.ndarray: Predicted values.
        """
        X = data[FEAT_COLS].copy()
        X_encoded = self.X_preprocessor.transform(X)
        predicted_values = self.model.predict(X_encoded)

        return predicted_values.reshape(-1, 1)

    def evaluate(self):
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        y_pred = cross_val_predict(self.model, self.X, self.y, cv=kf)

        rmse = np.sqrt(mean_squared_error(self.y, y_pred))
        mae = mean_absolute_error(self.y, y_pred)
        r2 = self.model.score(self.X, self.y)

        self.rmse = rmse
        self.mae = mae
        self.r2 = r2

        print(f"Cross-validated RMSE: {rmse:.2f}")
        print(f"Cross-validated MAE: {mae:.2f}")
        print(f"R2: {r2:.2f}")

    def save_model(self):
        model_name = randomname.get_name()
        model_date = datetime.now()
        model_mae = self.mae
        model_rmse = self.rmse
        model_r2 = self.r2
        model_binary = pickle.dumps(self.model)
        hparams = null()

        values = {
            ModelsCols.MODEL_NAME: model_name,
            ModelsCols.MODEL_DATE: model_date,
            ModelsCols.MODEL_MAE: model_mae,
            ModelsCols.MODEL_RMSE: model_rmse,
            ModelsCols.MODEL_R2: model_r2,
            ModelsCols.MODEL_BINARY: model_binary,
            ModelsCols.HPARAMS: hparams,
        }

        new_data = Models(**values)
        self.session.add(new_data)
        self.session.commit()

    def load_model(self, return_=False):
        row = (
            self.session.query(Models.model_binary, Models.model_name)
            .order_by(desc(Models.model_date))
            .first()
        )
        latest_model = pickle.loads(row.model_binary)  # noqa
        model_name = row.model_name  # noqa

        self.X_preprocessor = latest_model.X_preprocessor
        self.model = latest_model

        print(f"Successfully loaded the latest model! The model name: {model_name}")

        if return_:
            return latest_model
