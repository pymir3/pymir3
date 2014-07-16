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

Known issues:
------
*ImportError: libmarsyas.so: cannot open shared object file: No such file or
directory*

Currently we use Marsyas to perform the conversion between a wav sound and its
spectrogram. As it may be hard to install and adds an unnecessary dependency, we
**will** implement the conversion inside the framework using only the common
python scientific libraries. For now, just make sure Marsyas is in the library
path (see ldconfig).
