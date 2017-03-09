#!/usr/bin/env python

import sys
import socket
import urllib2
import time
import json
import argparse
import collections
from django.utils.encoding import smart_str, smart_unicode
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from urlparse import urlparse, parse_qs
import mgcolor

# This is a small color class I use to give the terminal some pizzazz
color  = mgcolor.TerminalColor
SERVER_PORT = 8675

searchParams = []
ignoredIPs = []
colabbr = {'city':'city','region_code':'rcode','region_name':'rname','ip':'ip','time_zone':'tz','longitude':'lon','metro_code':'mcode','latitude':'lat','country_code':'ccode','country_name':'cname','zip_code':'zip'}
match = False
iscached = False
ipcache = {}

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		try:
			self.send_response(200)
			self.send_header('Content-type','application/json')
			self.end_headers()
			# Send the html message
			query_components = parse_qs(urlparse(self.path).query)
			#self.wfile.write(query_components)
			ipaddr = ''.join(query_components["ip"])
			self.wfile.write(convert(geofetch(ipaddr)))
			return
		except KeyError:
			pass
def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

def print_row(dataobj,header=False):
	global searchParams,match,iscached,colabbr
# Trims the output to 17 characters. Because terminal.
# I eventually had to give up and use smart_str from django
	tmpdo =[] 
	for k in dataobj:
		if type(dataobj[k]) is unicode:
			dataobj[k]=smart_str(dataobj[k])[:17]
		if args.columns is not None and colabbr[k] not in args.columns:
			tmpdo.append(k)
	if tmpdo is not None:
		for dkey in tmpdo:
			del dataobj[dkey]

# Are we looking for visitors from a particular country or city?
# If it's a match, color it GREEN
	if len(searchParams)>0:
		for param_d in searchParams:
			if dataobj[param_d.keys()[0]]==param_d.values()[0]:
				match = True
				for key in dataobj.keys():
					dataobj[key] = color.GREEN+color.BOLD+("%-17s" % dataobj[key])+color.END

# Since we want to print across, not down, we gotta iterate twice
# BLUE if it's a new IP address, CYAN if it comes from the cache
	if header is True:
		hstart = color.BOLD+str(color.BLUE if not iscached else color.CYAN)
		pval = dataobj.keys()
	else:
		hstart = ''
		pval = dataobj.values()

	print (hstart+"%-17s "+color.END)*len(dataobj)  % tuple(pval)

# Then print a separator, GREEN if it matches something
	if header:
		divider = color.GREEN+"="+color.END if match is True else "="
		print (divider*17+" ")*len(dataobj)
	match = False
	time.sleep(0.6)

# Thank you for the magic, FreeGeoIP!
def geofetch(addr):
	global iscached
	exist = ipcache.get(str(addr),None)
	if exist is not None:
		iscached = True
		return ipcache[str(addr)]
	else:
		geo = urllib2.urlopen("http://freegeoip.net/json/"+addr)
		ipdata = geo.read()
		ipcache[addr] = json.loads(ipdata,'UTF-8')
		iscached = False
		return json.loads(ipdata,'UTF-8')

