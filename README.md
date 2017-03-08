# ipfinder

This is a clever little command line script I hacked together in Python. It takes either a domain name or IP address and returns the information about the IP address from the FreeGeoIP database. It can read a newline-separated list of IP addresss, it can highlight search terms, it can return just the lat,lon of an IP address. It can handle STDIN, so you can pipe out IP addresses from a live server log and get realtime information.

usage: ipfinder.py [-h] [-file [FILE]] [-hostname [HOSTNAME]] [-coordinates]
                   [-wait] [-raw] [-search key=val [key=val ...]]
                   [IP_ADDR]

IP Address Information Fetcher. A simple command line tool to retrieve
physical location information based on an IP address. Information supplied by
FreeGeoIP.

positional arguments:
  IP_ADDR               Fetch FreeGeoIP data of a single IP address

optional arguments:
  -h, --help            show this help message and exit
  -file [FILE]          Read a list of IP addresses from a file
  -hostname [HOSTNAME]  Retrieve information using a hostname.
  -coordinates          Return decimal values as "lat,lon" from results for
                        mapping. Not available when using -file flag.
  -wait                 Pause the script when a match to a search is found
  -raw                  Return the raw JSON result from FreeGeoIp as is (i.e.
                        in unicode format)
  -search key=val [key=val ...]
                        Key/value pairs to search for in the results. (Can be
                        paused with the -wait flag.)

Thanks for sharing!

TODO:
- Cache IP addresses so repeat addresses aren't continually fetched.
- Output report to file
