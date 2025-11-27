from setuptools import setup, find_packages

setup(
    name="banco-x-detector",
    version="0.1.0",
    packages=find_packages(exclude=("tests", "docs", "notebooks", "experiments", "deprecated")),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "prefect>=2.14.0",
        "psutil>=5.9.0",
        "pydantic>=2.0.0",
        "pandas>=1.5.0",
        "scikit-learn>=1.3.0",
        "xgboost>=2.0.0",
        "imbalanced-learn>=0.11.0",
        "sqlalchemy>=2.0.0",
        "pymysql>=1.1.0",
        "python-dotenv>=1.0.0",
        "mlflow>=2.10.0",
    ],
    python_requires=">=3.9",
    author="BancoX",
    description="Cliente detector model for BancoX",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)