import json
import pickle
from datetime import datetime

import randomname

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import Models


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
        """Push model to database

        Args:
            mae (float): Mean absolute error
            rmse (float): Root mean squared error
            r2 (float): R2 score
            model (model): Trained model
            hparams (dict): Hyperparameters
        """
        model_name = randomname.get_name()
        model_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        mae = float(mae)
        rmse = float(rmse)
        r2 = float(r2)
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

    def pull_artifact(
        self, model_name: str | None = None, model_date: str | None = None
    ):
        """Pull model from database. You can specify model_name or model_date to pull specific model.
        If none is specified, the latest model will be pulled.

        Args:
            model_name (str, optional): Model name. Defaults to None.
            model_date (str, optional): Model date. Defaults to None.

        Returns:
            model: Model"""
        try:
            if model_name is not None:
                latest_model = (
                    self.session.query(Models)
                    .filter(Models.model_name == model_name)
                    .first()
                )
            elif model_date is not None:
                latest_model = (
                    self.session.query(Models)
                    .filter(Models.model_date == model_date)
                    .first()
                )
            else:
                latest_model = (
                    self.session.query(Models)
                    .order_by(Models.model_date.desc())
                    .first()
                )

            if latest_model is None:
                print("\n-----------------------------------")
                print("No models found in the database.")
                return None

            model = pickle.loads(latest_model.model_binary)

            print("\n-----------------------------------")
            print(
                f"Model {latest_model.model_name} from {latest_model.model_date} pulled from database."
            )

            return model
        except Exception as e:
            print("\n-----------------------------------")
            print("Failed to pull model from database.")
            print(e)
