#!/usr/bin/env python3
"""
MPRIS Media Player Simulator for Dynamic Island
Registers a standard MPRIS2 DBus service to simulate music playback.
Dynamic Island will automatically detect this player, show the album art,
song title, artist name, and allow testing play/pause and next/previous controls.

Usage:
    python3 tests/simulate_mpris.py
"""

import os
import sys
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ART = f"file://{os.path.join(REPO_ROOT, 'icon.png')}"

PLAYLIST = [
    {
        "title": "Starboy (feat. Daft Punk)",
        "artist": "The Weeknd",
        "art": DEFAULT_ART,
        "album": "Starboy"
    },
    {
        "title": "Blinding Lights",
        "artist": "The Weeknd",
        "art": DEFAULT_ART,
        "album": "After Hours"
    },
    {
        "title": "PORZAX - ยิ้มอันตราย (Official MV)",
        "artist": "PORZAX",
        "art": DEFAULT_ART,
        "album": "Singles"
    },
]


class DynamicIslandMockPlayer(dbus.service.Object):
    def __init__(self, bus):
        super().__init__(bus, '/org/mpris/MediaPlayer2')
        self._bus = bus
        self._track_index = 0
        self._status = 'Playing'
        print(f"🎵 Initialized Mock MPRIS Player: {self.current_track['title']} - {self.current_track['artist']}")

    @property
    def current_track(self):
        return PLAYLIST[self._track_index % len(PLAYLIST)]

    def _get_metadata_dict(self):
        track = self.current_track
        return dbus.Dictionary({
            'mpris:trackid': dbus.ObjectPath(f"/org/mpris/MediaPlayer2/Track/{self._track_index}"),
            'xesam:title': dbus.String(track['title']),
            'xesam:artist': dbus.Array([track['artist']], signature='s'),
            'xesam:album': dbus.String(track.get('album', '')),
            'mpris:artUrl': dbus.String(track.get('art', DEFAULT_ART)),
            'xesam:url': dbus.String('https://spotify.com/mock-track'),
        }, signature='sv')

    def _emit_property_change(self, changed_props):
        self.PropertiesChanged(
            'org.mpris.MediaPlayer2.Player',
            changed_props,
            dbus.Array([], signature='s')
        )

    # --- DBus org.mpris.MediaPlayer2 ---
    @dbus.service.method('org.mpris.MediaPlayer2')
    def Raise(self):
        print("🔔 [MPRIS] Raise() called from Dynamic Island (cover art or title clicked)!")

    @dbus.service.method('org.mpris.MediaPlayer2')
    def Quit(self):
        print("👋 [MPRIS] Quit() called.")
        sys.exit(0)

    # --- DBus org.mpris.MediaPlayer2.Player ---
    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Play(self):
        print("▶️ [MPRIS] Play()")
        self._status = 'Playing'
        self._emit_property_change({'PlaybackStatus': self._status})

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Pause(self):
        print("⏸️ [MPRIS] Pause()")
        self._status = 'Paused'
        self._emit_property_change({'PlaybackStatus': self._status})

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def PlayPause(self):
        self._status = 'Paused' if self._status == 'Playing' else 'Playing'
        print(f"⏯️ [MPRIS] PlayPause() -> {self._status}")
        self._emit_property_change({'PlaybackStatus': self._status})

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Next(self):
        self._track_index = (self._track_index + 1) % len(PLAYLIST)
        print(f"⏭️ [MPRIS] Next() -> {self.current_track['title']}")
        self._emit_property_change({'Metadata': self._get_metadata_dict()})

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Previous(self):
        self._track_index = (self._track_index - 1) % len(PLAYLIST)
        print(f"⏮️ [MPRIS] Previous() -> {self.current_track['title']}")
        self._emit_property_change({'Metadata': self._get_metadata_dict()})

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Stop(self):
        print("⏹️ [MPRIS] Stop()")
        self._status = 'Stopped'
        self._emit_property_change({'PlaybackStatus': self._status})

    # --- DBus org.freedesktop.DBus.Properties ---
    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='ss', out_signature='v')
    def Get(self, iface, prop):
        if iface == 'org.mpris.MediaPlayer2':
            if prop == 'Identity':
                return dbus.String('Dynamic Island Mock Player')
            if prop == 'CanRaise':
                return dbus.Boolean(True)
            if prop == 'CanQuit':
                return dbus.Boolean(True)
        elif iface == 'org.mpris.MediaPlayer2.Player':
            if prop == 'PlaybackStatus':
                return dbus.String(self._status)
            if prop == 'Metadata':
                return self._get_metadata_dict()
            if prop in ('CanPlay', 'CanPause', 'CanGoNext', 'CanGoPrevious'):
                return dbus.Boolean(True)
            if prop == 'CanSeek':
                return dbus.Boolean(False)
        return dbus.String('')

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, iface):
        if iface == 'org.mpris.MediaPlayer2':
            return dbus.Dictionary({
                'Identity': dbus.String('Dynamic Island Mock Player'),
                'CanRaise': dbus.Boolean(True),
                'CanQuit': dbus.Boolean(True),
            }, signature='sv')
        if iface == 'org.mpris.MediaPlayer2.Player':
            return dbus.Dictionary({
                'PlaybackStatus': dbus.String(self._status),
                'Metadata': self._get_metadata_dict(),
                'CanPlay': dbus.Boolean(True),
                'CanPause': dbus.Boolean(True),
                'CanGoNext': dbus.Boolean(True),
                'CanGoPrevious': dbus.Boolean(True),
                'CanSeek': dbus.Boolean(False),
            }, signature='sv')
        return dbus.Dictionary({}, signature='sv')

    @dbus.service.signal('org.freedesktop.DBus.Properties', signature='sa{sv}as')
    def PropertiesChanged(self, iface, changed_props, invalidated_props):
        pass


def main():
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    bus_name = 'org.mpris.MediaPlayer2.MockPlayer'
    try:
        dbus.service.BusName(bus_name, bus)
    except Exception as e:
        print(f"Error acquiring bus name {bus_name}: {e}")
        return

    player = DynamicIslandMockPlayer(bus)
    print("\n=======================================================")
    print("🌟 Dynamic Island MPRIS Mock Player is now ACTIVE!")
    print("Look at your Dynamic Island on GNOME Shell.")
    print("It should display the music island with album art & controls.")
    print("You can test:")
    print("  - Clicking the island to expand/collapse")
    print("  - Clicking Play/Pause on the island")
    print("  - Clicking Next/Previous on the island")
    print("  - Clicking the Album Art to trigger Raise()")
    print("=======================================================")
    print("Press Ctrl+C to stop the mock player.\n")

    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        print("\nStopping Mock Player...")


if __name__ == '__main__':
    main()
