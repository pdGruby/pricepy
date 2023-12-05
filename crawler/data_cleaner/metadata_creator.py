from typing import List

import hashlib
from datetime import datetime
import pandas as pd

from _common.database_communicator.tables import DataMainCols
from crawler.common.create_run_id import create_run_id


class MetadataCreator:
    data: pd.DataFrame
    flow_name: str
    COLUMNS_FOR_HASH: List[str] = [DataMainCols.PRICE, DataMainCols.CURRENCY, DataMainCols.ROOMS, DataMainCols.FLOOR,
                                   DataMainCols.LOCATION]

    def add_metadata(self, data):
        today_date = datetime.now().strftime("%Y-%m-%d")

        data[DataMainCols.INSERT_DATE] = today_date
        data[DataMainCols.LAST_TIME_SEEN] = today_date
        data[DataMainCols.ROW_HASH] = data.apply(self._create_row_hash, axis=1)
        data[DataMainCols.RUN_ID] = create_run_id(self.flow_name)

        data[DataMainCols.INSERT_DATE] = pd.to_datetime(data[DataMainCols.INSERT_DATE])
        data[DataMainCols.LAST_TIME_SEEN] = pd.to_datetime(data[DataMainCols.LAST_TIME_SEEN])

        return data

    def _create_row_hash(self, row):
        values_to_hash = tuple(row[self.COLUMNS_FOR_HASH])
        hash_ = hashlib.sha256(str(values_to_hash).encode('utf-8')).hexdigest()
        return hash_
