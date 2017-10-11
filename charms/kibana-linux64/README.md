# Kibana Linux 64-Bit

Kibana is an open source analytics and visualization platform designed to
work with Elasticsearch. You use Kibana to search, view, and interact with
data stored in Elasticsearch indices. You can easily perform advanced data
analysis and visualize your data in a variety of charts, tables, and maps.

Kibana makes it easy to understand large volumes of data. Its simple,
browser-based interface enables you to quickly create and share dynamic
dashboards that display changes to Elasticsearch queries in real time.

This charm is useful when a version of kibana is not available for your
platform when using apt install (ppc64el for example), it downloads
the linux_x86_64 tar.gz file and replaces the nodejs binary with the linux
nodejs binary for the platform your running on. 

## Usage
     juju deploy ./kibana-linux64
     juju add-relation kibana-linux64 elasticsearch-deb

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
