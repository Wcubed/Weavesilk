__author__ = 'wybe'


from gi.repository import Gtk, Gdk, GLib
import cairo
import math
import time

from pencil import Line, Pencil


class MainWindow(Gtk.Window):

    def __init__(self):
        super(MainWindow, self).__init__()

        # -- Variables --
        self._last_x = 0
        self._last_y = 0

        self._last_buffer_time = time.time()
        self._last_update_time = time.time()

        self._mouse_pressed = False

        self._buffer_image = None
        self._lines = []

        # ---- Initialize the pencils. ----
        self._pencils = []

        for i in range(0, 50):
            self._pencils.append(Pencil(0, i * 2, 0.2, 0.8, 0.2, 0.5))

        print(len(self._pencils))

        # -- Drawing area --

        self._area = Gtk.DrawingArea()

        # Capture button presses in drawing area.
        self._area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self._area.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self._area.add_events(Gdk.EventMask.POINTER_MOTION_MASK)

        # Connect events.
        self._area.connect('draw', self._draw)
        self._area.connect('button-press-event', self._button_press)
        self._area.connect('button-release-event', self._button_release)
        self._area.connect('motion-notify-event', self._motion_notify)

        # Visuals update
        GLib.timeout_add(10, self._update)

        self.set_size_request(1000, 500)

        self.add(self._area)

    def _update(self):
        """
        Updates the pencils.
        """
        # Calculate delta time.
        now = time.time()
        dt = now - self._last_update_time
        self._last_update_time = now

        # Update the pencils and when the mouse is down, add the lines to the buffer.
        for pencil in self._pencils:
            line = pencil.update(dt, self._last_x, self._last_y)

            if self._mouse_pressed:
                self._lines.append(line)

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
            cr.move_to(line.start_x, line.start_y)
            cr.line_to(line.end_x, line.end_y)
            cr.stroke()

        # ---- Save the screen ----
        now = time.time()
        if now - self._last_buffer_time > 0.2:

            # Save screen.
            drawing_window = self._area.get_window()
            self._buffer_image = Gdk.pixbuf_get_from_window(drawing_window, 0, 0, width, height)

            # Clear the line buffer.
            self._lines.clear()

            # Update
            self._last_buffer_time = now

        # Circle
        cr.set_source_rgba(1, 1, 1)

        cr.arc(self._last_x, self._last_y, 25, 0, 2*math.pi)
        cr.stroke()

    def _button_press(self, widget, event):
        if event.button == 1:
            self._mouse_pressed = True

    def _button_release(self, widget, event):
        if event.button == 1:
            self._mouse_pressed = False

    def _motion_notify(self, widget, event):
        x = event.x
        y = event.y

        self._last_x = x
        self._last_y = y
