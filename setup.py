# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from ansible_bundle import __version__
import sys

setup(name='ansible-bundle',
      version=__version__,
      description="Manage ansible role and modules versioned dependencies.",
      long_description=open('README.md').read(),
      keywords='ansible roles modules',
      author='David PG',
      author_email='david.3pwood@gmail.com',
      url='https://github.com/devopsysadmin/ansible-bundle',
      license='GPL v2',
      packages=find_packages(exclude=['test']),
      entry_points={
          'console_scripts': [
             'ansible-bundle = ansible_bundle.main:main',
          ],
      },
      include_package_data=True,
      zip_safe=False,
      install_requires=[line for line in open('requirements.txt')],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
          'Topic :: Utilities'
      ]
)
