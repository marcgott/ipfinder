# ipfinder

This is a clever (IMHO) little command line script I hacked together in Python. It takes either a domain name or IP address and returns the information about the IP address from the FreeGeoIP database. It can read a newline-separated list of IP addresss, it can highlight search terms, it can return just the lat,lon of an IP address. It can handle STDIN, so you can pipe out IP addresses from a live server log and get realtime information on where your visitors (or malicious actors) are coming from.
<br>
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
  IP_ADDR               Fetch FreeGeoIP data of a single IP address
<br>
optional arguments:<br>
  -h, --help            show this help message and exit<br>
  -coordinates          Return decimal values as "lat,lon" from results for<br>
                        mapping. Not available when using -file flag.<br>
  -file [FILE]          Read a list of IP addresses from a file<br>
  -hostname [HOSTNAME]  Retrieve information using a hostname.<br>
  -ignore [IP_ADDR [IP_ADDR ...]]<br>
                        IP addresses to ignore, separated by spaces. Providing<br>
                        no arguments will ignore your public IP address.<br>
  -raw                  Return the raw JSON result from FreeGeoIp as is (i.e.<br>
                        in unicode format)<br>
  -search key=val [key=val ...]<br>
                        Key/value pairs to search for in the results. (Can be<br>
                        paused with the -wait flag.)<br>
  -wait                 Pause the script when a match to a search is found<br>

<br>
Because awk writes to a buffer, you need to run ipfinder against a live apache access_log with stdbuf:<br>
tail -f /path/to/apache/logs/access_log | stdbuf -oL awk '{print $1}' |python -m ipfinder<br>
<br>
Thanks for sharing!
<br>
TODO:<br>
- Output report to file
