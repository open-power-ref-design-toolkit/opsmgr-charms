# Filebeat Via Deb Package

Filebeat modules simplify the collection, parsing, and visualization of common log formats. A typical module is composed of one or more filesets.

This charm is intended for installation of filebeat on Power using Deb package.

## Usage

     juju deploy filebeat-deb

### Testing the deployment

The services provide extended status reporting to indicate when they are ready:

    juju status --format=tabular

This is particularly useful when combined with watch to track the on-going
progress of the deployment:

    watch -n 0.5 juju status --format=tabular

The message for each unit will provide information about that unit's state.
Once they all indicate that they are ready, you can use the provided
`generate-noise` action to test that the applications are working as expected:

    juju action do filebeat/0 generate-noise
    watch juju action status

Once the action is complete, you can retrieve the results:

    juju action fetch <action-id>

The &lt;action-id&gt; value will be in the juju action status output.

## Contact information

## Upstream Project Name

- Upstream website
- Upstream bug tracker
