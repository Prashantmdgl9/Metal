import turicreate as tc
import pandas as pd
import altair as alt

!pip install altair_viewer
alt.renderers.enable('mimetype')
alt.renderers.enable('altair_viewer')

df = pd.read_csv('metal_bands_2017.csv', encoding ='latin1')
df = df.drop('Unnamed: 0', axis = 1)

df

df.to_csv('corrected_file.csv')

sf = tc.SFrame.read_csv('corrected_file.csv')
sf = sf.drop_duplicates(subset = ['band_name'])
sf.shape


sf_no_origin = sf[sf['origin'] == ""]
sf = sf.filter_by(sf_no_origin['band_name'], 'band_name', exclude = True)
sf.shape


#Most bands from countries
sf_countries = sf.groupby('origin', tc.aggregate.COUNT()).sort('Count', ascending = False)

source = sf_countries.to_dataframe()


chart = alt.Chart(source[0:20]).mark_bar(color='#808080').encode(
    x=alt.X("Count:Q", axis=alt.Axis(title='Number of metal bands since 1964')),
    y=alt.Y('origin:O', sort = '-x', axis=alt.Axis(title='Country of origin')),
    color=alt.condition(
        alt.datum.origin == "Sweden",  #
        alt.value('orange'),     # which sets the bar orange.
        alt.value('grey')   # And if it's not true it sets the bar steelblue.
    )
).properties(height=400, width = 600, title='Most metal bands come from these countries')

chart.configure_title(
    fontSize=22,
    font='Helvetica',
    anchor='middle',
    color='#808080'
)
 # Let's find the per capita metal bands

 sf_w = tc.SFrame.read_csv('world_population_1960_2015.csv')

sf_countries

sf_w = sf_w.rename({'Country Name': 'origin'})
sf_w = sf_w['origin', '2015']
sf_m = sf_countries.join(sf_w, on='origin', how = "inner")
sf_m
sf_m['per_cap'] = sf_m.apply(lambda x: (x['Count']/x['2015'])*10000)
sf_m = sf_m.sort('per_cap', ascending = False)
sf_m.print_rows(30)

source = sf_m.to_dataframe()
chart = alt.Chart(source[0:20]).mark_bar(color='#808080').encode(
    x=alt.X("per_cap:Q", axis=alt.Axis(title='Metal bands per 10k people')),
    y=alt.Y('origin:O', sort = '-x', axis=alt.Axis(title='Country of origin')),
    color=alt.condition(
        alt.datum.origin == "Finland",  #
        alt.value('steelblue'),     # which sets the bar orange.
        alt.value('grey')   # And if it's not true it sets the bar steelblue.
    )
).properties(height=400, width = 600, title='Metal bands per 10k people for various countries')

chart.configure_title(
    fontSize=22,
    font='Helvetica',
    anchor='middle',
    color='#808080'
)
 # Famous genres

 sf.groupby('style', tc.aggregate.COUNT()).sort('Count', ascending = False)
# But there are mixed genres
dict = {}
for style in sf['style']:
    elements = style.split(',')
    for element in elements:
        if(element in dict):
            dict[element] = dict[element] + 1
        else:
            dict[element] = 1
sf_style = tc.SFrame({'style': dict.keys(), 'count':dict.values()}).sort('count', ascending = False)
source = sf_style.to_dataframe()

source

chart = alt.Chart(source[0:30]).mark_bar(color='#808080').encode(
    x=alt.X('style:O',sort = '-y', axis=alt.Axis(title='Genre and sub-genre')),
    y=alt.Y("count:Q", axis=alt.Axis(title='Total count includes main genre and subgenre of the bands')),
    color=alt.condition(
        alt.datum.style == "Black",  #
        alt.value('orange'),     # which sets the bar orange.
        alt.value('steelblue')   # And if it's not true it sets the bar steelblue.
    )
).properties(height=400, width = 600, title='Most popular genres in metal')

chart.configure_title(
    fontSize=22,
    font='Helvetica',
    anchor='middle',
    color='#808080'
)


# Metal bands over period of time
source = sf.groupby('formed', tc.aggregate.COUNT()).to_dataframe()


chart = alt.Chart(source).mark_bar(color='#808080').encode(
    x=alt.X('formed:O', axis=alt.Axis(title='Year of formation')),
    y=alt.Y("Count:Q", sort = 'x',axis=alt.Axis(title='Number of metal bands formed')),
    color=alt.condition(
        alt.datum.formed == 2005,  #
        alt.value('steelblue'),     # which sets the bar orange.
        alt.value('orange')   # And if it's not true it sets the bar steelblue.
    )
).properties(height=400, width = 600, title='Metal over years!!')

