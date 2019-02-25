from setuptools import find_packages
from setuptools import setup

setup(name='docker-run-compose-converter',
      version='0.1.0',
      description='Audit report',
      author='Haseeb Majid',
      author_email='me@haseebmajid.com',
      keywords='Python',
      license='Apache License',
      url='https://gitlab.com/hmajid2301/docker-run-compose-converter',
      python_requires='~=3.6',
      package_dir={'': 'src'},
      packages=find_packages(where='src'),
      zip_safe=False,
      include_package_data=True,
      install_requires=[
          "click==7.0",
      ],
      entry_points={
          'console_scripts': [
              'audit_report = audit_report.cli:cli'
          ]
      },
      classifiers=[
          'Programming Language :: Python',
          'License :: OSI Approved :: SKY License',
          'Intended Audience :: Developers',
          'Intended Audience :: SysAdmins',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ]
      )
