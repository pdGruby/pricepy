from typing import List, Tuple

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import BargainletterEmails, BargainletterEmailsCols
from _common.database_communicator.tables import Opportunities, OpportunitiesCols
from _common.database_communicator.tables import DataMain, DataMainCols
from _common.email_sender.email_sender import EmailSender

from app.bargainletter_html_templates import main_message_html, table_row_html

import pandas as pd


class Bargainletter(DBConnector):

    def __init__(self):
        super().__init__()

        self.session = self.create_session()
        self.engine = self.create_sql_engine()

    def send_bargains(self):
        subscriber_requirements = self.get_subscriber_requirements()
        opportunities = self.get_available_opportunities()
        messages = self.generate_subscriber_messages(subscriber_requirements, opportunities)
        self.send_messages(messages)
        print("All messages sent!")

    def get_subscriber_requirements(self):
        query = self.session.query(BargainletterEmails).statement
        data = pd.read_sql(query, self.engine)
        print("Got subscribers' requirements...")
        return data

    def get_available_opportunities(self):
        query = self.session.query(Opportunities).add_columns(DataMain.location, DataMain.image_url, DataMain.size,
                                                              DataMain.price).outerjoin(DataMain).statement
        data = pd.read_sql(query, self.engine)
        print(f"Got available opportunities. There are {data.shape[0]} available opportunities...")
        return data

    def generate_subscriber_messages(self, subscriber_requirements: pd.DataFrame, opportunities: pd.DataFrame):
        messages = []
        for _, sub_req in subscriber_requirements.iterrows():
            email = sub_req[BargainletterEmailsCols.EMAIL]
            max_real_price = sub_req[BargainletterEmailsCols.MAX_REAL_PRICE]
            min_potential_gain = sub_req[BargainletterEmailsCols.MIN_POTENTIAL_GAIN]
            location = sub_req[BargainletterEmailsCols.LOCATION]

            sub_opportunities = opportunities[
                (opportunities[DataMainCols.PRICE] <= max_real_price) &
                (opportunities[OpportunitiesCols.POTENTIAL_GAIN] >= min_potential_gain) &
                (opportunities[DataMainCols.LOCATION] == location)
            ]

            requirements = (max_real_price, min_potential_gain, location)
            message = self.generate_html_message(sub_opportunities, requirements)
            messages.append((email, message))

        print('Generated subscriber messages...')
        return messages

    def generate_html_message(self, df: pd.DataFrame, requirements: Tuple):
        if df.empty:
            return None

        table_content = ""
        for _, row in df.iterrows():
            real_price_per_square = row[DataMainCols.PRICE] / row[DataMainCols.SIZE]
            predicted_price_per_square = row[OpportunitiesCols.PREDICTED_PRICE] / row[DataMainCols.SIZE]
            values = {
                'potential_gain': self.format_float(row[OpportunitiesCols.POTENTIAL_GAIN] * 100),
                'real_price': self.format_float(row[DataMainCols.PRICE]),
                'predicted_price': self.format_float(row[OpportunitiesCols.PREDICTED_PRICE]),
                'real_price_per_square': self.format_float(real_price_per_square),
                'predicted_price_per_square': self.format_float(predicted_price_per_square),
                'link': row[OpportunitiesCols.URL]
            }

            table_row = table_row_html.format(**values)
            table_content += table_row

        values = {
            'table_rows': table_content,
            'max_real_price': self.format_float(requirements[0]),
            'min_potential_gain': self.format_float(requirements[1] * 100),
            'location': requirements[2]
        }
        html_content = main_message_html.strip().format(**values)

        return html_content

    @staticmethod
    def format_float(float_):
        formatted_float = "{:,.2f}".format(round(float_, 2)).replace(",", " ").replace(".", ",")
        return formatted_float

    @staticmethod
    def send_messages(messages: List[Tuple]):
        for recipient, message in messages:
            if message is None:
                print(f"No investment opportunities found for: {recipient}")
                continue

            sender = EmailSender(recipients=[recipient],
                                 subject=f"[PRICEPY] Znaleźliśmy potencjalne okazje inwestycyjne!")
            sender.create_body(message)
            sender.send()