chart.configure_title(
    fontSize=22,
    font='Helvetica',
    anchor='middle',
    color='#808080'
)
# Bands active over time
split = []
for x in sf['split']:
    if x == "-":
        split.append(0)
    else:
        split.append(int(x))

sf['split_x'] = split

active = []
year = []
for x in range(1964,2016):
    year.append(x)
    formed = sf[sf['formed'] <= x].shape[0]
    split = sf[(sf['split_x']  <= x) & (sf['split_x'] >= 1964)].shape[0]
    active.append(formed - split)

source = pd.DataFrame(list(zip(year, active)), columns = ['year', 'active'])

chart = alt.Chart(source).mark_bar(color='maroon').encode(
    x=alt.X('year:O', axis=alt.Axis(title='Year')),
    y=alt.Y("active:Q", sort = 'x',axis=alt.Axis(title='Number of metal bands active')),
    color=alt.condition(
        alt.datum.year >= 2001,  #
        alt.value('maroon'),     # which sets the bar orange.
        alt.value('orange')   # And if it's not true it sets the bar steelblue.
    )
).properties(height=400, width = 600, title='Metal bands active over years!!')

chart.configure_title(
    fontSize=22,
    font='Helvetica',
    anchor='middle',
    color='#808080'
)

# Famous bands overall
sf.sort('fans', ascending = False)

# Famous bands each country
sf_a = sf.groupby('origin', operations = {'band_name' : tc.aggregate.ARGMAX('fans', 'band_name')})
sf_b = sf.groupby('origin', tc.aggregate.COUNT())
sf_a = sf_a.join(sf_b, on ="origin", how ="inner").sort('Count', ascending = False)
sf_a
source = sf_a.to_dataframe()

chart = alt.Chart(source[0:20]).mark_bar(color='#808080').encode(
    x=alt.X("Count:Q", axis=alt.Axis(title='Number of metal bands')),
    y=alt.Y('origin:O', sort = '-x', axis=alt.Axis(title='Country of origin')),
    color=alt.condition(
        alt.datum.origin == "Sweden",  #
        alt.value('orange'),     # which sets the bar orange.
        alt.value('grey')   # And if it's not true it sets the bar steelblue.
    )
).properties(height=400, width = 600, title='Most metal bands come from these countries')



text = chart.mark_text(
    align='left',
    baseline='middle',
    color= 'steelblue',
    dx=3  # Nudges text to right so it doesn't appear on top of the bar
).encode(
    text= 'band_name:O'
)

(chart+text).configure_title(
    fontSize=22,
    font='Helvetica',
    anchor='middle',
    color='#808080'
)


# Folium map
import folium
from folium import plugins
from folium.plugins import HeatMap
import geojson

sf_m

df_m = sf_m.to_dataframe()

df_m["origin"].replace(to_replace="USA", value="United States of America", inplace=True)
df_m["origin"].replace(to_replace="UAE", value="United Arab Emirates", inplace=True)


with open("countries.geo.json") as f:
    countries = geojson.load(f)




metal_map2 = folium.Map(location=[51.5017963261, 0.00187999248], zoom_start=2, tiles="cartodbdark_matter")

metal_map2
folium.Choropleth(geo_data=countries, name="choropleth", data=df_m, columns=["origin", "per_cap"],
                  key_on="properties.admin", fill_color="Reds", nan_fill_color="grey", fill_opacity=0.8).add_to(metal_map2)

output_file = "map_per_cap.html"
metal_map2.save(output_file)

import webbrowser
webbrowser.open(output_file)


# Genres over the time
sf
sf.groupby('style', tc.aggregate.COUNT()).sort('Count', ascending = False)
sf_temp = sf[sf['style'] == "Black"]
sf_temp.groupby('formed', tc.aggregate.COUNT())

sf[sf['origin'] == "Germany"]
sf
sf_ma = tc.SFrame.read_csv('data/bands.csv')

sf_ma = sf_ma.rename({'name':'band_name'})
sf_ma.column_names()
cols = ['band_name', 'theme']
sf_ma = sf_ma[cols]
sf_ma = sf_ma.drop_duplicates(subset=['band_name'])
sf_wc = sf.join(sf_ma, on='band_name', how = "left")
sf_wc
sf.shape
!pip install wordcloud
from wordcloud import WordCloud, STOPWORDS

df_wc = sf_wc.to_dataframe()
catcloud = WordCloud(
    stopwords=STOPWORDS,
    background_color='black',
    width=1200,
    height=800
).generate(" ".join(df_wc.theme.dropna().str.replace("|", ",").values))

import matplotlib.pyplot as plt
plt.figure(figsize=(12,9))
plt.imshow(catcloud, alpha=0.8)
plt.axis('off')
plt.show()
