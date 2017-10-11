# Elasticsearch Via Deb Package

Elasticsearch is a flexible and powerful open source, distributed, real-time
search and analytics engine. Architected from the ground up for use in
distributed environments where reliability and scalability are must haves,
Elasticsearch gives you the ability to move easily beyond simple full-text
search. Through its robust set of APIs and query DSLs, plus clients for the
most popular programming languages, Elasticsearch delivers on the near
limitless promises of search technology.

Excerpt from [elasticsearch.org](http://www.elasticsearch.org/overview/ "Elasticsearch Overview")

# Usage

This charm is intended for installations were apt install elasticsearch will not
work because a build is not available for that platform. Because elasticsearch
is Java based it should run on any platform what supports Java 1.8

On the host running elasticsearch, create a file in the directory /etc/sysctl.d,
for example, 30-elasticsearch.conf with the contents being one line: 
    "vm.max_map_count=262144".  
Run "sysctl --system" after creating the file.

You can then deploy one node with:

    juju deploy elasticsearch-deb

### Relating to the Elasticsearch cluster

This charm currently provides the elasticsearch client interface to the
consuming service (cluster-name, host and port). Normally the other service
will only need this data from one elasticsearch unit to start as most client
libraries then query for the list of backends [1].

[1] http://elasticsearch-py.readthedocs.org/en/latest/api.html#elasticsearch

## Contact information

- William Irons &lt;William Irons@wdirons@us.ibm.com&gt;

## Upstream Project Name

- Upstream website
- Upstream bug tracker
