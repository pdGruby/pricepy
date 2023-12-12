import json
import pickle
from datetime import datetime

import randomname

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import Models
from ml_model.src.data.data_preprocessing import DataPreprocessor
from ml_model.src.models.train_model import XGBoostRegressor


class ArtifactManager:
    def __init__(self):
        db_connector = DBConnector()
        self.session = db_connector.create_session()

    def push_artifact(
        self,
        mae,
        rmse,
        r2,
        model,
        hparams,
    ):
        model_name = randomname.get_name()
        model_date = datetime.now().date().isoformat()
        mae = str(mae)
        rmse = str(rmse)
        r2 = str(r2)
        model_bytes = pickle.dumps(model)
        hparams = json.dumps(hparams)
        try:
            self.session.add(
                Models(
                    model_name=model_name,
                    model_date=model_date,
                    model_mae=mae,
                    model_rmse=rmse,
                    model_r2=r2,
                    model_binary=model_bytes,
                    hparams=hparams,
                )
            )
        except Exception as e:
            self.session.rollback()
            print("\n-----------------------------------")
            print("Failed to push model to database. Rolling back...")
            print(e)
        else:
            self.session.commit()
            print("\n-----------------------------------")
            print("Model pushed to database")
        finally:
            self.session.close()
            print("\n-----------------------------------")
            print("Session closed")

    def pull_artifact(self):
        pass


if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    preprocessor.run_preprocessing_pipeline()
    X_train, X_test, y_train, y_test = preprocessor.train_test_split()

    model = XGBoostRegressor()
    model.load_data(X_train, X_test, y_train, y_test)
    model.run_training_pipeline(n_iter=1)

    mae, rmse, r2 = model.evaluate(verbose=False)
    hparams = model.best_params_

    artifact_manager = ArtifactManager()
    artifact_manager.push_artifact(mae, rmse, r2, model, hparams)
