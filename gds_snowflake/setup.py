"""
Setup configuration for gds_snowflake package
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_file(filename):
    """Read file contents."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='gds-snowflake',
    version='1.0.0',
    author='GDS Team',
    author_email='gds@example.com',
    description='A Python package for Snowflake connection management and replication monitoring',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/davidvupham/snowflake',
    packages=find_packages(where='.', exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'snowflake-connector-python>=3.0.0',
        'croniter>=1.3.0',
        'gds-vault>=0.1.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-mock>=3.10.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'pylint>=2.17.0',
            'mypy>=1.0.0',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['py.typed'],
    },
    keywords='snowflake database replication monitoring failover gds',
    project_urls={
        'Bug Reports': 'https://github.com/davidvupham/snowflake/issues',
        'Source': 'https://github.com/davidvupham/snowflake',
        'Documentation': 'https://github.com/davidvupham/snowflake/tree/main/gds_snowflake',
    },
)
