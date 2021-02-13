import importlib
import subprocess

def checkDependencies():
	pypi_modules = {
		'psutil': False
	}
	bash_packages = {
		'awk': 'gawk',
		'netstat': 'net-tools',
		'ping': 'iputils-ping'
	}
	for module in pypi_modules.keys():
		try: importlib.import_module(module)
		except: pass
		else: pypi_modules[module] = True
	for package in bash_packages.keys():
		response = subprocess.run(['which', package], capture_output=True).stdout
		if response: bash_packages[package] = True

	print(pypi_modules)
	print(bash_packages)

if __name__ == "__main__":
	checkDependencies()