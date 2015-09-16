#!/usr/bin/env python3
"""Usage:
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
"""
# built-in
import re
from multiprocessing import Process, Pool
import socket

# Docopt is a library for parsing command line arguments
from docopt import docopt

# HTTP requests library
import requests

# Parse html
from lxml import html



class instance:
	""" Class to keep track of results, contains the details of 1 instance."""
	def __init__(self, hostname, instance, tag, silo, port):
		self.hostname = hostname
		self.instance = instance
		self.tag = tag
		self.silo = silo
		self.port = port

	def __str__(self):
		return ', '.join([self.hostname, self.instance, self.tag, self.silo, str(self.port)])

def visit(server, port):
	""" Does the HTTP request to the server. """
	i = ""
	try:
		dest = 'http://{}:{}'.format(server, port)
		debug("Requesting {}".format(dest))
		return extract(requests.get(dest, timeout=TIMEOUT).text)
	except requests.exceptions.Timeout:
		return None
	except requests.exceptions.ConnectionError as e:
		debug("{}: {}".format(str(e), server))
		return None

def extract(response):
	""" Extracts the information from the page. Returns one "instance" class. """
	# Convert the html to a tree
	tree = html.fromstring(response)
	# Find the fields using xpath
	fields = tree.xpath("//table/tr/td")
	# select only each second item (the value, not the description)
	values = [fields[x].text for x in range(1,10,2)]

	return instance(values[0], values[1], values[2], values[3], PORT_BASE+int(re.match('\+(\d+)', values[4]).group(0)))

def get_servers():
	options = []
	for server in SERVERS:
		try:
			hostname = socket.gethostbyname(server)
			for port in PORTS:
				options.append((hostname, port, ))
		except socket.gaierror:
			debug("{} has no DNS record.".format(server))
	return options

def log(message):
	if not arguments['--quiet']:
		print(message)

def debug(message):
	if arguments['--debug']:
		print(message)

if __name__ == '__main__':
	arguments = docopt(__doc__, version='JBoss Enumerator v0.1')
	debug(arguments)

	# Base port for the first instance on a server
	PORT_BASE=int(arguments['--port-base'])
	# Offset per instance
	PORT_OFFSET=int(arguments['--port-offset'])
	# Number of instances per server
	INSTANCES=int(arguments['--instances'])
	# Number of the first server
	SERVER_START=int(arguments['--server-start'])
	# Number of the last server
	SERVER_END=int(arguments['--server-end'])
	# Format of the server hostname
	SERVER_FORMAT = arguments['--server-format']
	# List of all servers
	SERVERS = [SERVER_FORMAT.format(x) for x in range(SERVER_START,SERVER_END+1)]
	# List of ports per server
	PORTS = [PORT_BASE + x*PORT_OFFSET for x in range(0,INSTANCES)]
	# Timeout in seconds for each server connection
	TIMEOUT = int(arguments['--timeout'])
	

	log("Scanning servers from {} to {}.".format(SERVERS[0], SERVERS[-1]))
	log("Scanning ports: {}".format(','.join([str(x) for x in PORTS])))
	options = get_servers()

	# Make a pool worker for each server/port combination
	p = Pool(processes=len(options))#(SERVER_END-SERVER_START+1)*INSTANCES)
	# Start all of them	
	results = [result for result in p.starmap(visit, options) if result != None]
	
	for result in results:
		print(result)
	#	p = Process(target=call, args=(server, port))
	#	p.start()
