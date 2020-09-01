from setuptools import setup
import sdist_upip

setup(cmdclass={"sdist": sdist_upip.sdist})
