# Elasticsearch Dashboards - Ceph

This charm loads all Ceph related visualizations, Searches and dashboards into
Elasticsearch. They can be seen in kibana browser.

## Usage
     juju deploy ./elasticsearch-dashboards/elasticsearch-dashboards-ceph
     juju add-relation elasticsearch-dashboards-ceph elasticsearch-deb

The service provides extended status reporting to indicate when they are ready:

    juju status

This is particularly useful when combined with watch to track the on-going
progress of the deployment:

    watch -n 0.5 juju status

## Contact information

- Poorna Thanneeru &lt;poorna@us.ibm.com&gt;

## Upstream Project Name

- Upstream website
- Upstream bug tracker
