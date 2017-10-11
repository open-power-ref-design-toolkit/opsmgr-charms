# Filebeat Configuration for ceph-mon

Writes out /etc/filebeat/conf/ceph-osd.yml and restarts filebeat in order for
filebeat to process the application logs

## Usage
     juju deploy ceph-osd
     juju deploy ./filebeat-deb
     juju deploy ./filebeat-config-ceph-osd
     juju add-relation ceph-osd filebeat-deb
     juju add-relation ceph-osd filebeat-config-ceph-osd

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
