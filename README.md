# BME280-backend
Python Flask backend microservice for Bosch BME280 sensor data and calculated meteorogical metrics (https://www.bosch-sensortec.com/bst/products/all_products/bme280)

BME280 is an affordable and accurate digital pressure, temperature and humidity sensor, than can be easily connected to any Raspberry Pi using I2C, therebefore making it ideal for remote temperature/humidity monitoring.

Thanks to Matt Hawkins library (https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/bme288.py), I just had to implement the endpoints and upgrade a few line to Python 3 syntaxis to make it work, also added
atmospheric metrics that are calculated using BME280 metrics. I'm not a weather professional, so please double check the formulas. PRs are welcome for fixes/additions.

## Configuration and runtime
Edit bme280.py and set sensor BUS and ID properly (tool i2cdetect can help with that)

After ID and BUS are set you can use the included Dockerfile to build the container and then run it with the following commands:

$ sudo docker build -t bme280-backend .
$ sudo docker run -p 8000:8000 --privileged bme280-backend

This will expose the service port 8000. Like http://localhost:8000/metrics

After the endpoint is exposed could be easily attached to a metric collector like Telegraf (https://www.influxdata.com/time-series-platform/telegraf/)

## This backend implements 3 endpoints

- /metrics (sensor data in JSON)
{"temperature": 20.67, "pressure": 1009.4834511590609, "humidity": 60.5365803099204}

- /ids (sensor ID info)
{"chip_id": 96, "chip_version": 0}

- /atmos (calculated meteorological metrics/KPI)
{"altitude": 0.03168493302340608, "precipitable_water": 2.3728284551975314, "dew_point": 12.898732023314297, "frost_point": 10.110273017462305, "cloud_base": 3124.5071906742814, "humidity_index": 23.40544603781366, "heat_index": 20.71}
