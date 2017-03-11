# IPFinder

This is a clever (IMHO) little command line script I hacked together in Python. It takes either a domain name or IP address and returns the information about the IP address from the FreeGeoIP database. It can read a newline-separated list of IP addresss, it can highlight search terms, it can return just the lat,lon of an IP address. It can handle STDIN, so you can pipe out IP addresses from a live server log and get realtime information on where your visitors (or malicious actors) are coming from.
<br>
##Basic Usage and  Switches
usage: ipfinder.py [-h] [-coordinates] [-file [FILE]] [-hostname [HOSTNAME]]<br>
                   [-ignore [IP_ADDR [IP_ADDR ...]]] [-raw]<br>
                   [-search key=val [key=val ...]] [-wait]<br>
                   [IP_ADDR]<br>
<br>
IP Address Information Fetcher. A simple command line tool to retrieve
physical location information based on an IP address. Information supplied by
FreeGeoIP.
<br>
positional arguments:<br>
 **IP_ADDR**               Fetch FreeGeoIP data of a single IP address<br>
<br>
optional arguments:<br>
  **-h, --help**	show this help message and exit mapping. Not available when using -file flag.<br>
  **-columns**	 [{city,rcode,rname,ip,tz,lat,lon,mcode,ccode,cname,zip} [{city,rcode,rname,ip,tz,lat,lon,mcode,ccode,cname,zip} ...]]<br>
		Select which columns to show, separated by spaces:<br>
		city:   City name<br>
		rcode:  Region code (US States)<br>
		rname:  Region name (US States)<br>
		ip:     IP address<br>
		tz:     Timezone<br>
		lat:    Latitude<br>
		lon:    Longitude<br>
		mcode:  Metro Code<br>
		ccode:  City Code<br>
		cname:  City Name<br>
		zip:    Zip/postal code<br>
  **-coordinates**          Return decimal values as "lat,lon" from results for mapping. Not available when using -file flag.<br>
  **-delay DELAY**          Delay in seconds after output (accepts decimals as fractions of a second.)<br>
  **-file [FILE]**          Read a list of IP addresses from a file<br>
  **-hostname [HOSTNAME]**  Retrieve information using a hostname.<br>
  **-http [PORT [PORT ...]]**	Starts as a web server on PORT (8675 by default). Server accepts querystring ?ip=nnn.nnn.nnn.nnn and returns raw JSON object<br>
  **-ignore [IP_ADDR [IP_ADDR ...]]**	IP addresses to ignore, separated by spaces. Providing no IP addresses will ignore your own public IP address.<br>
  **-raw**	Return the raw JSON result from FreeGeoIp as is (i.e. in unicode format)<br>
  **-search key=val [key=val ...]**	Key/value pairs to search for in the results. (Can be paused with the -wait flag.)<br>
  **-wait**	Pause the script when a match to a search is found. Will not work on piped live file (yet).<br>
<br>
Because awk writes to a buffer, you need to run ipfinder against a live apache access_log with stdbuf:<br>
`tail -f /path/to/apache/logs/access_log | stdbuf -oL awk '{print $1}' |python -m ipfinder`
<br>
<br>
Thanks for sharing!
<br>
TODO:<br>
- Output report to file
