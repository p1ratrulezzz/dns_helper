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
    return None

zone = dns.zone.from_file(zoneFile,origin='retracker.local')

recordA = str(zone.get_rdataset('@', 'a')).split(' ')
recordSoa = str(zone.get_rdataset('@', 'soa')).split(' ')

oldIP = recordA[-1] 

# print (recordSoa)

# sys.exit()

def updateSoa():
  serial = int(recordSoa[5])
  recordSoa[5] = str(serial + 1);
  textRdata = ' '.join(recordSoa[3:])
  rdataset = dns.rdataset.from_text('in', 'soa', 60, textRdata)
  zone.replace_rdataset('@', rdataset)
  print('SOA Updated')

def getNewIp():
  resolver = dns.resolver.Resolver()
  resolver.nameservers = [
    resolverIP,
  ]

  answer = resolver.query('retracker.local', 'a')
  return str(answer[0])

def rndcReload():
  os.system('rndc reload')
  os.system('rndc flush')
  print('rndc reload')

newIP = getNewIp()
if newIP and newIP != oldIP:
  updateSoa()
  rdataset = dns.rdataset.from_text('in', 'a', 60, newIP)
  zone.replace_rdataset('@', rdataset)
  zone.to_file(zoneFile, sorted=True, relativize=False)
  rndcReload()
  eprint('Zone updated with a new IP: ' + newIP + '; old IP: ' + oldIP)
else:
  print('Zone no needs to be updated.')
