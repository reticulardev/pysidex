#!/usr/bin/env python3
import math
import os
import platform
import subprocess
import sys
from enum import Enum

from PySide6 import QtGui, QtWidgets
from __feature__ import snake_case

from PySideX.tools.desktop_entry_parse import DesktopFile


SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SRC_DIR)


class EnvSettings(object):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        self.__kwinrc = self.rc_file_content(
            os.path.join(os.environ['HOME'], '.config', 'kwinrc'))
        self.__breezerc = self.rc_file_content(
            os.path.join(os.environ['HOME'], '.config', 'breezerc'))

    @property
    def breeze_rc_content(self) -> dict:
        """..."""
        return self.__breezerc

    @staticmethod
    def command_output(command_args: list) -> str | None:
        """..."""
        # ['ls', '-l']
        try:
            command = subprocess.Popen(
                command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = command.communicate()
        except ValueError as er:
            print(er)
            print(f'Error in command args: "{command_args}"')
        else:
            return stdout.decode() if not stderr.decode() else None

    @staticmethod
    def context_menu_border_color(window_is_dark: bool) -> tuple:
        """RGBA tuple: (127, 127, 127, 0.8)"""
        if window_is_dark:
            return 127, 127, 127, 0.8
        return 127, 127, 127, 0.8

    @staticmethod
    def context_menu_padding() -> int:
        """..."""
        return 4

    @staticmethod
    def context_menu_separator_margin() -> tuple:
        """Left, top, right and bottom margins tuple"""
        return 0, 4, 0, 4

    @staticmethod
    def context_menu_spacing() -> int:
        """..."""
        return 0

    @staticmethod
    def control_button_order() -> tuple:
        """XAI M -> (2, 1, 0), (3,)

        Close     Max       Min       Icon      Above all
        X = 2     A = 1     I = 0     M = 3     F = 4

        (2, 1, 0), (3,) -> [Close Max Min ............. Icon]
        """
        return (2, 1, 0), (3,)

    @staticmethod
    def control_button_style(*args, **kwargs) -> str:
        """..."""
        return (
            'QControlButton {'
            '  border: 0px;'
            '  border-radius: 10px;'
            '  padding: 1px;'
            '  background-color: rgba(127, 127, 127, 0.2);'
            '}'
            'QControlButton:hover {'
            '  background-color: rgba(200, 200, 200, 0.2);'
            '}')

    @property
    def kwin_rc_content(self) -> dict:
        """..."""
        return self.__kwinrc

    @staticmethod
    def rc_file_content(file_url: str) -> dict:
        """..."""
        if os.path.isfile(file_url):
            return DesktopFile(url=file_url).content
        return {}

    def use_global_menu(self) -> bool:
        """..."""
        top, key = '[Windows]', 'BorderlessMaximizedWindows'
        if top in self.__kwinrc and key in self.__kwinrc[top]:
            return True if self.__kwinrc[top][key] == 'true' else False

    @staticmethod
    def window_border_radius() -> tuple:
        """..."""
        return 5, 5, 5, 5


class EnvSettingsPlasma(EnvSettings):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)

    @staticmethod
    def context_menu_border_color(window_is_dark: bool) -> tuple:
        """RGBA tuple: (127, 127, 127, 0.8)"""
        if window_is_dark:
            return 127, 127, 127, 0.8
        return 127, 127, 127, 0.8

    @staticmethod
    def context_menu_padding() -> int:
        """..."""
        return 4

    @staticmethod
    def context_menu_separator_margin() -> tuple:
        """Left, top, right and bottom margins tuple"""
        return 8, 4, 8, 4

    @staticmethod
    def context_menu_spacing() -> int:
        """..."""
        return 0

    def control_button_order(self) -> tuple:
        """..."""
        right_buttons = 'IAX'  # X = close, A = max, I = min
        left_buttons = 'M'  # M = icon, F = above all

        top = '[org.kde.kdecoration2]'
        key_left, key_right = 'ButtonsOnLeft', 'ButtonsOnRight'
        if top in self.kwin_rc_content:
            if key_left in self.kwin_rc_content[top]:
                left_buttons = self.kwin_rc_content[top][key_left]

            if key_right in self.kwin_rc_content[top]:
                right_buttons = self.kwin_rc_content[top][key_right]

        d = {'X': 2, 'A': 1, 'I': 0, 'M': 3}
        return tuple(
            d[x] for x in left_buttons
            if x == 'X' or x == 'A' or x == 'I' or x == 'M'), tuple(
            d[x] for x in right_buttons
            if x == 'X' or x == 'A' or x == 'I' or x == 'M')

    def control_button_style(
            self, window_is_dark: bool,
            button_name: str,
            button_state: str) -> str:
        """..."""
        # window_is_dark: True or False
        # button_name: 'minimize', 'maximize', 'restore' or 'close'
        # button_state: 'normal', 'hover', 'inactive'

        if button_name == 'minimize':
            button_name = 'go-down'
        elif button_name == 'maximize':
            button_name = 'go-up'
        elif button_name == 'restore':
            button_name = 'window-restore'
        else:
            button_name = 'window-close-b'
            top, key = '[Common]', 'OutlineCloseButton'
            if (top in self.breeze_rc_content and
                    key in self.breeze_rc_content[top]):
                if self.breeze_rc_content[top][key] == 'true':
                    button_name = 'window-close'

        if button_state == 'hover':
            if button_name == 'window-close-b':
                button_name = 'window-close'
            button_name += '-hover'
        if button_state == 'inactive':
            button_name += '-inactive'

        if window_is_dark:
            button_name += '-symbolic'

        url_icon = os.path.join(
            SRC_DIR, 'kde-breeze-control-buttons', button_name + '.svg')
        return (
            # f'background: url({url_icon}) top center no-repeat;'
            'QControlButton {'
            f'background: url({url_icon}) center no-repeat;'
            '}')

    def use_global_menu(self) -> bool:
        """..."""
        top, key = '[Windows]', 'BorderlessMaximizedWindows'
        if top in self.kwin_rc_content and key in self.kwin_rc_content[top]:
            return True if self.kwin_rc_content[top][key] == 'true' else False

    @staticmethod
    def window_border_radius() -> tuple:
        """..."""
        return 4, 4, 0, 0


