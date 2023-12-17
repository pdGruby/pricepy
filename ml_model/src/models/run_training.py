from ml_model.src.data.data_preprocessing import DataPreprocessor
from ml_model.src.models.artifact_manager import ArtifactManager
from ml_model.src.models.model import HousePriceRegressor


def main():
    preprocessor = DataPreprocessor()
    preprocessor.run_preprocessing_pipeline()
    X_train, X_test, y_train, y_test = preprocessor.train_test_split()

    model = HousePriceRegressor()
    model.load_data(X_train, X_test, y_train, y_test)
    model.run_training_pipeline(n_iter=1000)

    mae, rmse, r2 = model.evaluate(verbose=False)
    hparams = model.best_params_

    artifact_manager = ArtifactManager()
    artifact_manager.push_artifact(mae, rmse, r2, model, hparams)


if __name__ == "__main__":
    main()
