import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clockify_idleless",
    version="0.0.1",
    author="Dário Marcelino",
    author_email="dario@appscot.com",
    description="Simple Clockify script to track active time",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dmarcelino/clockify-idleless",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=['python-dateutil>=2.8.0', 'requests>=2.22.0', 'wxPython>=4.0.6', 'XlsxWriter>=1.2.2'],
    entry_points = {
        'gui_scripts': ['clockify_idleless=clockify_idleless.idleless:main'],
        'console_scripts': ['clockify_to_workbook=clockify_idleless.clockify_to_workbook:main'],
    },
    include_package_data=True,
)
