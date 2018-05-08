This Python3 script can be used to fetch [GeoLite2 Free Downloadable Databases](https://dev.maxmind.com/geoip/geoip2/geolite2/)

## Usage
```
Usage: maxmind.py [options]

Options:
  -h, --help            show this help message and exit
  -d DB, --db=DB, --database=DB
                        database (asn|city|country) [default: city]
  -f FORMAT, --format=FORMAT
                        database format (binary|csv) [default: binary]
  -p PATH, --path=PATH  path to extract the files [default: .]
  -q, --quiet           don't print any messages
```

## Systemd
A sample systemd service and timer template are provided which downloads the specified database in binary format every week.
```
systemctl enable maxmind@country.timer
systemctl start maxmind@country.timer
```
