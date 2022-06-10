import streamlit as st
import requests
import pandas as pd
import altair as alt

default_history = 10
tage = default_history

@st.cache
def get_data(records:int):
    records = 10000 if records > 10000 else records
    url = f'https://data.bs.ch/api/records/1.0/search/?dataset=100046&q=&rows={records}&sort=startzeitpunkt&facet=startzeitpunkt'
    data = requests.get(url).json()
    data = data['records']
    df = pd.DataFrame(data)['fields']
    df = pd.DataFrame(x for x in df)
    df = df.rename(columns={'rus_w_o_s3_o2': 'O2', 'rus_w_o_s3_ph': 'pH', 'startzeitpunkt': 'zeit', 'rus_w_o_s3_te':'temperatur', 'rus_w_o_s3_lf':'leitfaehigkeit' })
    df["zeit"] = pd.to_datetime(df["zeit"])
    return df
    

def show_time_series(df):
    chart = alt.Chart(df).mark_line().encode(
        alt.X('zeit:T', axis=alt.Axis(title="")), 
        alt.Y('value:Q', axis=alt.Axis(title="Temperatur (°C)")), 
        color = 'variable',
        tooltip=['zeit', 'value'])
    st.altair_chart(chart, use_container_width=True)


def get_emoji(temp)-> str:
    result =""
    if temp<18:
        result = "🥶"
    elif temp < 23:
        result = "😀"
    else:
        result = "🥵"
    
    return result


def main():
    st.image('./images/rheinschwimmen-2006-4.jpg',width=800)
    df = get_data(1)
    
    temp = df.iloc[0]['temperatur']
    obs_time = df.iloc[0]['zeit']
    obs_time = obs_time.strftime("%d.%m.%Y %H:%M")
    st.markdown(f"## Rhein Temperatur 🌡️")
    st.markdown(f"aktuell: ({obs_time}): <b>{temp}</b> C° {get_emoji(temp)}", unsafe_allow_html=True)
    tage = st.number_input('Anzeige seit n Tagen', value = default_history)
    df = get_data(tage * 24 * 4)
    # Beschränke Felder auf Zeit + Ausgewählte Variablen
    df = df[['zeit', 'temperatur']]
    # Entpivotiere den Dataframe
    df = pd.melt(df, id_vars=['zeit'], value_vars='temperatur')
    with st.beta_expander("Grafik"):
        show_time_series(df)

    st.markdown(f"<sup>Datenquelle: [opendata.bs](https://data.bs.ch/explore/dataset/100046/table/?sort=startzeitpunkt)</sup><br><sup>[github repo](https://github.com/lcalmbach/bach-app)</sup>", unsafe_allow_html=True)


if __name__ == '__main__':
    main()
