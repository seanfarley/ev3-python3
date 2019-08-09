"""Module for defining specific EV3 errors."""


class DirCmdError(Exception):
    """Direct command reply error."""


class SysCmdError(Exception):
    """System command reply error."""
