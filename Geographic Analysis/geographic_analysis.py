import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import pandas as pd
import geopandas as gpd


# ===== READING DATA =====
data_metln = pd.read_csv('./Final Project/Data/METLN_data.csv')
#data_metln = pd.read_csv('METLN_data.csv')
#print(set(data_metln['Date']), len(set(data_metln['Date'])))

# TIGER shapefiles
#print('Reading county subdivisions')
shapefile_path = './Final Project/Data/tl_rd22_23_cousub.zip'
gdf = gpd.read_file(shapefile_path)

# Poulation data
pop_data_path = './Final Project/Data/maine_pop_est2024_23.csv'
pop_data_all = pd.read_csv(pop_data_path)


# ===== HELPER FUNCTIONS =====
def metln_info(dataset = data_metln):
  print(f'columns = {len(dataset.columns)}; rows = {len(dataset[dataset.columns[0]])}')
  for col in dataset.columns:
    len_types = len(set(dataset[col]))
    print(f'{col} | {len_types} ')#| {set(dataset[col])}')


# ====== DATA PROCESSING & CLEANING =====
# = = = = = = = Original METLN Data = = = = = = = 
#print('Original data:') 
#metln_info()
#print('total nulls for Day Pattern METLN =', data_metln['Day pattern'].isna().sum())
data = data_metln.dropna(subset=['State', 'City', 'Zip']).reset_index(drop=True)
data['State'] = [state.upper() for state in data['State']]
data['City'] = [city.title() for city in data['City']]
data['Zip'] = [str(int(zip)) if type(zip) != str else zip for zip in data['Zip']]
data['Date'] = [str(int(date)) for date in data['Date']]
#print('\nFiltered data:')
#metln_info(data)

# List of all dates from the data in order
all_dates = list(set(data['Date']))
all_dates.sort()
first_date = all_dates[0]
first_date_formatted = f'{first_date[0:2]}/{first_date[2:4]}/{first_date[4:6]}'
most_recent = all_dates[0]
most_recent_formatted = f'{most_recent[0:2]}/{most_recent[2:4]}/{most_recent[4:6]}'

# Media type = Digital or Print
data['Media type'] = ['Digital' if pattern == 'O7Day' else 'Print' for pattern in data['Day pattern']]

# = = = = = = = Maine-only METLN data = = = = = = = 
data_me = data[data['State'] == 'ME'].copy()[['AccoutID','State','City','Zip','Date','Media type']]
data_not_me = data[data['State'] != 'ME'].copy()[['AccoutID','State','City','Zip','Date','Media type']]
print(f"Total accounts in Maine: {len(data_me[data_me['Date'] == most_recent]['AccoutID'])}")
print(f"Total accounts NOT in Maine: {len(data_not_me[data_not_me['Date'] == most_recent]['AccoutID'])}")

# Top cities in ME
print(f"Account by City in ME:")
grouped_me_date_city_data = data_me[data_me['Date'] == most_recent][['City', 'AccoutID']].groupby(by=['City']).size()
print(grouped_me_date_city_data.sort_values(ascending=False))
print()

# Quick check for all locales (States) and # of respective subscriptions 
loc_subs_dict = {}
recent_data = data[data['Date'] == most_recent].copy()
all_locs = recent_data['State'].unique()
for loc in all_locs:
    loc_subs_dict[loc] = len(recent_data[recent_data['State'] == loc])
    #print(f"# Subscriptions in {loc}: {len(recent_data[recent_data['State'] == loc])}")
#print(loc_subs_dict)
loc_subs_df = pd.DataFrame(list(loc_subs_dict.items()), columns=['State', '# Subs'])
print(loc_subs_df.sort_values(by=['# Subs'], ascending=False))

#print('\nMaine data:')
#metln_info(data_me)

#data_me_dates = data_metln[data_metln['State'] == 'ME'].groupby(['Date'], dropna=False).size().reset_index(name='Count_per_date')
#data_me_dates.fillna(0, inplace=True)

# Media type (print vs digital) per city
data_me_media_type = data_me[data_me['Date'] == most_recent].groupby(['City', 'Media type'], dropna=False).size().reset_index(name='Count_per_city')
# Adding a row for each city in case it does not have a Digital or Print value
for city in data_me_media_type['City']:
    city_medias = data_me_media_type[data_me_media_type['City'] == city]['Media type'].to_list()
    if 'Digital' not in city_medias:
        temp_df = pd.DataFrame({'City':[city],'Media type':['Digital'],'Count_per_city':[0]})
        data_me_media_type = pd.concat([data_me_media_type, temp_df])
    elif 'Print' not in city_medias:
        temp_df = pd.DataFrame({'City':[city],'Media type':['Print'],'Count_per_city':[0]})
        data_me_media_type = pd.concat([data_me_media_type, temp_df])

data_me_media_type.reset_index(inplace=True, drop=True)
digital_list = []
print_list = []
for i, r in data_me_media_type.iterrows():
    if r['Media type'] == 'Digital':
        digital_list.append(r['Count_per_city'])
        print_list.append(0)
    else:
        print_list.append(r['Count_per_city'])
        digital_list.append(0)

data_me_media_type['Digital Counts'] = digital_list
data_me_media_type['Print Counts'] = print_list

data_me_media_type = data_me_media_type[['City', 'Count_per_city', 'Digital Counts', 'Print Counts']].groupby(['City'], dropna=False).sum().reset_index()
data_me_media_type['Digital Percent'] = 100 * data_me_media_type['Digital Counts'] / data_me_media_type['Count_per_city']

