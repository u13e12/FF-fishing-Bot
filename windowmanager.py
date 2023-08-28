import win32gui
import re

class WindowMgr:
    """ Encapsulates some calls to the winapi for window management"""
    def __init__ (self):
        """ Constructor """
        self._handle = None
    
    def find_window (self, class_name, window_name = None):
        """ Find a window by its class name """
        self._handle = win32gui.FindWindow(class_name, window_name)
        print(self._handle)
    
    def _window_enum_callback (self, hwnd, wildcard):
        """ Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
                self._handle = hwnd
    
    def find_window_wildcard(self, wildcard):
        """ Find a window whose title matches the wildcard reegex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """Put window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)

