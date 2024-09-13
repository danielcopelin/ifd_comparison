# %%
import streamlit as st
import pandas as pd

st.set_page_config(layout='wide')

aeps = ['63pct', '50pct', '20pct', '10pct', '5pct', '2pct', '1pct', '1in200', '1in500', '1in1000', '1in2000']
durations = ['5min', '10min', '15min', '20min', '25min', '30min', '45min', '1hr', '90min', '2hr', '3hr', '270min', '6hr', '9hr', '12hr', '18hr', '24hr', '30hr', '36hr', '48hr', '72hr', '96hr', '120hr', '144hr', '168hr']

# Load the data (you'd replace this with the path to your local file or keep it as is if running in the same environment)
percent_changes = pd.read_parquet('percent_changes.parquet')
equivalent_aeps = pd.read_parquet('equivalent_aeps.parquet')
old_vs_new_values = pd.read_parquet('old_vs_new_values.parquet')

# %%
# Separate data based on layers
layers = percent_changes['base'].unique()

# Comparison method
methods = {
    'Percentage difference': percent_changes,
    'Equivalent AEP': equivalent_aeps,
    'Old vs new values': old_vs_new_values
}

# %%
# Streamlit Interface
st.sidebar.title("Comparison tool for IFD datasets")
st.sidebar.text("Brisbane local creek catchments")

# Method Selection
method = st.sidebar.selectbox("Select comparison method", list(methods.keys()))

# Layer Selection
base_layer = st.sidebar.selectbox("Select base IFD dataset", layers)
changes = methods[method]

selected_layer = st.sidebar.selectbox("Select IFD dataset for comparison", [layer for layer in layers if layer != base_layer])

# AEP Selection
available_aeps = [a for a in aeps if a in changes['aep'].unique()]
selected_aeps = st.sidebar.multiselect("Select AEP(s)", available_aeps, default=['10pct', '1pct', '1in2000'])

# Duration Selection
available_durations = [d for d in durations if d in changes['duration'].unique()]
selected_durations = st.sidebar.multiselect("Select duration(s)", available_durations, default=['10min', '30min', '1hr', '3hr', '6hr', '12hr', '24hr'])

# Catchment Selection
available_names = changes['name'].unique()
selected_names = st.sidebar.multiselect("Select catchment(s)", available_names, default=available_names)

# Filter Data
if len(selected_names) == 1:
    selected_data = changes.loc[(changes['base'] == base_layer) & (changes['layer'] == selected_layer)]
    filtered_data = selected_data.loc[selected_data['name'].isin(selected_names) & selected_data['aep'].isin(selected_aeps) & selected_data['duration'].isin(selected_durations)]
    filtered_data = filtered_data.pivot(columns=['duration'], index='aep', values=['value'])
    filtered_data.columns = [' '.join(col[1:]).strip() for col in filtered_data.columns.values]

    filtered_data = filtered_data[[d for d in durations if d in filtered_data.columns]]
    filtered_data = filtered_data.reindex([a for a in aeps if a in filtered_data.index], axis=0)

    st.dataframe(filtered_data, height=len(selected_aeps)*50, use_container_width=True)
else:
    selected_data = changes.loc[(changes['base'] == base_layer) & (changes['layer'] == selected_layer)]
    filtered_data = selected_data.loc[selected_data['name'].isin(selected_names) & selected_data['aep'].isin(selected_aeps) & selected_data['duration'].isin(selected_durations)]
    filtered_data = filtered_data.pivot(columns=['aep', 'duration'], index='name', values=['value'])
    filtered_data.columns = [' '.join(col[1:]).strip() for col in filtered_data.columns.values]    

    st.dataframe(filtered_data, height=len(selected_names)*40, use_container_width=True)
# filtered_data.style.background_gradient(axis=None)
