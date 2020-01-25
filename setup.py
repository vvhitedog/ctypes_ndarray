from setuptools import setup

__version__ = '0.0.1'

setup(
    name='cndarray',
    version=__version__,
    author='Matt Gara',
    author_email='gara.matt@gmail.com',
    description='A simple interface to use numpy.ndarray in C++ or C code, allowing python to hold ownership at all times.',
    long_description='',
    install_requires=['numpy',],
    packages=['cndarray'],
    zip_safe=False,
)
