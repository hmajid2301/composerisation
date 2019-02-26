from setuptools import find_packages
from setuptools import setup

setup(
    name="composerisation",
    version="0.1.0-beta.1",
    description="A tool used to convert between Docker compose and Docker run.",
    author="Haseeb Majid",
    author_email="hello@haseebmajid.dev",
    keywords="Python",
    license="Apache License",
    url="https://gitlab.com/hmajid2301/composerisation",
    python_requires="~=3.6",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    zip_safe=False,
    include_package_data=True,
    install_requires=["click>=7.0", "pyyaml>=5.1"],
    entry_points={"console_scripts": ["composerisation = composerisation.cli:cli"]},
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
