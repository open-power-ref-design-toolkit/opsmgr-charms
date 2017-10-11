# Filebeat Configuration for rabbitmq

Writes out /etc/filebeat/conf/rabbitmq.yml and restarts filebeat in order for
filebeat to process the application logs

## Usage
     juju deploy rabbitmq-server
     juju deploy ./filebeat-deb
     juju deploy ./filebeat-config-rabbitmq
     juju add-relation rabbitmq-server filebeat-deb
     juju add-relation rabbitmq-server filebeat-config-rabbitmq

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
