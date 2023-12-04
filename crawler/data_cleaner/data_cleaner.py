import pandas as pd

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import DataStaging
from crawler.data_cleaner.data_transformer import DataTransformer
from crawler.data_cleaner.metadata_creator import MetadataCreator

# do orkiestracji:
# from prefect.context import FlowRunContext
# @task
# def my_task():
#    flow_run_name = FlowRunContext.get().flow_run.dict().get('name')
# powyższe flowname przekazujesz do DataCleanera


class DataCleaner(DBConnector, DataTransformer, MetadataCreator):
    def __init__(self, flow_name):
        super().__init__()

        self.flow_name = flow_name
        self.session = self.create_session()
        self.engine = self.create_sql_engine()

    def __del__(self):
        self.session.close()

    def clean_and_save_data(self) -> None:
        data = self._get_data()
        data = self.transform_data(data)
        data = self.add_metadata(data)
        self.save_data(data)

    def _get_data(self) -> pd.DataFrame:
        query = self.session.query(DataStaging).select().statement
        data = pd.read_sql(query, self.engine)
        return data

    def save_data(self, data) -> None:
        raise NotImplementedError
