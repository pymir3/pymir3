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
