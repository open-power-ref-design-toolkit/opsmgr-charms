# Filebeat Configuration for ceph-mon

Writes out /etc/filebeat/conf/ceph-mon.yml and restarts filebeat in order for
filebeat to process the application logs

## Usage
     juju deploy ceph-mon
     juju deploy ./filebeat-deb
     juju deploy ./filebeat-config-ceph-mon
     juju add-relation ceph-mon filebeat-deb
     juju add-relation ceph-mon filebeat-config-ceph-mon

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
