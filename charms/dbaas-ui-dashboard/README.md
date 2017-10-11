# DBaas-UI-dashboard charm

This charm installs, and updates the DBaaS UI (Database as a service) Openstack dashboard
function.  The target plaform is Ubuntu LTS + Openstack.

The Horizon Openstack dashboard and the Trove Openstack dashboard must be installed to use
the DBaaS UI dashboard function.

## Usage
    cd dbaas-ui-dashboard
    juju deploy dbaas-ui-dashboard
    juju add-relation dbaas-ui-dashboard openstack-dashboard
    juju add-relation dbaas-ui-dashboard trove-dashboard

The dashboard is accessible on:
http(s)://service_unit_address/horizon

## Contact information

- William Irons &lt;wdirons@us.ibm.com&gt;

## Upstream Project Name

- Upstream website
- Upstream bug tracker
