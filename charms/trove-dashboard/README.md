# Trove-dashboard charm

This charm installs, and updates the Trove DBaaS (Database as a service) Openstack dashboard
function.  The target plaform is Ubuntu LTS + Openstack.

The Horizon Openstack dashboard must be installed to use the Trove dashboard function.

## Usage
    cd trove-dashboard
    juju deploy trove-dashboard
    juju add-relation trove-dashboard openstack-dashboard

The dashboard is accessible on:
http(s)://service_unit_address/horizon

## Contact information

- William Irons &lt;wdirons@us.ibm.com&gt;

## Upstream Project Name

- Upstream website
- Upstream bug tracker