#print(data_me_media_type)
#print([len(data_me_media_type[data_me_media_type['City']==city_name]) for city_name in data_me_media_type['City']])
#print(data_me_media_type[data_me_media_type['City'] == 'Acton'])
#print(data_me_media_type[data_me_media_type['City'] == 'Acton']['Media type'].to_list())
#print('Print' in data_me_media_type[data_me_media_type['City'] == 'Acton']['Media type'].to_list())

# Number of accounts per city on most recent date file
data_me_cities = data_me[data_me['Date'] == most_recent].groupby(['City'], dropna=False).size().reset_index(name='Count_per_city')
data_me_cities.fillna(0, inplace=True)
data_me_cities_first = data_me[data_me['Date'] == first_date].groupby(['City'], dropna=False).size().reset_index(name=f'Count_per_city_{first_date}')
data_me_cities_first.fillna(0, inplace=True)

# = = = = = = = Population Data = = = = = = =
me_pop = pop_data_all[['NAME', 'POPESTIMATE2024']].drop_duplicates(subset=['NAME']).drop(0)
me_pop['NAME'] = [' '.join(name.split(' ')[:-1]) for name in me_pop['NAME']]  # getting rid of "town" and "city" at end of each name
#print(data_me_cities.head(), sum(data_me_cities['Count_per_city']))
#data_me_pop_cities = data_me_cities.merge(me_pop, how='left', left_on='City', right_on='NAME')
#data_me_pop_cities.drop(['NAME'], axis=1, inplace=True)
#data_me_pop_cities.dropna(subset=['POPESTIMATE2024'], inplace=True)
#data_me_pop_cities['Count_by_pop'] = data_me_pop_cities['Count_per_city'] / data_me_pop_cities['POPESTIMATE2024']
#print(data_me_pop_cities.head(), sum(data_me_pop_cities['Count_per_city']))

# = = = = = = = Shapefile / Geopandas Data = = = = = = =
# Merging Shapefile Geopandas with the Maine account data
gdf_me = gdf.merge(data_me_cities, how='left', left_on='NAME', right_on='City')
gdf_me.fillna({'City': gdf_me['NAME']}, inplace=True)
gdf_me.fillna({'Count_per_city': 0}, inplace=True)

# Merging in population data
gdf_me = gdf_me.merge(me_pop, how='left')
gdf_me['Account_rates'] = gdf_me['Count_per_city'] / gdf_me['POPESTIMATE2024']  # account rates = number of accounts in city / population of city
#print(gdf_me)

# Merging in Digital % data
gdf_me = gdf_me.merge(data_me_media_type[['City', 'Digital Percent']], how='left', left_on='NAME', right_on='City')
#gdf_me.fillna({'Digital Percent': 0.0}, inplace=True)

# gdf_me_none : No data (0 accounts) or greater than some max val (filtering out Portland, other major cities to look at smaller counties)
# For Plot 1: # accounts per city
max_val_limit_account = 1 * max(gdf_me['Count_per_city'])
gdf_me_none = gdf_me[(gdf_me['Count_per_city'] == 0) | (gdf_me['Count_per_city'] > max_val_limit_account)]
gdf_me_real = gdf_me[(gdf_me['Count_per_city'] != 0) & (gdf_me['Count_per_city'] <= max_val_limit_account)] 

# For Plot 2: # accounts per city divided by population (accounts/pop)
max_val_limit_rates = 0.6 * max(gdf_me['Account_rates'])
gdf_me_high_rates = gdf_me[gdf_me['Account_rates'] > max_val_limit_rates]
gdf_me_low_rates = gdf_me[gdf_me['Account_rates'] <= max_val_limit_rates] 

# For Plot 3: % of digital per city
gdf_me_digital_pct_none = gdf_me[gdf_me['Digital Percent'].isnull()]
gdf_me_digital_pct_all = gdf_me[gdf_me['Digital Percent'].notnull()] 

# ===== PLOTTING ======
# PLOT 1 : Number of Accounts by City Area
fig1, ax1 = plt.subplots(1, 1, figsize=(6, 8))
ax1.set_title(f'Number of Accounts by City Area\n(logarithmic scale)')#\nDate: {most_recent_formatted}')
ax1.set_axis_off()
gdf_me_none.plot(ax = ax1, color='lightgrey', edgecolor='grey', linewidth=0.4, aspect=1)
gdf_me_real.plot(ax = ax1, column='Count_per_city', norm=matplotlib.colors.LogNorm(vmin=gdf_me_real['Count_per_city'].min(), vmax=gdf_me_real['Count_per_city'].max()), legend=True)

# PLOT 2 : Rate of Accounts per Population
fig2, ax2 = plt.subplots(1, 1, figsize=(6, 8))
ax2.set_title(f'Rate of Accounts per Population')#\nDate: {most_recent_formatted}')
ax2.set_axis_off()
#gdf_me_high_rates.plot(ax = ax2, color='lightgrey', edgecolor='grey', linewidth=0.4, aspect=1)
gdf_me_low_rates.plot(ax = ax2, column='Account_rates', legend=True)
gdf_me_none.plot(ax = ax2, color='lightgrey', edgecolor='grey', linewidth=0.4)

# PLOT 3 : Percentage of Digital Per Total Accounts
fig3, ax3 = plt.subplots(1, 1, figsize=(6, 8))
ax3.set_title(f'Percentage of Digital Per Total Accounts\nDate: {most_recent_formatted}')
ax3.set_axis_off()
#gdf_me_high_rates.plot(ax = ax2, color='lightgrey', edgecolor='grey', linewidth=0.4, aspect=1)
gdf_me_digital_pct_none.plot(ax = ax3, color='lightgrey', edgecolor='grey', linewidth=0.4, aspect = 1)
gdf_me_digital_pct_all.plot(ax = ax3, column='Digital Percent', cmap='RdBu', legend=True)

plt.show()
