from distutils.core import setup

setup(
    name="renfepy",  # How you named your package folder (MyLib)
    packages=["renfepy"],  # Chose the same as "name"
    version="1.9",  # Start with a small number and increase it with every change you make
    license="MIT",  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description="A library to search for trains in renfe.com",  # Give a short description about your library
    author="Teko",  # Type in your name
    author_email="tekofxx@gmail.com",  # Type in your E-Mail
    url="https://github.com/Tekofx/renfepy",  # Provide either the link to your github or to your website
    download_url="https://github.com/Tekofx/renfepy/archive/refs/tags/v1.0.zip",  # I explain this later on
    keywords=[
        "renfe",
        "train",
    ],
    install_requires=[
        "selenium",
        "webdriver-manager",
        "rich",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",  # Again, pick a license
        "Programming Language :: Python :: 3",  # Specify which pyhton versions that you want to support
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={
        "console_scripts": [
            "renfepy=renfepy.__main__:main",
        ]
    },
)
