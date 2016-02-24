import mir3.module

class Threshold(mir3.module.Module):
    def get_help(self):
        return """binarize the activation using a hard threshold"""
