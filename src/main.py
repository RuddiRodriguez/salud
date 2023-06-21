import pandas as pd 
import streamlit as st
from googletrans import Translator
import plotly.graph_objects as go
from migraine_trace import migraine_trace_figure

translator = Translator()

st.set_page_config(layout="wide")
@st.cache_data
def get_data():
    path ='/Users/ruddirodriguez/Documents/salud/Data/MigraineBuddy_20220923_20230506_1683388430995_-472361220.csv'

    df = pd.read_csv(path,skiprows=2)

    # select only columns with object data type
    object_cols = df.select_dtypes(include='object')

    for col in object_cols.columns:
    
        df[col] = df[col].apply(translator.translate, src='es', dest='en').apply(getattr, args=('text',))
    return df

df = get_data()

# define a translation function
def translate_text(text):
    return translator.translate(text, dest='en').text

# translate the column names
translated_cols = [translate_text(col) for col in df.columns]

# create a dictionary of old and new column names
columns_dict = dict(zip(df.columns, translated_cols))
#st.write(columns_dict)
# rename the columns
df = df.rename(columns=columns_dict)

# get number of days between today and the first date of the data

days = max((pd.to_datetime('today') - pd.to_datetime(df['Started'])).dt.days)
            
df.rename(columns={'Started':'Date'}, inplace=True)

col = st.columns(2)
with col[0]:
    st.metric ('Number of days', days)
with col[1]:
    st.metric ('Number of migraines', len(df))    


# Convert the "Date" column to datetime format
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = df['Date'].dt.date
df['Date'] = pd.to_datetime(df['Date'])
st.experimental_data_editor(df)

fig_migraine_trace,merged_df = migraine_trace_figure(df)
st.plotly_chart(fig_migraine_trace, use_container_width=True)

# Group the data by month and calculate the average pain intensity
# Create a new column with year and month
def intensity(df, merged_df):
    merged_df['YearMonth'] = merged_df['Date'].dt.to_period('M')
    df['YearMonth'] = df['Date'].dt.to_period('M')
    average_intensity_monthly = df.groupby('YearMonth')['Pain intensity'].mean().reset_index()
    std_intensity_monthly = df.groupby('YearMonth')['Pain intensity'].std().reset_index()

# Create a bar trace for the average pain intensity per day
    bar_trace = go.Bar(x=df['Date'], y=df['Pain intensity'],
                   marker=dict(color='blue'),
                   name='Daily Average Intensity'
                   )

# Create a line trace for the average pain intensity per month
    line_trace = go.Scatter(x=average_intensity_monthly['YearMonth'].dt.to_timestamp(), y=average_intensity_monthly['Pain intensity'],
                        mode='lines',
                        line=dict(color='red'),
                        name='Monthly Average Intensity'
                        )

# Calculate the upper and lower bounds of the error bars
    upper_bound = average_intensity_monthly['Pain intensity'] + std_intensity_monthly['Pain intensity']
    lower_bound = average_intensity_monthly['Pain intensity'] - std_intensity_monthly['Pain intensity']

# Create error bars for the line trace
    line_error_bars = go.Scatter(x=average_intensity_monthly['YearMonth'].dt.to_timestamp(),
                             y=average_intensity_monthly['Pain intensity'],
                             mode='lines',
                             line=dict(color='red', width=0),
                             error_y=dict(
                                 type='data',
                                 symmetric=False,
                                 array=std_intensity_monthly['Pain intensity'],
                                 arrayminus=std_intensity_monthly['Pain intensity'],
                                 color='red',
                                 thickness=1,
                                 width=3
                             ),
                             name='Monthly Intensity Error',
                             showlegend=False
                             )

# Create a layout for the figure
    layout = go.Layout(title='Average Pain Intensity', xaxis=dict(title='Date'), yaxis=dict(title='Average Intensity'),width=1000)

# Create the figure and add the bar, line, and error bar traces, and layout
    fig = go.Figure(data=[bar_trace, line_trace , line_error_bars], layout=layout)
    return fig

fig = intensity(df, merged_df)

st.plotly_chart(fig)


df ['Possible causes'] = df['Possible causes'].str.lower()
# Split the values in the "Possible cause" column and stack them into a Series
causes = df["Possible causes"].str.split(",\s*", expand=True).stack()

# Count the occurrences of each cause
cause_counts = causes.value_counts()

# Calculate the percentage of occurrence for each cause
cause_percentages = (cause_counts / cause_counts.sum()) * 100

# Create a bar trace for the cause percentages
bar_trace = go.Bar(x=cause_percentages.index, y=cause_percentages.values,
                   marker=dict(color='blue'),
                   )

# Sort the cause percentages in descending order
sorted_cause_percentages = cause_percentages.sort_values(ascending=False)

# Create a layout for the figure
layout = go.Layout(title='Cause Occurrence Percentage', xaxis=dict(title='Possible Cause'), yaxis=dict(title='Percentage'))

# Create the figure and add the bar trace and layout
fig = go.Figure(data=[bar_trace], layout=layout)

# Sort the x-axis categories based on the cause percentages
fig.update_xaxes(categoryorder='array', categoryarray=sorted_cause_percentages.index)

st.plotly_chart(fig)



# Group the data by week and calculate the average number of attacks per week
weekly_average = merged_df.groupby('YearMonth')['Migraine'].sum().reset_index()

# Create a bar trace for the average number of attacks per week
bar_trace = go.Bar(x=weekly_average['YearMonth'].dt.to_timestamp(), y=weekly_average['Migraine'],
                        
                        
                        name='Monthly Average Number of Attacks'
                        )
                   

# Create a layout for the figure
layout = go.Layout(title='Average Number of Attacks per Week', yaxis=dict(title='Number of Attacks'))

# Create the figure and add the bar trace and layout
fig = go.Figure(data=[bar_trace], layout=layout)

st.plotly_chart(fig)