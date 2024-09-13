# %%
import streamlit as st
import pandas as pd

st.set_page_config(layout='wide')

@st.cache_data
def calculate_percent_changes(data, base):
    base_data = data[data['layer'] == base].reset_index(drop=True)
    percent_changes = {}

    for layer in layers:
        if layer != base:
            current_layer_data = data[data['layer'] == layer].reset_index(drop=True)
            percent_change = ((current_layer_data['value'] - base_data['value']) / base_data['value'] * 100).apply(lambda x: f'{x:.1f}%')
            percent_changes[layer] = pd.concat([current_layer_data[['name', 'aep', 'duration']], percent_change], axis=1)

    return percent_changes


# Load the data (you'd replace this with the path to your local file or keep it as is if running in the same environment)
file_path = 'merged_ifds.csv'  # Update this path if running locally
data = pd.read_csv(file_path)
data.drop(['path'], axis=1, inplace=True)
data = data.melt(['layer', 'name'])
data.columns = ['layer', 'name', 'event', 'value']
data['aep'] = data['event'].str.split("_").apply(lambda x: x[0])
data['duration'] = data['event'].str.split("_").apply(lambda x: x[1])
data.drop(['event'], axis=1, inplace=True)
data.sort_values(['layer', 'name'], inplace=True)

# %%
# Separate data based on layers
layers = data['layer'].unique()

# Calculate percentage change relative to 'limb'
percentage_changes = calculate_percent_changes(data, 'limb')

# %%
# Streamlit Interface
st.sidebar.title("Comparison tool for IFD datasets")
st.sidebar.text("Brisbane local creek catchments")

# Layer Selection
base_layer = st.sidebar.selectbox("Select base IFD dataset", layers)
percentage_changes = calculate_percent_changes(data, base_layer)

selected_layer = st.sidebar.selectbox("Select IFD dataset for comparison", [layer for layer in layers if layer != base_layer])

# AEP Selection
available_aeps = data['aep'].unique()
selected_aeps = st.sidebar.multiselect("Select AEP(s)", available_aeps, default=['10pct', '1pct', '1in2000'])

# Duration Selection
available_durations = data['duration'].unique()
selected_durations = st.sidebar.multiselect("Select duration(s)", available_durations, default=['10min', '1hr', '3hr', '6hr', '12hr', '24hr'])

# Catchment Selection
available_names = percentage_changes[selected_layer]['name'].unique()
selected_names = st.sidebar.multiselect("Select catchment(s)", available_names, default=available_names)

# Filter Data
selected_data = percentage_changes[selected_layer]
filtered_data = selected_data.loc[selected_data['name'].isin(selected_names) & selected_data['aep'].isin(selected_aeps) & selected_data['duration'].isin(selected_durations)]
filtered_data = filtered_data.pivot(columns=['aep', 'duration'], index='name', values=['value'])
filtered_data.columns = [' '.join(col[1:]).strip() for col in filtered_data.columns.values]
# filtered_data.style.background_gradient(axis=None)

# Display Data
st.dataframe(filtered_data, height=len(selected_names)*40, use_container_width=True)

# To run this app, save this script as `app.py` and run it using:
# streamlit run app.py