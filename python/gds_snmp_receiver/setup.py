import os

from setuptools import find_packages, setup

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gds-snmp-receiver",
    version="0.1.0",
    description="Production-ready SNMP trap receiver with RabbitMQ integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GDS Team",
    author_email="gds@example.com",
    url="https://github.com/davidvupham/dbtools",
    packages=find_packages(exclude=["tests", "tests.*", "tools", "tools.*"]),
    install_requires=[
        "pysnmp>=4.4.12",
        "pika>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gds-snmp-receiver=gds_snmp_receiver.receiver:main",
        ],
    },
    python_requires=">=3.9",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="snmp trap receiver rabbitmq monitoring alerting gds",
    include_package_data=True,
    zip_safe=False,
)
