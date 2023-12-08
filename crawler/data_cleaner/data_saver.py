import random
import string
import pandas as pd
from sqlalchemy import update
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from _common.database_communicator.tables import DataMain, DataMainCols, DataStaging


class DataSaver:
    engine: Engine
    conn: Connection
    session: Session
    flow_name: str

    def save_data(self, data: pd.DataFrame) -> None:
        print(f"Scraped {data.shape[0]} new records from the websites...")

        self._clone_table(DataMain.__tablename__)
        data.to_sql(self.temp_table_name, con=self.conn, if_exists='append', index=False)

        already_in_db, not_in_db = self._split_duplicates_and_new_records(data)
        print(f"There are {not_in_db.shape[0]} new records that will be inserted into the database...")
        print(f"Found {already_in_db.shape[0]} records that are already in the database. Updating the 'last_time_seen' "
              f"& 'run_id' columns...")

        not_in_db.to_sql(DataMain.__tablename__, con=self.engine, if_exists='append', index=False)
        if not already_in_db.empty:
            self._update_columns(already_in_db)

        self._delete_clone_table()
        self.session.query(DataStaging).delete()
        self.session.commit()
        print("The database has been successfully updated!")

    def _clone_table(self, table_name: str) -> None:
        char_set = string.ascii_lowercase + string.digits
        temp_table_name = 'zzz' + ''.join([random.choice(char_set) for _ in range(10)])

        query = text(f'CREATE TABLE {temp_table_name} AS SELECT * FROM {table_name} LIMIT 0')
        self.conn.execute(query)
        self.conn.commit()  # noqa

        self.temp_table_name = temp_table_name

    def _delete_clone_table(self) -> None:
        self.conn.execute(text(f'DROP TABLE {self.temp_table_name}'))
        self.conn.commit()  # noqa

    def _split_duplicates_and_new_records(self, data: pd.DataFrame):
        select_duplicates_query = (f'SELECT temp."{DataMainCols.URL}" FROM {self.temp_table_name} temp '
                                   f'INNER JOIN {DataMain.__tablename__} main '
                                   f'ON temp."{DataMainCols.URL}" = main."{DataMainCols.URL}"')

        duplicates = pd.read_sql(select_duplicates_query, con=self.engine)
        mask_in_db = data[DataMainCols.URL].isin(duplicates[DataMainCols.URL].to_numpy())

        already_in_db = data.loc[mask_in_db, :]
        not_in_db = data.loc[~mask_in_db, :]

        return already_in_db, not_in_db

    def _update_columns(self, data: pd.DataFrame) -> None:
        urls_to_update = data[DataMainCols.URL]

        update_query = update(DataMain).where(DataMain.url.in_(urls_to_update))
        self.session.execute(update_query)
        self.session.commit()
