# Logstash Configuration for Ceph

Copies configuration files for logstash on how to parse Ceph
log files. Restarts the logstash service.

## Usage
     juju deploy ./logstash-deb
     juju deploy ./logstash-config/logstash-config-ceph
     juju add-relation logstash-deb logstash-config-ceph

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

