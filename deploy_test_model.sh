#!/bin/bash
set -x
set -e
set -o pipefail

MODEL_NAME=test-model
NUMBER_HA_NODES=3

# assumes this is running from the opsmgr-juju directory
# creates a model called test-model
juju add-model $MODEL_NAME

# Deploy OpenStack And Nagios
juju deploy -m $MODEL_NAME ./bundles/horizon_minimal_with_nagios/bundle.yaml 

# Deploy the ELK charms
juju deploy -m $MODEL_NAME ./charms/elasticsearch-deb elasticsearch -n $NUMBER_HA_NODES
juju deploy -m $MODEL_NAME ./charms/logstash-deb logstash -n $NUMBER_HA_NODES
juju deploy -m $MODEL_NAME ./charms/kibana-linux64 kibana -n $NUMBER_HA_NODES
juju deploy -m $MODEL_NAME ./charms/filebeat-deb filebeat
juju deploy -m $MODEL_NAME ./charms/metricbeat-deb metricbeat

# Deploy the DBaaS UI charms
juju deploy -m $MODEL_NAME ./charms/trove-dashboard
juju deploy -m $MODEL_NAME ./charms/dbaas-ui-dashboard
juju deploy -m $MODEL_NAME ./charms/opsmgr

# Deploy the ELK dashboard subordinate charms
juju deploy -m $MODEL_NAME ./charms/elasticsearch-dashboards/elasticsearch-dashboards-openstack
juju deploy -m $MODEL_NAME ./charms/elasticsearch-dashboards/elasticsearch-dashboards-ceph
juju deploy -m $MODEL_NAME ./charms/elasticsearch-dashboards/elasticsearch-dashboards-metricbeat

# Deploy the Logstash configuration subordinate charms
juju deploy -m $MODEL_NAME ./charms/logstash-config/logstash-config-openstack
juju deploy -m $MODEL_NAME ./charms/logstash-config/logstash-config-ceph

# Deploy the Filebeat Configuration subordinate charms
juju deploy -m $MODEL_NAME ./charms/filebeat-config/filebeat-config-mysql
juju deploy -m $MODEL_NAME ./charms/filebeat-config/filebeat-config-horizon
juju deploy -m $MODEL_NAME ./charms/filebeat-config/filebeat-config-keystone

# Add relationships between the ELK packages
juju add-relation -m $MODEL_NAME elasticsearch logstash
juju add-relation -m $MODEL_NAME elasticsearch kibana
juju add-relation -m $MODEL_NAME filebeat logstash
juju add-relation -m $MODEL_NAME metricbeat elasticsearch

# Add relationships between filebeat and the OpenStack packages
juju add-relation -m $MODEL_NAME filebeat mysql
juju add-relation -m $MODEL_NAME filebeat keystone
juju add-relation -m $MODEL_NAME filebeat openstack-dashboard

# Add relationships between nrpe and the ELK packages
juju add-relation -m $MODEL_NAME nrpe elasticsearch
juju add-relation -m $MODEL_NAME nrpe logstash
juju add-relation -m $MODEL_NAME nrpe kibana

# Add relationships between elasticsearch and the elasticsearch dashboard charms
juju add-relation -m $MODEL_NAME elasticsearch elasticsearch-dashboards-openstack
juju add-relation -m $MODEL_NAME elasticsearch elasticsearch-dashboards-ceph
juju add-relation -m $MODEL_NAME elasticsearch elasticsearch-dashboards-metricbeat

# Add relationships between logstash and the logstash configuration charms
juju add-relation -m $MODEL_NAME logstash logstash-config-openstack
juju add-relation -m $MODEL_NAME logstash logstash-config-ceph

# Add relationships between the DBaaS UI charms and horizon
juju add-relation -m $MODEL_NAME openstack-dashboard trove-dashboard
juju add-relation -m $MODEL_NAME openstack-dashboard dbaas-ui-dashboard
juju add-relation -m $MODEL_NAME openstack-dashboard opsmgr
juju add-relation -m $MODEL_NAME trove-dashboard dbaas-ui-dashboard
juju add-relation -m $MODEL_NAME mysql opsmgr

# Add relationships between the OpenStack charma and the app specific filebeat configuration charm 
juju add-relation -m $MODEL_NAME mysql filebeat-config-mysql
juju add-relation -m $MODEL_NAME openstack-dashboard filebeat-config-horizon
juju add-relation -m $MODEL_NAME keystone filebeat-config-keystone


# Validation Remarks
set +x
echo "Run: 'watch -n 0.5 juju status' to monitor the install of everything. Wait for it to finish"
echo "Access Info:"
echo "Horizon port 80 of the openstack-dashboard container. admin/openstack"
echo "Nagios port 80 of the nagios container. nagiosadmin/nagiosadmin"
echo "Kibana port 8443 of the kibana container. kibana/kibana"
