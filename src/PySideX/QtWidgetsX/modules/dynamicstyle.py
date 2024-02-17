#!/usr/bin/env python3
import logging
import os
import re
import sys

from PySide6 import QtGui, QtWidgets
from __feature__ import snake_case

import PySideX.QtWidgetsX.modules.color as color
from PySideX.QtWidgetsX.modules.envsettings import GuiEnv

SRC_DIR = os.path.dirname(os.path.abspath(__file__))


class StyleParser(object):
    """..."""
    def __init__(self, style_sheet: str) -> None:
        """..."""
        self.__stylesheet_arg = style_sheet
        self.__scopes = self.__split_widgets_scops()
        self.__stylesheet = None

    def scopes(self) -> dict:
        """..."""
        return self.__scopes

    def set_style_sheet(self, style_sheet: str) -> None:
        """..."""
        self.__stylesheet_arg = style_sheet
        self.__scopes = self.__split_widgets_scops()
        self.__stylesheet = None

    def style_sheet(self, update: bool = False) -> str:
        """..."""
        if not self.__stylesheet or update:
            self.__stylesheet = ''
            for scope_key, scope_value in self.__scopes.items():
                self.__stylesheet += scope_key + ' {' + scope_value + '} '
        return self.__stylesheet

    def widget_scope(
            self, widget_class_name: str, propertie: str = None) -> str:
        """..."""
        for scope_key, scope_value in self.__scopes.items():
            if not propertie:
                if widget_class_name == scope_key:
                    return scope_value
            else:
                if widget_class_name in scope_key and propertie in scope_key:
                    return scope_value
        return ''

    def __split_widgets_scops(self) -> dict:
        # ...
        cleanstyle = re.sub(r'(/\*.+\*/)|(^#.+$)', r'', self.__stylesheet_arg)

        scopes = {}
        all_scopes = cleanstyle.replace('\n', '').replace('  ', ' ').split('}')
        for scope in all_scopes:
            if '{' in scope:
                scope_keys, scope_value = scope.split('{')

                for scope_key in scope_keys.split(','):
                    scope_key = self.__clean_key(scope_key)
                    if scope_key and scope_key in scopes:
                        scope_value = self.__join_duplicate_values(
                            scope_value, scopes[scope_key])

                    scopes[scope_key] = self.__clean_value(scope_value)
        return scopes

    def __join_duplicate_values(self, new_value: str, old: str) -> str:
        # ...
        new_values = [self.__clean_value(x) for x in new_value.split(';') if x]
        old_values = [self.__clean_value(x) for x in old.split(';') if x]
        new_keys = [self.__clean_key(self.__clean_value(x).split(':')[0])
                    for x in new_value.split(';') if x]

        for old_value in old_values:
            old_key = self.__clean_key(old_value.split(':')[0])
            if old_key not in new_keys:
                new_values.insert(0, old_value)

        return ' '.join(new_values)

    @staticmethod
    def __clean_value(value: str) -> str:
        # ...
        return value.strip().strip(';').strip().replace(',', ', ').replace(
            ' ;', ';').replace(';', '; ').replace('  ', ' ').strip().replace(
            ';;', ';') + ';'

    @staticmethod
    def __clean_key(value: str) -> str:
        # ...
        return value.lstrip('#').replace(' ', '').strip()

    def __str__(self) -> str:
        return 'StyleParser'

    def __repr__(self) -> str:
        return 'StyleParser(object)'


