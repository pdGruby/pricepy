import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from _common.database_communicator.db_connector import DBConnector
from _common.misc.variables import LOCATION_LIST

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

with col7:
    st.markdown('#### Pricepy')
    st.text('Precyzyjnie oszacujemy cenę każdego\nmieszkania oraz wskażemy najlepsze\ndostępne oferty, zapewniając '
            'najbardziej\naktualne informacje o nieruchomościach.')

with col8:
    st.markdown('#### Kontakt')
    st.text('Adres')
    st.text('Telefon XXX XXX XXX')
    st.text('Mail pricepy@pr.pl')
