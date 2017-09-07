"""Unofficial wrapper for Google Sheets API, based on python 3.5+
See:
https://github.com/HolmesInc/PythonGoogleSpreadsheet
"""
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup

setup(
    name='PythonGoogleSpreadsheet',
    version='0.4.3',
    install_requires=[
        'apiclient',
        'argparse',
        'google',
        'google-api-python-client',
        'httplib2',
        'oauth2client',
        'pyasn1',
        'pyasn1-modules',
        'requests',
        'rsa',
        'simplejson',
        'six',
        'uritemplate',
        'urllib3',
    ],
    author="Andrew Babenko",
    author_email="andruonline11@gmail.com",
    description='Simple wrapper to create Google Spreadsheet, using Python 3+"',
    license="LICENSE",
    url='https://github.com/HolmesInc/PythonGoogleSpreadsheet',
    packages=['PythonGoogleSpreadsheet'],
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
    ],
)