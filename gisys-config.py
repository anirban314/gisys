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

	for module in pypi_modules.keys():
		try: importlib.import_module(module)
		except: pass
		else: pypi_modules[module] = True

	for package in bash_packages.keys():
		if subprocess.run(['which', package], capture_output=True).stdout:
			bash_packages[package] = True

	pypi_installed = all(pypi_modules.values())
	bash_installed = all(bash_packages.values())

	if not pypi_installed:
		print("Please install the following Python modules:")
		for module, flag in pypi_modules.items():
			if not flag:
				print(" -> ", module)
	else:
		print("Required Python modules installed...")

	if not bash_installed:
		print("Please install the following Linux packages:")
		for package, flag in bash_packages.items():
			if not flag:
				print(" -> ", package)
	else:
		print("Required Linux packages installed...")

	return pypi_installed and bash_installed

if __name__ == "__main__":
	if not checkDependencies():
		print("Quitting!")
		sys.exit(1)