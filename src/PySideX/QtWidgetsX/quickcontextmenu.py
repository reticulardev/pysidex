#!/usr/bin/env python3
import logging
import os

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import snake_case

from PySideX.QtWidgetsX.applicationwindow import QApplicationWindow
from PySideX.QtWidgetsX.label import ContextLabel
from PySideX.QtWidgetsX.tooltip import QTooltip
from PySideX.QtWidgetsX.modules.envsettings import GuiEnv
from PySideX.QtWidgetsX.modules.dynamicstyle import StyleParser
import PySideX.QtWidgetsX.modules.color as color


SRC_DIR = os.path.dirname(os.path.abspath(__file__))


class QQuickContextMenuSeparatorLine(QtWidgets.QFrame):
    """..."""
    def __init__(self, *args, **kwargs) -> None:
        """..."""
        super().__init__(*args, **kwargs)
        self.set_frame_shape(QtWidgets.QFrame.HLine)
        self.set_frame_shadow(QtWidgets.QFrame.Plain)
        self.set_line_width(0)
        self.set_mid_line_width(3)


class QQuickContextMenuSeparator(QtWidgets.QFrame):
    """..."""
    def __init__(self, *args, **kwargs) -> None:
        """..."""
        super().__init__(*args, **kwargs)
        box = QtWidgets.QVBoxLayout()
        box.set_contents_margins(0, 0, 0, 0)
        self.set_layout(box)

        line = QQuickContextMenuSeparatorLine()
        line.set_contents_margins(0, 0, 0, 0)
        box.add_widget(line)


