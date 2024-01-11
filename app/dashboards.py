import pandas as pd
import plotly.express as px

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import DataMain, DataMainCols


class Dashboards(DBConnector):
    def __init__(self):
        super().__init__()
        self.session = self.create_session()
        self.engine = self.create_sql_engine()
        query = self.session.query(DataMain).statement
        self.data = pd.read_sql(query, self.engine)

    def average_price_per_location(self):
        df = (
            self.data.groupby(DataMainCols.LOCATION)[DataMainCols.PRICE]
            .mean()
            .reset_index()
        )
        df = df.sort_values(by=DataMainCols.PRICE, ascending=False)
        fig = px.bar(
            df,
            x=DataMainCols.LOCATION,
            y=DataMainCols.PRICE,
            color=DataMainCols.LOCATION,
        )
        return fig


if __name__ == "__main__":
    dashboards = Dashboards()
    dashboards.average_price_per_location().show()
