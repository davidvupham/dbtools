from setuptools import setup, find_packages
import os

# Read README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gds-vault",
    version="0.1.0",
    description=("HashiCorp Vault helper for secret retrieval via AppRole auth."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GDS Team",
    author_email="gds@example.com",
    url="",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    install_requires=["requests>=2.25.0"],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="vault hashicorp secrets approle gds",
    include_package_data=True,
)
