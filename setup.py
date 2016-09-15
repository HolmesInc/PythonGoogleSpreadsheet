try:
    from setuptools import setup, find_packages
except: 
    from distutils.core import setup

setup(
    name = "PythonGoogleSpreadsheet",
    version = '0.1',
    packages = find_packages(),
    requires = [],
    author = "Andrew Babenko",
    author_email = "andruonline11@gmail.com",
    description = "Simple framework to create Google Spreadsheet with python",
    long_description = open('README').read(),
    license = "LICENSE",
    keywords = "'google-spreadsheet', 'spreadsheet', 'create-google-spreadsheet'",
    url = "https://github.com/HolmesInc/gspreadsheet-py",
    include_package_data = True,
    classifiers=[
        "Development Status :: 1 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
    ],
)