class QQuickContextMenuButtonLabel(QtWidgets.QLabel):
    """..."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        """..."""


class QQuickContextMenuButton(QtWidgets.QFrame):
    """..."""
    enter_event_signal = QtCore.Signal(object)
    leave_event_signal = QtCore.Signal(object)
    mouse_press_event_signal = QtCore.Signal(object)
    mouse_release_event_signal = QtCore.Signal(object)

    def __init__(
            self,
            toplevel: QApplicationWindow,
            context_menu: QtWidgets.QWidget,
            text: str,
            receiver: callable,
            icon: QtGui.QIcon | None = None,
            shortcut: QtGui.QKeySequence | None = None,
            is_quick_action: bool = False,
            quick_action_label_as_tooltip: bool = True,
            *args, **kwargs) -> None:
        """..."""
        super().__init__(*args, **kwargs)
        self.__toplevel = toplevel
        self.__context_menu = context_menu
        self.__text = text
        self.__receiver = receiver
        self.__icon = icon
        self.__shortcut = shortcut
        self.__shortcut_txt = shortcut.to_string() if shortcut else ' '
        self.__is_quick_action = is_quick_action
        self.__quick_action_label_as_tooltip = quick_action_label_as_tooltip
        self.__tooltip = None
        self.__is_tooltip_open = False
        self.__tooltip_timer = QtCore.QTimer()

        self.__env = GuiEnv(
            self.__toplevel.platform().operational_system(),
            self.__toplevel.platform().desktop_environment())

        self.__style_parser = StyleParser(self.__toplevel.style_sheet())
        self.__normal_style = self.__updated_normal_style()
        self.__hover_style = self.__updated_hover_style()
        self.__main_layout = QtWidgets.QHBoxLayout()
        self.__main_layout.set_contents_margins(0, 0, 0, 0)
        self.__main_layout.set_spacing(0)
        self.set_layout(self.__main_layout)

        self.__left_layout = QtWidgets.QHBoxLayout()
        self.__left_layout.set_alignment(QtCore.Qt.AlignLeft)
        self.__main_layout.add_layout(self.__left_layout)

        self.__configure_icon()
        icon_label = QtWidgets.QLabel()
        icon_label.set_pixmap(self.__icon.pixmap(QtCore.QSize(16, 16)))
        icon_label.set_alignment(QtCore.Qt.AlignLeft)
        if self.__is_quick_action:
            icon_label.set_contents_margins(0, 2, 0, 2)
        else:
            icon_label.set_contents_margins(0, 0, 5, 0)
        self.__left_layout.add_widget(icon_label)

        self.__text_label = QQuickContextMenuButtonLabel(self.__text)
        self.__text_label.set_alignment(QtCore.Qt.AlignLeft)
        if not self.__is_quick_action:
            self.__left_layout.add_widget(self.__text_label)

        if not self.__is_quick_action:
            shortcut_label = ContextLabel(self.__shortcut_txt)
            shortcut_label.set_contents_margins(20, 0, 0, 0)
            shortcut_label.set_alignment(QtCore.Qt.AlignRight)
            self.__main_layout.add_widget(shortcut_label)

        if self.__is_quick_action and self.__quick_action_label_as_tooltip:
            self.__tooltip = QTooltip(
                self.__toplevel, self, self.__text, None, self.__shortcut)

        self.__toplevel.set_style_signal.connect(self.__set_style_signal)
        self.__toplevel.reset_style_signal.connect(self.__set_style_signal)

    def text(self) -> str:
        """..."""
        return self.__text

    def tooltip_widget(self) -> QtWidgets.QWidget | None:
        return self.__tooltip

    def __configure_icon(self):
        # ...
        if not self.__icon:
            sym = '-symbolic' if self.__env.settings().window_is_dark() else ''
            icon_path = os.path.join(
                SRC_DIR, 'modules', 'static', f'context-menu-item{sym}.svg')
            self.__icon = QtGui.QIcon(QtGui.QPixmap(icon_path))

    def __set_style_signal(self) -> None:
        # ...
        self.__style_parser.set_style_sheet(self.__toplevel.style_sheet())
        self.__normal_style = self.__updated_normal_style()
        self.__hover_style = self.__updated_hover_style()
        self.__text_label.set_style_sheet(self.__normal_style)

    def __tooltip_exec(self):
        if self.__tooltip and not self.__is_tooltip_open:
            self.__tooltip.exec()
            self.__tooltip_timer.stop()
            self.__is_tooltip_open = True

    def __updated_hover_style(self) -> str:
        # ...
        updated_hover_style = self.__style_parser.widget_scope(
            'QQuickContextMenuButtonLabel', 'hover')
        if not updated_hover_style:
            fg = self.__env.settings().contextmenubutton_label_hover_color()
            return (
                'color: rgba'
                f'({fg.red()}, {fg.green()}, {fg.blue()}, {fg.alpha()});')

        return updated_hover_style

    def __updated_normal_style(self) -> str:
        # ...
        updated_normal_style = self.__style_parser.widget_scope(
            'QQuickContextMenuButtonLabel')
        if not updated_normal_style:
            fg = self.__env.settings().label_color()
            return (
                'color: rgba'
                f'({fg.red()}, {fg.green()}, {fg.blue()}, {fg.alpha()});')

        return updated_normal_style

    def enter_event(self, event: QtGui.QEnterEvent) -> None:
        """..."""
        if self.__tooltip and self.__is_quick_action:
            if not self.__is_tooltip_open:
                self.__tooltip_timer.timeout.connect(self.__tooltip_exec)
                self.__tooltip_timer.start(500)
        else:
            self.enter_event_signal.emit(event)
            self.__text_label.set_style_sheet(self.__hover_style)

    def leave_event(self, event: QtGui.QEnterEvent) -> None:
        """..."""
        self.leave_event_signal.emit(event)
        self.__text_label.set_style_sheet(self.__normal_style)

        if self.__tooltip and self.__is_quick_action:
            self.__is_tooltip_open = False
            self.__tooltip.close()
            self.__tooltip_timer.stop()

    def mouse_press_event(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_press_event_signal.emit(event)

    def mouse_release_event(self, event: QtGui.QMouseEvent) -> None:
        """..."""
        self.mouse_release_event_signal.emit(event)
        if self.under_mouse():
            self.__receiver()
            self.__text_label.set_style_sheet(self.__normal_style)
            self.__context_menu.close()


class QQuickContextMenu(QtWidgets.QFrame):
    """..."""

    def __init__(
            self,
            toplevel: QApplicationWindow,
            quick_action_label_as_tooltip: bool = True,
            *args, **kwargs) -> None:
        """Class constructor

        Initialize class attributes

        :param toplevel: QApplicationWindow app main window instance
        """
        super().__init__(*args, **kwargs)
        self.__toplevel = toplevel
        self.__quick_action_label_as_tooltip = quick_action_label_as_tooltip

        self.set_attribute(QtCore.Qt.WA_TranslucentBackground)
        self.set_window_flags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.set_minimum_width(50)
        self.set_minimum_height(35)

        self.__gui_env = GuiEnv(
            self.__toplevel.platform().operational_system(),
            self.__toplevel.platform().desktop_environment())

        self.__is_dark = self.__gui_env.settings().window_is_dark()
        self.__style_saved = self.__toplevel.style_sheet()
        self.__style_parser = StyleParser(self.__style_saved)
        self.__context_separators = []
        self.__action_buttons = []
        self.__quick_action_buttons = []
        self.__point_x = None
        self.__point_y = None
        self.__quick_buttons_on_top = True
        self.__force_quick_mode = False
        self.__quick_mode = self.__is_quick_mode()

        # Main layout
        self.__main_layout = QtWidgets.QHBoxLayout()
        self.set_layout(self.__main_layout)

        self.__main_widget = QtWidgets.QFrame()
        self.__main_widget.set_object_name('QQuickContextMenu')
        self.__main_layout.add_widget(self.__main_widget)

        # Layout
        self.__menu_context_box = QtWidgets.QVBoxLayout()
        self.__menu_context_box.set_contents_margins(0, 0, 0, 0)
        self.__menu_context_box.set_spacing(0)
        self.__main_widget.set_layout(self.__menu_context_box)

        # Top
        self.__quick_actions_top_hbox = QtWidgets.QHBoxLayout()
        self.__quick_actions_top_hbox.set_alignment(QtCore.Qt.AlignLeft)
        self.__menu_context_box.add_layout(self.__quick_actions_top_hbox)

        self.__quick_actions_box = QtWidgets.QVBoxLayout()
        self.__menu_context_box.add_layout(self.__quick_actions_box)

        self.__quick_top_separator = QQuickContextMenuSeparator()
        self.__quick_top_separator.set_visible(False)
        self.__menu_context_box.add_widget(self.__quick_top_separator)
        self.__context_separators.append(self.__quick_top_separator)

        # Body
        self.__actions_box = QtWidgets.QVBoxLayout()
        self.__menu_context_box.add_layout(self.__actions_box)

        # Bottom
        self.__quick_bottom_separator = QQuickContextMenuSeparator()
        self.__quick_bottom_separator.set_visible(False)
        self.__menu_context_box.add_widget(self.__quick_bottom_separator)
        self.__context_separators.append(self.__quick_bottom_separator)

        self.__quick_actions_bottom_hbox = QtWidgets.QHBoxLayout()
        self.__quick_actions_bottom_hbox.set_alignment(QtCore.Qt.AlignLeft)
        self.__menu_context_box.add_layout(self.__quick_actions_bottom_hbox)

        # Shadow
        self.__shadow_effect = QtWidgets.QGraphicsDropShadowEffect(self)
        self.__shadow_effect.set_blur_radius(5)
        self.__shadow_effect.set_offset(QtCore.QPointF(0.0, 0.0))

        if self.__is_dark:
            self.__shadow_effect.set_color(QtGui.QColor(10, 10, 10, 100))
        else:
            self.__shadow_effect.set_color(QtGui.QColor(10, 10, 10, 70))
        self.__main_widget.set_graphics_effect(self.__shadow_effect)

        self.__toplevel.set_style_signal.connect(self.__set_style_signal)
        self.__toplevel.reset_style_signal.connect(self.__set_style_signal)

    def add_action(
            self,
            text: str,
            receiver: callable,
            icon: QtGui.QIcon | None = None,
            shortcut: QtGui.QKeySequence | None = None,
            is_quick_action: bool = False,
            ) -> None:
        """..."""
        quick = False if not self.__quick_mode else is_quick_action
        ctx_btn = QQuickContextMenuButton(
            self.__toplevel, self, text, receiver, icon, shortcut,
            quick, self.__quick_action_label_as_tooltip)
        self.__action_buttons.append(ctx_btn)

        if is_quick_action:
            if self.__quick_mode:
                self.__quick_actions_top_hbox.add_widget(ctx_btn)
            else:
                self.__quick_actions_box.add_widget(ctx_btn)
            self.__quick_action_buttons.append(ctx_btn)
        else:
            ctx_btn.set_style_sheet(self.__style_saved)
            self.__actions_box.add_widget(ctx_btn)

    def add_separator(self) -> None:
        """..."""
        separator = QQuickContextMenuSeparator()
        self.__actions_box.add_widget(separator)
        self.__context_separators.append(separator)

    def exec(self, point: QtCore.QPoint) -> None:
        """..."""
        self.__point_x = point.x()
        self.__point_y = point.y()

        self.__main_widget.set_style_sheet(self.__set_style())
        for btn in self.__action_buttons:
            btn.set_style_sheet(self.__style_saved)

        for btn in self.__quick_action_buttons:
            if btn.tooltip_widget():
                btn.tooltip_widget().set_style_sheet(self.__style_saved)
            btn.set_style_sheet(self.__style_saved)

        for sep in self.__context_separators:
            sep.set_style_sheet(self.__style_saved)

        self.move(self.__point_x - 10, self.__point_y - 10)
        self.show()
        self.__set_dynamic_positioning()

    def mouse_press_event(self, event: QtGui.QMouseEvent) -> None:
        """..."""
        logging.info(event)
        self.close()

    def set_force_quick_mode(self, force: bool) -> None:
        """..."""
        self.__force_quick_mode = force
        self.__quick_mode = self.__is_quick_mode()

    def __is_quick_mode(self) -> bool:
        if (self.__toplevel.platform().desktop_environment() == 'windows-11' or
                self.__force_quick_mode):
            return True
        return False

    def __set_dynamic_positioning(self) -> None:
        # ...
        x = self.geometry().x()
        y = self.geometry().y()

        screen_width = self.__toplevel.screen().geometry().width()
        screen_height = self.__toplevel.screen().geometry().height()

        if self.geometry().x() + self.geometry().width() > screen_width:
            x = screen_width - self.geometry().width()

        self.__quick_buttons_on_top = True
        if self.geometry().y() + self.geometry().height() > screen_height:
            y = self.geometry().y() - self.geometry().height() + 20
            self.__quick_buttons_on_top = False

        if self.__quick_mode:
            self.__toggle_quick_buttons_position()
        self.move(x, y)

    def __set_style_signal(self) -> None:
        # ...
        self.__style_saved = self.__toplevel.style_sheet()
        self.__style_parser.set_style_sheet(self.__style_saved)

    def __set_style(self) -> str:
        # ...
        if not self.__style_saved:
            self.__set_style_signal()

        return ('#QQuickContextMenu {'
                f'{self.__style_parser.widget_scope("QQuickContextMenu")}' '}')

    def __toggle_quick_buttons_position(self):
        for btn in self.__quick_action_buttons:
            self.__quick_actions_top_hbox.remove_widget(btn)

        for btn in self.__quick_action_buttons:
            self.__quick_actions_bottom_hbox.remove_widget(btn)

        if self.__quick_buttons_on_top:
            for btn in self.__quick_action_buttons:
                self.__quick_actions_top_hbox.add_widget(btn)
                self.__quick_top_separator.set_visible(True)
                self.__quick_bottom_separator.set_visible(False)
        else:
            for btn in self.__quick_action_buttons:
                self.__quick_actions_bottom_hbox.add_widget(btn)
                self.__quick_top_separator.set_visible(False)
                self.__quick_bottom_separator.set_visible(True)