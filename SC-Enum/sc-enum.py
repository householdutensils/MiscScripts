#!/usr/bin/python


import argparse



parser = argparse.ArgumentParser( description="Shellcode Byte Enumerator" )

mutgroup = parser.add_mutually_exclusive_group(required=True)

mutgroup.add_argument("-eb", "--enumbytes", help="Dispay a list of unique bytes in the input", action="store_true")
mutgroup.add_argument("-bc", "--badchars", help="Display a lit of potentially bad characters in the input", action="store_true")
mutgroup.add_argument("-os", "--outputstring", help="Display the input as a string", action="store_true")
mutgroup.add_argument("-l", "--length", help="Display the length of the input", action="store_true")

parser.add_argument("shellcode", help="Raw shellcode input (From bin or msfpayload etc)")

args = parser.parse_args()

if args.shellcode is not None:
	
	#Drop the SC into a variable
	shellcode = args.shellcode

	#Decode and put in a list
	byte_list = list()
	for char in shellcode:
		byte_list.append(hex(ord(char))[2:])
	
	#Dump the SC as a string of bytes represented in ascii
	if args.outputstring:

		output_string = ""
		for byte in byte_list:
			#Add leading 0s to 0-9 and a-f
			if len(byte) is 1:
				byte = "0" + byte
			if len(byte) is 0:
				byte = "00"
			output_string += "\\x" + byte
		print output_string

	#Output a list of bytes that exist within the sc
	elif args.enumbytes:
		byte_set = set(byte_list)
		for byte in byte_set:
			if len(byte) is 1:
				byte = "0" + byte
			elif len(byte) is 0:
				byte = "00"
			print "\\x" + byte
	
	#Check for common badchars
	elif args.badchars:
		bad_chars = ["00","09", "0a", "0d", "22", "25", "26", "27", "2f", "3a", "3e", "3f", "FF", "5c", "0b", "1a", "0c", "04"]
		count = 1
		for byte in byte_list:
			for char in bad_chars:
				if len(byte) is 1:
					byte = "0" + byte
				elif len(byte) is 0:
					byte = "00"
				if byte == char:
					print byte + " at: " + str(count)
			count = count + 1
	elif args.length:
		print "Length: " + str(byte_list.__len__())
