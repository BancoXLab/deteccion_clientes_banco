from setuptools import setup, find_packages

setup(
    name="banco-x-detector",
    version="0.1.0",
    packages=["scr"],
    install_requires=[
        "fastapi",
        "uvicorn",
        "prefect",
        "psutil",
        "pydantic"
    ],
)