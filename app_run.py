from io import BytesIO
import re
import pandas as pd
import requests
import streamlit as st
from PIL import Image
from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import DataMain, Opportunities
from _common.misc.variables import (
    LOCATION_LIST,
    PROPERTY_CONDITION_LIST,
    PROPERTY_TYPE_LIST,
    STATUS_LIST,
)
from ml_model.pricepy_model import PricepyModel

st.set_page_config(
    page_title="Pricepy",
    page_icon="app/images/logo_icon.png"
)


def is_valid_email(email):
    email_regex = r'^\S+@\S+\.\S+$'
    return re.match(email_regex, email) is not None


def format_number_with_spaces(number):
    formatted_number = '{:,.0f}'.format(number).replace(',', ' ')
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

dbconn = DBConnector()
model = PricepyModel()
model.load_model()

engine = dbconn.create_sql_engine()
session = dbconn.create_session()
query = session.query(Opportunities).add_columns(DataMain.location, DataMain.image_url, DataMain.price).outerjoin(
    DataMain)
df = pd.read_sql(query.statement, engine)

common_size = (200, 150)
display_msg = False

st.image('app/images/logo.png', width=460)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Okazje inwestycyjne", "Ile to kosztuje?", "Artykuły", "Raporty", "Mój nowy dom"]
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

        price = format_number_with_spaces(df_to_show.loc[0, "price"])
        predicted_price = format_number_with_spaces(df_to_show.loc[0, "predicted_price"])
        response = requests.get(df_to_show.loc[0, "image_url"])
        img = Image.open(BytesIO(response.content))
        resized_img = img.resize(common_size)
        st.image(resized_img)
        st.markdown("#### " + df_to_show.loc[0, "location"])
        st.markdown("**Rzeczywista cena:** " + str(price) + " zł", unsafe_allow_html=True)
        st.markdown("**Przewidywana cena:** " + str(predicted_price) + " zł", unsafe_allow_html=True)
        url = df_to_show.loc[0, "url"]
        show_button(url)

    with col5:
        df_to_show, display_msg = adjust_df(df_to_show, df, [0, 1], display_msg)

        price = format_number_with_spaces(df_to_show.loc[1, "price"])
        predicted_price = format_number_with_spaces(df_to_show.loc[1, "predicted_price"])
        response = requests.get(df_to_show.loc[1, "image_url"])
        img = Image.open(BytesIO(response.content))
        resized_img = img.resize(common_size)
        st.image(resized_img)
        st.markdown("#### " + df_to_show.loc[1, "location"])
        st.markdown("**Rzeczywista cena:** " + str(price) + " zł", unsafe_allow_html=True)
        st.markdown("**Przewidywana cena:** " + str(predicted_price) + " zł", unsafe_allow_html=True)
        url = df_to_show.loc[1, "url"]
        show_button(url)

    with col6:
        df_to_show, display_msg = adjust_df(df_to_show, df, [0, 1, 2], display_msg)

        price = format_number_with_spaces(df_to_show.loc[2, "price"])
        predicted_price = format_number_with_spaces(df_to_show.loc[2, "predicted_price"])
        response = requests.get(df_to_show.loc[2, "image_url"])
        img = Image.open(BytesIO(response.content))
        resized_img = img.resize(common_size)
        st.image(resized_img)
        st.markdown("#### " + df_to_show.loc[2, "location"])
        st.markdown("**Rzeczywista cena:** " + str(price) + " zł", unsafe_allow_html=True)
        st.markdown("**Przewidywana cena:** " + str(predicted_price) + " zł", unsafe_allow_html=True)
        url = df.loc[2, "url"]
        show_button(url)

if display_msg:
    st.warning('Oj, niewiele okazji w tej lokalizacji...', icon='😔')

st.markdown(
    """

            ---

            """
)

col7, col8 = st.columns([0.7, 0.3])

with tab2:
    col1, col2 = st.columns([0.5, 0.5])

    with col1:
        location = st.selectbox("Lokalizacja", options=LOCATION_LIST)
        size = st.number_input("Metraż", min_value=1, value=60)

    with col2:
        property_condition = st.selectbox(
            "Stan nieruchomości", options=PROPERTY_CONDITION_LIST
        )
        rooms = st.slider("Liczba pomieszczeń", min_value=1, max_value=10, value=3)

    with st.expander("Więcej cech"):
        col1, col2 = st.columns([0.5, 0.5])

        with col1:
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

        with col2:
            property_type = st.selectbox(
                "Typ budynku",
                options=PROPERTY_TYPE_LIST,
                index=None,
                placeholder="brak informacji",
            )
            floor = st.number_input(
                "Piętro", min_value=0, value=None, placeholder="brak informacji"
            )

    if st.button("Sprawdź", type="primary"):
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
            st.error('Dobierz sensowniejsze parametry', icon='❌')
            st.markdown("### Przewidywana cena: " + str(format_number_with_spaces(predicted_price)) + " zł")
            st.markdown("### Za m2: " + str(predicted_price_per_m2) + " zł")
        else:
            st.markdown("### Przewidywana cena: " + str(format_number_with_spaces(predicted_price)) + " zł")

with tab5:
    st.markdown('#### Bargainletter')
    email = st.text_input('Mail', label_visibility='hidden', placeholder='Wpisz mail')
    if st.button('Subskrybuj', type='primary'):

        if is_valid_email(email):
            emails = pd.read_sql("SELECT * FROM emails", con=engine)
            if email in emails['email'].values:
                st.warning('Już jesteś zapisany!', icon='✨')
            else:
                df = pd.DataFrame({'email': [email]})
                df.to_sql('emails', con=engine, if_exists='append', index=False)
                st.success('Super oferty już lecą!', icon="✅")
        else:
            st.error('Wprowadź poprawny mail!', icon="❗")

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
