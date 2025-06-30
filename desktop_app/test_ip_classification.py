#!/usr/bin/env python3
"""Test IP classification"""

import ipaddress

test_ips = [
    "203.0.113.100",  # RFC5737 TEST-NET-3
    "198.51.100.50",  # RFC5737 TEST-NET-2 
    "192.0.2.1",      # RFC5737 TEST-NET-1
    "192.168.1.1",    # Private
    "10.0.0.1",       # Private
    "8.8.8.8"         # Public
]

for ip in test_ips:
    ip_obj = ipaddress.ip_address(ip)
    print(f"{ip}: is_private={ip_obj.is_private}, is_global={ip_obj.is_global}")
