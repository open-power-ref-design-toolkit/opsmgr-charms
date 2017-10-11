# Filebeat Configuration for Designate

Writes out /etc/filebeat/conf/designate.yml and restarts filebeat in order for
filebeat to process the application logs

## Usage
     juju deploy designate
     juju deploy ./filebeat-deb
     juju deploy ./filebeat-config-designate
     juju add-relation keystone filebeat-deb
     juju add-relation keystone filebeat-config-designate

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
