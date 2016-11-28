from setuptools import setup, find_packages
setup(
    name = "pymir3",
    version = "1.0",
    #package_dir = {'': 'mir3'}
    packages = find_packages(),
    scripts = ['pymir3-cl.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    # install_requires = ['docutils>=0.3'],

    #package_data = {
        # If any package contains *.txt or *.rst files, include them:
    #    '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
    #    'hello': ['*.msg'],
    #},

    exclude_package_data = {'': ['.gitignore', '.git/*']},


    # metadata for upload to PyPI
    author = "Tiago F. Tavares, Conrado Miranda",
    author_email = "tavares@dca.fee.unicamp.br",
    description = "Python utilities for Music Information Retrieval applications",
    license = "MIT License",
    keywords = "music information retrieval, mir, prototyping",
    url = "https://github.com/pymir3/pymir3",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)

