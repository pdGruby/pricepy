from ml_model.src.data.data_preprocessing import DataPreprocessor
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from sklearn.model_selection import RandomizedSearchCV
from lightgbm import LGBMRegressor
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from _common.misc.variables import CATEGORICAL_FEATS, NUMERIC_FEATS
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import pickle
from typing import Dict, List, Union


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

    def save_model(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load_model(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)


class LightGBMRegressor(LGBMRegressor):
    """LightGBM Regressor with RandomizedSearchCV, learning curves plotting and evaluation methods."""

    param_grid = {
        "learning_rate": [0.001, 0.01, 0.1],
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [5, 10, 15],
        "num_leaves": [5, 10, 15, 30],
        "subsample": [0.5, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.8, 0.9, 1.0],
        "min_child_samples": [5, 10, 20],
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
        self.set_params(**self.best_params_, n_jobs=8, random_state=self.random_state)

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

    def save_model(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load_model(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)


class CatBoostRegressorModel(CatBoostRegressor):
    """CatBoost Regressor with RandomizedSearchCV, learning curves plotting and evaluation methods."""

    param_grid = {
        "learning_rate": [0.001, 0.01, 0.1, 0.2],
        "depth": [5, 10, 15],
        "l2_leaf_reg": [1, 3, 5, 7, 9],
        "border_count": [32, 5, 10, 20, 50, 100, 200],
        "iterations": [100, 200, 300],
    }

    def __init__(self, **kwargs):
        self.cat_features = CATEGORICAL_FEATS
        if "cat_features" not in kwargs:
            kwargs["cat_features"] = self.cat_features
        super().__init__(**kwargs)

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
            cat_features=self.cat_features,
            eval_metric="RMSE",
            early_stopping_rounds=10,
        )

        eval_set = [(X_test, y_test)]
        self.fit(X_train, y_train, eval_set=eval_set, **kwargs)

        self.results = self.get_evals_result()

    def plot_learning_curves(self):
        # plot learning curves
        plt.plot(self.results["learn"]["RMSE"], label="train")
        plt.plot(self.results["validation"]["RMSE"], label="test")
        plt.xlabel("Steps")
        plt.ylabel("RMSE")
        plt.title("CatBoost learning curves")
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

    def save_model(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load_model(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)


class RegressionModel:
    def __init__(self, params=None):
        self.params = params

    def train(self, X_train, y_train):
        categorical_features = CATEGORICAL_FEATS
        numerical_features = NUMERIC_FEATS

        # Create transformers for categorical and numerical features
        categorical_transformer = Pipeline(
            steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))]
        )

        numerical_transformer = Pipeline(steps=[("scaler", StandardScaler())])

        # Combine transformers using ColumnTransformer
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numerical_transformer, numerical_features),
                ("cat", categorical_transformer, categorical_features),
            ]
        )

        # Create final pipeline with preprocessor and estimator
        model = Pipeline(
            steps=[("preprocessor", preprocessor), ("regressor", LinearRegression())]
        )
        model.fit(X_train, y_train)
        self.params = model.get_params()
        self.model = model
        return model

    def evaluate(self, X_test, y_test):
        preds = self.model.predict(X_test)

        # Evaluate the model
        mae_score = mean_absolute_error(y_test, preds)
        print("MAE:", mae_score)

        rmse_score = np.sqrt(mean_squared_error(y_test, preds))
        print("RMSE:", rmse_score)

        r2 = r2_score(y_test, preds)
        print("R2:", r2)


def infer_model(model_path: str, data: Dict[str, List[Union[str, float]]]) -> float:
    """This function is used to infer model on new data.

    Args:
        model_path (str): Model path
        data (Dict[str, List[Union[str, float]]]): Data to be infered as a dictionary. Here is an example:
        {'status' : ['pierwotny'],
        'size' : [100.0],
        'property_type' : ['kamienica'],
        'rooms' : [1.0],
        'floor' : ['2'],
        'year_built' : ['2024'],
        'property_condition' : ['do_wykonczenia'],
        'location' : ['Stare Miasto']}

    Returns:
        float: Predicted price
    """
    model = XGBoostRegressor.load_model(model_path)
    data = pd.DataFrame(data)
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
        X_train, y_train, n_iter=2, random_state=30, verbose=2
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

    # print('-'*50)
    # print('LightGBM Regressor')
    # lgbm_regressor = LightGBMRegressor()
    # lgbm_regressor.random_search_cv(X_train, y_train, n_iter=1, random_state=30, verbose=10)
    # lgbm_regressor.train(X_train, y_train, X_test, y_test)
    # lgbm_regressor.plot_learning_curves()
    # lgbm_regressor.evaluate(X_test, y_test)

    # print('-'*50)
    # print('CatBoost Regressor')
    # catboost_regressor = CatBoostRegressorModel()
    # catboost_regressor.random_search_cv(X_train, y_train, n_iter=5, random_state=30, verbose=1)
    # catboost_regressor.train(X_train, y_train, X_test, y_test, verbose=False)
    # catboost_regressor.plot_learning_curves()
    # catboost_regressor.evaluate(X_test, y_test)

    # print('-'*50)
    # print('Linear Regression')
    # linear_regressor = RegressionModel()
    # linear_regressor.train(X_train, y_train)
    # linear_regressor.evaluate(X_test, y_test)
