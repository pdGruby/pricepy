from typing import Union, List, Any

import re
import pandas as pd

from _common.misc.variables import LOCATION_LIST
from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import DataStagingCols, DataStaging


class DataCleaner(DBConnector):
    def __init__(self):
        super().__init__()
        self.data = self._get_data()
        self.session = self.create_session()
        self.engine = self.create_sql_engine()

    def __del__(self):
        self.session.close()

    def clean(self):
        data = self.data
        data = self._preprocess_data(data)

        data = self._process_price(data)
        data = self._process_size(data)
        data = self._process_location(data)
        data = self._process_floor(data)
        data = self._process_property_type(data)

        return data

    def add_metadata(self):
        data = self.data
        pass
        # Zastanów się czy wszystkich dotychczasowych metod nie wyrzucić do innej klasy (DataCleaner),
        # a w osobnej klasie trzymać logikę operowania tymi danymi (wrzucania/wyciągania z bazy danych).
        # Pomyśl gdzie bardziej pasuje add_metadata

    def _get_data(self) -> pd.DataFrame:
        query = self.session.query(DataStaging).select().statement
        data = pd.read_sql(query, self.engine)
        return data

    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.applymap(lambda value: value.lower().replace(' ', '') if isinstance(value, str) else value)
        data = data.drop_duplicates(DataStagingCols.URL, keep='last')

        # When a given information is missing, but it is not stored as NA, then convert the information to NA
        no_info_columns = [DataStagingCols.FLOOR, DataStagingCols.STATUS, DataStagingCols.PROPERTY_TYPE,
                           DataStagingCols.YEAR_BUILT, DataStagingCols.PROPERTY_CONDITION]

        data = self.replace_with_na(data, no_info_columns, 'brakinformacji')
        data = self.replace_with_na(data, [DataStagingCols.PRICE], 'zapytajocenę')
        data = self.replace_with_na(data, [DataStagingCols.FLOOR, DataStagingCols.PROPERTY_CONDITION], 'zapytaj')

        return data

    def _process_price(self, data: pd.DataFrame) -> pd.DataFrame:
        price = data[DataStagingCols.PRICE]
        price = price.apply(self.extract_float)
        currency = price.apply(self.extract_currency)

        data[DataStagingCols.CURRENCY] = currency
        data[DataStagingCols.PRICE] = price
        return data

    def _process_size(self, data: pd.DataFrame) -> pd.DataFrame:
        size = data[DataStagingCols.SIZE]
        size = size.apply(self.extract_float)

        data[DataStagingCols.SIZE] = size
        return data

    def _process_location(self, data: pd.DataFrame) -> pd.DataFrame:
        location = data[DataStagingCols.LOCATION]
        location = location.apply(self.extract_location)

        data[DataStagingCols.LOCATION] = location
        return data

    def _process_floor(self, data: pd.DataFrame) -> pd.DataFrame:
        floor = data[DataStagingCols.FLOOR]
        floor = floor.apply(self.extract_floor)

        data[DataStagingCols.FLOOR] = floor
        return data

    def _process_property_type(self, data: pd.DataFrame) -> pd.DataFrame:
        property_type = data[DataStagingCols.PROPERTY_TYPE]
        property_type = property_type.apply(self.extract_property_type)

        data[DataStagingCols.PROPERTY_TYPE] = property_type
        return data

    @staticmethod
    def replace_with_na(data: pd.DataFrame, columns: List[str], value_to_replace: Any) -> pd.DataFrame:
        for column in columns:
            data[column] = data.replace(value_to_replace, pd.NA)
        return data

    @staticmethod
    def extract_float(value: Union[str, None]) -> Union[float, None]:
        if value is None:
            return None

        pattern = '([0-9]*[,]?[0-9]+)'
        value = re.search(pattern, value)
        if value is None:
            return None

        value = value.group(1).replace(',', '.')
        value = float(value)
        return value

    @staticmethod
    def extract_currency(value: Union[str, None]) -> Union[str, None]:
        if value is None:
            return None

        pattern = '([0-9]*[,]?[0-9]+)(.*)'
        value = re.search(pattern, value)
        if value is None:
            return None

        value = value.group(2).upper()
        return value

    @staticmethod
    def extract_location(value: Union[str, None]) -> Union[str, None]:
        matched_locs = [loc for loc in LOCATION_LIST if loc.lower() in value]
        if matched_locs:
            return '/'.join(matched_locs)
        return None

    @staticmethod
    def extract_floor(value: Union[str, None]) -> Union[int, None]:
        if value is None:
            return None

        value = value.\
            replace('parter', '0').\
            replace('poddasze', '100').\
            replace('suterena', '-1')

        pattern = '(-?[0-9]{1,3})[/]([0-9]{1,2})'
        value = re.search(pattern, value)
        if value is None:
            return None

        value = value.group(1)
        value = int(value)
        return value

    @staticmethod
    def extract_property_type(value: Union[str, None]) -> Union[str, None]:
        if value is None:
            return None

        def search_keywords(actual_value, keywords):
            for keyword in keywords:
                if keyword.lower() in actual_value.lower():
                    return True

        categories_dict = {
            'dom': ['wolnostojący', 'dom', 'bliźniak', 'szeregowiec'],
            'kamienica': ['kamienica'],
            'blok': ['blok'],
            'apartamentowiec': ['apartamentowiec'],
            'inne': ['plomba', 'pozostałe']
        }

        for category, keywords_ in categories_dict.items():
            if search_keywords(value, keywords_):
                return category
        return None
