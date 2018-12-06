import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(
            os.path.join(here, 'sheet_disk', '__version__.py'),
            mode='r',
            encoding='utf-8'
         ) as f:
    exec(f.read(), about)

with open('README.md') as rd:
    long_description = rd.read()

install_requires = [
    'gspread>=3.0.1',
    'oauth2client>=4.1.3'
]

setuptools.setup(
    name=about['__title__'],
    version=about['__version__'],
    
    author=about['__author__'],
    author_email=about['__author_email__'],
    
    description=about['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    url='https://github.com/vinay-deshmukh/Sheet-Disk',
    
    packages=['sheet_disk'],

    # Specify dependencies
    install_requires=install_requires,

    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)