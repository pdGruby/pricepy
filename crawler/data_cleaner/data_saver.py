import random
import string
import pandas as pd
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from _common.database_communicator.tables import DataMain, DataMainCols


class DataSaver:
    engine: Engine
    flow_name: str

    def save_data(self, data: pd.DataFrame) -> None:
        self._clone_table(DataMain.__name__)
        data.to_sql(self.temp_table_name, con=self.engine, if_exists='append', index=False)

        already_in_db, not_in_db = self._split_duplicates_and_new_records(data)
        not_in_db.to_sql(DataMain.__name__, con=self.engine, if_exists='append', index=False)
        self._update_columns(already_in_db)

        self._delete_clone_table()

    def _clone_table(self, table_name: str) -> None:
        char_set = string.ascii_uppercase + string.digits
        temp_table_name = ''.join([random.choice(char_set) for _ in range(10)])

        query = f'CREATE TABLE {temp_table_name} AS SELECT * FROM {table_name} LIMIT 0'
        self.engine.execute(query)

        self.temp_table_name = temp_table_name

    def _delete_clone_table(self) -> None:
        self.engine.execute(f'DROP TABLE {self.temp_table_name}')

    def _split_duplicates_and_new_records(self, data: pd.DataFrame):
        select_duplicates_query = (f'SELECT {DataMainCols.URL} FROM {DataMain.__name__} main'
                                   f'INNER JOIN {self.temp_table_name} temp'
                                   f'ON main."{DataMainCols.URL}" = temp."{DataMainCols.URL}"')

        duplicates = pd.read_sql(select_duplicates_query, con=self.engine)
        mask_in_db = data[DataMainCols.URL].isin(duplicates[DataMainCols.URL].to_numpy())

        already_in_db = data.loc[mask_in_db, :]
        not_in_db = data.loc[~mask_in_db, :]

        return already_in_db, not_in_db

    def _update_columns(self, data: pd.DataFrame) -> None:
        data = data.to_dict(orient='records').copy()
        today_date = datetime.today()

        query = insert(DataMain).values(data)
        query = query.on_conflict_do_update(
            index_elements=[DataMainCols.URL],
            set_={DataMainCols.LAST_TIME_SEEN: datetime.today(),
                  DataMainCols.RUN_ID: today_date.strftime("%Y-%m-%d") + self.flow_name}
        )

        self.engine.execute(query)
