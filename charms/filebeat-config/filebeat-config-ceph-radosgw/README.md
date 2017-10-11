# Filebeat Configuration for ceph-radosgw

Writes out /etc/filebeat/conf/ceph-radosgw.yml and restarts filebeat in order for
filebeat to process the application logs

## Usage
     juju deploy ceph-radosgw
     juju deploy ./filebeat-deb
     juju deploy ./filebeat-config-ceph-radosgw
     juju add-relation ceph-radosgw filebeat-deb
     juju add-relation ceph-rados filebeat-config-ceph-radosgw

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
