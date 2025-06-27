#!/usr/bin/env python3
"""
CodeVerse CLI - AI-Powered Development Assistant
Production-ready CLI tool for the CodeVerse platform
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="codeverse-cli",
    version="1.0.0",
    author="IBDA AI LTD",
    author_email="support@ibda.me",
    description="AI-powered development assistant with 54 specialized agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ibda-ai/codeverse-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "websocket-client>=1.6.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "cryptography>=41.0.0",
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
        "aiofiles>=23.0.0",
        "watchdog>=3.0.0",
        "gitpython>=3.1.0",
        "keyring>=24.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codeverse=codeverse_cli.main:main",
            "cv=codeverse_cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/ibda-ai/codeverse-cli/issues",
        "Documentation": "https://docs.codeverse.ibda.me",
        "Source": "https://github.com/ibda-ai/codeverse-cli",
        "Website": "https://codeverse.ibda.me",
    },
)