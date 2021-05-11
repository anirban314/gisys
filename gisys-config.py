import importlib
import os
import subprocess
import sys

def checkDependencies():
	pypi_modules = {
		'psutil': False,
		'influxdb': False
	}
	bash_packages = {}

	print("\nChecking Dependencies...")

	for module in pypi_modules.keys():
		print(f"  {module} is ", end='')
		try:
			importlib.import_module(module)
		except:
			print("MISSING")
		else:
			print("installed")
			pypi_modules[module] = True
	pypi_installed = all(pypi_modules.values())

	for package in bash_packages.keys():
		print(f"  {package} is ", end='')
		if not subprocess.run(['which', package], capture_output=True).stdout:
			print("MISSING")
		else:
			print("installed")
			bash_packages[package] = True
	bash_installed = all(bash_packages.values())

	if not pypi_installed or not bash_installed:
		choice = input("\nDependencies Missing!\nInstall them now (yes/no)? ").lower()
		if choice=='y' or choice=='yes':
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
			install_command.append(package)
	
	if len(install_command) > 4:
		subprocess.run(install_command)


if __name__ == "__main__":
	if checkDependencies():
		print("\nAll dependencies installed. Proceeding...")
	else:
		print("\nDependencies not installed. Quitting!")
		sys.exit(1)