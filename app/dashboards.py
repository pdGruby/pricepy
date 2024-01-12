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
            x=DataMainCols.PRICE,
            y=DataMainCols.LOCATION,
            color=DataMainCols.LOCATION,
            orientation="h",
            labels={
                DataMainCols.PRICE: "Średnia cena",
                DataMainCols.LOCATION: "Lokalizacja",
            },
            title="Średnia cena mieszkania w Poznaniu w zależności od lokalizacji",
        )
        return fig

    def average_price_per_property_type(self):
        df = (
            self.data.groupby(DataMainCols.PROPERTY_TYPE)[DataMainCols.PRICE]
            .mean()
            .reset_index()
        )
        df = df.sort_values(by=DataMainCols.PRICE, ascending=False)
        fig = px.bar(
            df,
            x=DataMainCols.PROPERTY_TYPE,
            y=DataMainCols.PRICE,
            color=DataMainCols.PROPERTY_TYPE,
            orientation="v",
            labels={
                DataMainCols.PRICE: "Średnia cena",
                DataMainCols.PROPERTY_TYPE: "Typ nieruchomości",
            },
            title="Średnia cena mieszkania w Poznaniu w zależności od typu nieruchomości",
        )
        return fig

    def average_price_in_time_per_location(self, window_size=5):
        # Add a new column for price per m2
        self.data["PRICE_PER_M2"] = (
            self.data[DataMainCols.PRICE] / self.data[DataMainCols.SIZE]
        )

        df = (
            self.data.groupby([DataMainCols.INSERT_DATE, DataMainCols.LOCATION])[
                "PRICE_PER_M2"
            ]
            .mean()
            .reset_index()
        )
        df = df.sort_values(by=DataMainCols.INSERT_DATE, ascending=True)

        # Calculate moving average
        df["PRICE_PER_M2"] = df.groupby(DataMainCols.LOCATION)[
            "PRICE_PER_M2"
        ].transform(lambda x: x.rolling(window=window_size).mean())

        fig = px.line(
            df,
            x=DataMainCols.INSERT_DATE,
            y="PRICE_PER_M2",
            color=DataMainCols.LOCATION,
            labels={
                "PRICE_PER_M2": "Średnia cena za metr kwadratowy",
                DataMainCols.INSERT_DATE: "Data",
            },
            title="Średnia cena mieszkania za metr kwadratowy w Poznaniu w zależności od daty",
        )

        locations = df[DataMainCols.LOCATION].unique()

        buttons = [
            dict(
                label="All",
                method="update",
                args=[{"visible": [True for _ in locations]}],
            )
        ]

        for i, location in enumerate(locations):
            visibility = [False if loc != location else True for loc in locations]
            buttons.append(
                dict(label=location, method="update", args=[{"visible": visibility}])
            )

        fig.update_layout(updatemenus=[dict(active=0, buttons=buttons)])

        return fig

    def offers_per_location(self):
        df = (
            self.data.groupby(DataMainCols.LOCATION)[DataMainCols.PRICE]
            .count()
            .reset_index()
        )
        df = df.sort_values(by=DataMainCols.PRICE, ascending=False)
        fig = px.bar(
            df,
            x=DataMainCols.PRICE,
            y=DataMainCols.LOCATION,
            color=DataMainCols.LOCATION,
            orientation="h",
            labels={
                DataMainCols.PRICE: "Liczba ofert",
                DataMainCols.LOCATION: "Lokalizacja",
            },
            title="Liczba ofert mieszkań w Poznaniu w zależności od lokalizacji",
        )
        return fig


if __name__ == "__main__":
    dashboards = Dashboards()
    dashboards.average_price_per_location().show()
    dashboards.average_price_per_property_type().show()
    dashboards.average_price_in_time_per_location().show()
    dashboards.offers_per_location().show()
