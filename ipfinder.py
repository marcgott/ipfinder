#!/usr/bin/env python

import base64
import mgcolor
color  = mgcolor.TerminalColor
import sys
import socket
import urllib2
import time
import json
import pip
import pip.req
import pkg_resources
import argparse
from argparse import RawTextHelpFormatter
import collections
from django.utils.encoding import smart_str, smart_unicode
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
SERVER_PORT = 8675
from urlparse import urlparse, parse_qs

# This is a small color class I use to give the terminal output some pizzazz

colabbr = {'city':'city','region_code':'rcode','region_name':'rname','ip':'ip','time_zone':'tz','longitude':'lon','metro_code':'mcode','latitude':'lat','country_code':'ccode','country_name':'cname','zip_code':'zip'}
match = False
iscached = False
ipcache = {}
searchParams = []
#Get an API key here: https://ipstack.com/
ipstack_key=""
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
		temp = []
		for p in pval:
			title = smart_str(p).upper() if p=='ip' else smart_str(p).replace("_"," ").title()
			temp.append( title )
		pval = tuple(temp)
	else:
		hstart = ''
		pval = dataobj.values()

	print (hstart+"%-17s "+color.END)*len(dataobj)  % tuple(pval)

# Then print a separator, GREEN if it matches something
	if header:
		divider = color.GREEN+"="+color.END if match is True else "="
		print (divider*17+" ")*len(dataobj)
	else:
		time.sleep(args.delay)
	match = False

# Thank you for the magic, FreeGeoIP!
def geofetch(addr):
	if addr == "0.0.0.0":
		addr="check"
	global iscached
	exist = ipcache.get(str(addr),None)
	if exist is not None:
		iscached = True
		return ipcache[str(addr)]
	else:
		try:
			#geo = urllib2.urlopen("http://freegeoip.net/json/"+addr)
			geo = urllib2.urlopen("http://api.ipstack.com/"+addr+"?access_key="+ipstack_key+"&output=json&legacy=1")
			ipdata = geo.read()
			ipcache[addr] = json.loads(ipdata,'UTF-8')
			iscached = False
			return json.loads(ipdata,'UTF-8')
		except urllib2.HTTPError:
			print (addr+ " not a valid ip address.")

# Initialize the command line parsing arguments
desc = "IP Address Information Fetcher. A simple command line tool to retrieve physical location information based on an IP address. Information supplied by FreeGeoIP."
parser = argparse.ArgumentParser(description=desc,epilog='''Note: Because awk writes to a buffer, you need to run ipfinder against a live Apache-style access_log with stdbuf:
tail -f /path/to/logs/access_log | stdbuf -oL awk '{print $1}' |python -m ipfinder.

Thanks for sharing!''',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('ipaddr', metavar='IP_ADDR', nargs='?', help='Fetch data of a single IP address. If omitted, you will be prompted to enter an IP address or hostname.',type=str)
parser.add_argument('-columns', nargs='*', choices=['city','rcode','rname','ip','tz','lat','lon','mcode','ccode','cname','zip'],help='''\
Select which columns to show, separated by spaces:
'''+color.BOLD+'city:'''+color.END+'''	City name
'''+color.BOLD+'rcode:'''+color.END+'''	Region code (US States)
'''+color.BOLD+'''rname:'''+color.END+'''	Region name (US States)
'''+color.BOLD+'''ip:'''+color.END+'''	IP address 
'''+color.BOLD+'''tz:'''+color.END+'''	Timezone
'''+color.BOLD+'''lat:'''+color.END+'''	Latitude
'''+color.BOLD+'''lon:'''+color.END+'''	Longitude
'''+color.BOLD+'''mcode:'''+color.END+'''	Metro Code
'''+color.BOLD+'''ccode:'''+color.END+'''	City Code
'''+color.BOLD+'''cname:'''+color.END+'''	City Name
'''+color.BOLD+'''zip:'''+color.END+'''	Zip/postal code
''')
parser.add_argument('-coordinates', action='store_true', help='Return decimal values as "lat,lon" from results for mapping. Not available when using -file flag.')
parser.add_argument('-delay', metavar='DELAY', nargs=1, help='Delay in seconds after output (accepts decimals as fractions of a second.)',default=0.4)
parser.add_argument('-file', metavar='FILE', nargs='?', help='Read a list of IP addresses from a file')
parser.add_argument('-hostname', metavar='HOSTNAME', nargs='?', help='Retrieve information using a hostname.')
parser.add_argument('-http', metavar='PORT', nargs='*', type=int, help='Starts as a web server on PORT (8675 by default). Server accepts querystring ?ip=nnn.nnn.nnn.nnn and returns raw JSON object')
parser.add_argument('-ignore', metavar='IP_ADDR', nargs='*', help='IP addresses to ignore, separated by spaces. Providing no IP addresses will ignore your own public IP address.')
parser.add_argument('-raw', action='store_true', help='Return the raw JSON result from FreeGeoIp as is (i.e. in unicode format)')
parser.add_argument('-search', metavar='key=val', nargs='+', help='Key/value pairs to search for in the results. (Can be paused with the -wait flag.)')
parser.add_argument('-wait', action='store_true', help='Pause the script when a match to a search is found. Will not work on piped live file (yet).')
args = parser.parse_args()

if not args.raw:
	print(color.PERIWINKLE)
	print(base64.b64decode("ICBfX19fX19fX19fXyAgX19fX19fIF8gICAgICAgICAgIF8NCiB8XyAgIF98IF9fXyBcIHwgIF9fXyhfKSAgICAgICAgIHwgfA0KICAgfCB8IHwgfF8vIC8gfCB8XyAgIF8gXyBfXyAgIF9ffCB8IF9fXyBfIF9fDQogICB8IHwgfCAgX18vICB8ICBffCB8IHwgJ18gXCAvIF9gIHwvIF8gXCAnX198DQogIF98IHxffCB8ICAgICB8IHwgICB8IHwgfCB8IHwgKF98IHwgIF9fLyB8DQogIFxfX18vXF98ICAgICBcX3wgICB8X3xffCB8X3xcX18sX3xcX19ffF98DQoNCiAgICBodHRwczovL2dpdGh1Yi5jb20vbWFyY2dvdHQvaXBmaW5kZXINCg=="))					                                                 
	print(color.END)
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
				mydata = geofetch('check')
				args.ignore.append(smart_str(mydata["ip"]))
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
					if args.ignore is not None and addr in args.ignore:
						pass
					else:
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
			if args.ignore is not None and addr in args.ignore:
				pass
			else:
				try:
					socket.inet_aton(addr)
				except:
					pass
				try:
					addr = socket.gethostbyname(addr)
				except socket.gaierror:
					print (addr + "not a valid IP address")
				except:
					if addr.startswith('\x08'):
						parser.print_help()
					else:
						raise #print("Invalid IP address or hostname.")
				else:
					dataobj = geofetch(addr)
					if addr is None:
						noloop = True
					if args.raw:
						# Return raw JSON format
						#print dataobj
						print json.dumps(dataobj).decode('unicode-escape').encode('utf8')
						sys.exit(0)
					elif args.coordinates:
						# Return lat,lon
						print str(dataobj["latitude"])+","+str(dataobj["longitude"])
						sys.exit(0)
					else:
						print_row(dataobj,True)
						print_row(dataobj)
						print "\n"
						if noloop:
							exit(0)
		
		except (KeyboardInterrupt):
			print color.ORANGE+"\nExiting...\n"+color.END
			sys.exit(0)
		except:
			if noloop is True:
				exit(0)

if __name__ == "__main__":
    main()
