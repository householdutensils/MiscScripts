SC-Enum - Shellcode Byte Enumerator

usage: sc-enum.py [-h] (-eb | -bc | -os | -l) shellcode

Shellcode Byte Enumerator

positional arguments:
  shellcode            Raw shellcode input (From bin or msfpayload etc)

optional arguments:
  -h, --help           show this help message and exit
  -eb, --enumbytes     Dispay a list of unique bytes in the input
  -bc, --badchars      Display a lit of potentially bad characters in the
                       input
  -os, --outputstring  Display the input as a string
  -l, --length         Display the length of the input







Usage Examples:
#python sc-enum.py -os "$(msfpayload windows/messagebox R)"


#python sc-enum.py -l "$(cat test.bin)"
