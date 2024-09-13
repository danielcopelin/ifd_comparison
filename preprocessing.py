# %%
import pandas as pd

def calculate_percent_changes(data, base):
    base_data = data[data['layer'] == base].reset_index(drop=True)
    percent_changes = pd.DataFrame(columns=['base', 'layer', 'name', 'aep', 'duration'])

    for layer in layers:
        if layer != base:
            current_layer_data = data[data['layer'] == layer].reset_index(drop=True)
            percent_change = ((current_layer_data['value'] - base_data['value']) / base_data['value'] * 100).apply(lambda x: f'{x:.1f}%')
            percent_change = pd.concat([current_layer_data[['name', 'aep', 'duration']], percent_change], axis=1)
            percent_change['base'] = base
            percent_change['layer'] = layer
            percent_changes = pd.concat([percent_change, percent_changes])

    return percent_changes

def calculate_old_vs_new_values(data, base):
    base_data = data[data['layer'] == base].reset_index(drop=True)
    old_vs_new_values = pd.DataFrame(columns=['base', 'layer', 'name', 'aep', 'duration'])

    for layer in layers:
        if layer != base:
            current_layer_data = data[data['layer'] == layer].reset_index(drop=True)
            old_vs_new_value = base_data['value'].apply(lambda x: f"{x:.1f}") + " -> " + current_layer_data['value'].apply(lambda x: f"{x:.1f}")
            old_vs_new_value = pd.concat([current_layer_data[['name', 'aep', 'duration']], old_vs_new_value], axis=1)
            old_vs_new_value['base'] = base
            old_vs_new_value['layer'] = layer
            old_vs_new_values = pd.concat([old_vs_new_value, old_vs_new_values])

    return old_vs_new_values

def bd(base_data, name, duration):
    base_depths = base_data.drop('layer', axis=1).set_index(['name', 'aep', 'duration']).loc[name, :, duration]
    base_depths = pd.concat([base_depths['value'], pd.Series({f"<{base_depths.index[0]}": base_depths.values[0][0]*0.95, f">{base_depths.index[-1]}": base_depths.values[-1][0]*1.05})])

    return base_depths

def equiv_aeps(base_data, name, duration, new_depth):
    base_depths = bd(base_data, name, duration)
    new_aep = abs(base_depths - new_depth).idxmin()

    return new_aep

def calculate_equivalent_aeps(data, base):
    base_data = data[data['layer'] == base].reset_index(drop=True)
    equivalent_aeps = pd.DataFrame(columns=['base', 'layer', 'name', 'aep', 'duration'])

    for layer in layers:
        if layer != base:
            current_layer_data = data[data['layer'] == layer].reset_index(drop=True)
            equivalent_aep = current_layer_data.apply(lambda x: equiv_aeps(base_data, x['name'], x['duration'], x['value']), axis=1)
            equivalent_aep = pd.concat([current_layer_data[['name', 'aep', 'duration']], equivalent_aep], axis=1)
            equivalent_aep['base'] = base
            equivalent_aep['layer'] = layer
            equivalent_aeps = pd.concat([equivalent_aep, equivalent_aeps])

    return equivalent_aeps

# %%
file_path = 'merged_ifds.csv'  # Update this path if running locally
data = pd.read_csv(file_path)
data.drop(['path'], axis=1, inplace=True)
data = data.melt(['layer', 'name'])
data.columns = ['layer', 'name', 'event', 'value']
data['aep'] = data['event'].str.split("_").apply(lambda x: x[0])
data['duration'] = data['event'].str.split("_").apply(lambda x: x[1])
data.drop(['event'], axis=1, inplace=True)
data.sort_values(['layer', 'name'], inplace=True)

# Separate data based on layers
layers = data['layer'].unique()

# %%
percent_changes = pd.DataFrame()
for base in layers:
    percent_changes = pd.concat([percent_changes, calculate_percent_changes(data, base)])
percent_changes.to_csv('percent_changes.csv')

# %%
old_vs_new_values = pd.DataFrame()
for base in layers:
    old_vs_new_values = pd.concat([old_vs_new_values, calculate_old_vs_new_values(data, base)])
old_vs_new_values.to_csv('old_vs_new_values.csv')

# %%
equivalent_aeps = pd.DataFrame()
for base in layers:
    equivalent_aeps = pd.concat([equivalent_aeps, calculate_equivalent_aeps(data, base)])
equivalent_aeps.columns = ['name','aep','duration','value','base','layer']
equivalent_aeps.to_csv('equivalent_aeps.csv')

# %%
