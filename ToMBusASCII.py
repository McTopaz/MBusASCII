'''
Creates an MBusASCII read request for one item as a byte array according to PiiGAB M-Bus ASCII protocol.
Specify TID, PID, ADR and ITEM to receive the request as byte array from the standard output.
Use the prefix and suffix fields to insert prefixes and suffixes before and after each byte.

ToMBusASCII.py <TID> <PID> <ADR> <ITEM> <PREFIX*> <SUFFIX*>
Tid: 0 - 99
PID: 0 = No checksum, 1 = With checksum
ADR: 0 - 99
ITEM: The item to read
PREFIX: (Optional) Each byte will start with the prefix
SUFFIX: (Optional) Each byte will end with the suffix

ToMBusASCII.py 0 0 0 a.b.c => 02 30 30 30 30 30 30 41 2E 42 2E 43 03 (without spaces)
ToMBusASCII.py 0 0 0 a.b.c 0x , => 0x02, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x41, 0x2E, 0x42, 0x2E, 0x43, 0x03,
'''

import sys
import struct

# Print command line information.
if len(sys.argv) == 1:
	print("Creates an MBusASCII read request for one item as byte array")
	print("ToMBusASCII.py <TID> <PID> <ADR> <ITEM>")
	print("ToMBUSASCII.py <TID> <PID> <ADR> <ITEM> <PREFIX*> <SUFFIX*>")
	print("Prefix and suffix fields will add prefixes and suffixes before/after each bytes")
	sys.exit()

stx = 0x02
tid = 0x00
pid = 0x00
adr = 0x00
item = ""
crc = 0x00
etx = 0x03

prefix = "0x"
suffix = ", "

# Get arguments.
tid = str(("%02d"%(int(sys.argv[1])))[:2]) # Parse tid to always 2 digits.
pid = str(("%02d"%(int(sys.argv[2])))[:2]) # Parse pid to always 2 digits.
adr = str(("%02d"%(int(sys.argv[3])))[:2]) # Parse adr to always 2 digits.
item = sys.argv[4]
prefix = sys.argv[5] if len(sys.argv) > 5 else ""
suffix = sys.argv[6] if len(sys.argv) > 6 else ""

includeCheckSum = pid == "01"	# Flag if checksum should be included in request.

# Create the request
request = struct.pack("B", stx)
request += bytearray(tid, 'ascii')
request += bytearray(pid, 'ascii')
request += bytearray(adr, 'ascii')
request += bytearray(item, 'ascii')

# Include checksum if PID = 1.
if includeCheckSum:
	for b in request[1:]:
		crc += b
		
	crc = crc & 0xFF
	crc = ("%02X"%(crc))
	request += bytearray(crc, 'ascii')

request += struct.pack("B", etx)

# Print each byte in request.
for b in request:
	print("%s%02X%s"%(prefix, b, suffix), end="")
print("")

