import source
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 9):
    sys.exit('Sorry, Python < 3.9 is not supported')

with open('README.md') as f:
    long_description = f.read()

setup(
    name='ShopGoodwill',
    version=source.__version__,
    description='Python package for interfacing with ShopGoodwill.com ',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT License',
    author='Alec Barran',
    author_email='alexanderbarran@gmail.com',
    url='https://github.com/abarran02/ShopGoodwill',
    package_data={"source": ["search_request.json", "fallback_ua.txt"]},
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        'bs4',
        'requests',
        'requests-html'
    ]
)
