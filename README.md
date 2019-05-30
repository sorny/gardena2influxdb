# Gardena2InfluxDB
### Version 0.1

Gardena2InfluxDB is a Python script for parsing events received on a GARDENA smart system websocket. 
Events are then parsed and forwarded to InfluxDB to create fancy charts and dashboards on e.g. sensor reading history

# Main Features:

  - Parsing incoming events from websocket and convert them to go into InfluxDB.
  - Used standard python libs for the maximum compatibility.
  - Having an external **settings.ini** for comfortable changing parameters.

Json format that the script send to InfluxDB looks like for a GARMDEA smart Sensor sensor eading update:
```
[
  {
    "measurement": "2f0cd24c-9e98-4057-905d-ac0429dfdff3",
    "tags": {
      "event_type": "SENSOR"
    },
    "fields": {
      "soilHumidity": 62
    },
    "time": "Thu May 30 13:08:24 2019"
  },
  {
    "measurement": "2f0cd24c-9e98-4057-905d-ac0429dfdff3",
    "tags": {
      "event_type": "SENSOR"
    },
    "fields": {
      "soilTemperature": 13
    },
    "time": "Thu May 30 13:07:51 2019"
  },
  {
    "measurement": "2f0cd24c-9e98-4057-905d-ac0429dfdff3",
    "tags": {
      "event_type": "SENSOR"
    },
    "fields": {
      "ambientTemperature": 16
    },
    "time": "Thu May 30 14:39:12 2019"
  },
  {
    "measurement": "2f0cd24c-9e98-4057-905d-ac0429dfdff3",
    "tags": {
      "event_type": "SENSOR"
    },
    "fields": {
      "lightIntensity": 688
    },
    "time": "Thu May 30 14:39:12 2019"
  }
]
```
Measurement is set to a unique device_id 

### Tech

Gardena2InfluxDB uses open source libs and open data to work properly:

* [InfluxDB-Python](https://github.com/influxdata/influxdb-python) - Python client for InfluxDB.
* [1689.cloud](https://developer.1689.cloud/) - Developer Portal from HusqvarnaGroup along documentation on GARDENA smart system and authentication endpoints

# Installation
1) Goto https://developer.1689.cloud/, sign in using your GARDENA smart system account and create a new application
2) Connect GARDENA smart system API and Authentication API to your application
2) Clone the repository to `/etc` install requirements
```sh
$ cd /etc/gardena2influxdb
$ pip3 install -r requirements.txt
```
3) Modify **settings.ini** & **gardena2influxdb.service** files and copy service to systemd.
```sh
$ cp settings.ini.bak settings.ini
$ vi settings.ini
$ cp gardena2influxdb.service.template /lib/systemd/system/gardena2influxdb.service
```
4) Then enable and start service
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
