__author__ = 'wybe'
# Python 3.4.3

from gi.repository import Gtk

import mainwindow


def main():

    window = mainwindow.MainWindow()

    # Connect the cross to the quit function.
    window.connect("destroy", Gtk.main_quit)

    # Show the window.
    window.show_all()

    # Main loop.
    Gtk.main()
    print("Exiting...")


if __name__ == "__main__":
    main()