# Initialize the command line parsing arguments
desc = "IP Address Information Fetcher. A simple command line tool to retrieve physical location information based on an IP address. Information supplied by FreeGeoIP."
parser = argparse.ArgumentParser(description=desc,epilog='Thanks for sharing!')
parser.add_argument('ipaddr', metavar='IP_ADDR', nargs='?', help='Fetch FreeGeoIP data of a single IP address',type=str)
parser.add_argument('-columns', nargs='*', choices=['city','rcode','rname','ip','tz','lat','lon','mcode','ccode','cname','zip'],help='Select which columns to show:\ncity: city name\nrcode: region code (US States) '+color.BOLD+'rname:'+color.END+' region name (US States) '+color.BOLD+'ip:'+color.END+' IP address '+color.BOLD+'tz:'+color.END+' Timezone')
parser.add_argument('-coordinates', action='store_true', help='Return decimal values as "lat,lon" from results for mapping. Not available when using -file flag.')
parser.add_argument('-file', metavar='FILE', nargs='?', help='Read a list of IP addresses from a file')
parser.add_argument('-hostname', metavar='HOSTNAME', nargs='?', help='Retrieve information using a hostname.')
parser.add_argument('-http', metavar='PORT', nargs='*', type=int, help='Starts as a web server on PORT (8675 by default). Server accepts querystring ?ip=nnn.nnn.nnn.nnn and returns raw JSON object')
parser.add_argument('-ignore', metavar='IP_ADDR', nargs='*', help='IP addresses to ignore, separated by spaces. Providing no IP addresses will ignore your own public IP address.')
parser.add_argument('-raw', action='store_true', help='Return the raw JSON result from FreeGeoIp as is (i.e. in unicode format)')
parser.add_argument('-search', metavar='key=val', nargs='+', help='Key/value pairs to search for in the results. (Can be paused with the -wait flag.)')
parser.add_argument('-wait', action='store_true', help='Pause the script when a match to a search is found. Will not work on piped live file (yet).')
args = parser.parse_args()

if args.http is not None:
	try:
		SERVER_PORT = SERVER_PORT if len(args.http)<1 else args.http[0]
		#Create a web server and define the handler to manage the
		#incoming request
		server = HTTPServer(('', SERVER_PORT), myHandler)
		print 'Started httpserver on port' , SERVER_PORT
		server.serve_forever()
	except KeyboardInterrupt:
		print color.ORANGE+"\nExiting...\n"+color.END
		exit(0)

# The loop
def main():
	while True:
		#print("\n")
		addr = args.ipaddr
		noloop = False
		if addr:
			# Single IP address
			noloop = True
		if args.search:
			# Initializes the search key/value pairs
			for s in args.search:
				sdict = dict( (k,v) for k,v in (a.split('=') for a in s.split() ) )
				searchParams.append(sdict)
		if args.ignore is not None:
			if not args.ignore:
				mydata = geofetch('')
				args.ignore.append(smart_str(mydata["ip"]))
			else:
				for a in args.ignore:
					ignoredIPs.append(a)
		if args.hostname:
			addr = socket.gethostbyname(args.hostname)
			if args.hostname is not None:
				# Single hostname
				noloop = True
		if args.file:
			print "Filename "+args.file+" provided"
			ipfile = open(args.file,"r")
			ipar = ipfile.read()
			try:
				for addr in ipar.split("\n"):
					if addr in ignoredIPs:
						pass
					dataobj = geofetch(addr)
					if args.raw:
						print dataobj
					else:
						print_row(dataobj,True)
						print_row(dataobj)
						print "\n"
						if args.wait and match is True:
							raw_input("Press enter key to continue")
						match=False
			except (KeyboardInterrupt,SystemExit):
				print color.ORANGE+"\nExiting...\n"+color.END
				sys.exit(2)
			finally:
				sys.exit(0)
		try:
			prompt = "Enter an IP address or hostname: " if sys.stdin.isatty() else ""
			if addr is None and args.file is None:
				addr = raw_input(prompt)
			if addr  in ignoredIPs:
				raise Exception
			dataobj = geofetch(addr)
			if addr is None:
				noloop = True
			if args.raw:
				# Return raw JSON format
				print dataobj
				sys.exit(0)
			elif args.coordinates:
				# Return lat,lon
				print str(dataobj["latitude"])+","+str(dataobj["longitude"])
				sys.exit(0)
			else:
				print_row(dataobj,True)
				print_row(dataobj)
				print "\n"
			if noloop is True:
				sys.exit(0)
		except (Exception):
			pass
		except (KeyboardInterrupt):
			print color.ORANGE+"\nExiting...\n"+color.END
			sys.exit(0)

if __name__ == "__main__":
    main()