class EnvSettingsGnome(EnvSettings):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)

    @staticmethod
    def context_menu_border_color(window_is_dark: bool) -> tuple:
        """RGBA tuple: (127, 127, 127, 0.8)"""
        if window_is_dark:
            return 127, 127, 127, 0.8
        return 127, 127, 127, 0.8

    @staticmethod
    def context_menu_padding() -> int:
        """..."""
        return 6

    @staticmethod
    def context_menu_separator_margin() -> tuple:
        """Left, top, right and bottom margins tuple"""
        return 0, 6, 0, 6

    @staticmethod
    def context_menu_spacing() -> int:
        """..."""
        return 0

    @staticmethod
    def control_button_order() -> tuple:
        """XAI M -> (2, 1, 0), (3,)

        Close     Max       Min       Icon      Above all
        X = 2     A = 1     I = 0     M = 3     F = 4

        (2, 1, 0), (3,) -> [Close Max Min ............. Icon]
        """
        # TODO: Auto
        return (3,), (0, 1, 2)

    @staticmethod
    def control_button_style(*args, **kwargs) -> str:
        """..."""
        return (
            'QControlButton {'
            '  border: 0px;'
            '  border-radius: 10px;'
            '  padding: 1px;'
            '  background-color: rgba(127, 127, 127, 0.2);'
            '}'
            'QControlButton:hover {'
            '  background-color: rgba(200, 200, 200, 0.2);'
            '}')

    def use_global_menu(self) -> bool:
        """..."""
        return False

    @staticmethod
    def window_border_radius() -> tuple:
        """..."""
        return 10, 10, 10, 10


class EnvSettingsCinnamon(EnvSettingsGnome):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)


class EnvSettingsXFCE(EnvSettingsGnome):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)


class EnvSettingsMac(EnvSettings):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)


class EnvSettingsWindows11(EnvSettings):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)


class EnvSettingsWindows10(EnvSettingsWindows11):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)


class EnvSettingsWindows7(EnvSettingsWindows11):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)


