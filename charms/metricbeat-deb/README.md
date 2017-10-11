# Matricbeat Deb Package

Matricbeat helps monitor servers and the services they host by collecting 
metrics from the operating system and services.

This charm is intended for installation of metricbeat on Power using Deb package.

## Usage

     juju deploy metricbeat-deb

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
