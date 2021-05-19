# Gardena2InfluxDB
### Version 0.3
![Alt text](https://github.com/sorny/gardena2influxdb/blob/master/gardena2influxdb.png?raw=true "Grafana dashboard example")

Gardena2InfluxDB is a Python script for parsing events received on a GARDENA smart system websocket. 
Events are then parsed and forwarded to InfluxDB to create fancy charts and dashboards on e.g. sensor reading history



# Main Features:

  - Parsing incoming events from websocket and convert them to go into InfluxDB.
  - Having an external **settings.ini** for comfortable changing parameters.
  - Get things up and running ASAP with some docker lovin <3

Example payload of the script which is sent to InfluxDB following a GARDENA smart Sensor values update event:
```
[
  {
    "measurement": "sensor-00012345",
    "tags": {
      "event_type": "SENSOR",
	  "device_id": "2f0cd24c-9e98-4057-905d-ac0429dfdff3"
    },
    "fields": {
      "soilHumidity": 62
    },
    "time": "Thu May 30 13:08:24 2019"
  },
  {
    "measurement": "sensor-00012345",
    "tags": {
      "event_type": "SENSOR",
	  "device_id": "2f0cd24c-9e98-4057-905d-ac0429dfdff3"
    },
    "fields": {
      "soilTemperature": 13
    },
    "time": "Thu May 30 13:07:51 2019"
  },
  {
    "measurement": "sensor-00012345",
    "tags": {
      "event_type": "SENSOR",
	  "device_id": "2f0cd24c-9e98-4057-905d-ac0429dfdff3"
    },
    "fields": {
      "ambientTemperature": 16
    },
    "time": "Thu May 30 14:39:12 2019"
  },
  {
    "measurement": "sensor-00012345",
    "tags": {
      "event_type": "SENSOR",
	  "device_id": "2f0cd24c-9e98-4057-905d-ac0429dfdff3"
    },
    "fields": {
      "lightIntensity": 688
    },
    "time": "Thu May 30 14:39:12 2019"
  }
]
```


### Tech

Gardena2InfluxDB uses open source libs and open data to work properly:

* [husqvarnagroup.cloud](https://developer.husqvarnagroup.cloud/) - Developer Portal from Husqvarna Group along documentation on GARDENA smart system and authentication API endpoints
* [InfluxDB-Python](https://github.com/influxdata/influxdb-python) - Python client for InfluxDB.
* [pickleDB](https://github.com/patx/pickledb) - lightweight and simple key-value store.
* [docker-influxdb-grafana](https://github.com/philhawthorne/docker-influxdb-grafana) - A Docker container which runs InfluxDB and Grafana ready for persisting data.


# Installation
## The docker-composy way of life
#### Gardena2InfluxDB, Grafana and InfluxDB in docker
1) Goto https://developer.husqvarnagroup.cloud/, sign in using your GARDENA smart system account and create a new application
2) Connect GARDENA smart system API and Authentication API to your application
3) Have `docker` and `docker-compose` installed on your host
4) Clone this repository 
5) Modify **settings.ini** files and fill in your GARDENA credentials and API key.
```sh
$ cp settings.ini.docker.bak settings.ini
$ vi settings.ini
```
6) Build the gardena2influxdb docker image and create some necessary data dirs to add persistency to your collected data
```sh
$ mkdir -p data
$ mkdir -p data/influxdb
$ mkdir -p data/grafana
$ mkdir -p data/gardena2influxdb
$ docker build -t gardena2influxdb .
```
7) Run docker-compose to get everything up and running
```sh
$ docker-compose up
```
8) Enjoy Grafana at http://localhost:3003


## The docker way of life
#### Dockerized Gardena2InfluxDB
1) Goto https://developer.husqvarnagroup.cloud/, sign in using your GARDENA smart system account and create a new application
2) Connect GARDENA smart system API and Authentication API to your application
3) Have `docker` installed, InfluxDB is running at some place only you know ;)
4) Clone this repository 
5) Modify **settings.ini** files and fill in your GARDENA credentials, API key and InfluxDB connection settings.
```sh
$ cp settings.ini.bak settings.ini
$ vi settings.ini
```
6) Build the gardena2influxdb docker image
```sh
$ docker build -t gardena2influxdb .
```
7) Run gardena2influxdb docker image
```sh
$ docker run -d \
  --name gardena2influxdb \
  -v $PWD/settings.ini:/app/settings.ini \
  -v $PWD/data/gardena2influxdb:/app/data/gardena2influxdb \
  gardena2influxdb:latest
```


## The systemctl way of life
#### Gardena2InfluxDB as a service
1) Goto https://developer.husqvarnagroup.cloud/, sign in using your GARDENA smart system account and create a new application
2) Connect GARDENA smart system API and Authentication API to your application
3) Clone the repository to `/etc` and install requirements
```sh
$ cd /etc/gardena2influxdb
$ mkdir -p data/gardena2influxdb
$ pip3 install -r requirements.txt
```
4) Modify **settings.ini** & **gardena2influxdb.service** files and copy service to systemd.
```sh
$ cp settings.ini.bak settings.ini
$ vi settings.ini
$ cp gardena2influxdb.service.template /lib/systemd/system/gardena2influxdb.service
```
5) Then enable and start service
```sh
$ systemctl daemon-reload
$ systemctl enable gardena2influxdb.service
$ systemctl start gardena2influxdb.service
```
Optional Setup - Configure logrotation for gardena2influxdb.service
1) Edit **/etc/rsyslog.d/50-default.conf** and append the following ling
```
:programname,isequal,"gardena2influxdb"         /var/log/gardena2influxdb.log
```
2) Restart Rsyslog-Daemon for changes to take effect
```
systemctl restart rsyslog
```
3) Configure logrotation for gardena2influxdb.log by creating `/etc/logrotate.d/gardena2influxdb` with the following content
```
/var/log/gardena2influxdb.log { 
    su root syslog
    daily
    rotate 5
    compress
    delaycompress
    missingok
    postrotate
        systemctl restart rsyslog > /dev/null
    endscript    
}
```

After the first events will go to the InfluxDB you can create nice Grafana dashboards.

Have fun !

License
----

MIT

**Free Software, Hell Yeah!**
