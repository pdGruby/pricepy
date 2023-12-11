from typing import Union, List, Any, Callable

import re
import pandas as pd

from _common.misc.variables import LOCATION_LIST

from _common.database_communicator.tables import DataMainCols, DataStagingCols


class DataTransformer:
    data: pd.DataFrame

    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self._preprocess_data(data)

        data = self.process_column(data, DataStagingCols.PRICE, extractor_func=self.extract_currency,
                                   insert_column=DataMainCols.CURRENCY)
        data = self.process_column(data, DataStagingCols.PRICE, extractor_func=self.extract_float)
        data = self.process_column(data, DataStagingCols.SIZE, extractor_func=self.extract_float)
        data = self.process_column(data, DataStagingCols.LOCATION, extractor_func=self.extract_location)
        data = self.process_column(data, DataStagingCols.FLOOR, extractor_func=self.extract_floor)
        data = self.process_column(data, DataStagingCols.PROPERTY_TYPE, extractor_func=self.extract_property_type)

        self.cast_type(data, DataStagingCols.URL, str)
        self.cast_type(data, DataStagingCols.PRICE, float)
        self.cast_type(data, DataMainCols.CURRENCY, str)
        self.cast_type(data, DataStagingCols.STATUS, str)
        self.cast_type(data, DataStagingCols.SIZE, float)
        self.cast_type(data, DataStagingCols.PROPERTY_TYPE, str)
        self.cast_type(data, DataStagingCols.ROOMS, int)
        self.cast_type(data, DataStagingCols.FLOOR, int)
        self.cast_type(data, DataStagingCols.YEAR_BUILT, int)
        self.cast_type(data, DataStagingCols.PROPERTY_CONDITION, str)
        self.cast_type(data, DataStagingCols.LOCATION, str)
        self.cast_type(data, DataStagingCols.DESC, str)

        return data

    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.drop_duplicates(DataStagingCols.URL, keep='last')
        data = data.applymap(lambda value: value.lower().strip()
                             if isinstance(value, str) and 'http' not in value and 'www' not in value
                             else value)

        # These are the offers that do not exist anymore, but for some reason they are still present in the OLX browser
        price_mask = data[DataStagingCols.PRICE].apply(lambda x: False if 'nie istnieje' in str(x) else True)
        data = data.loc[price_mask, :]

        # When a given information is missing, but it is not stored as NA, then convert the information to NA
        no_info_columns = [DataStagingCols.FLOOR, DataStagingCols.STATUS, DataStagingCols.PROPERTY_TYPE,
                           DataStagingCols.YEAR_BUILT, DataStagingCols.PROPERTY_CONDITION, DataStagingCols.ROOMS]

        data = self.replace_with_na(data, no_info_columns, 'brak informacji')
        data = self.replace_with_na(data, [DataStagingCols.PRICE], 'zapytaj o cenę')
        data = self.replace_with_na(data, [DataStagingCols.FLOOR, DataStagingCols.PROPERTY_CONDITION], 'zapytaj')

        return data

    @staticmethod
    def replace_with_na(data: pd.DataFrame, columns: List[str], value_to_replace: Any) -> pd.DataFrame:
        for column in columns:
            data[column] = data[column].replace(value_to_replace, None)
        return data

    @staticmethod
    def process_column(data: pd.DataFrame, column: str, extractor_func: Callable, insert_column: str = None):
        values = data[column]
        values = values.apply(extractor_func)

        if insert_column is not None:
            column = insert_column

        data[column] = values
        return data

    @staticmethod
    def extract_float(value: Union[str, None]) -> Union[float, None]:
        if pd.isna(value):
            return None

        value = value.replace(' ', '')
        pattern = '([0-9]*[,]?[0-9]+)'
        value = re.search(pattern, value)
        if value is None:
            return None

        value = value.group(1).replace(',', '.')
        value = float(value)
        return value

    @staticmethod
    def extract_currency(value: Union[str, None]) -> Union[str, None]:
        if pd.isna(value):
            return None

        value = value.replace(' ', '')
        pattern = '([0-9]*[,]?[0-9]+)(.*)'
        value = re.search(pattern, value)
        if value is None:
            return None

        value = value.group(2).upper()
        return value

    @staticmethod
    def extract_location(value: Union[str, None]) -> Union[str, None]:
        if value is None:
            return None

        matched_locs = [loc for loc in LOCATION_LIST if loc.lower() in value]
        if matched_locs:
            return matched_locs[0]
        return None

    @staticmethod
    def extract_floor(value: Union[str, None]) -> Union[int, None]:
        if pd.isna(value):
            return None

        value = value.replace(' ', '')

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
        if pd.isna(value):
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

        value = value.replace(' ', '')
        for category, keywords_ in categories_dict.items():
            if search_keywords(value, keywords_):
                return category
        return None

    @staticmethod
    def cast_type(data: pd.DataFrame, column: str, col_type: Any):
        mask = data[column].notna()
        data.loc[mask, column] = data.loc[mask, column].astype(col_type)
