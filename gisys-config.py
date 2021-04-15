import sys
import importlib
import subprocess

def checkDependencies():
	pypi_modules = {
		'psutil': False,
		'influxdb': False
	}
	bash_packages = {
		'awk': False,
		'netstat': False,
		'ping': False
	}

	print("Checking Dependencies...\n")

	for module in pypi_modules.keys():
		print("  Python Module:\t{}  \t".format(module), end='')
		try:
			importlib.import_module(module)
		except:
			print("not installed")
		else:
			print("installed")
			pypi_modules[module] = True
	pypi_installed = all(pypi_modules.values())

	for package in bash_packages.keys():
		print("  Linux Package:\t{}     \t".format(package), end='')
		if not subprocess.run(['which', package], capture_output=True).stdout:
			print("not installed")
		else:
			print("installed")
			bash_packages[package] = True
	bash_installed = all(bash_packages.values())

	if not pypi_installed or not bash_installed:
		user_choice = input("\nDependencies Missing!\nDo you want to install them now (yes/no)? ").lower()
		if user_choice=='y' or user_choice=='yes':
			installDependencies(pypi_modules, bash_packages)
		else:
			return False
	
	return True

def installDependencies(pypi_modules, bash_packages):
	install_command = ['sudo', 'pip', 'install']
	for module, installed in pypi_modules.items():
		if not installed:
			install_command.append(module)
	if len(install_command) > 3:
		subprocess.run(install_command)
	
	install_command = ['sudo', 'apt-get', 'install', '--yes']
	for package, installed in bash_packages.items():
		if not installed:
			install_command.append(module)
	if len(install_command) > 4:
		subprocess.run(install_command)

if __name__ == "__main__":
	if not checkDependencies():
		print("\nQuitting!")
		sys.exit(1)