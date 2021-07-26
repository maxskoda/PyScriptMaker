from setuptools import setup, find_packages
import pathlib
here = pathlib.Path(__file__).parent.resolve()

setup(
    name='MaxSkript',
    version='0.1.0',
    packages=find_packages(include=['MaxSkript', 'MaxSkript.*']),
    url='',
    license='',
    author='Maximilian Skoda',
    author_email='maximilian.skoda@stfc.ac.uk',
    description='Script generator neutron experiments at ISIS'
)
