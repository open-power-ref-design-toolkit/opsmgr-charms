# Logstash Via Deb Package

A flexible, open source data collection, enrichment, and
transportation pipeline. With connectors to common infrastructure for easy
integration, Logstash is designed to efficiently process a growing list of log,
event, and unstructured data sources for distribution into a variety of outputs,
including Elasticsearch.

This charm is intended for installations were apt install logstash will not
work because a build is not available for that platform. Because logstash
is Java based it should run on any platform what supports Java 1.8


## Usage
     juju deploy ./logstash-deb

The service provides extended status reporting to indicate when they are ready:

    juju status

This is particularly useful when combined with watch to track the on-going
progress of the deployment:

    watch -n 0.5 juju status

## Contact information

- William Irons &lt;wdirons@us.ibm.com&gt;

## Upstream Project Name

- Upstream website
- Upstream bug tracker
