import pandas as pd
import plotly.express as px

from _common.database_communicator.tables import DataMainCols


class Dashboards:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def average_price_per_location(self):
        self.data["PRICE_PER_M2"] = (
            self.data[DataMainCols.PRICE] / self.data[DataMainCols.SIZE]
        )
        df = (
            self.data.groupby(DataMainCols.LOCATION)["PRICE_PER_M2"]
            .mean()
            .reset_index()
        )
        df = df.sort_values(by="PRICE_PER_M2", ascending=False)
        fig = px.bar(
            df,
            x="PRICE_PER_M2",
            y=DataMainCols.LOCATION,
            color=DataMainCols.LOCATION,
            orientation="h",
            labels={
                "PRICE_PER_M2": "Średnia cena za metr kwadratowy",
                DataMainCols.LOCATION: "Lokalizacja",
            },
            title="Średnia cena za metr kwadratowy nieruchomości w Poznaniu w zależności od lokalizacji",
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
            title="Średnia cena nieruchomości w Poznaniu w zależności od typu",
        )
        return fig

    def average_price_in_time_per_location(self, window_size=4):
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
            title="Średnia cena za metr kwadratowy nieruchomości w czasie",
        )

        locations = df[DataMainCols.LOCATION].unique().tolist()

        trace_id = 3
        for trace in fig.data:
            trace.visible = False
        fig.data[trace_id].visible = True

        buttons = [
            dict(
                label="Wszystkie",
                method="update",
                args=[{"visible": [True for _ in locations]}],
            )
        ]

        for i, location in enumerate(locations):
            visibility = [False if loc != location else True for loc in locations]
            buttons.append(
                dict(label=location, method="update", args=[{"visible": visibility}])
            )

        fig.update_layout(
            updatemenus=[
                dict(
                    type="dropdown",
                    direction="down",
                    x=1.3,
                    y=1.2,
                    showactive=True,
                    active=trace_id + 1,
                    buttons=buttons,
                )
            ]
        )

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
            title="Liczba ofert nieruchomości w Poznaniu w zależności od lokalizacji",
        )
        return fig

    def get_all_figs(self):
        return [
            self.average_price_per_location(),
            self.average_price_per_property_type(),
            self.average_price_in_time_per_location(),
            self.offers_per_location(),
        ]
