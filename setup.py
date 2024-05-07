import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mikrotik-bt5",
    version="1.0.1",
    description="MikroTik BT5 scanner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Anrijs/MikroTik-BT5-Python",
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'bleak'
    ]
)
