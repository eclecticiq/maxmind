#!/usr/bin/env python3

import os
import pathlib
import sys
import tempfile
from optparse import OptionParser
from string import Template

import urllib.request
import hashlib
import tarfile
import zipfile

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

url = "https://geolite.maxmind.com/download/geoip/database/"
template = Template('GeoLite2-$db$suffix')
database = {"asn": "ASN", "city": "City", "country": "Country"}
suffix = {"csv": "-CSV.zip", "binary": ".tar.gz"}


def download(url, path):
    logger.info("downloading: %s", url)
    filename = pathlib.PurePath(path, os.path.basename(url))
    urllib.request.urlretrieve(url, filename)
    return filename


def binary_files(members):
    for info in members:
        if os.path.splitext(info.name)[1] == ".mmdb":
            info.name = os.path.basename(info.name)
            logger.info("extracting: %s", info.name)
            yield info


def csv_files(members):
    for info in members:
        if os.path.splitext(info.filename)[1] == ".csv":
            info.filename = os.path.basename(info.filename)
            logger.info("extracting: %s", info.filename)
            yield info


def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--db", "--database",
                      dest="db",
                      choices=["asn", "city", "country"],
                      default="city",
                      help="database (asn|city|country) [default: %default]")
    parser.add_option("-f", "--format",
                      dest="format",
                      choices=["csv", "binary"],
                      default="binary",
                      help="database format (binary|csv) [default: %default]")
    parser.add_option("-p", "--path",
                      dest="path",
                      default=".",
                      help="path to extract the files [default: %default]")
    parser.add_option("-q", "--quiet",
                      dest="quiet",
                      action="store_true",
                      default=False,
                      help="don't print any messages")

    (options, args) = parser.parse_args()

    if options.quiet:
        logger.setLevel(logging.ERROR)

    filename = template.substitute(db=database[options.db],
                                   suffix=suffix[options.format])

    with tempfile.TemporaryDirectory(prefix='maxmind') as tmp:
        logger.info("created tmp directory: %s", tmp)
        filepath = download(url + filename, tmp)
        md5path = download(url + filename + '.md5', tmp)

        logger.info("verifying checksum...")
        checksum = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
        md5sum = open(md5path, 'r').read()

        if checksum != md5sum:
            logger.error("file checksum mismatch!")
            sys.exit(1)

        logger.info("extracting files to: '%s/'", options.path)
        if tarfile.is_tarfile(filepath):
            with tarfile.open(filepath) as tar:
                tar.extractall(members=binary_files(tar), path=options.path)
        elif zipfile.is_zipfile(filepath):
            with zipfile.ZipFile(filepath) as zip:
                zip.extractall(members=csv_files(zip.infolist()),
                               path=options.path)


if __name__ == "__main__":
    main()
