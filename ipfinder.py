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

def print_row(dataobj,header=False):
	global searchParams,match

	for k in dataobj:
		if type(dataobj[k]) is unicode:
			dataobj[k]=smart_str(dataobj[k])[:17]

	if len(searchParams)>0:
		for param_d in searchParams:
			if dataobj[param_d.keys()[0]]==param_d.values()[0]:
				match = True
				rval = "%-17s" % dataobj[param_d.keys()[0]]
				dataobj[param_d.keys()[0]]=color.GREEN+color.BOLD+rval+color.END
	if header is True:
		hstart = color.BOLD+color.BLUE 
		pval = dataobj.keys()
	else:
		hstart = ''
		pval = dataobj.values()

	print (hstart+"%-17s "+color.END)*11  % tuple(pval)
	if header:
		print ("="*17+" ")*11

def geofetch(addr):
	geo = urllib2.urlopen("http://freegeoip.net/json/"+addr)
	ipdata = geo.read()
	return json.loads(ipdata,'UTF-8')

def main():
	while True:
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
		addr = args.ipaddr
		noloop = False

		if args.search:
			for s in args.search:
				sdict = dict( (k,v) for k,v in (a.split('=') for a in s.split() ) )
				searchParams.append(sdict)

		if args.hostname:
			addr = socket.gethostbyname(args.hostname)
			if args.hostname is not None:
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
				#raise
				print color.ORANGE+"\nStopping program execution...\n"+color.END
				sys.exit(2)
			finally:
				sys.exit(0)
		try:
			if addr is None and args.file is None:
				addr = raw_input()

			dataobj = geofetch(addr)
			if addr is not None:
				noloop = True
			if args.raw:
				print dataobj
				sys.exit(0)
			elif args.coordinates:
				print str(dataobj["latitude"])+","+str(dataobj["longitude"])
				sys.exit(0)
			else:
				print_row(dataobj,True)
				print_row(dataobj)
			if noloop is True:
				sys.exit(0)
		except (KeyboardInterrupt,SystemExit):
			print color.ORANGE+"\nStopping program execution...\n"+color.END
			sys.exit(3)
	
if __name__ == "__main__":
    # execute only if run as a script
    main()
