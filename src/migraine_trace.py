
import pandas as pd
import plotly.graph_objects as go

def migraine_trace_figure(df):
    # Get the minimum and maximum dates from the DataFrame
    min_date = df['Date'].min()
    max_date = df['Date'].max()

    # Create a new DataFrame for the days with migraines
    migraine_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    migraine_df = pd.DataFrame({'Date': migraine_dates})

    # Merge the migraine DataFrame with the original DataFrame
    merged_df = pd.merge(migraine_df, df, on='Date', how='left')

    #st.dataframe(merged_df)

    # Create a new column to indicate the presence of migraines
    merged_df['Migraine'] = merged_df['Date'].apply(lambda x: 1 if x in df['Date'].values else 0)

    # Replace NaN values in the "Pain intensity" column with 0
    merged_df['Pain intensity'].fillna(0, inplace=True)

    # Create a trace for the migraine events
    migraine_trace = go.Scatter(x=merged_df['Date'], y=merged_df['Migraine'],
                                mode='markers',
                                marker=dict(color=merged_df['Migraine'],
                                            size=merged_df['Pain intensity']/5,
                                            colorscale=[[0, 'blue'], [1, 'red']],
                                            cmin=0, cmax=1,
                                            sizemode='diameter',
                                            sizeref=0.1,
                                            ),
                                text=merged_df.apply(lambda row: f"Date: {row['Date']}<br>Notes: {row['Grades']}<br>Cause: {row['Possible causes']}", axis=1),
                                hovertemplate='%{text}<extra></extra>',
                                )

    # Create a layout for the figure
    layout = go.Layout(title='Days with Migraines', xaxis=dict(title='Date'), yaxis=dict(title='Migraine'),width=1000, height=250)

    # Create the figure and add the migraine trace and layout
    fig = go.Figure(data=[migraine_trace], layout=layout)
    return fig, merged_df