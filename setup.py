import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

test_deps = [
    'pytest',
    'flake8',
    'pylint',
    'mypy',
]
extras = {
    'test': test_deps
}

setuptools.setup(
    name="python-package-template",
    version="0.0.0",
    author="Ruben Lipperts",
    author_email="",
    description="Write a short description of the package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rlipperts/python_package_template",
    package_dir={'': 'src'},
    packages=['package_name'],
    package_data={'package_name': ['py.typed']},
    tests_require=test_deps,
    extras_require=extras,
    install_requires=[
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: https://pypi.org/classifiers/",
    ],
    python_requires='~=3.9',
)
