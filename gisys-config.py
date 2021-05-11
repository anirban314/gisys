import importlib
import os
import subprocess
import sys


def check_script():
	if os.path.isfile('gisys.py'):
		return True
	else:
		return False


def check_modules():
	modules = {
		'psutil': False,
		'influxdb': False
	}

	print("\nChecking Python Modules...")
	for module in modules.keys():
		print(f"  {module} is ", end='')
		try:
			importlib.import_module(module)
		except:
			print("MISSING")
		else:
			print("installed")
			modules[module] = True

	if all(modules.values()):
		return True
	else:
		choice = input("\nModules MISSING! Install them now (yes/no)? ").lower()
		if choice=='y' or choice=='yes':
			install_modules(modules)
			return True
		else:
			return False


def install_modules(modules):
	command = ['sudo', 'pip', 'install']
	for module, installed in modules.items():
		if not installed:
			command.append(module)
	
	if len(command) > 3:
		subprocess.run(command)


if __name__ == "__main__":
	if check_script():
		print("Script gisys.py found.")
	else:
		print("Script gisys.py MISSING! Has it been moved or renamed?")
		choice = input("Do you want to continue anyway (yes/no)? ").lower()
		if choice=='n' or choice=='no':
			print("Quitting!")
			sys.exit(1)

	if check_modules():
		print("\nRequired modules are installed.")
	else:
		print("\nRequired modules are MISSING. Quitting!")
		sys.exit(1)