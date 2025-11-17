import os

from setuptools import find_packages, setup

# Read README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gds-liquibase",
    version="0.1.0",
    description="Liquibase wrapper for database change management CI/CD with GitHub Actions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GDS Team",
    author_email="gds@example.com",
    url="https://github.com/davidvupham/dbtools",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*", "docs"]),
    install_requires=[
        "gds-database>=0.1.0",
        "gds-postgres>=0.1.0",
        "gds-mssql>=0.1.0",
        "gds-mongodb>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
    },
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="liquibase database migration cicd github-actions schema gds",
    include_package_data=True,
    project_urls={
        "Homepage": "https://github.com/davidvupham/dbtools",
        "Repository": "https://github.com/davidvupham/dbtools",
        "Documentation": "https://github.com/davidvupham/dbtools/tree/main/gds_liquibase",
    },
)
