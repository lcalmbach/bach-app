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
    chart = alt.Chart(df).mark_circle().encode(
        alt.X('zeit:T'), 
        alt.Y('value:Q'), 
        color = 'variable',
        tooltip=['zeit', 'variable', 'value'])
    st.altair_chart(chart, use_container_width=True)

def show_box_plot(df):
    chart =  alt.Chart(df).mark_boxplot().encode(
        x='variable:O',
        y='value:Q')
    st.altair_chart(chart, use_container_width=True)

def main():
    st.image('./images/rheinschwimmen-2006-4.jpg',width=800)
    df = get_data(1)
    
    temp = df.iloc[0]['temperatur']
    obs_time = df.iloc[0]['zeit']
    obs_time = obs_time.strftime("%d.%m.%Y %H:%M")
    st.markdown(f"## Rhein Temperatur ")
    st.markdown(f"aktuell: ({obs_time}): <b>{temp}</b> C°", unsafe_allow_html=True)
    tage = st.number_input('Anzeige seit n Tagen',value = default_history)
    df = get_data(tage * 24 * 4)
    variablen = st.multiselect('Variablen in Grafik',['temperatur','leitfaehigkeit','O2','pH'], default=['temperatur'])
    # Beschränke Felder auf Zeit + Ausgewählte Variablen
    df = df[['zeit'] + variablen]
    # Entpivotiere den Dataframe
    df = pd.melt(df, id_vars=['zeit'], value_vars=variablen)
    
    show_time_series(df)
    show_box_plot(df)
    


if __name__ == '__main__':
    main()
