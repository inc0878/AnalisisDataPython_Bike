import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def get_total_count_by_hour_df(hour_df):
  hour_count_df =  hour_df.groupby(by="hr").agg({"cnt": ["sum"]})
  return hour_count_df

def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return day_df_count_2011

def total_registered_df(day_df):
   reg_df =  day_df.groupby(by="dteday").agg({
      "registered": "sum"
    })
   reg_df = reg_df.reset_index()
   reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return reg_df

def total_casual_df(day_df):
   cas_df =  day_df.groupby(by="dteday").agg({
      "casual": ["sum"]
    })
   cas_df = cas_df.reset_index()
   cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return cas_df

def sum_order (hour_df):
    sum_order_items_df = hour_df.groupby("hr").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def macem_season (day_df): 
    season_df = day_df.groupby(by="season").cnt.sum().reset_index() 
    return season_df

days_df = pd.read_csv("dashboard/day_clean.csv")
hours_df = pd.read_csv("dashboard/hour_clean.csv")

datetime_columns = ["dteday"]
days_df.sort_values(by="dteday", inplace=True)
days_df.reset_index(inplace=True)   

hours_df.sort_values(by="dteday", inplace=True)
hours_df.reset_index(inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

min_date_hour = hours_df["dteday"].min()
max_date_hour = hours_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/inc0878/AnalisisDataPython_Bike/main/0TZ0bsPAR7gGvOoEu.jpg")
    
        # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])
  
main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & 
                       (days_df["dteday"] <= str(end_date))]

main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) & 
                        (hours_df["dteday"] <= str(end_date))]

hour_count_df = get_total_count_by_hour_df(main_df_hour)
day_df_count_2011 = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = macem_season(main_df_hour)

#Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Bike Sharing :sparkles:')

st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_orders = day_df_count_2011.cnt.sum()
    st.metric("Total Sharing Bike", value=total_orders)

with col2:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_sum)

with col3:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_sum)

st.subheader("Grafik Jumlah Pelanggan dari Bulan ke Bulan")
mnth_counts = days_df.groupby(days_df['dteday'].dt.to_period('M'))['cnt'].max()

fig, ax = plt.subplots(figsize=(16, 8))
plt.scatter(mnth_counts.index.astype(str), mnth_counts.values, c="#0000FF", s=50, marker='o')
plt.plot(mnth_counts.index.astype(str), mnth_counts.values)
plt.xlabel('Bulan')
plt.ylabel('Jumlah')
plt.title('Grafik Jumlah Pelanggan dari Bulan ke Bulan')
plt.xticks(rotation=90)
st.pyplot(fig)

st.subheader("Perbandingan Penggunaan Sepeda pada Hari Kerja vs Hari Libur")
working_vs_holiday = days_df.groupby('workingday')['cnt'].sum()
fig, ax = plt.subplots(figsize=(8, 5))
working_vs_holiday.plot(kind='bar', color=['#1f77b4', '#ff7f0e'], ax=ax)
ax.set_xlabel('0 = Hari Libur, 1 = Hari Kerja')
ax.set_ylabel('Total Penggunaan Sepeda')
ax.set_title('Perbandingan Penggunaan Sepeda pada Hari Kerja vs Hari Libur')
st.pyplot(fig)

st.subheader("musim apa yang paling banyak disewa?")
colors = ["#D3D3D3"] * 4
season_totals = days_df.groupby("season")["cnt"].sum()
max_season = season_totals.idxmax()
season_order = season_totals.index.tolist()
colors[season_order.index(max_season)] = "#FF6F61"

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    y="cnt", 
    x="season",
    data=days_df,
    order=season_order,
    palette=colors,
    ax=ax
)
ax.set_title("Grafik Antar Musim", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

st.subheader("Perbandingan Pengguna Casual dan Registered")
total_casual = sum(days_df['casual'])
total_registered = sum(days_df['registered'])
data = [total_casual, total_registered]
labels = ['Casual', 'Registered']

fig, ax = plt.subplots()
plt.pie(data, labels=labels, autopct='%1.1f%%', colors=["#808080", "#ADD8E6"])
plt.title('Casual vs Registered Users')
st.pyplot(fig)
