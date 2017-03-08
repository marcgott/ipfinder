#!/usr/bin/python

import sys
import socket
import urllib2
import json
import argparse
from django.utils.encoding import smart_str, smart_unicode
import mgcolor

color  = mgcolor.TerminalColor
searchParams = []
match = False
iscached = False
ipcache = {}
def print_row(dataobj,header=False):
	global searchParams,match,iscached

	for k in dataobj:
		if type(dataobj[k]) is unicode:
			dataobj[k]=smart_str(dataobj[k])[:17]

	if len(searchParams)>0:
		for param_d in searchParams:
			if dataobj[param_d.keys()[0]]==param_d.values()[0]:
				match = True
				#rval = "%-17s" % dataobj[param_d.keys()[0]]
				#dataobj[param_d.keys()[0]]=color.GREEN+color.BOLD+rval+color.END
				for key in dataobj.keys():
					dataobj[key] = color.GREEN+color.BOLD+("%-17s" % dataobj[key])+color.END
	if header is True:
		hstart = color.BOLD+str(color.BLUE if not iscached else color.CYAN)
		pval = dataobj.keys()
	else:
		hstart = ''
		pval = dataobj.values()

	print (hstart+"%-17s "+color.END)*11  % tuple(pval)
	if header:
		divider = color.GREEN+"="+color.END if match is True else "="
		print (divider*17+" ")*11

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

desc = "IP Address Information Fetcher. A simple command line tool to retrieve physical location information based on an IP address. Information supplied by FreeGeoIP."
parser = argparse.ArgumentParser(description=desc,epilog='Thanks for sharing!')
parser.add_argument('ipaddr', metavar='IP_ADDR', nargs='?', help='Fetch FreeGeoIP data of a single IP address',type=str)
parser.add_argument('-file', metavar='FILE', nargs='?', help='Read a list of IP addresses from a file')
parser.add_argument('-hostname', metavar='HOSTNAME', nargs='?', help='Retrieve information using a hostname.')
parser.add_argument('-coordinates', action='store_true', help='Return decimal values as "lat,lon" from results for mapping. Not available when using -file flag.')
parser.add_argument('-wait', action='store_true', help='Pause the script when a match to a search is found')
parser.add_argument('-raw', action='store_true', help='Return the raw JSON result from FreeGeoIp as is (i.e. in unicode format)')
parser.add_argument('-search', metavar='key=val', nargs='+', help='Key/value pairs to search for in the results. (Can be paused with the -wait flag.)')

args = parser.parse_args()
wait = args.wait if not None else False

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
				print color.ORANGE+"\nStopping program execution...\n"+color.END
				sys.exit(2)
			finally:
				sys.exit(0)
		try:
			prompt = "Enter an IP address or hostname: " if sys.stdin.isatty() else ""
			if addr is None and args.file is None:
				addr = raw_input(prompt)

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
			if noloop is True:
				sys.exit(0)

		except (KeyboardInterrupt):
			print color.ORANGE+"\nExiting...\n"+color.END
			sys.exit(0)
	
if __name__ == "__main__":
    # execute only if run as a script
    main()
