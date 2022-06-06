from altair import Chart, X, Y, Axis, Data, DataFormat
import pandas as pd
import numpy as np
from flask import render_template, url_for, flash, redirect, request, make_response, jsonify, abort
from web import app
from web.utils import utils, altair_plots
import json


#loading data
df_climate, df_migration, df_crop, df_food = utils.load_data()

@app.route("/")
@app.route("/altair")
def plot_altair_global():
    #ploting
    altair_global_map = altair_plots.altair_global_map(df_climate)
    altair_global_line_chart = altair_plots.altair_global_line_chart(df_climate)
    context = {'plot_chlorepleth': altair_global_map, 
                'plot_linechart': altair_global_line_chart}
    return render_template('altair.html', context=context)
