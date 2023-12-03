import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from _common.database_communicator.db_connector import DBConnector
from _common.misc.variables import LOCATION_LIST, PROPERTY_CONDITION_LIST, STATUS_LIST, PROPERTY_TYPE_LIST
from ml_model.src.models.train_model import *

st.set_page_config(
    page_title='Pricepy',
    page_icon='🏠'
)


def keep_valid_elements(text):
    valid_elements = [elem.strip() for elem in text.split(',') if
                      elem.strip() in LOCATION_LIST]
    return ' '.join(valid_elements)


dbconn = DBConnector()
engine = dbconn.create_sql_engine()
df = pd.read_sql("SELECT * FROM temp_table", con=engine)

common_size = (200, 150)
df['location'] = df['location'].apply(keep_valid_elements)

st.title('🏠 Pricepy')

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    'Okazje inwestycyjne',
    'Ile to kosztuje?',
    'Artykuły',
    'Raporty',
    'Mój nowy dom'
])

with tab1:
    col1, col2, col3 = st.columns([0.35, 0.5, 0.15])

    with col1:
        st.text_input(label='loc', placeholder='Wyszukaj lokalizację', label_visibility='hidden')

    with col2:
        st.text(' ')
        st.text(' ')
        st.button("Szukaj ", type="primary")

    col4, col5, col6 = st.columns(3)

    with col4:
        response = requests.get(df.loc[0, 'image_url'])
        img = Image.open(BytesIO(response.content))
        resized_img = img.resize(common_size)
        st.image(resized_img)
        st.markdown('#### ' + df.loc[0, 'location'])
        st.markdown('#### ' + df.loc[0, 'price'])

    with col5:
        response = requests.get(df.loc[1, 'image_url'])
        img = Image.open(BytesIO(response.content))
        resized_img = img.resize(common_size)
        st.image(resized_img)
        st.markdown('#### ' + df.loc[1, 'location'])
        st.markdown('#### ' + df.loc[1, 'price'])

    with col6:
        response = requests.get(df.loc[2, 'image_url'])
        img = Image.open(BytesIO(response.content))
        resized_img = img.resize(common_size)
        st.image(resized_img)
        st.markdown('#### ' + df.loc[2, 'location'])
        st.markdown('#### ' + df.loc[2, 'price'])

st.markdown("""

            ---

            """)

col7, col8 = st.columns([0.7, 0.3])

with tab2:
    col1, col2 = st.columns([0.5, 0.5])

    with col1:
        location = st.selectbox('Lokalizacja', options=LOCATION_LIST)
        size = st.number_input('Metraż', min_value=1, value=60)

    with col2:
        property_condition = st.selectbox('Stan nieruchomości', options=PROPERTY_CONDITION_LIST)
        rooms = st.slider('Liczba pomieszczeń', min_value=1, max_value=20, value=4)

    with st.expander('Więcej cech'):
        col1, col2 = st.columns([0.5, 0.5])

        with col1:
            status = st.selectbox('Rynek', options=STATUS_LIST, index=None, placeholder='brak informacji')
            year_built = st.number_input('Rok budowy', min_value=1700, max_value=2050, value=None,
                                         placeholder='brak informacji')

        with col2:
            property_type = st.selectbox('Typ budynku', options=PROPERTY_TYPE_LIST, index=None,
                                         placeholder='brak informacji')
            floor = st.number_input('Piętro', min_value=0, value=None, placeholder='brak informacji')

    if st.button('Sprawdź', type='primary'):
        floor = 'brak informacji' if floor is None else floor
        year_built = 'brak informacji' if year_built is None else floor
        data = {'status': [status], 'size': [size], 'property_type': [property_type], 'rooms': [rooms],
                'floor': [str(floor)], 'year_built': [str(year_built)], 'property_condition': [property_condition],
                'location': [location]}
        data = pd.DataFrame(data)
        data.fillna("brak informacji", inplace=True)
        predicted_price = infer_model(model_path='ml_model/src/models/xgboost_regressor.pkl', data=data)
        st.markdown('### Przewidywana cena: ' + str(predicted_price) + 'zł')

with col7:
    st.markdown('#### Pricepy')
    st.text('Precyzyjnie oszacujemy cenę każdego\nmieszkania oraz wskażemy najlepsze\ndostępne oferty, zapewniając '
            'najbardziej\naktualne informacje o nieruchomościach.')

with col8:
    st.markdown('#### Kontakt')
    st.text('Adres')
    st.text('Telefon XXX XXX XXX')
    st.text('Mail pricepy@pr.pl')
