from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path

import ideascube

here = path.abspath(path.dirname(__file__))


# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Doc: http://pythonhosted.org/setuptools/setuptools.html#including-data-files.
setup(
    name='ideascube',
    version=ideascube.__version__,
    description=('This Django repository is the main application of the Ideas '
                 'Box server.'),
    long_description=long_description,
    url='https://framagit.org/ideascube/ideascube/',
    author='BSF IT Team',
    author_email='it@bibliosansfrontieres.org',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='ideasbox, koombook, offline content, humanitarian',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,  # Means all files reference in MANIFEST.in.
)
