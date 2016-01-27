#!/usr/bin/python
import csv
from binascii import unhexlify
import re
import sys

def upperfirst(x):
    return x[0].upper() + x[1:]

def parsetag(x):
    substrate = x
    firstOctet = substrate[0]
    substrate = substrate[1:]
    t = ord(firstOctet)
    tagClass = t & 0xC0
    tagFormat = t & 0x20
    tagId = t & 0x1F
    if tagId == 0x1F:
        tagId = 1
        while 1:
            if not substrate:
                raise Exception(
                    'Short octet stream on long tag decoding'
                )
            t = ord(substrate[0])
            tagId = tagId << 7 | (t & 0x7F)
            substrate = substrate[1:]
            if not t & 0x80:
                break
    return (tagClass, tagFormat, tagId)

dr = csv.DictReader(open(sys.argv[1], 'rb'), dialect='excel-tab')
tags = {}
for r in dr:
    try:
        int(r['Tag'], 16)
    except:
        pass
    else:
        tags[r['Tag']] = r

taglist = sorted(tags.keys())

maxlen = 0
for t in taglist:
    ### clean up the names so they can be ASN.1 identifiers
    name = tags[t]['Name'].replace(' ', '')
    name = re.sub('\([^)]+\)', '', name)
    name = name.replace(',','')
    name = name.replace('/','')
    tags[t]['name'] = upperfirst(name)
    maxlen = max(maxlen, len(tags[t]['name']))

print """EMV DEFINITIONS IMPLICIT TAGS::=

BEGIN
"""

for t in taglist:
    try:
        tcls, tfmt, tid = parsetag(unhexlify(t))
    except TypeError:
        print "-- Failed to parse '%s' (%s)" % (t,tags[t]['Name'])
        continue
    cls = { 0 : 'UNIVERSAL', 64 : 'APPLICATION', 128 : '', 192 : 'PRIVATE' }[tcls]
    fmt = { 0 : 'SIMPLE', 32 : 'CONSTRUCTED' }[tfmt]
    asntypes = { 'CONSTRUCTED' : 'EXPLICIT OCTET STRING', 'SIMPLE' : 'OCTET STRING' }
    asntype = asntypes[fmt]
    print " {:{namewidth}} ::= [{:12} {:5}] {:{typewidth}}  -- {} {} {}".format(
        tags[t]['name'], cls, tid, asntype, t, fmt, tags[t]['Format'],
        namewidth=maxlen, typewidth=max(map(len, asntypes.values()))
    )

print """
END"""
