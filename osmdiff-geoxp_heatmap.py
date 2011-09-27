#!/usr/bin/env python
import urllib2
import datetime
import os
import time
import sys
import re



SECRET = 'fill yours'
GEOXPAPI = 'fill yours'


BASEURL = 'http://planet.openstreetmap.org'
FREQ = '/minute-replicate/'
STATE = 'state.txt'
FILEEXT = '.osc.gz'
TMPDIFF = '/tmp/diff.osm'
LATEST = '/tmp/latest_osmdiff'
LASTSEQ = '0'

seqre = re.compile(r'.*sequenceNumber=([0-9]+).*')

def isdone(num):
  print ('Last Seq : ' + num )
  seqReq = urllib2.Request( BASEURL + FREQ + STATE )
  seqReq.add_header('Cache-Control', 'no-cache')
  try:
    f = urllib2.urlopen(seqReq)
    m = seqre.search(f.read(64))
    if m:
      currentseq = m.group(1)
      print ('Current Seq : ' + currentseq)
      if currentseq > num:
        num = currentseq
        print ('New Last Seq !')
        return num
      else:
        return False
  except urllib2.HTTPError:
    print("Missing")
    return False
  except:
    print("Failed")
    return False
  f.close()

def dl(dest, src):
  print("Downloading: " + src)
  req = urllib2.Request(src)
  req.add_header('Cache-Control', 'no-cache')
  try:
    f = urllib2.urlopen(req)
  except urllib2.HTTPError:
    print("Missing")
    return False
  except:
    print("Failed")
    return False
  g = file(dest, "w")
  try:
    d = f.read()
    g.write(d)
  except:
    print("Failed")
    g.close()
    os.unlink(dest)
    return False
  f.close()
  g.close()
  return True

def upload_latest():
  print("Upload to geoxp...")
  r = os.system('curl --data-binary @/tmp/diff.osm %s' % GEOXPAPI)
  return (r == 0)


def convert_latest():
  print("Converting")
  r = os.system('echo "SECRET %s"> /tmp/diff.osm' % SECRET)
  r = os.system('zcat /tmp/latest_osmdiff |grep "<node"|grep -v "</node>"|awk \'BEGIN { FS = "lat" } ; {print $2}\'|sed -e \'s/="/:/\' -e \'s/"\ lon="/:/\' -e \'s/"/:1:/\' -e \'s/\/*>$//\' >> %s' % TMPDIFF)
  return (r == 0)


while True:
  success = False
  tmpseq = isdone(LASTSEQ)
  if tmpseq is not False:
    LASTSEQ = tmpseq
    AAA = int(LASTSEQ) / 1000000
    BBB = int(LASTSEQ) /1000 - AAA * 1000
    CCC = int(LASTSEQ) - BBB * 1000 - AAA * 1000000
    if AAA == 0:
      AAA = '0'
    print ('Downloading osc... ')
    if (dl(LATEST, '%s%s%03d/%03d/%03d%s' % (BASEURL,FREQ,AAA,BBB,CCC,FILEEXT))):
      print ('Downloaded !')
      success = convert_latest()
      if (success):
        success = upload_latest()
        if (success):
          print ('Uploaded !')
  else:
    time.sleep(31)
  
