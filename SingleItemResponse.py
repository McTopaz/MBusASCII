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
data = ""
error = 0
errorChr = ''
errorStr = ""
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

response = []	# This will contain the package specified from the arguments.
temp = None

# More than one argument. Parse the package into an array: 02 30 31 30 30 30 30 47 61 etc.
if len(sys.argv) > 2:

	# Iterate over all arguments containing the package.
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
			print("Error: '%s' is not a valid hexadecimal number."%(arg))
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
			print("Error: '%s' contains a non hexadecimal number."%(sys.argv[1]))
			sys.exit()
''''
# Print data in request	
for b in response:
	print(b)

print("")
'''	
# Verify that package contains ACK or NAK, TID, PID, ADR and ETX amount of bytes.
if len(response) < 8:
	print("Error: Invalid package length.")
	sys.exit()

isAck = response[0] == ack
isNak = response[0] == nak

# Check if package is positive (ACK) or negative (NAK).
if isAck == False and isNak == False:
	print("Error: Unknown package. Please check first byte in package.")
	sys.exit()
	
length = len(response)
isEtx = response[length-1] == etx

# Check package ends with ETX.
if isEtx == False:
	print("Error: Package doesn't end with ETX.")
	sys.exit()

tid = "%s%s"%(response[1] - 0x30, response[2] - 0x30)
tid = int(tid)
pid = "%s%s"%(response[3] - 0x30, response[4] - 0x30)
pid = int(pid)
adr = "%s%s"%(response[5] - 0x30, response[6] - 0x30)
adr = int(adr)
checkSumIncluded = pid == 0x01

# Verify that package contains STX, TID, PID = 1, ADR, CRC, and ETX amount of bytes.
if checkSumIncluded and len(response) < 10:
	print("Error: Invalid package length with checksum.")
	sys.exit()

# Calculate checksum.
crc = 0
if checkSumIncluded:
	crc = 0
	for b in response[1:len(response)-3]:
		#print("%02x : %s"%(b, b))
		crc += b
		
	crc = crc & 0xFF

okCrc = False
	
# Check checksum.
if checkSumIncluded:
	crcStr = "%02X"%(crc)
	okCrc = crcStr[0] == chr(response[length-3]) and crcStr[1] == chr(response[length-2])

if checkSumIncluded and okCrc == False:
	print("Error: Invalid checksum.")
	sys.exit()
	
# For ACK responses.
if isAck:
	if checkSumIncluded:
		data = response[7:len(response)-3]	# Get DATA from package, ignore STX, TID, PID, ADR and ETX.
	else:
		data = response[7:len(response)-1]	# Get DATA from package, ignore STX, TID, PID, ADR, CRC and ETX.

	data = "".join(chr(i) for i in data)

# For NAK responses.
elif isNak:
	error = response[7]
	errorChr = chr(error)
	
	if error == 0x43:	# 'C'
		errorStr = "Checksum fault"
	elif error == 0x44:	# 'D'
		errorStr = "Invalid data type. Data type must be string, VT_BSTR"
	elif error == 0x49:	# 'I'
		errorStr = "Unknown item ID"
	elif error == 0x4D:	# 'M'
		errorStr = "Timeout on MBusHub's master port"
	elif error == 0x4F:	# 'O'
		errorStr = "To many read items"
	elif error == 0x54:	# 'T'
		errorStr = "Timeout on MBusHub's slave port"
	elif error == 0x56:	# 'V'
		errorStr = "Validation, write value out of range"
	elif error == 0x58:	# 'X'
		errorStr = "Internal use for wrong multi-drop address"

# This state should never happen.
else:
	pass

# =====================
# === Print results ===
# =====================
	
# These are kept for output if needed"
#print("TID:\t%s\t(%x, %x)"%(tid, response[1], response[2]))
#print("PID:\t%s\t(%x, %x)"%(pid, response[3], response[4]))
#print("ADR:\t%s\t(%x, %x)"%(adr, response[5], response[6]))
#if checkSumIncluded:
#	print("CRC:\t%X\t(%x, %x)"%(crc, response[length-3], response[length-2]))

if isAck:
	#print("DATA:\t%s"%(data))
	print("[ACK] %s"%(data))
	
if isNak:
	#print("ERROR:\t%s\t(%X, %s)"%(errorChr, error, errorStr))
	print("[NAK] %s (%X, %s)"%(errorChr, error, errorStr))
