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

	print("CHECKING DEPENDENCIES...")

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
	
	return pypi_installed and bash_installed

if __name__ == "__main__":
	if not checkDependencies():
		print("\nQuitting!")
		sys.exit(1)