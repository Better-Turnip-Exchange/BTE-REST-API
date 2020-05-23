import setuptools

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bteapi",
    version="0.0.1",
    author="Zagan",
    description="turnip.exchange companion api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Better-Turnip-Exchange/BTE-REST-API",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    python_requires=">=3.6",
)
