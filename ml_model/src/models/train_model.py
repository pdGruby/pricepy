import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBRegressor

from ml_model.src.data.data_preprocessing import DataPreprocessor


class XGBoostRegressor(XGBRegressor):
    """XGBoost Regressor with RandomizedSearchCV, learning curves plotting and evaluation methods.

    Args:
        enable_categorical (bool, optional): Whether to enable categorical features. Defaults to True.
    """

    param_grid = {
        "learning_rate": [0.001, 0.01, 0.1, 0.2, 0.3],
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [5, 10, 15, 25, 30],
        "min_child_weight": [5, 7, 10, 15, 20],
        "subsample": [0.5, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.5, 0.8, 0.9, 1.0],
        "gamma": [0, 0.1, 0.2, 0.3, 0.5],
        "scale_pos_weight": [1, 2, 3, 4, 5],
        "eta": [0.01, 0.1, 0.2, 0.3, 0.5],
        "reg_alpha": [0, 0.01, 0.05, 0.1],
        "reg_lambda": [0.1, 0.5, 1],
    }

    def __init__(self, enable_categorical=True, **kwargs):
        super().__init__(**kwargs)
        self.enable_categorical = enable_categorical

    def random_search_cv(
        self, X_train, y_train, n_iter=150, cv=5, n_jobs=8, verbose=2, random_state=40
    ):
        random_cv = RandomizedSearchCV(
            estimator=self,
            param_distributions=self.param_grid,
            cv=cv,
            n_iter=n_iter,
            scoring="neg_mean_absolute_error",
            n_jobs=n_jobs,
            verbose=verbose,
            return_train_score=True,
            random_state=random_state,
        )
        random_cv.fit(X_train, y_train)

        self.best_params_ = random_cv.best_params_

    def train(self, X_train, y_train, X_test, y_test, **kwargs):
        self.set_params(
            **self.best_params_,
            eval_metric="rmse",
            early_stopping_rounds=10,
            enable_categorical=self.enable_categorical,
            n_jobs=8,
        )
        eval_set = [(X_train, y_train), (X_test, y_test)]
        self.fit(X_train, y_train, eval_set=eval_set, **kwargs)

        self.results = self.evals_result()

    def plot_learning_curves(self):
        # plot learning curves
        plt.plot(self.results["validation_0"]["rmse"], label="train")
        plt.plot(self.results["validation_1"]["rmse"], label="test")
        plt.xlabel("Steps")
        plt.ylabel("RMSE")
        plt.title("XGBoost learning curves")
        plt.legend()
        plt.show()

    def evaluate(self, X_test, y_test):
        preds = self.predict(X_test)

        # Evaluate the model
        mae_score = mean_absolute_error(y_test, preds)
        print("MAE:", mae_score)

        rmse_score = np.sqrt(mean_squared_error(y_test, preds))
        print("RMSE:", rmse_score)

        r2 = r2_score(y_test, preds)
        print("R2:", r2)

    def save_model(self, fname):
        with open(fname, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load_model(fname="xgboost_regressor.pkl"):
        with open(fname, "rb") as file:
            return pickle.load(file)


def infer_model(model_path: str, data: pd.DataFrame) -> float:
    """This function is used to infer model on new data.

    Args:
        model_path (str): Model path
        data (pd.DataFrame): Data to be infered as a DataFrame.

    Returns:
        float: Predicted price
    """
    model = XGBoostRegressor.load_model(model_path)
    data = DataPreprocessor.static_cast_types(data)
    return model.predict(data)[0]


if __name__ == "__main__":
    preprocessor = DataPreprocessor()

    preprocessor.run_preprocessing_pipeline()
    X_train, X_test, y_train, y_test = preprocessor.train_test_split()

    print("-" * 50)
    print("XGBoost Regressor")
    xgb_regressor = XGBoostRegressor()
    xgb_regressor.random_search_cv(
        X_train, y_train, n_iter=500, random_state=30, verbose=2
    )
    xgb_regressor.train(X_train, y_train, X_test, y_test, verbose=False)
    xgb_regressor.plot_learning_curves()
    xgb_regressor.evaluate(X_test, y_test)
    xgb_regressor.save_model("xgboost_regressor.pkl")

    data_to_infer = {
        "status": ["pierwotny"],
        "size": [100.0],
        "property_type": ["kamienica"],
        "rooms": [1.0],
        "floor": ["2"],
        "year_built": ["2024"],
        "property_condition": ["do_wykonczenia"],
        "location": ["Stare Miasto"],
    }
    print(infer_model("xgboost_regressor.pkl", data_to_infer))
