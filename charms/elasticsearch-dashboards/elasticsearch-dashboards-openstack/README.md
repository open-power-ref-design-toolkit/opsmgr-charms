# Elasticsearch Dashboards - Openstack

This charm loads all Openstack related visualizations, Searches and dashboards into
Elasticsearch. They can be seen in kibana browser.

## Usage
     juju deploy ./elasticsearch-dashboards/elasticsearch-dashboards-openstack
     juju add-relation elasticsearch-dashboards-openstack elasticsearch-deb

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
