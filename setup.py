from setuptools import setup

setup(
    name="mlcontrol",
    version="0.1",
    py_modules=["mlcontrol"],
    install_requires=[
        "click",
        "google-api-python-client",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
    ],
    entry_points="""
        [console_scripts]
        mlcontrol=mlcontrol:cli
    """,
)
