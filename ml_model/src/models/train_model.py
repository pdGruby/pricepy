from ml_model.src.data.data_preprocessing import DataPreprocessor
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import RandomizedSearchCV
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


if __name__ == "__main__":
    preprocessor = DataPreprocessor()

    preprocessor.run_preprocessing_pipeline()
    X_train, X_test, y_train, y_test = preprocessor.train_test_split()

    regressor = XGBRegressor(enable_categorical=True)

    param_grid = {
        "learning_rate": [0.001, 0.01, 0.1, 0.2, 0.3],
        "n_estimators": [50, 100, 200, 300, 500],
        "max_depth": [3, 5, 7, 9, 15, 25, 30],
        "min_child_weight": [1, 3, 5, 7, 10, 15, 20],
        "subsample": [0.5, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.5, 0.8, 0.9, 1.0],
        "gamma": [0, 0.1, 0.2, 0.3, 0.5],
        "scale_pos_weight": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "eta": [0.01, 0.1, 0.2, 0.3, 0.5],
        "reg_alpha": [0, 0.001, 0.005, 0.01, 0.05],
    }

    random_cv = RandomizedSearchCV(
        estimator=regressor,
        param_distributions=param_grid,
        cv=5,
        n_iter=150,
        scoring="neg_mean_absolute_error",
        n_jobs=8,
        verbose=2,
        return_train_score=True,
        random_state=42,
    )
    random_cv.fit(X_train, y_train)

    print(random_cv.best_params_)
    print(random_cv.best_score_)
    print(random_cv.best_estimator_.feature_importances_)

    eval_set = [(X_train, y_train), (X_test, y_test)]

    regressor = XGBRegressor(
        **random_cv.best_params_, enable_categorical=True, objective="reg:squarederror"
    )
    regressor.set_params(eval_metric="rmse", early_stopping_rounds=10)
    regressor.fit(X_train, y_train, eval_set=eval_set, verbose=False)

    results = regressor.evals_result()

    # plot learning curves
    plt.plot(results["validation_0"]["rmse"], label="train")
    plt.plot(results["validation_1"]["rmse"], label="test")
    plt.xlabel("Steps")
    plt.ylabel("RMSE")
    plt.title("XGBoost learning curves")
    plt.legend()
    plt.show()

    preds = regressor.predict(X_test)

    # Evaluate the model
    mae_score = mean_absolute_error(y_test, preds)
    print("MAE:", mae_score)

    rmse_score = np.sqrt(mean_squared_error(y_test, preds))
    print("RMSE:", rmse_score)

    r2 = r2_score(y_test, preds)
    print("R2:", r2)
