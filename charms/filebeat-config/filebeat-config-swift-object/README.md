# Filebeat Configuration for swift-object

Writes out /etc/filebeat/conf/swift-object.yml and restarts filebeat in order for
filebeat to process the application logs

## Usage
     juju deploy swift-storage
     juju deploy ./filebeat-deb
     juju deploy ./filebeat-config-swift-object
     juju add-relation swift-storage filebeat-deb
     juju add-relation swift-storage filebeat-config-swift-object

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