class DynamicStyle(object):
    """..."""
    def __init__(self, toplevel: QtWidgets.QMainWindow) -> None:
        """..."""
        self.__toplevel = toplevel

        self.__env = GuiEnv(
            self.__toplevel.platform().operational_system(),
            self.__toplevel.platform().desktop_environment(),
            self.__toplevel.follow_platform())

        self.__win_is_dark = self.__env.settings(
            ).window_is_dark()
        self.__win_background_color = self.__env.settings(
            ).window_background_color()
        self.__win_border_radius = self.__env.settings(
            ).window_border_radius()
        self.__win_border_color = self.__env.settings(
            ).window_border_color()

        self.__ctxmenu_margin = self.__env.settings(
            ).contextmenu_margin()
        self.__ctxmenu_padding = self.__env.settings(
            ).contextmenu_padding()
        self.__ctxmenu_background_color = self.__env.settings(
            ).contextmenu_background_color()
        self.__ctxmenu_border_color = self.__env.settings(
            ).contextmenu_border_color()
        self.__ctxmenu_border_radius = self.__env.settings(
            ).contextmenu_border_radius()

        self.__ctxmenu_separator_margin = self.__env.settings(
            ).contextmenu_separator_margin()
        self.__ctxmenu_separator_color = self.__env.settings(
            ).contextmenu_separator_color()

        self.__ctxmenubutton_background_hover_color = self.__env.settings(
            ).contextmenubutton_background_hover_color()
        self.__ctxmenubutton_border_hover_color = self.__env.settings(
            ).contextmenubutton_border_hover_color()
        self.__ctxmenubutton_border_radius = self.__env.settings(
            ).contextmenubutton_border_radius()

        self.__ctxtmenubutton_label_hover_color = self.__env.settings(
            ).contextmenubutton_label_hover_color()

        self.__ctxtmenubutton_shortcut_label_hover_color = self.__env.settings(
            ).contextmenubutton_shortcut_label_color()

        self.__ctxmenubutton_padding = self.__env.settings(
            ).contextmenubutton_padding()

    def build_style(self) -> str:
        """..."""
        if self.__toplevel.is_server_side_decorated():
            window_style = (
                'QMainWindow {'
                'background-color: rgba('
                f'{self.__win_background_color.red()},'
                f'{self.__win_background_color.green()},'
                f'{self.__win_background_color.blue()},'
                f'{self.__win_background_color.alpha_f()});'
                '}')
        else:
            window_style = (
                'QMainWindow {'
                'background-color: rgba('
                f'{self.__win_background_color.red()},'
                f'{self.__win_background_color.green()},'
                f'{self.__win_background_color.blue()},'
                f'{self.__win_background_color.alpha_f()});'
                'border: 1px solid rgba('
                f'{self.__win_border_color.red()},'
                f'{self.__win_border_color.green()},'
                f'{self.__win_border_color.blue()},'
                f'{self.__win_border_color.alpha()});'
                f'border-top-left-radius: {self.__win_border_radius[0]};'
                f'border-top-right-radius: {self.__win_border_radius[1]};'
                f'border-bottom-right-radius: {self.__win_border_radius[2]};'
                f'border-bottom-left-radius: {self.__win_border_radius[3]};'
                '}')

        context_menu_style = (
            'QQuickContextMenu {'
            'margin:'
            f' {self.__ctxmenu_margin[0]}px'
            f' {self.__ctxmenu_margin[1]}px'
            f' {self.__ctxmenu_margin[2]}px'
            f' {self.__ctxmenu_margin[3]}px;'
            'padding:'
            f' {self.__ctxmenu_padding[0]}px'
            f' {self.__ctxmenu_padding[1]}px'
            f' {self.__ctxmenu_padding[2]}px'
            f' {self.__ctxmenu_padding[3]}px;'
            'background-color: rgba('
            f' {self.__ctxmenu_background_color.red()},'
            f' {self.__ctxmenu_background_color.green()},'
            f' {self.__ctxmenu_background_color.blue()},'
            f' {self.__ctxmenu_background_color.alpha()});'
            'border: 1px solid rgba('
            f' {self.__ctxmenu_border_color.red()},'
            f' {self.__ctxmenu_border_color.green()},'
            f' {self.__ctxmenu_border_color.blue()},'
            f' {self.__ctxmenu_border_color.alpha_f()});'
            f'border-radius: {self.__ctxmenu_border_radius}px;'
            '}'
            'QQuickContextMenuSeparator {'
            'margin:'
            f' {self.__ctxmenu_separator_margin[0]}px'
            f' {self.__ctxmenu_separator_margin[1]}px'
            f' {self.__ctxmenu_separator_margin[2]}px'
            f' {self.__ctxmenu_separator_margin[3]}px;'
            '}'
            'QQuickContextMenuSeparatorLine {'
            'color: rgba('
            f' {self.__ctxmenu_separator_color.red()},'
            f' {self.__ctxmenu_separator_color.green()},'
            f' {self.__ctxmenu_separator_color.blue()},'
            f' {self.__ctxmenu_separator_color.alpha()});'
            '}'
            'QQuickContextMenuButton {'
            'background: transparent;'
            'padding:'
            f' {self.__ctxmenubutton_padding[0]}px'
            f' {self.__ctxmenubutton_padding[1]}px'
            f' {self.__ctxmenubutton_padding[2]}px'
            f' {self.__ctxmenubutton_padding[3]}px;'
            'border: 1px solid rgba(0, 0, 0, 0.0);'
            f'border-radius: {self.__ctxmenubutton_border_radius}px;'
            '}'
            'QQuickContextMenuButton:hover {'
            'color: rgba('
            f' {self.__ctxtmenubutton_label_hover_color.red()},'
            f' {self.__ctxtmenubutton_label_hover_color.green()},'
            f' {self.__ctxtmenubutton_label_hover_color.blue()},'
            f' {self.__ctxtmenubutton_label_hover_color.alpha()});'
            'background-color: rgba('
            f' {self.__ctxmenubutton_background_hover_color.red()},'
            f' {self.__ctxmenubutton_background_hover_color.green()},'
            f' {self.__ctxmenubutton_background_hover_color.blue()},'
            f' {self.__ctxmenubutton_background_hover_color.alpha()});'
            'border: 1px solid rgba('
            f' {self.__ctxmenubutton_border_hover_color.red()},'
            f' {self.__ctxmenubutton_border_hover_color.green()},'
            f' {self.__ctxmenubutton_border_hover_color.blue()},'
            f' {self.__ctxmenubutton_border_hover_color.alpha()});'
            '}'
            'QQuickContextMenuButtonLabel:hover {'
            'color: rgba('
            f' {self.__ctxtmenubutton_label_hover_color.red()},'
            f' {self.__ctxtmenubutton_label_hover_color.green()},'
            f' {self.__ctxtmenubutton_label_hover_color.blue()},'
            f' {self.__ctxtmenubutton_label_hover_color.alpha()});'
            '}'
            'QQuickContextMenuButtonShortcutLabel {'
            'color: rgba('
            f' {self.__ctxtmenubutton_shortcut_label_hover_color.red()},'
            f' {self.__ctxtmenubutton_shortcut_label_hover_color.green()},'
            f' {self.__ctxtmenubutton_shortcut_label_hover_color.blue()},'
            f' {self.__ctxtmenubutton_shortcut_label_hover_color.alpha()});'
            '}'
        )

        style_path = os.path.join(SRC_DIR, 'static', 'style.qss')
        with open(style_path, 'r') as style_qss_file:
            file_style = style_qss_file.read()

        return window_style + context_menu_style + file_style

    @staticmethod
    def fullscreen_adapted_style(style: str) -> str:
        # ...
        styleparser = StyleParser(style)
        style = styleparser.widget_scope('QMainWindow')
        return (
            'QMainWindow {' f'{style}'
            'border-radius: 0px; border: 0px;}')
