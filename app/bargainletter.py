from typing import List, Tuple, Union

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import BargainletterEmails, BargainletterEmailsCols
from _common.database_communicator.tables import Opportunities, OpportunitiesCols
from _common.database_communicator.tables import DataMain, DataMainCols
from _common.email_sender.email_sender import EmailSender

import pandas as pd


class Bargainletter(DBConnector):

    def __init__(self):
        super().__init__()

        self.session = self.create_session()
        self.engine = self.create_sql_engine()

        self.message_structure_html = self.load_html_template('message_structure.html')
        self.table_html = self.load_html_template('table.html')
        self.table_row_html = self.load_html_template('table_row.html')

    def send_bargains(self) -> None:
        subscriber_requirements = self.get_subscriber_requirements()
        opportunities = self.get_available_opportunities()
        messages = self.generate_subscriber_messages(subscriber_requirements, opportunities)

        self.send_messages(messages)
        print("All messages sent!")

    def get_subscriber_requirements(self) -> pd.DataFrame:
        query = self.session.query(BargainletterEmails).statement
        data = pd.read_sql(query, self.engine)
        print("Got subscribers' requirements...")
        return data

    def get_available_opportunities(self) -> pd.DataFrame:
        query = self.session.query(Opportunities).add_columns(DataMain.location, DataMain.image_url, DataMain.size,
                                                              DataMain.price).outerjoin(DataMain).statement
        data = pd.read_sql(query, self.engine)
        print(f"Got available opportunities. There are {data.shape[0]} available opportunities...")
        return data

    def generate_subscriber_messages(self, subscriber_requirements: pd.DataFrame,
                                     opportunities: pd.DataFrame) -> List[Tuple]:
        messages = []
        reqs_per_subscriber = subscriber_requirements.groupby(BargainletterEmailsCols.EMAIL)

        for email, reqs in reqs_per_subscriber:
            tables_content = ""

            for _, row in reqs.iterrows():
                max_real_price = row[BargainletterEmailsCols.MAX_REAL_PRICE]
                min_potential_gain = row[BargainletterEmailsCols.MIN_POTENTIAL_GAIN]
                location = row[BargainletterEmailsCols.LOCATION]

                sub_opportunities = opportunities[
                    (opportunities[DataMainCols.PRICE] <= max_real_price) &
                    (opportunities[OpportunitiesCols.POTENTIAL_GAIN] >= min_potential_gain)
                ]

                if location != "Cały Poznań":
                    sub_opportunities = sub_opportunities[sub_opportunities[DataMainCols.LOCATION] == location]

                sub_opportunities = sub_opportunities.sort_values(by=OpportunitiesCols.POTENTIAL_GAIN)
                requirements = (max_real_price, min_potential_gain, location)
                table_content = self.generate_table_content(sub_opportunities, requirements)
                if table_content:
                    tables_content += table_content

            if tables_content == "":
                print(f'No offers found for the {email}. Continuing...')
                continue

            message = self.message_structure_html.strip().format(**{"table": tables_content})
            messages.append((email, message))

        print('Generated subscriber messages...')
        return messages

    def generate_table_content(self, sub_opportunities: pd.DataFrame, requirements: Tuple) -> Union[str, None]:
        if sub_opportunities.empty:
            return None

        table_rows = ""
        for _, row in sub_opportunities.iterrows():
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

            table_row = self.table_row_html.format(**values)
            table_rows += table_row

        values = {
            'table_rows': table_rows,
            'max_real_price': self.format_float(requirements[0]),
            'min_potential_gain': self.format_float(requirements[1] * 100),
            'location': requirements[2]
        }
        table_content = self.table_html.strip().format(**values)

        return table_content

    @staticmethod
    def format_float(float_) -> str:
        formatted_float = "{:,.2f}".format(round(float_, 2)).replace(",", " ").replace(".", ",")
        return formatted_float

    @staticmethod
    def send_messages(messages: List[Tuple]) -> None:
        for recipient, message in messages:
            if message is None:
                print(f"No investment opportunities found for: {recipient}")
                continue

            sender = EmailSender(recipients=[recipient],
                                 subject=f"[PRICEPY] Znaleźliśmy potencjalne okazje inwestycyjne!")
            sender.create_body(message)
            sender.send()

    @staticmethod
    def load_html_template(html_file_name) -> str:
        with open(f'app/bargainletter_message_html_templates/{html_file_name}', 'r', encoding='utf-8') as file:
            return file.read()
