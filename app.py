import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime
from dateutil import tz

DEFAULT_DAYS = 10
MAX_RECORDS = 10000

@st.cache
def get_air_temp():
    url = f'https://data.bs.ch/api/records/1.0/search/?dataset=100009&q=&rows=1&sort=dates_max_date&facet=name_original&facet=name_custom&facet=dates_max_date&refine.name_custom=Unterer+Rheinweg'
    data = requests.get(url).json()
    data = data['records']
    df = pd.DataFrame(data)['fields']
    df = pd.DataFrame(x for x in df)
    air_temp = df.iloc[0]["meta_airtemp"]
    return air_temp

@st.cache
def get_water_temp_data(records:int):
    records = MAX_RECORDS if records > MAX_RECORDS else records
    url = f'https://data.bs.ch/api/records/1.0/search/?dataset=100046&q=&rows={records}&sort=startzeitpunkt&facet=startzeitpunkt'
    data = requests.get(url).json()
    data = data['records']
    df = pd.DataFrame(data)['fields']
    df = pd.DataFrame(x for x in df)
    df = df.rename(columns={'rus_w_o_s3_o2': 'O2', 'rus_w_o_s3_ph': 'pH', 'startzeitpunkt': 'zeit', 'rus_w_o_s3_te':'temperatur', 'rus_w_o_s3_lf':'leitfaehigkeit' })
    df["zeit"] = pd.to_datetime(df["zeit"])
    return df
    
def show_time_series(df):
    def myround(x, base, dir):
        """Rounds a number to a user specified base. Default is 5, e.g. 46.4 -> 50"""
        result = base * round(x/base)
        if result > x and dir == -1:
            result -= base
        elif result < x and dir == 1:
            result += base
        return result

    # calculate min max and round to base 5 
    min_y = myround(df['value'].min(), 5, -1)
    max_y = myround(df['value'].max(), 5, +1)

    scale=alt.Scale(domain=[min_y, max_y])
    chart = alt.Chart(df).mark_line().encode(
        alt.X('zeit:T', axis=alt.Axis(title="")), 
        alt.Y('value:Q', axis=alt.Axis(title="Temperatur (°C)"), scale=scale),
        color=alt.Color('variable', legend=None),
        tooltip=['zeit', 'value'])
    st.altair_chart(chart, use_container_width=True)

def to_local_tz(utc_time):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Europe/Zurich')
    utc_time = utc_time.replace(tzinfo=from_zone)
    return utc_time.astimezone(to_zone)

def main():
    st.image('./images/rheinschwimmen-2006-4.jpg', width=800)
    df = get_water_temp_data(1)
    air_temp = get_air_temp()
    
    temp = df.iloc[0]['temperatur']
    utc_time = df.iloc[0]['zeit']
    local_time = to_local_tz(utc_time)
    local_time = local_time.strftime('%d. %B %H:%M')
    
    st.markdown(f"## Rhein Temperatur 🌡️")
    st.markdown(f"Datum/Zeit: {local_time}")
    cols = st.columns((1,1,2))
    with cols[0]:
        st.metric(label="Wasser Temperatur", value=f"{temp:.1f} °C")
    with cols[1]:
        st.metric(label="Luft Temperatur", value=f"{air_temp:.1f} °C")
    
    with st.expander('Zeitlicher Verlauf'):
        days = st.number_input('Anzeige seit n Tagen', min_value = 1, max_value=90, value = DEFAULT_DAYS)
        df = get_water_temp_data(days * 24 * 4)
        df = df[['zeit', 'temperatur']]
        # unpivot dataframe
        df = pd.melt(df, id_vars=['zeit'], value_vars='temperatur')
        show_time_series(df)

    st.markdown(f"<sup>BachApp Version 1.2</sup><br><sup>Datenquelle: [opendata.bs](https://data.bs.ch/explore/dataset/100046/table/?sort=startzeitpunkt)</sup><br><sup>[github repo](https://github.com/lcalmbach/bach-app)</sup>", unsafe_allow_html=True)


if __name__ == '__main__':
    main()
