'''
Parse an MBusASCII response for one item as a byte array according to PiiGAB M-Bus ASCII protocol.
Specify the entire package to to parse the response.

FromMBusASCII.py <PACKAGE>
Will parse into either:

Positive response:
	ACK, TID, PID, ADR, ITEM, CRC, ETX
Negative response:
	NAK, TID, PID, ACR, ERROR, ETX
	
ITEM:	Gateway.67002656_15701045T.Temperature
REQ:	02 30 31 30 30 30 30 47 61 74 65 77 61 79 2E 36                   
		37 30 30 32 36 35 36 5F 31 35 37 30 31 30 34 35                   
		54 2E 54 65 6D 70 65 72 61 74 75 72 65 03                         
RES:	06 30 31 30 30 30 30 32 32 2E 33 03

ITEM:	Gateway.67002656_15701045T.Temperature
REQ:	02 30 32 30 31 30 30 47 61 74 65 77 61 79 2E 36                   
		37 30 30 32 36 35 36 5F 31 35 37 30 31 30 34 35                   
		54 2E 54 65 6D 70 65 72 61 74 75 72 65 43 39 03                   
RES:	06 30 32 30 31 30 30 32 32 2E 33 45 38 03 
	
'''

import sys
import struct

ack = 0x06
nak = 0x15
etx = 0x03

# Print command line information.
if len(sys.argv) == 1:
	print("Parse an MBusASCII response for one item")
	print("FromMBusASCII.py <PACKAGE>")
	print("FromMBusASCII.py 06303030 ...")
	print("FromMBusASCII.py 153030 ... ")
	sys.exit()

# Package must have even length.
if len(sys.argv) == 2 and len(sys.argv[1]) % 2 == True:
	print("Error: Given package has not an even length.")
	sys.exit()

response = []	
temp = None

# Parse the package into an array: 02 30 31 30 30 30 30 47 61 etc.
if len(sys.argv) > 2:

	# If there are more than one arguments, count all as the package.
	for arg in sys.argv[1:]:
		
		# arg contains one or two characters, use as is: 4, 0C, F4 etc.
		if len(arg) <= 2:
			temp = arg
			
		# arg contains more then two characters: Use only first two characters: 000, BEEF, 347 or 8F3A5C.
		else:
			temp = arg[:2]

		# Try to convert hex string to int.
		try:
			response.append(int(temp, 16))
		except:
			print("Error: '%s' is not a valid hexadecimal number"%(arg))
			sys.exit()

# First argument is just one long string: 023031303030304761 etc.
else:
	
	# Iterate over every other characters.
	for start in range(0, len(sys.argv[1]), 2):
	
		# Try to convert hex string to int.
		try:
			temp = int(sys.argv[1][start:start + 2], 16)
			response.append(temp)
		except:
			print("Error: '%s' contains a non hexadecimal number"%(sys.argv[1]))
			sys.exit()
''''
# Print data in request	
for b in response:
	print(b)

print("")
'''	
# Verify that package contains STX, TID, PID = 0, ADR and ETX amount of bytes.
if len(response) < 8:
	print("Error: Invalid package length.")
	sys.exit()

isAck = response[0] == ack
isNak = response[0] == nak

# Check if package is positive (ACK) or negative (NAK).
if isAck == False and isNAk == False:
	print("Error: Unknown package")
	sys.exit()

isEtx = response[len(response)-1] == etx

# Check package ends with ETX.
if isEtx == False:
	print("Error: package don't end with etx")
	sys.exit()

tid = "%s%s"%(response[1] - 0x30, response[2] - 0x30)
tid = int(tid)
pid = "%s%s"%(response[3] - 0x30, response[4] - 0x30)
pid = int(pid)
adr = "%s%s"%(response[5] - 0x30, response[6] - 0x30)
adr = int(adr)
checkSumIncluded = pid == 0x01

# Get checksum from package.
crc = 0
if checkSumIncluded:
	length = len(response)
	i = response[length-3]
	print(i)
	i = response[length-2]
	print(i)
	crc = "%s%s"%(response[length-3] - 0x30, response[length-2] - 0x30)
	print(crc)
	crc = int(crc)
	print("%02x"%(crc))

# Verify that package contains STX, TID, PID = 1, ADR, CRC, and ETX amount of bytes.
if checkSumIncluded and len(response) < 10:
	print("Error: Invalid package length with checksum.")
	sys.exit()

# Calculate checksum and check it.
okCrc = False
if checkSumIncluded:
	cs = 0
	for b in response[1:len(response)-3]:
		print("%02x : %s"%(b, b))
		cs += b
		
	cs = cs & 0xFF
	okCrc = cs == crc
	print(crc)
	print(cs)
	print("OK CRC: %s"%(okCrc))
	
# For ACK responses.
if ack:
	data = None
	if checkSumIncluded:
		data = response[7:len(response)-3]	# Ignore STX, TID, PID, ADR and ETX.
	else:
		data = response[7:len(response)-1]	# Ignore STX, TID, PID, ADR, CRC and ETX.

	#for b in data:
	#	print(b)

	print("".join(chr(i) for i in data))

# For NAK responses.
elif nak:
	pass

# This state should never happen.
else:
	
	pass

'''
print(tid)
print(pid)
print(adr)
print(crc)
'''
