"""
Setup script for the table-allocator package.
"""

from setuptools import setup, find_packages

setup(
    name="table-allocator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "networkx>=2.8.0",
        "openpyxl>=3.0.0"
    ],
    author="Yuechen Zhu",
    description="A tool for optimizing table seating arrangements using simulated annealing",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
    ],
    package_data={
        'table_allocator': ['table_allocation_template.xlsx'],
    },
    entry_points={
        'console_scripts': [
            'table-allocator=table_allocator.main:main',
        ],
    },
)
