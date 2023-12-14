import pandas as pd
from datetime import datetime, timedelta

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import DataMain, DataMainCols, Opportunities, OpportunitiesCols
from _common.misc.variables import FEAT_COLS
from ml_model.pricepy_model import PricepyModel


class OpportunityFinder(DBConnector):
    MIN_GAIN: float = 0.08
    MAX_GAIN: float = float('inf')  # to be discussed what the upper limit is

    def __init__(self):
        super().__init__()
        self.session = self.create_session()
        self.engine = self.create_sql_engine()

        self.data = None
        self.opps = None

    def get_data(self):
        cut_date = (datetime.today() - timedelta(days=1)).date()
        query = self.session.query(DataMain).where(DataMain.last_time_seen >= cut_date).statement
        data = pd.read_sql(query, self.engine)
        self.data = data

        print("Successfully downloaded the data!")

    def find_opportunities(self):
        model = PricepyModel()
        model.load_model()

        data = self.data.copy()
        data = data.dropna()
        predicted_values = model.predict(data[FEAT_COLS])[:, 0].tolist()

        data[OpportunitiesCols.PREDICTED_PRICE] = predicted_values
        data['diff'] = data[OpportunitiesCols.PREDICTED_PRICE] - data[DataMainCols.PRICE]
        data[OpportunitiesCols.POTENTIAL_GAIN] = data['diff'] / data[DataMainCols.PRICE]

        data = data[(data[OpportunitiesCols.POTENTIAL_GAIN] >= self.MIN_GAIN) &
                    (data[OpportunitiesCols.POTENTIAL_GAIN] <= self.MAX_GAIN)]

        self.opps = data[[OpportunitiesCols.URL, OpportunitiesCols.PREDICTED_PRICE, OpportunitiesCols.POTENTIAL_GAIN]]

        print(f"Opportunities successfully found! There are {self.opps.shape[0]} investment opportunities.")

    def save_opportunities(self):
        self.session.query(Opportunities).delete()
        self.session.commit()
        self.opps.to_sql(Opportunities.__tablename__, self.engine, if_exists='append', index=False)

        print("Investment opportunities successfully inserted into the database!")
