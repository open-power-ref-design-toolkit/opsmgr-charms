# Filebeat Configuration for Keystone

Writes out /etc/filebeat/conf/keystone.yml and restarts filebeat in order for
filebeat to process the application logs.

Because keystone has different tags for the three log files it doesn't use the
normal config.yaml file to configure filebeat. Instead in files is the filebeat
configuration file. This charm can't be modified with juju configure.

## Usage
     juju deploy keystone
     juju deploy ./filebeat-deb
     juju deploy ./filebeat-config-keystone
     juju add-relation keystone filebeat-deb
     juju add-relation keystone filebeat-config-keystone

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