class PlatformSettings(object):
    """..."""
    OperationalSystem = Enum(
        'OperationalSystem', ['UNKNOWN', 'LINUX', 'BSD', 'MAC', 'WINDOWS'])
    DesktopEnvironment = Enum(
        'DesktopEnvironment',
        ['UNKNOWN', 'PLASMA', 'GNOME', 'CINNAMON', 'XFCE', 'MAC', 'WINDOWS_7',
         'WINDOWS_10', 'WINDOWS_11'])

    def __init__(self, platform_integration: bool = True):
        """..."""
        self.__platform_integration = platform_integration
        self.__operational_system = self.__get_operational_system()
        self.__desktop_environment = self.__get_desktop_environment()
        self.__env_settings = self.__get_env_settings()

    @staticmethod
    def is_dark(widget: QtWidgets) -> bool:
        color = widget.palette().color(QtGui.QPalette.Window)
        r, g, b = (color.red(), color.green(), color.blue())
        hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
        return False if hsp > 127.5 else True

    @property
    def desktop_environment(self) -> DesktopEnvironment:
        """..."""
        return self.__desktop_environment

    @property
    def operational_system(self) -> OperationalSystem:
        """..."""
        return self.__operational_system

    def context_menu_border_color(self, window_is_dark: bool) -> tuple:
        """..."""
        return self.__env_settings.context_menu_border_color(window_is_dark)

    def context_menu_padding(self) -> int:
        """..."""
        return self.__env_settings.context_menu_padding()

    def context_menu_separator_margin(self) -> tuple:
        """..."""
        return self.__env_settings.context_menu_separator_margin()

    def context_menu_spacing(self) -> int:
        """..."""
        return self.__env_settings.context_menu_spacing()

    def window_control_button_style(
            self, window_is_dark: bool,
            button_name: str,
            button_state: str) -> str | None:
        """Control button style

        :param window_is_dark: True or False
        :param button_name: 'minimize', 'maximize', 'restore' or 'close'
        :param button_state: 'normal', 'hover', 'inactive'
        """
        return self.__env_settings.control_button_style(
            window_is_dark, button_name, button_state)

    def window_control_button_order(self) -> tuple | None:
        """..."""
        return self.__env_settings.control_button_order()

    def window_border_radius(self) -> tuple | None:
        """..."""
        return self.__env_settings.window_border_radius()

    def window_use_global_menu(self) -> bool:
        """..."""
        return self.__env_settings.use_global_menu()

    def __get_desktop_environment(self) -> DesktopEnvironment:
        # ...
        if self.__platform_integration:
            if self.__operational_system == self.OperationalSystem.LINUX:
                if (os.environ['DESKTOP_SESSION'] == 'plasma' or
                        os.environ['XDG_SESSION_DESKTOP'] == 'KDE' or
                        os.environ['XDG_CURRENT_DESKTOP'] == 'KDE'):
                    return self.DesktopEnvironment.PLASMA

                # TODO: Gnome, Cinnamon, XFCE
                return self.DesktopEnvironment.GNOME

            elif self.__operational_system == self.OperationalSystem.WINDOWS:
                if platform.release() == '10':
                    return self.DesktopEnvironment.WINDOWS_10

                elif platform.release() == '11':
                    return self.DesktopEnvironment.WINDOWS_11

                return self.DesktopEnvironment.WINDOWS_7

            elif self.__operational_system == self.OperationalSystem.MAC:
                return self.DesktopEnvironment.MAC

            elif self.__operational_system == self.OperationalSystem.BSD:
                return self.DesktopEnvironment.BSD

        return self.DesktopEnvironment.UNKNOWN

    def __get_env_settings(self) -> EnvSettings | None:
        """..."""
        if self.__platform_integration:
            if self.__operational_system == self.OperationalSystem.LINUX:

                if (self.__desktop_environment ==
                        self.DesktopEnvironment.PLASMA):
                    return EnvSettingsPlasma()

                if (self.__desktop_environment ==
                        self.DesktopEnvironment.CINNAMON):
                    return EnvSettingsCinnamon()

                if (self.__desktop_environment ==
                        self.DesktopEnvironment.XFCE):
                    return EnvSettingsXFCE()

                return EnvSettingsGnome()

            if self.__operational_system == self.OperationalSystem.MAC:
                return EnvSettingsMac()

            if self.__operational_system == self.OperationalSystem.WINDOWS:

                if (self.__desktop_environment ==
                        self.DesktopEnvironment.WINDOWS_7):
                    return EnvSettingsWindows7()

                if (self.__desktop_environment ==
                        self.DesktopEnvironment.WINDOWS_10):
                    return EnvSettingsWindows10()
                
                return EnvSettingsWindows11()

        return EnvSettings()

    def __get_operational_system(self) -> OperationalSystem:
        # Win config path: $HOME + AppData\Roaming\
        # Linux config path: $HOME + .config
        if os.name == 'posix':
            if platform.system() == 'Linux':
                return self.OperationalSystem.LINUX

            elif platform.system() == 'Darwin':
                return self.OperationalSystem.MAC

        elif os.name == 'nt' and platform.system() == 'Windows':
            return self.OperationalSystem.WINDOWS


