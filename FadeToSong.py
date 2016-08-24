# -*- Mode: python; coding: utf-8; tab-width: 4; indent-tabs-mode: nil; -*-
#
#    FadeToSong.py
#
#    Adds an option to fade to the next song to the right click context menu.
#    Copyright (C) 2016 Pedro Guridi <pedro.guridi@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gio, GObject, Gtk, Peas, RB, PeasGtk
import logging

DCONF_DIR = 'org.gnome.rhythmbox.plugins.fadetosong'


class FadeToSong(GObject.Object, Peas.Activatable, PeasGtk.Configurable):

    """Adds an option to fade to the next song to the right click context menu."""

    object = GObject.property(type=GObject.Object)

    _action = 'fade-to-song'
    _locations = ['browser-popup',
                  'playlist-popup',
                  'podcast-episode-popup',
                  'queue-popup']

    def __init__(self):
        super(FadeToSong, self).__init__()
        self._app = Gio.Application.get_default()
        self.settings = Gio.Settings(DCONF_DIR)
        self.default_volume = 1.0

    def fade_out(self):
        current = self.player.get_volume()[1]
        if self.player.get_volume()[1] > 0.3:    
            self.player.set_volume(current - 0.1)
            return True
        else:
            self.player.set_volume(self.default_volume)
            self.player.do_next()
            return False
    
    def fade_to_next(self, *args):
        shell = self.object
        self.player = shell.props.shell_player
        self.default_volume = self.player.get_volume()[1]
        GObject.timeout_add(500, self.fade_out)
        
    def do_activate(self):
        """Activate the plugin."""
        logging.debug('Activating plugin...')
        
        rb_settings = Gio.Settings("org.gnome.rhythmbox")

        action = Gio.SimpleAction(name=FadeToSong._action)
        action.connect('activate', self.fade_to_next)
        self._app.add_action(action)

        item = Gio.MenuItem()
        item.set_label('Fade to next song')
        item.set_detailed_action('app.%s' % FadeToSong._action)

        for location in FadeToSong._locations:
            self._app.add_plugin_menu_item(location,
                                           FadeToSong._action,
                                           item)

    def do_deactivate(self):
        """Deactivate the plugin."""
        logging.debug('Deactivating plugin...')

        for location in FadeToSong._locations:
            self._app.remove_plugin_menu_item(location,
                                              FadeToSong._action)
                                              
    def do_create_configure_widget(self):
        dialog = Gtk.VBox()
        
        # switch for use-custom-label
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["use-custom-label"])
        switch.connect("notify::active", self.switch_toggled)
        
        label = Gtk.Label()
        label.set_text("Use custom label")
        
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)
        dialog.pack_start(hbox, False, False, 5)
        
        # entry for label-text
        hbox = Gtk.HBox()
        entry = Gtk.Entry()
        entry_buffer = Gtk.EntryBuffer()
        entry_buffer.set_text(self.settings["label-text"], len(self.settings["label-text"]))
        entry_buffer.connect("inserted-text", self.label_edited)
        entry_buffer.connect("deleted-text", self.label_edited)
        entry.set_buffer(entry_buffer)
        
        
        label = Gtk.Label()
        label.set_text("Label text")
        
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(entry, False, False, 5)
        dialog.pack_start(hbox, False, False, 5)
        
        dialog.set_size_request(300, -1)
        
        return dialog
        
    def switch_toggled(self, switch, active):
        self.settings["use-custom-label"] = switch.get_active()
        
    def label_edited(self, entry_buffer, *args):
        self.settings["label-text"] = entry_buffer.get_text()
