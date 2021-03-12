import setuptools
from distutils.core import setup

setup(
  name='steinbit',
  packages=['steinbit', 'steinbit.core'],
  version='0.1',
  description='Mineralogical data processing library',
  author='Rocktype',
  author_email='henrik@rocktype.com',
  url='https://github.com/Rocktype/steinbit',
  keywords=['steinbit', 'qemscan'],
  entry_points={
      'console_scripts': [
          'steinbit = steinbit.steinbit:main',
      ],
  },
  classifiers=[]
)
