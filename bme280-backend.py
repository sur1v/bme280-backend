#!/usr/bin/env python3

"""
File: bme280-backend.py
Author: sur1v (https://github.com/sur1v)
---
About:
This Flask web backend will import the bme280 library and read the sensor data from it,
exposing as a service at routes /metrics and /ids. Making them available for data collection.
Configure bme280.py with your sensor settings before use.
---
Attention:
"""

import os
import math
from flask import Flask, Response
import bme280 as sensor
import json

app = Flask(__name__)

# List available metrics
@app.route('/metrics')
def get_metrics():
    temperature, pressure, humidity = sensor.readBME280All()
    x = { "temperature": temperature, "pressure": pressure, "humidity": humidity }
    metrics = json.dumps(x)
    return Response(metrics, mimetype="application/json", status=200)

# List available ids
@app.route('/ids')
def get_ids():
    chip_id, chip_version = sensor.readBME280ID()
    y = { "chip_id": chip_id, "chip_version": chip_version }
    ids = json.dumps(y)
    return Response(ids, mimetype="application/json", status=200)

# List available meteorological data
@app.route('/atmos')
def get_atmos():
    sea_level_pressure = 1013.25
    temp_air, pressure, relative_humidity = sensor.readBME280All()
    temp_kelvin = temp_air + 273.15

    ## Altitude (mts): Hypsometric
    ## https://keisan.casio.com/has10/SpecExec.cgi?id=system/2006/1224585971
    altitude = ((math.pow((sea_level_pressure/pressure), (1/5257))-1) * temp_kelvin) / 0.0065

    ## Precipitable water (cms): Keogh and Blakers
    ## https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.atmosphere.gueymard94_pw.html
    T = temp_kelvin
    theta = T / 273.15
    pw = ( 0.1 *
         (0.4976 + 1.5265*theta + math.exp(13.6897*theta - 14.9188*(theta)**3)) *
         (216.7*relative_humidity/(100*T)*math.exp(22.330 - 49.140*(100/T) -
         10.922*(100/T)**2 - 0.39015*T/100)))

    ## Dew point (celcius): Magnus + Arden Buck constants pair
    ## https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
    arden = dict(positive=dict(b=17.368, c=238.88),
            negative=dict(b=17.966, c=247.15))
    buck = arden['positive'] if temp_air > 0 else arden['negative']
    magnus = (buck['b'] * temp_air /(buck['c'] + temp_air)) + math.log(relative_humidity / 100.0)
    dewpoint = (buck['c'] * magnus) / (buck['b'] - magnus)

    ## Frost point (celcius):
    ## https://gist.github.com/sourceperl/45587ea99ff123745428
    dewpoint_k = 273.15 + dewpoint
    frostpoint_k = dewpoint_k - temp_kelvin + 2671.02 / ((2954.61 / temp_kelvin) + 2.193665 * math.log(temp_kelvin) - 13.3448)
    frostpoint = frostpoint_k - 273.15

    ## Cloud base (mts): Formula used by U.S. Federal Aviation Administration
    ## https://en.wikipedia.org/wiki/Cloud_base
    cloudbase = ((temp_air - dewpoint) / 2.5) * 1000

    ## Humidity index (none): Canadian Weather Standards
    saturation_pressure = (6.112 * (10.0**(7.5 * temp_air / (237.7 + temp_air))) * relative_humidity / 100.0)
    humidity_index = temp_air + (0.555 * (saturation_pressure - 10.0))

    ## Heat index (none): U.S. National Weather Service Standards
    ## not valid for T < 26.7C, Dew Point < 12C, or RH < 40%
    ## http://en.wikipedia.org/wiki/Heat_index
    if temp_air < 26.7 or relative_humidity < 40 or dewpoint < 12.0:
        heat_index = temp_air
    else:
        T = (temp_air * 1.8) + 32.0
        R = relative_humidity
        c_1 = -42.379
        c_2 = 2.04901523
        c_3 = 10.14333127
        c_4 = -0.22475541
        c_5 = -0.00683783
        c_6 = -0.05481717
        c_7 = 0.00122874
        c_8 = 0.00085282
        c_9 = -0.00000199
        heat_index = ((c_1 + (c_2 * T) + (c_3 * R) + (c_4 * T * R) + (c_5 * (T**2)) +
                     (c_6 * (R**2)) + (c_7 * (T**2) * R) + (c_8 * T * (R**2)) +
                     (c_9 * (T**2) * (R**2))) - 32.0) / 1.8

    ## Response
    x = { "aprox_altitude": altitude, "precipitable_water": pw, "dew_point": dewpoint, "frost_point": frostpoint,
        "cloud_base": cloudbase, "humidity_index": humidity_index, "heat_index": heat_index }
    atmos = json.dumps(x)
    return Response(atmos, mimetype="application/json", status=200)
