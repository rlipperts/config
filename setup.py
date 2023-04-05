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
    name="static_config_class",
    version="0.0.3",
    author="Ruben Lipperts",
    author_email="",
    description="Configuration manager for medium-sized projects (created for personal use)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rlipperts/config",
    package_dir={'': 'src'},
    packages=['static_config_class'],
    package_data={'static_config_class': ['py.typed']},
    tests_require=test_deps,
    extras_require=extras,
    install_requires=[
        'jsonschema'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Installation/Setup",
    ],
    python_requires='~=3.9',
)