class StyleBuilder(object):
    """..."""
    def __init__(self, main_window: QtWidgets.QMainWindow) -> None:
        """..."""
        self.__main_window = main_window
        self.__src = os.path.dirname(os.path.abspath(__file__))
        self.__bd_radius = (
            self.__main_window.platform_settings().window_border_radius())

        self.__bg_color = self.__main_window.palette().color(
            QtGui.QPalette.Window)
        
        self.__bg_accent_color = QtGui.QColor(
            QtGui.QPalette().color(
                QtGui.QPalette.Active, QtGui.QPalette.Highlight))
        
        self.__bd_color = self.__main_window.palette().color(
            QtGui.QPalette.Window.Mid)
        # https://doc.qt.io/qtforpython-6/PySide6/QtGui/
        # QPalette.html#PySide6.QtGui.PySide6.QtGui.QPalette.ColorGroup

    def build_style(self) -> str:
        """..."""
        if self.__main_window.is_decorated():
            main_window_style = (
                '#QApplicationWindow {'
                'background-color: rgba('
                f'{self.__bg_color.red()}, {self.__bg_color.green()}, '
                f'{self.__bg_color.blue()}, {self.__bg_color.alpha_f()});'
                '}')
        else:
            main_window_style = (
                '#QApplicationWindow {'
                'background-color: rgba('
                f'{self.__bg_color.red()}, {self.__bg_color.green()}, '
                f'{self.__bg_color.blue()}, {self.__bg_color.alpha_f()});'
                'border: 1px solid rgba('
                f'{self.__bd_color.red()}, {self.__bd_color.green()}, '
                f'{self.__bd_color.blue()}, {self.__bd_color.alpha_f()});'
                f'border-top-left-radius: {self.__bd_radius[0]};'
                f'border-top-right-radius: {self.__bd_radius[1]};'
                f'border-bottom-right-radius: {self.__bd_radius[2]};'
                f'border-bottom-left-radius: {self.__bd_radius[3]};'
                '}')

        main_window_style += (
            '#QQuickContextMenu {'
            'background-color: rgba('
            f'{self.__bg_color.red()}, {self.__bg_color.green()}, '
            f'{self.__bg_color.blue()}, 0.9);'
            'border: 1px solid rgba('
            f'{self.__bd_color.red()}, {self.__bd_color.green()}, '
            f'{self.__bd_color.blue()}, {self.__bd_color.alpha_f()});'
            f'border-radius: {self.__bd_radius[0]}px;'
            '}'
            'QQuickContextMenuButton {'
            'background: transparent;'
            'padding: 2px;'
            'border: 1px solid rgba(0, 0, 0, 0.0);'
            'border-radius: 3px;'
            '}'
            'QQuickContextMenuButton:hover {'
            'background-color: rgba('
            f'{self.__bg_accent_color.red()}, '
            f'{self.__bg_accent_color.green()}, '
            f'{self.__bg_accent_color.blue()}, 0.2);'
            'padding: 2px;'
            'border: 1px solid rgba('
            f'{self.__bg_accent_color.red()}, '
            f'{self.__bg_accent_color.green()}, '
            f'{self.__bg_accent_color.blue()}, 0.9);'
            'border-radius: 3px;'
            '}')

        style_path = os.path.join(self.__src, 'static', 'style.qss')
        with open(style_path, 'r') as style_qss_file:
            style = style_qss_file.read()

        return main_window_style + style

    @staticmethod
    def adapt_to_fullscreen(style: str) -> str:
        # ...
        central_widget = [
            x for x in style.split('}') if
            x.strip().startswith(f'#QApplicationWindow')][-1]

        return style.replace(
            central_widget, central_widget + 'border-radius: 0px; border: 0px')
