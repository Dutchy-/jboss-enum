# jboss-enum
JBoss Deploy Enumerator

By default, JBoss has a very nice 'welcome.war' that shows which application is deployed on a specific instance. 
This tool enumerates all instances in a cluster environment given a server name pattern and a starting port. 
The output is a list of servers with the silo/tag that is deployed to the instance.

## Usage
Before running, change at least the server name pattern (line 19 in the docstring) or supply it using `--server-format`.

```
Usage:
  jboss-enum.py [--debug] [--quiet] [--port-base=N] [--port-offset=N] 
                [--instances=N] [--server-start=N] [--server-end=N] 
				[--server-format=FMT] [--timeout=N]
  jboss-enum.py [ -h | --help ]
  jboss-enum.py --version
Options:
  -h --help            Show this help.
  --version            Show version information.
  --debug              Print extra info.
  --quiet              Print less info.
  --port-base=N        The first port used per server [default: 8080].
  --port-offset=N      The distance in port number between each instance [default: 100].
  -i, --instances=N    The number of instances per server [default: 10].
  --server-start=N     The number of the first server in the cluster [default: 1].
  --server-end=N       The number of the last server in the cluster [default: 25].
  --server-format=FMT  The format for the server hostnames [default: jboss{0:04d}.evil-corp.local].
  -t, --timeout=N      The timeout in seconds for each server connection [default: 1].
```

## Examples
```
./jboss-enum.py
./jboss-enum.py --server-format=testjboss{0:03d}.domain.local
./jboss-enum.py --debug --port-base=8080 --port-offset=100 --instances=5 --server-start=10 --server-end=50 --server-format='testjboss{0:03d}.domain.local' -t 10
```
