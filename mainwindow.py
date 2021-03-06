__author__ = 'wybe'


from gi.repository import Gtk, Gdk, GLib
import cairo
import math
import time
import copy

from pencil import Line, Pencil
from vector import Vector


class MainWindow(Gtk.Window):

    def __init__(self):
        super(MainWindow, self).__init__()

        # -- Variables --
        self._h_mirror = False
        self._r_mirror = True
        self._r_mirror_amount = 5

        self._is_fullscreen = False

        self._last_x = 0
        self._last_y = 0

        self._last_buffer_time = time.time()
        self._last_update_time = time.time()

        self._mouse_pressed = False

        # Image that holds the drawing.
        self._buffer_image = None

        # Image that holds the drawing, minus the last stroke (one continuous drag with the mouse).
        self._undo_buffer_image = None

        # Line buffer.
        self._lines = []

        # ---- Initialize the pencils. ----
        self._pencils = []

        for i in range(0, 50):
            self._pencils.append(Pencil(0, 0, 0.2, 0.8, 0.8, 0.5))

        # -- Drawing area --

        self._area = Gtk.DrawingArea()

        # Capture button presses in drawing area.
        self._area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self._area.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self._area.add_events(Gdk.EventMask.POINTER_MOTION_MASK)

        # Connect events.
        self._area.connect('draw', self._draw)
        self.connect('key-press-event', self._key_press)
        self._area.connect('button-press-event', self._button_press)
        self._area.connect('button-release-event', self._button_release)
        self._area.connect('motion-notify-event', self._motion_notify)

        # Visuals update
        GLib.timeout_add(10, self._update)

        self.set_size_request(1000, 500)

        self.add(self._area)

    def _update(self):
        """
        Updates the pencils and queues a redraw of the DrawingArea.
        """
        # Calculate delta time.
        now = time.time()
        dt = now - self._last_update_time
        self._last_update_time = now

        # Update the pencils and when the mouse is down, add the lines to the buffer.
        lines = []

        for pencil in self._pencils:
            line = pencil.update(dt, self._last_x, self._last_y, self._mouse_pressed)

            if line:
                lines.append(line)

        # ---- Mirroring. ----

        width = self.get_allocated_width()
        height = self.get_allocated_height()

        if self._h_mirror:
            lines = self.mirror_lines_h(lines, width)

        if self._r_mirror:
            lines = self.mirror_lines_r(lines, width, height)

        for l in lines:
            self._lines.append(l)

        self._area.queue_draw()
        return True

    def _draw(self, widget, cr):
        width = self.get_allocated_width()
        height = self.get_allocated_height()

        cr.set_operator(cairo.OPERATOR_SOURCE)

        # Background
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()

        # ---- Image ----
        if self._buffer_image:
            Gdk.cairo_set_source_pixbuf(cr, self._buffer_image, 0, 0)
            cr.paint()

        cr.set_operator(cairo.OPERATOR_ADD)

        # ---- Line buffer ----
        cr.set_line_width(1)

        for line in self._lines:
            cr.set_source_rgba(line.r, line.g, line.b, line.a)

            cr.move_to(line.start.x, line.start.y)
            cr.line_to(line.end.x, line.end.y)
            cr.stroke()

        # ---- Save the screen ----
        now = time.time()
        if now - self._last_buffer_time > 0.05:

            # Save screen.
            drawing_window = self._area.get_window()
            self._buffer_image = Gdk.pixbuf_get_from_window(drawing_window, 0, 0, width, height)

            # Clear the line buffer.
            self._lines.clear()

            # Update
            self._last_buffer_time = now

        # Circle
        cr.set_source_rgba(1, 1, 1)

        cr.arc(self._last_x, self._last_y, 10, 0, 2*math.pi)
        cr.stroke()

    def _key_press(self, widget, event):
        if event.keyval == Gdk.KEY_1:
            # Magenta color.
            for pencil in self._pencils:
                pencil._col = [0.2, 0.8, 0.8, 0.5]

        elif event.keyval == Gdk.KEY_2:
            # Red color.
            for pencil in self._pencils:
                pencil._col = [0.8, 0.1, 0.1, 0.5]

        elif event.keyval == Gdk.KEY_3:
            # Green color.
            for pencil in self._pencils:
                pencil._col = [0.2, 0.8, 0.2, 0.5]

        elif event.keyval == Gdk.KEY_4:
            # Orange color.
            for pencil in self._pencils:
                pencil._col = [0.8, 0.2, 0.0, 0.5]

        elif event.keyval == Gdk.KEY_5:
            # "Black" color.
            for pencil in self._pencils:
                pencil._col = [0.3, 0.3, 0.3, 0.5]

        elif event.keyval == Gdk.KEY_6:
            # Purple color.
            for pencil in self._pencils:
                pencil._col = [0.8, 0.3, 0.8, 0.5]

        elif event.keyval == Gdk.KEY_7:
            # Pink color.
            for pencil in self._pencils:
                pencil._col = [0.9, 0.3, 0.3, 0.5]

        elif event.keyval == Gdk.KEY_q:
            # Toggle horizontal mirror.
            self._h_mirror = not self._h_mirror

        elif event.keyval == Gdk.KEY_e:
            # Toggle radial mirror.
            self._r_mirror = not self._r_mirror

        elif event.keyval == Gdk.KEY_c:
            # Clear screen.
            self._buffer_image = None

        elif event.keyval == Gdk.KEY_s:
            # Save screen to file.
            filename = "Images/" + time.strftime('%d-%m-%Y-%H:%M:%S') + ".png"
            self._buffer_image.savev(filename, 'png', [], [])

        elif event.keyval == Gdk.KEY_z:
            # Undo the last stroke.
            if self._undo_buffer_image:
                self._buffer_image = self._undo_buffer_image

        elif event.keyval == Gdk.KEY_f:
            # Fullscreen.
            if self._is_fullscreen:
                self.unfullscreen()
                self._is_fullscreen = False
            else:
                self.fullscreen()
                self._is_fullscreen = True

        elif event.keyval == Gdk.KEY_Escape:
            # Exit.
            Gtk.main_quit()

    def _button_press(self, widget, event):
        if event.button == 1:
            self._mouse_pressed = True

            # We start a new stroke, make the last one permanent.
            self._undo_buffer_image = self._buffer_image.copy()

    def _button_release(self, widget, event):
        if event.button == 1:
            self._mouse_pressed = False

    def _motion_notify(self, widget, event):
        x = event.x
        y = event.y

        self._last_x = x
        self._last_y = y

    def mirror_lines_h(self, lines, width):
        """
        Mirrors a list of lines horizontally.
        :param lines: A list of lines to be mirrored.
        :return: The original lines, plus the mirrored ones.
        """

        mir_lines = lines[:]
        half_width = width / 2

        for line in lines:
            mir_line = copy.copy(line)

            s_x = mir_line.start.x
            e_x = mir_line.end.x

            if s_x > half_width:
                s_x -= 2 * (s_x - half_width)
            else:
                s_x += 2 * (half_width - s_x)

            if e_x > half_width:
                e_x -= 2 * (e_x - half_width)
            else:
                e_x += 2 * (half_width - e_x)

            mir_line.start = Vector(s_x, mir_line.start.y)
            mir_line.end = Vector(e_x, mir_line.end.y)

            mir_lines.append(mir_line)

        return mir_lines

    def mirror_lines_r(self, lines, width, height):
        """
        Mirrors lines with radial symmetry.
        :param lines:
        :param width:
        :param height:
        :return:
        """

        mir_lines = lines[:]
        center = Vector(width / 2, height / 2)

        step_angle = 2 * math.pi / self._r_mirror_amount

        for line in lines:
            for i in range(1, self._r_mirror_amount):
                mir_line = copy.copy(line)

                mir_start = mir_line.start - center
                mir_end = mir_line.end - center

                mir_start.rotate(step_angle * i)
                mir_end.rotate(step_angle * i)

                mir_line.start = mir_start + center
                mir_line.end = mir_end + center

                mir_lines.append(mir_line)

        return mir_lines
