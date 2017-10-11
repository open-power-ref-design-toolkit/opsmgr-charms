# Filebeat Configuration for horizon

Writes out /etc/filebeat/conf/horizon.yml and restarts filebeat in order for
filebeat to process the application logs

## Usage
     juju deploy openstack-dashboard
     juju deploy ./filebeat-deb
     juju deploy ./filebeat-config-horizon
     juju add-relation openstack-dashboard filebeat-deb
     juju add-relation openstack-dashboard filebeat-config-horizon

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
