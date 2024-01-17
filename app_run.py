import pandas as pd
import streamlit as st
import requests
import re
from PIL import Image
from io import BytesIO
from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import (BargainletterEmails,
                                                  DataMain, Opportunities)
from _common.misc.variables import (LOCATION_LIST, PROPERTY_CONDITION_LIST,
                                    PROPERTY_TYPE_LIST, STATUS_LIST)
from app.dashboards import Dashboards
from ml_model.pricepy_model import PricepyModel


st.set_page_config(
    page_title="Pricepy",
    page_icon="app/images/logo_icon.png"
)


@st.cache_resource
def create_db_connection():
    dbconn = DBConnector()
    engine = dbconn.create_sql_engine()
    return dbconn, engine


@st.cache_data
def load_dashboards_data(_dbconn, _engine):
    session = _dbconn.create_session()
    query = session.query(DataMain)
    return pd.read_sql(query.statement, _engine)


@st.cache_data
def load_opportunities_data(_dbconn, _engine):
    session = _dbconn.create_session()
    query = session.query(Opportunities).add_columns(DataMain.location, DataMain.image_url, DataMain.price).outerjoin(
        DataMain)
    return pd.read_sql(query.statement, _engine)


def add_bargainletter_info_to_db(_dbconn, email, max_real_price, min_potential_gain, location):
    session = _dbconn.create_session()
    email_obj = BargainletterEmails(email=email, max_real_price=max_real_price,
                                    min_potential_gain=min_potential_gain / 100, location=location)
    session.add(email_obj)
    session.commit()
    session.close()


@st.cache_resource
def load_model():
    model = PricepyModel()
    model.load_model()
    return model


def is_valid_email(email):
    email_regex = r'^\S+@\S+\.\S+$'
    return re.match(email_regex, email) is not None


def format_number_with_spaces(number):
    formatted_number = '{:,.0f}'.format(round(number, -2)).replace(',', ' ')
    return formatted_number


def show_button(url):
    st.markdown(
        f'<a href="{url}" style="display: inline-block; padding: 8px 12px; background-color: #10500a; color: white; '
        f'text-align: center; text-decoration: none; font-size: 16px; border-radius: 8px;">Zobacz 👀</a>',
        unsafe_allow_html=True
    )


def adjust_df(df_to_show, df, list, display_msg):
    if df_to_show.shape[0] in list:
        display_msg = True
        return df, display_msg
    else:
        return df_to_show, display_msg


def display_property_info(df, index):
    price = format_number_with_spaces(df.loc[index, "price"])
    predicted_price = format_number_with_spaces(df.loc[index, "predicted_price"])
    response = requests.get(df.loc[index, "image_url"])
    img = Image.open(BytesIO(response.content))
    resized_img = img.resize(common_size)
    st.image(resized_img)
    st.markdown("#### " + df.loc[index, "location"])
    st.markdown("**Rzeczywista cena:** " + str(price) + " zł", unsafe_allow_html=True)
    st.markdown("**Przewidywana cena:** " + str(predicted_price) + " zł", unsafe_allow_html=True)
    url = df.loc[index, "url"]
    show_button(url)


hide_img_fs = '''
<style>

button[title="View fullscreen"] {
    visibility: hidden;
    }

    .block-container {
    padding-top: 1rem;
                }  

</style>
'''

st.markdown(hide_img_fs, unsafe_allow_html=True)

dbconn, engine = create_db_connection()
df = load_opportunities_data(dbconn, engine)
model = load_model()
common_size = (200, 150)
display_msg = False

st.image('app/images/logo.png', width=385)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Okazje inwestycyjne", "Ile to kosztuje?", "Raporty", "Bargainletter"]
)

with tab1:
    col1, col2, col3 = st.columns([0.35, 0.5, 0.15])

    with col1:
        location = st.selectbox("Lokalizacja", options=['Cały Poznań'] + LOCATION_LIST, label_visibility='hidden')
        df_to_show = df[df['location'] == location].reset_index()

    df_to_show = df if location == 'Cały Poznań' else df_to_show

    col4, col5, col6 = st.columns(3)

    with col4:
        df_to_show, display_msg = adjust_df(df_to_show, df, [0], display_msg)
        display_property_info(df=df_to_show, index=0)

    with col5:
        df_to_show, display_msg = adjust_df(df_to_show, df, [0, 1], display_msg)
        display_property_info(df=df_to_show, index=1)

    with col6:
        df_to_show, display_msg = adjust_df(df_to_show, df, [0, 1, 2], display_msg)
        display_property_info(df=df_to_show, index=2)

    if display_msg:
        st.warning('Oj, niewiele okazji w tej lokalizacji...', icon='😔')

