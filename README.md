pymir3
======

This framework intents to make research in music information retrieval (MIR)
easier to conduct and share, by separating the data processing in minimal
modules, focused on performing only one job, and by using common structures to
talk between modules.

The default behavior is to save every single intermediary result and to focus
on shell scripts to call specific tools of the framework, which implement the
data processing modules. This incurs an overhead because many files may be used,
so the user has the option of creating their own python programs to glue the
modules required. In this case, it's up to the user to save the states she/he
desires.

Installing:
------
To install, execute the following steps:

1) Download the release branch from the git repository:

git clone -b release https://github.com/pymir3/pymir3.git

2) CD to the pymir3 directory and execute setup.py:

cd pymir3

sudo pip install --upgrade .

3) To test, try switching to another directory and executing:

python

import mir3

If no error is displayed, pymir3 is installed!

Dependencies:
------
Before installing, you may have to install:

1) git

sudo apt-get install git

2) numpy, scipy and scikit-learn modules for python:

sudo apt-get install python-numpy

sudo apt-get install python-scipy

sudo apt-get install python-sklearn
