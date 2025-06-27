import os
from setuptools import setup, find_packages

setup(
    name="codeverse-cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "httpx>=0.25.0",
        "websockets>=11.0",
        "rich>=13.0.0",
        "watchdog>=3.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "cryptography>=41.0.0",
        "asyncio>=3.4.3",
        "aiofiles>=23.0.0",
        "prompt_toolkit>=3.0.0",
        "pygments>=2.15.0",
    ],
    entry_points={
        "console_scripts": [
            "codeverse=codeverse_cli.main:cli",
            "cv=codeverse_cli.main:cli",  # Short alias
        ],
    },
    python_requires=">=3.8",
    author="IBDA AI LTD",
    author_email="contact@ibda.me",
    url="https://codeverse.ibda.me",
    description="Local CLI client for CodeVerse Terminal - AI-powered development platform by IBDA AI LTD",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
)