st.markdown(
    """

            ---

            """
)

col7, col8 = st.columns([0.7, 0.3])

with col7:
    st.markdown("#### Pricepy")
    st.text(
        "Precyzyjnie oszacujemy cenę każdego\nmieszkania oraz wskażemy najlepsze\ndostępne oferty, zapewniając "
        "najbardziej\naktualne informacje o nieruchomościach."
    )

with col8:
    st.markdown("#### Kontakt")
    st.text("Adres")
    st.text("Telefon XXX XXX XXX")
    st.text("Mail pricepy@pr.pl")

with tab2:
    with st.form("Properties"):
        col1, col2 = st.columns([0.5, 0.5])

        with col1:
            location = st.selectbox("Lokalizacja", options=LOCATION_LIST)
            size = st.number_input("Metraż", min_value=1, value=60)

        with col2:
            property_condition = st.selectbox(
                "Stan nieruchomości", options=PROPERTY_CONDITION_LIST
            )
            rooms = st.slider("Liczba pokojów", min_value=1, max_value=10, value=3)

        with st.expander("Więcej cech"):
            col3, col4 = st.columns([0.5, 0.5])

            with col3:
                status = st.selectbox(
                    "Rynek", options=STATUS_LIST, index=None, placeholder="brak informacji"
                )
                year_built = st.number_input(
                    "Rok budowy",
                    min_value=1700,
                    max_value=2050,
                    value=None,
                    placeholder="brak informacji",
                )

            with col4:
                property_type = st.selectbox(
                    "Typ budynku",
                    options=PROPERTY_TYPE_LIST,
                    index=None,
                    placeholder="brak informacji",
                )
                floor = st.number_input(
                    "Piętro", min_value=0, value=None, placeholder="brak informacji"
                )

        col5, col6, col7 = st.columns([0.43, 0.32, 0.25])

        with col6:
            btn_check = st.form_submit_button("Sprawdź", type="primary")

        if btn_check:
            floor = "brak informacji" if floor is None else floor
            year_built = "brak informacji" if year_built is None else year_built
            data = {
                "status": [status],
                "size": [size],
                "property_type": [property_type],
                "rooms": [rooms],
                "floor": [floor],
                "year_built": [year_built],
                "property_condition": [property_condition],
                "location": [location]
            }
            data = pd.DataFrame(data)
            data.fillna("brak informacji", inplace=True)
            predicted_price = model.predict(data)[0][0]
            predicted_price_per_m2 = predicted_price / size

            if (predicted_price_per_m2 > 20000) or (predicted_price_per_m2 < 8000):
                st.error('Proszę dobrać inne parametry', icon='❌')
            else:
                st.markdown("### Przewidywana cena: " + str(format_number_with_spaces(predicted_price)) + " zł")

with tab3:
    dashboards_df = load_dashboards_data(dbconn, engine)
    plots = Dashboards(data=dashboards_df).get_all_figs()
    for plot in plots:
        st.plotly_chart(plot)

with tab4:
    col1, col2, col3 = st.columns([0.40, 0.30, 0.30])

    with col2:
        st.markdown('#### Bargainletter')

    with st.form("Bargainletter"):
        col4, col5 = st.columns([0.5, 0.5])

        with col4:
            location = st.selectbox("Lokalizacja", options=['Cały Poznań'] + LOCATION_LIST, key='loc_bl')
            max_real_price = st.number_input(
                "Maksymalna rzeczywista cena mieszkania [zł]",
                min_value=0,
                value=700000,
                step=10000
            )

        with col5:
            min_potential_gain = st.number_input(
                "Minimalny procent zysku",
                min_value=0,
                max_value=100,
                value=10
            )
            email = st.text_input('Email', placeholder='przyklad@gmail.com')

        col6, col7, col8 = st.columns([0.421, 0.279, 0.30])

        with col7:
            btn_subskrybuj = st.form_submit_button('Subskrybuj', type="primary")

        if btn_subskrybuj:
            if is_valid_email(email):
                add_bargainletter_info_to_db(dbconn, email, max_real_price, min_potential_gain, location)
                st.success('Super oferty już lecą!', icon="✅")
            else:
                st.error('Wprowadź poprawny mail!', icon="❗")

