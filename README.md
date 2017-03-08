# ipfinder

This is a clever little command line script I hacked together in Python. It takes either a domain name or IP address and returns the information about the IP address from the FreeGeoIP database. It can read a newline-separated list of IP addresss, it can highlight search terms, it can return just the lat,lon of an IP address. It can handle STDIN, so you can pipe out IP addresses from a live server log and get realtime information.

TODO:
- Cache IP addresses so repeat addresses aren't continually fetched.
- Output report to file
