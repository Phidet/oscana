"""\
oscana / escape.py

--------------------------------------------------------------------------------

Author - Aditya Marathe
Email  - aditya.marathe.20@ucl.ac.uk

--------------------------------------------------------------------------------

ANSI escape codes for terminal text formatting (a.k.a. fancy printing).
"""

__all__ = []


class _Colour:
    def __init__(self, is_fg: bool) -> None:
        if is_fg:
            self._string = "\x1b[38;5;{0}m"
        else:
            self._string = "\x1b[48;5;{0}m"

    def __getitem__(self, colour_value: int) -> str:
        if (colour_value >= 0) and (colour_value <= 255):
            return self._string.format(colour_value)

        return ""


class Style:
    BD = "\x1b[1m"  # Bold
    DI = "\x1b[2m"  # Dim
    IT = "\x1b[3m"  # Italics
    UL = "\x1b[4m"  # Underline
    BL = "\x1b[5m"  # Blink
    RV = "\x1b[7m"  # Reverse
    HI = "\x1b[8m"  # Hide

    BD_R = "\x1b[21m"  # Bold Off
    DI_R = "\x1b[22m"  # Dim Off
    IT_R = "\x1b[23m"  # Italics Off
    UL_R = "\x1b[24m"  # Underline Off
    BL_R = "\x1b[25m"  # Blink Off
    RV_R = "\x1b[27m"  # Reverse Off
    HI_R = "\x1b[28m"  # Hide Off

    FG = _Colour(is_fg=True)  # Foreground Colour
    BG = _Colour(is_fg=False)  # Background Colour

    R = "\x1b[0m"  # Off / Reset
