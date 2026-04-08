from setuptools import setup, find_packages

setup(
    name="polymarket-obfuscation-detector",
    version="0.1.0",
    description="Data analysis pipeline for detecting obfuscated trades on Polymarket",
    author="",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "web3>=6.0.0",
        "pandas>=2.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary",
        "py2neo>=4.10.0",
        "networkx>=3.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "httpx>=0.24.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0"],
        "dashboard": ["streamlit>=1.28.0"],
    },
)
