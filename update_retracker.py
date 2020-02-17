#!/usr/bin/python3

import os
import dns.zone
import dns.rdatatype
import dns.query
import dns.resolver
import dns.rdataset
import sys

# Configs

zoneFile = '/var/cache/bind/zones/db.retracker.local'
resolverIP = '192.168.1.1'

####################################################################################3

def eprint(error):
    print(error, file=sys.stderr)

zone = dns.zone.from_file(zoneFile,origin='retracker.local')

recordA = str(zone.get_rrset('@', 'a')).split(' ')
oldIP = recordA[-1]

def getNewIp():
  resolver = dns.resolver.Resolver()
  resolver.nameservers = [
    resolverIP,
  ]

  answer = resolver.query('retracker.local', 'a')
  return str(answer[0])

def rndcReload():
  os.system('rndc reload')
  print('rndc reload')

newIP = getNewIp()
if newIP and newIP != oldIP:
  rdataset = dns.rdataset.from_text('in', 'a', 3600, newIP)
  zone.replace_rdataset('@', rdataset)
  zone.to_file(zoneFile)
  rndcReload()
  eprint('Zone updated with a new IP: ' + newIP + '; old IP: ' + oldIP)
else:
  print('Zone no needs to be updated.')
