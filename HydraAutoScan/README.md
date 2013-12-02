usage: HydraAutoScan.py [-h] [-pr PROTOCOL] [-po PORT] [-v] [-nT] <br>
                        (-u USER | -U USERSFILE)<br>
                        (-p PASSWORD | -P PASSWORDSFILE)<br>
                        target<br>
<br>
Hydra/Nmap Auto Scan and Brute<br>
<br>
positional arguments:<br>
  target                Target(s) CIDR or Range.<br>
<br>
optional arguments:<br>
  -h, --help            show this help message and exit<br>
  -pr PROTOCOL, --protocol PROTOCOL
                        Protocol to test (Default: rdp)<br>
  -po PORT, --port PORT
                        Port to test (Default: 3389)<br>
  -v, --verbose         Increase verbosity of output<br>
  -nT, --notitle        Don't display the title<br>
  -u USER, --user USER  Username to test<br>
  -U USERSFILE, --usersfile USERSFILE
                        File containing usernames to test<br>
  -p PASSWORD, --password PASSWORD
                        Password to test<br>
  -P PASSWORDSFILE, --passwordsfile PASSWORDSFILE
                        File containing passwords to test<br>

