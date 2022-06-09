import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
import cartopy.feature as cfeature
import xarray as xr
import numpy as np
from urllib.request import urlopen
import json
import os
from netCDF4 import Dataset
import requests
import h5py
import os
import altair as alt
from vega_datasets import data
from altair import datum
from web.utils.utils import get_by_country_merged

def timestamp(t):
    return pd.to_datetime(t)

def altair_global_map(final_df):
    # Plot Altair 1: Per country total cases and cases/million populations
    # Only plotting 100 countries
    dfnew = final_df
    alt.data_transformers.disable_max_rows()
    #base configuration
    countries = alt.topo_feature(data.world_110m.url, 'countries')

    slider = alt.binding_range(
        step=0.5,
        min=-5, 
        max=5,
        name='Temperature: '
    )

    select_temp = alt.selection_single(
        name=" ", 
        fields=['tempstep'],
        bind=slider, 
    )

    background = alt.Chart(countries).mark_geoshape(
        fill='lightgray',
        stroke='white'
    )

    foreground = alt.Chart(dfnew).mark_geoshape()\
        .encode(color=alt.Color('gfsi_hat:Q', scale=alt.Scale(domain=[dfnew['gfsi_hat'].min(), dfnew['gfsi_hat'].max()], scheme=alt.SequentialMultiHue('viridis'))),
                tooltip=[
                    alt.Tooltip("name:N", title="Country"),
                    alt.Tooltip("gfsi_hat:Q", title="GFSI"),
                    alt.Tooltip("gdp:Q", title="GDP"),
                    alt.Tooltip("surfacetempanomaly:Q", title="Temp Anomaly")
                ])\
        .add_selection(select_temp)\
        .transform_filter(select_temp)\
        .transform_lookup(
            lookup='country-code',
            from_=alt.LookupData(countries, key='id',
                                fields=["type", "properties", "geometry"])
        )

    bubble_chart = alt.Chart(dfnew).mark_circle().encode(
        x='surfacetempanomaly',
        y='gfsi_hat',
        size = alt.Size('gdp', scale=alt.Scale(type='pow', exponent=0.5)),
        color='region',
        tooltip=['name', 'gfsi_hat','surfacetempanomaly', 'precipitationflux', 'gdp', 'population','migration']
    ).add_selection(select_temp
    ).transform_filter(select_temp
    ).properties(
        width=250,
        height=250
    )

    ranked_text = alt.Chart(dfnew).mark_text(align='right').encode(
        y=alt.Y('row_number:O',axis=None)
    ).transform_filter(
        select_temp
    ).transform_window(
        row_number='row_number()',
        rank='rank(gfsi_hat)',
        sort=[alt.SortField('gfsi_hat', order='ascending')]
    ).transform_filter(
        alt.datum.rank <= 10
    ).properties(width=30)

    final_map = (
        (background + foreground)
        .properties(width=600, height=400, title='Global Food Security Index')
        .project("naturalEarth1")
    )

    temperature = ranked_text.encode(text='gfsi_hat:N').properties(title=alt.TitleParams(text='GFSI', align='right'))
    country = ranked_text.encode(text='name:N').properties(title=alt.TitleParams(text='Country', align='right'))
    text = alt.hconcat(country, temperature) # Combine data tables

    cat = alt.hconcat(final_map, text)
    cat2 = alt.vconcat(cat, bubble_chart)

    final_map_json = cat2.to_json()
    return final_map_json


def altair_global_line_chart(final_df):
    #Plot Altair 6; Global time series chart for daily new cases, recovered, and deaths - version 3 (more fancy selector)
    #declare data and initialization
    df = final_df
    alt.data_transformers.disable_max_rows()
    highlight = alt.selection(type='single', on='mouseover',
                          fields=['country_y'], nearest=True)

    base = alt.Chart(df).mark_line(point=True)\
        .encode(
            alt.X('soiltemp', scale=alt.Scale(zero=False)),
            alt.Y('precipitationflux', scale=alt.Scale(zero=False)),
            order=['year'],
            color=alt.Color('country_y', legend=None)
        )

    points = base.mark_circle().encode(
            opacity=alt.value(0)
        ).add_selection(
            highlight
        )

    lines = base.mark_line().encode(
        size=alt.condition(~highlight, alt.value(1), alt.value(3)),
        color=alt.condition(highlight, 'country_y:N', alt.value("lightgray"), legend=None),
        tooltip=[alt.Tooltip("country_y:N", title="Country"), alt.Tooltip("year:N", title="Year")]
    )

    final_map = (
        (points + lines)
        .properties(width=600, height=400, title='Surface Temperature by Country/Year')
    )
    chart_json = final_map.to_json()
    return chart_json