# opsmgr charm

This charm installis the opsmgr command line and horizon dashboard for
inventory management of a cluster. 

The Horizon Openstack dashboard must be installed to use the opsmgr function.

## Usage
    cd opsmgr
    juju deploy opsmgr
    juju add-relation opsmgr openstack-dashboard

The dashboard is accessible on:
http(s)://service_unit_address/horizon

## Contact information

- William Irons &lt;wdirons@us.ibm.com&gt;

## Upstream Project Name

- Upstream website
- Upstream bug tracker
