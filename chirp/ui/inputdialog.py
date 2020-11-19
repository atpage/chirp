# Copyright 2008 Dan Smith <dsmith@danplanet.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk
from gi.repository import GObject
import logging

from .miscwidgets import make_choice
from chirp.ui import reporting

LOG = logging.getLogger(__name__)


class TextInputDialog(Gtk.Dialog):
    def respond_ok(self, _):
        self.response(Gtk.ResponseType.OK)

    def __init__(self, **args):
        buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                   Gtk.STOCK_OK, Gtk.ResponseType.OK)
        GObject.GObject.__init__(self, buttons=buttons, **args)

        self.label = Gtk.Label()
        self.label.set_size_request(300, 100)
        # pylint: disable-msg=E1101
        self.vbox.pack_start(self.label, 1, 1, 0)

        self.text = Gtk.Entry()
        self.text.connect("activate", self.respond_ok, None)
        # pylint: disable-msg=E1101
        self.vbox.pack_start(self.text, 1, 1, 0)

        self.label.show()
        self.text.show()


class ChoiceDialog(Gtk.Dialog):
    editable = False

    def __init__(self, choices, **args):
        buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                   Gtk.STOCK_OK, Gtk.ResponseType.OK)
        GObject.GObject.__init__(self, buttons=buttons, **args)

        self.label = Gtk.Label()
        self.label.set_size_request(300, 100)
        # pylint: disable-msg=E1101
        self.vbox.pack_start(self.label, 1, 1, 0)
        self.label.show()

        try:
            default = choices[0]
        except IndexError:
            default = None

        self.choice = make_choice(sorted(choices), self.editable, default)
        # pylint: disable-msg=E1101
        self.vbox.pack_start(self.choice, 1, 1, 0)
        self.choice.show()

        self.set_default_response(Gtk.ResponseType.OK)


class EditableChoiceDialog(ChoiceDialog):
    editable = True

    def __init__(self, choices, **args):
        ChoiceDialog.__init__(self, choices, **args)

        self.choice.get_child().set_activates_default(True)


class ExceptionDialog(Gtk.MessageDialog):
    def __init__(self, exception, **args):
        GObject.GObject.__init__(self, buttons=Gtk.ButtonsType.OK,
                                   type=Gtk.MessageType.ERROR, **args)
        self.set_property("text", _("An error has occurred"))
        self.format_secondary_text(str(exception))

        import traceback
        import sys
        reporting.report_exception(traceback.format_exc(limit=30))
        LOG.error("--- Exception Dialog: %s ---" % exception)
        LOG.error(traceback.format_exc(limit=100))
        LOG.error("----------------------------")


class FieldDialog(Gtk.Dialog):
    def __init__(self, **kwargs):
        if "buttons" not in list(kwargs.keys()):
            kwargs["buttons"] = (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                 Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

        self.__fields = {}
        self.set_default_response(Gtk.ResponseType.OK)

        GObject.GObject.__init__(self, **kwargs)

    def response(self, _):
        LOG.debug("Blocking response")
        return

    def add_field(self, label, widget, validator=None):
        box = Gtk.HBox(True, 2)

        lab = Gtk.Label(label=label)
        lab.show()

        widget.set_size_request(150, -1)
        widget.show()

        box.pack_start(lab, 0, 0, 0)
        box.pack_start(widget, 0, 0, 0)
        box.show()

        # pylint: disable-msg=E1101
        self.vbox.pack_start(box, 0, 0, 0)

        self.__fields[label] = widget

    def get_field(self, label):
        return self.__fields.get(label, None)


class OverwriteDialog(Gtk.MessageDialog):
    def __init__(self, filename):
        GObject.GObject.__init__(self,
                            buttons=(_("Overwrite"), Gtk.ResponseType.OK,
                                     Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        self.set_property("text", _("File Exists"))

        text = \
            _("The file {name} already exists. "
              "Do you want to overwrite it?").format(name=filename)

        self.format_secondary_text(text)

if __name__ == "__main__":
    # pylint: disable-msg=C0103
    d = FieldDialog(buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK))
    d.add_field("Foo", Gtk.Entry())
    d.add_field("Bar", make_choice(["A", "B"]))
    d.run()
    Gtk.main()
    d.destroy()
