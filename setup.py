# -*- coding: utf-8 -*-

from ansible_bundle import __version__
from setuptools import setup, find_packages

setup(name='ansible-bundle',
      version=__version__,
      description="Manage ansible role and modules versioned dependencies.",
      long_description=open('README.md').read(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
          'Operating System :: OS Independent',
          'Topic :: Utilities',
      ],
      keywords='ansible',
      author='David PG',
      author_email='david.3pwood@gmail.com',
      url='https://github.com/devopsysadmin/ansible-bundle',
      license='',
      packages=find_packages(exclude=['test']),
      entry_points={
          'console_scripts': [
             'ansible-bundle = ansible_bundle.main:main',
          ],
      },
      include_package_data=True,
      zip_safe=False,
      install_requires=[line for line in open('requirements.txt')],
)
