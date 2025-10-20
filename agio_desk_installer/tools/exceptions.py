class WinFspIsRunning(Exception):

    def __init__(self):
        super().__init__("Please shut down WinFsp")

class HaveOldVersion(Exception):

    def __init__(self):
        super().__init__("Please shut down old agio drive")


class HaveLatestVersion(Exception):

    def __init__(self):
        super().__init__("You have latest agio drive, nothing to upgrade")

class WinFspNotInstalling(Exception):

    def __init__(self):
        super().__init__("WinFsp is not installed")