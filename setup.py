import setuptools

with open('README.md') as rd:
    long_description = rd.read()

setuptools.setup(
    name='sheet_disk',
    version='0.0.0.1',
    author='Vinay Deshmukh',
    author_email='vinay.deshmukh.official@outlook.com',
    description='Use Google Sheets as a storage device!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vinay-deshmukh/Sheet-Disk',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)