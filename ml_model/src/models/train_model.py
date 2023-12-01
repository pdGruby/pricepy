import random
from ml_model.src.data.data_preprocessing import DataPreprocessor
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.tree import DecisionTreeRegressor
from lightgbm import LGBMRegressor
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


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
        super().__init__(
            **self.best_params_, enable_categorical=self.enable_categorical, n_jobs=8
        )
        eval_set = [(X_train, y_train), (X_test, y_test)]
        self.set_params(eval_metric="rmse", early_stopping_rounds=10)
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


class LightGBMRegressor(LGBMRegressor):
    """LightGBM Regressor with RandomizedSearchCV, learning curves plotting and evaluation methods."""

    param_grid = {
        "learning_rate": [0.001, 0.01, 0.1],
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [-1, 5, 10, 15],
        "num_leaves": [5, 7, 10, 15],
        "subsample": [0.5, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.5, 0.8, 0.9, 1.0],
        "min_child_samples": [5, 10, 20, 30, 50],
        "reg_alpha": [0.05, 0.1],
        "reg_lambda": [0.1, 0.5, 1],
    }

    def __init__(self, random_state=40, **kwargs):
        super().__init__(**kwargs)
        self.random_state = random_state

    def random_search_cv(
        self, X_train, y_train, n_iter=150, cv=5, n_jobs=8, verbose=3, random_state=40
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
        eval_set = [(X_train, y_train), (X_test, y_test)]
        fit_params = {
            "early_stopping_rounds": 10,
            "eval_metric": "rmse",
            "eval_set": eval_set,
            "eval_names": ["train", "valid"],
            "verbose": 100,
        }
        super().__init__(**self.best_params_, n_jobs=8, random_state=self.random_state)

        self.fit(X_train, y_train, eval_set=eval_set, **fit_params, **kwargs)

        self.results = self.evals_result()

    def plot_learning_curves(self):
        # plot learning curves
        plt.plot(self.results["training"]["rmse"], label="train")
        plt.plot(self.results["valid_1"]["rmse"], label="test")
        plt.xlabel("Steps")
        plt.ylabel("RMSE")
        plt.title("LightGBM learning curves")
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


class RandomForestRegressor:
    pass


if __name__ == "__main__":
    preprocessor = DataPreprocessor()

    preprocessor.run_preprocessing_pipeline()
    X_train, X_test, y_train, y_test = preprocessor.train_test_split()

    xgb_regressor = XGBoostRegressor(enable_categorical=True)
    xgb_regressor.random_search_cv(X_train, y_train, n_iter=200)
    xgb_regressor.train(X_train, y_train, X_test, y_test)
    xgb_regressor.plot_learning_curves()
    xgb_regressor.evaluate(X_test, y_test)

    # lgbm_regressor = LightGBMRegressor()
    # lgbm_regressor.random_search_cv(X_train, y_train, n_iter=5, random_state=30)
    # lgbm_regressor.train(X_train, y_train, X_test, y_test)
    # lgbm_regressor.plot_learning_curves()
    # lgbm_regressor.evaluate(X_test, y_test)
