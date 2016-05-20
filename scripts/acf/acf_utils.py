import importlib

def extract_filename(filepath, ext=None):
    """
    This function returns the filename from a complete filepath including its extension.
    If ext is set to an extension it is removed from the filename.

    :param filepath:
    :type filepath: str
    :param ext:
    :type ext: str

    :return:
    :rtype: str
    """
    if ext[0] != ".":
        ext = "." + ext

    filename = filepath.split("/")[-1]
    if ext is not None:
        filename = filename.split(ext)[0]

    return filename


def behavior_factory(exp_param, step_key, behavior_key, step_prefix):

    # get the module filename from the parameter dictionary. The module file is expected to be named step_prefix_[behavior],
    # where behavior is the value of params[step_key][behavior]. For example, the bandwise
    # feature extractor is called fe_bandwise.py
    mod_name = (exp_param[step_key][behavior_key])

    try:
        module = importlib.import_module(step_prefix + mod_name)
    except ImportError:
        print "module %s_%s not found! Check the spelling of the %s key in the experiment file." \
              % (step_prefix, mod_name, step_key)
        exit(1)

    # instantiate the desired StepBehavior subclass. Notice that the subclass must be called
    # the same as the file, except for the step_prefix prefix. Check fe_bandwise.py for an example.
    mod_name = (exp_param[step_key][behavior_key]).capitalize()
    behavior = eval("module." + mod_name + behavior_key.capitalize())()

    # save the experiment file parameters so they can be used by the derived classes.
    behavior.params = exp_param
    behavior.name = mod_name

    return behavior