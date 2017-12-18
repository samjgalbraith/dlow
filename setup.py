from distutils.core import setup
from setuptools import find_packages

setup(
    name='dlow',
    version='0.3.3',
    packages=find_packages(),
    install_requires=['boto3>=1.0.0'],
    url='https://github.com/theflyingnerd/dlow',
    license='MIT',
    author='Sam Galbraith',
    author_email='sam.j.galbraith@gmail.com',
    description='A library for downloading an S3 folder recursively and unzipping its contents. Extensible to other sources and post-processes.',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Topic :: System :: Archiving',
        'Topic :: System :: Filesystems',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
)
