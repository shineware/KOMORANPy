import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="komoranPi",
    version="0.0.1",
    author="Junsoo Shin",
    author_email="ceo@shineware.co.kr",
    description="KOMORAN의 native python 버전입니다.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shineware/komoranpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)