# coding: utf-8

"""
    Flywheel Bids Client
"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "flywheel-bids"
VERSION = "0.0.1"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["jsonschema==2.6.0", "flywheel-sdk >= 2.1.1"]

setup(
    name=NAME,
    version=VERSION,
    description="Flywheel BIDS Client",
    author_email="support@flywheel.io",
    url="",
    keywords=["Flywheel", "flywheel", "BIDS", "SDK"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('templates', ['templates/bids-v1.json'])
    ],
    license="MIT",
    project_urls={
        'Source': 'https://github.com/flywheel-io/bids-client'
    },
    long_description="""\
    Flywheel BIDS Client
    ============

    An SDK for interacting with BIDS formatted data on a Flywheel instance. 

    """,
    entry_points = {
        'console_scripts': [
            'curate_bids=flywheel_bids.curate_bids:main',
            'export_bids=flywheel_bids.export_bids:main',
            'upload_bids=flywheel_bids.upload_bids:main'
        ]
    }
)
