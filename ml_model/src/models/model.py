import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBRegressor

from _common.misc.variables import NUMERIC_FEATS
from ml_model.src.data.data_preprocessing import DataPreprocessor


class HousePriceRegressor(XGBRegressor):
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

    def load_data(self, X_train, X_test, y_train, y_test):
        """Load data

        Args:
            X_train (pd.DataFrame): Train features
            y_train (pd.Series): Train target
            X_test (pd.DataFrame): Test features
            y_test (pd.Series): Test target
        """

        self.X_train = X_train
        self.X_test = X_test

        self.y_train = y_train
        self.y_test = y_test

    def random_search_cv(self, n_iter=150, cv=5, n_jobs=8, verbose=2, random_state=40):
        """RandomizedSearchCV for hyperparameter tuning

        Args:
            n_iter (int, optional): Number of iterations
            cv (int, optional): Number of cross-validation folds
            n_jobs (int, optional): Number of jobs
            verbose (int, optional): Verbosity
            random_state (int, optional): Random state
        """

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
        random_cv.fit(self.X_train, self.y_train)

        self.best_params_ = random_cv.best_params_

    def train(self, **kwargs):
        """Train the model

        Args:
            **kwargs: Keyword arguments for XGBRegressor.fit()
        """

        self.set_params(
            **self.best_params_,
            eval_metric="rmse",
            early_stopping_rounds=10,
            enable_categorical=self.enable_categorical,
            n_jobs=8,
        )
        eval_set = [(self.X_train, self.y_train), (self.X_test, self.y_test)]
        self.fit(self.X_train, self.y_train, eval_set=eval_set, **kwargs)

        self.results = self.evals_result()

    def plot_learning_curves(self):
        """Plot train and test RMSE scores"""

        plt.plot(self.results["validation_0"]["rmse"], label="train")
        plt.plot(self.results["validation_1"]["rmse"], label="test")
        plt.xlabel("Steps")
        plt.ylabel("RMSE")
        plt.title("XGBoost learning curves")
        plt.legend()
        plt.show()

    def evaluate(self, verbose=True):
        """Evaluate the model

        Args:
            verbose (bool, optional): Whether to print scores. Defaults to True.

        Returns:
            tuple[float, float, float]: MAE, RMSE and R2 scores
        """

        preds = self.predict(self.X_test)

        mae_score = mean_absolute_error(self.y_test, preds)
        rmse_score = np.sqrt(mean_squared_error(self.y_test, preds))
        r2 = r2_score(self.y_test, preds)

        if verbose:
            print("MAE:", mae_score)
            print("RMSE:", rmse_score)
            print("R2:", r2)

        return mae_score, rmse_score, r2

    def run_training_pipeline(self, save_pkl=False, **kwargs):
        """Run training pipeline

        Args:
            **kwargs: Keyword arguments for random_search_cv()
        """

        self.random_search_cv(**kwargs)
        self.train()
        if save_pkl:
            self.save_model("xgboost_regressor.pkl")

    def save_model(self, fname):
        """Save model to a file using pickle

        Args:
            fname (str): File name
        """

        with open(fname, "wb") as file:
            pickle.dump(self, file)

    def load_model(self, fname):
        """Load model from a file using pickle

        Args:
            fname (str): File name
        """

        with open(fname, "rb") as file:
            self.model = pickle.load(file)

    def infer(self, data: pd.DataFrame, scaler_path: str = "scaler.pkl") -> float:
        """This function is used to infer model on new data.

        Args:
            data (pd.DataFrame): Data to be infered as a DataFrame.

        Returns:
            float: Predicted price
        """

        scaler = pickle.load(open(scaler_path, "rb"))
        data = DataPreprocessor.static_cast_types(data)
        data[NUMERIC_FEATS] = scaler.transform(data[NUMERIC_FEATS])

        return self.model.predict(data)[0]
