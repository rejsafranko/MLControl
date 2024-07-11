from setuptools import setup, find_packages

setup(
    name="mlcontrol",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "click==8.1.7",
        "google-api-python-client==2.134.0",
        "google-auth==2.30.0",
        "google-auth-oauthlib==1.2.0",
        "google-auth-httplib2==0.2.0",
        "vastai==0.2.5",
    ],
    entry_points={
        "console_scripts": [
            "mlcontrol=mlcontrol.cli:main",
        ],
    },
)
