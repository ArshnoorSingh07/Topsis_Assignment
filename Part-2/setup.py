from setuptools import setup, find_packages

setup(
    name="topsis-arshnoor-102317161",
    version="1.0.0",
    author="Arshnoor Singh",
    packages=find_packages(),
    install_requires=["pandas","numpy","openpyxl"],
    entry_points={
        "console_scripts": [
            "topsis=topsis_arshnoor_102317161.topsis:main"
        ]
    },
)
