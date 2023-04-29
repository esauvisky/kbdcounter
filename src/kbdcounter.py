#!/usr/bin/env python

from __future__ import print_function, division
import sqlite3
from collections import Counter, namedtuple
import os
import time
from datetime import datetime, timedelta
from optparse import OptionParser
from xlib import XEvents
import seaborn as sns
import matplotlib.pyplot as plt

import pandas as pd
import sqlite3

import xlib
import keyboardlayout as kl
import keyboardlayout.pygame as klp
import pygame

KEY_SIZE = 60


def get_key_positions(keyboard_layout, layout_name):
    return {
        "KEY_BACKQUOTE": keyboard_layout.keys[layout_name]["`"].rect,
        "KEY_1": keyboard_layout.keys[layout_name]["1"].rect,
        "KEY_2": keyboard_layout.keys[layout_name]["2"].rect,
        "KEY_3": keyboard_layout.keys[layout_name]["3"].rect,
        "KEY_4": keyboard_layout.keys[layout_name]["4"].rect,
        "KEY_5": keyboard_layout.keys[layout_name]["5"].rect,
        "KEY_6": keyboard_layout.keys[layout_name]["6"].rect,
        "KEY_7": keyboard_layout.keys[layout_name]["7"].rect,
        "KEY_8": keyboard_layout.keys[layout_name]["8"].rect,
        "KEY_9": keyboard_layout.keys[layout_name]["9"].rect,
        "KEY_0": keyboard_layout.keys[layout_name]["0"].rect,
        "KEY_MINUS": keyboard_layout.keys[layout_name]["-"].rect,
        "KEY_EQUAL": keyboard_layout.keys[layout_name]["="].rect,
        "KEY_TAB": keyboard_layout.keys[layout_name]["tab"].rect,
        "KEY_Q": keyboard_layout.keys[layout_name]["q"].rect,
        "KEY_W": keyboard_layout.keys[layout_name]["w"].rect,
        "KEY_E": keyboard_layout.keys[layout_name]["e"].rect,
        "KEY_R": keyboard_layout.keys[layout_name]["r"].rect,
        "KEY_T": keyboard_layout.keys[layout_name]["t"].rect,
        "KEY_Y": keyboard_layout.keys[layout_name]["y"].rect,
        "KEY_U": keyboard_layout.keys[layout_name]["u"].rect,
        "KEY_I": keyboard_layout.keys[layout_name]["i"].rect,
        "KEY_O": keyboard_layout.keys[layout_name]["o"].rect,
        "KEY_P": keyboard_layout.keys[layout_name]["p"].rect,
        "KEY_LEFTBRACKET": keyboard_layout.keys[layout_name]["["].rect,
        "KEY_RIGHTBRACKET": keyboard_layout.keys[layout_name]["]"].rect,
        "KEY_BACKSLASH": keyboard_layout.keys[layout_name]["\\"].rect,
        "KEY_CAPSLOCK": keyboard_layout.keys[layout_name]["caps lock"].rect,
        "KEY_A": keyboard_layout.keys[layout_name]["a"].rect,
        "KEY_S": keyboard_layout.keys[layout_name]["s"].rect,
        "KEY_D": keyboard_layout.keys[layout_name]["d"].rect,
        "KEY_F": keyboard_layout.keys[layout_name]["f"].rect,
        "KEY_G": keyboard_layout.keys[layout_name]["g"].rect,
        "KEY_H": keyboard_layout.keys[layout_name]["h"].rect,
        "KEY_J": keyboard_layout.keys[layout_name]["j"].rect,
        "KEY_K": keyboard_layout.keys[layout_name]["k"].rect,
        "KEY_L": keyboard_layout.keys[layout_name]["l"].rect,
        "KEY_SEMICOLON": keyboard_layout.keys[layout_name][";"].rect,
        "KEY_QUOTE": keyboard_layout.keys[layout_name]["'"].rect,
        "KEY_LEFTSHIFT": keyboard_layout.keys[layout_name]["left shift"].rect,
        "KEY_Z": keyboard_layout.keys[layout_name]["z"].rect,
        "KEY_X": keyboard_layout.keys[layout_name]["x"].rect,
        "KEY_C": keyboard_layout.keys[layout_name]["c"].rect,
        "KEY_V": keyboard_layout.keys[layout_name]["v"].rect,
        "KEY_B": keyboard_layout.keys[layout_name]["b"].rect,
        "KEY_N": keyboard_layout.keys[layout_name]["n"].rect,
        "KEY_M": keyboard_layout.keys[layout_name]["m"].rect,
        "KEY_COMMA": keyboard_layout.keys[layout_name][","].rect,
        "KEY_PERIOD": keyboard_layout.keys[layout_name]["."].rect,
        "KEY_SLASH": keyboard_layout.keys[layout_name]["/"].rect,
        "KEY_RIGHTSHIFT": keyboard_layout.keys[layout_name]["right shift"].rect,
        "KEY_LEFTCTRL": keyboard_layout.keys[layout_name]["left ctrl"].rect,
        "KEY_LEFTMETA": keyboard_layout.keys[layout_name]["left meta"].rect,
        "KEY_LEFTALT": keyboard_layout.keys[layout_name]["left alt"].rect,
        "KEY_SPACE": keyboard_layout.keys[layout_name]["space"].rect,
        "KEY_RIGHTALT": keyboard_layout.keys[layout_name]["right alt"].rect,
        "KEY_RIGHTMETA": keyboard_layout.keys[layout_name]["right meta"].rect,
        "KEY_CONTEXTMENU": keyboard_layout.keys[layout_name]["context menu"].rect,
        "KEY_RIGHTCTRL": keyboard_layout.keys[layout_name]["right ctrl"].rect,}


def generate_heatmap(data):
    # Filter data to consider only KEY_ values
    data = data[data['id'].str.startswith('KEY_')]

    # Pivot the data into a matrix
    data_pivot = data.pivot_table(index='id', values='total_count', aggfunc='sum')

    # Reverse the data (biggest number shows up first)
    data_pivot = data_pivot.sort_values('total_count', ascending=False)

    # Create the heatmap
    plt.figure(figsize=(10, 20))
    sns.heatmap(data_pivot, annot=True, fmt=".0f", cmap="YlGnBu", cbar=False)
    plt.title("Heatmap")
    plt.tight_layout()
    plt.show()


def fetch_data(query, db_path):
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)
    return df


def get_screen():
    XY = namedtuple('XY', ['x', 'y'])
    try:
        screen = xlib.display.Display().screen()
        width_px = screen['width_in_pixels']
        height_px = screen['height_in_pixels']
        width_mm = screen['width_in_mms']
        height_mm = screen['height_in_mms']
        return XY(width_px, height_px), XY(width_mm, height_mm)
    except:
        # not sure
        return XY(1, 1), XY(1, 1)


MODIFIERS = {
    'KEY_SHIFT_L': 0x1,
    'KEY_CONTROL_L': 0x2,
    'KEY_ALT_L': 0x4,
    'KEY_META_L': 0x8,
    'KEY_SUPER_L': 0x10,
                            # treat left and right as the same (for now)
    'KEY_SHIFT_R': 0x1,
    'KEY_CONTROL_R': 0x2,
    'KEY_ALT_R': 0x4,
    'KEY_META_R': 0x8,
    'KEY_SUPER_R': 0x10,}


class Storage:
    # Simple record storage.
    # An open paren:
    # KEY_9, 1, 0, 0, 0, 0, 314, 9/25/2015, 19
    # 0x224

    SCHEMA = [
        '''
create table keyboard(
    id text,
    count int,
    day date,
    hour int,
    shift int,
    ctrl int,
    alt int,
    meta int,
    super int,
    primary key (id, day, hour, shift, ctrl, alt, meta, super)
);''', '''create table mouse(
    id text,
    count int,
    day date,
    hour int,
    shift int,
    ctrl int,
    alt int,
    meta int,
    super int,
    primary key (id, day, hour, shift, ctrl, alt, meta, super)
);''', '''create table mouse_distance(
    x int,
    y int,
    dist real,
    day date,
    hour int,
    primary key (day, hour)
);''', '''create table schema_version(version int);''', '''insert into schema_version(version) values (1);''']

    def __init__(self, path):
        self.db = path
        with sqlite3.connect(self.db) as conn:
            create = False
            try:
                conn.execute('select version from schema_version')
            except sqlite3.OperationalError:
                create = True

            if create:
                print("Initialize database...")
                for statement in self.SCHEMA:
                    print(statement)
                    conn.execute(statement)

    def _write_keyboard(self, conn, keyboard, when, hour):
        keyboard_update = '''
            update or ignore keyboard
                set count = count + :count
            where
                id = :key
            and shift = :shift
            and ctrl = :ctrl
            and alt = :alt
            and meta = :meta
            and super = :super
            and day = :day
            and hour = :hour'''

        keyboard_insert = '''insert or ignore into keyboard (
                id,
                shift, ctrl, alt, meta, super,
                count, day, hour)
            values (
                :key,
                :shift, :ctrl, :alt, :meta, :super,
                :count, :day, :hour)'''

        params = [{
            'key': key[0],
            'count': value,
            'day': when,
            'hour': hour,
            'shift': (key[1] & MODIFIERS['KEY_SHIFT_L']) > 0,
            'ctrl': (key[1] & MODIFIERS['KEY_CONTROL_L']) > 0,
            'alt': (key[1] & MODIFIERS['KEY_ALT_L']) > 0,
            'meta': (key[1] & MODIFIERS['KEY_META_L']) > 0,
            'super': (key[1] & MODIFIERS['KEY_SUPER_L']) > 0,} for key, value in keyboard.items()]

        # First, update any values that exist
        conn.executemany(keyboard_update, params)

        # Then, insert any new values
        conn.executemany(keyboard_insert, params)

    def _write_mouse(self, conn, mouse, when, hour):
        mouse_update = '''
            update or ignore mouse
                set count = count + :count
            where
                id = :key
            and shift = :shift
            and ctrl = :ctrl
            and alt = :alt
            and meta = :meta
            and super = :super
            and day = :day
            and hour = :hour'''

        mouse_insert = '''
            insert or ignore into mouse(id,
                shift, ctrl, alt, meta, super,
                count, day, hour)
            values (
                :key,
                :shift, :ctrl, :alt, :meta, :super,
                :count, :day, :hour)'''

        params = [{
            'key': key[0],
            'count': value,
            'day': when,
            'hour': hour,
            'shift': (key[1] & MODIFIERS['KEY_SHIFT_L']) > 0,
            'ctrl': (key[1] & MODIFIERS['KEY_CONTROL_L']) > 0,
            'alt': (key[1] & MODIFIERS['KEY_ALT_L']) > 0,
            'meta': (key[1] & MODIFIERS['KEY_META_L']) > 0,
            'super': (key[1] & MODIFIERS['KEY_SUPEsR_L']) > 0,} for key, value in mouse.items()]

        # First, update any values that exist
        conn.executemany(mouse_update, params)

        # Then, insert any new values
        conn.executemany(mouse_insert, params)

    def _write_mouse_distance(self, conn, distance, when, hour):
        x, y = distance

        select = '''select x, y from mouse_distance
                        where day = :day and hour = :hour'''
        delete = '''delete from mouse_distance
                        where day = :day and hour = :hour'''
        insert = '''insert into mouse_distance(x, y, dist, day, hour)
                        values (:x, :y, :dist, :day, :hour)'''

        row = conn.execute(select, {'day': when, 'hour': hour})
        row = row.fetchone()
        if row:
            oldx = row[0]
            oldy = row[1]
            x += oldx
            y += oldy
            conn.execute(delete, {'day': when, 'hour': hour})

        dist = (x**2 + y**2)**0.5
        conn.execute(insert, {'x': x, 'y': y, 'dist': dist, 'day': when, 'hour': hour})

    def write_data(self, keyboard, mouse, when, distance):
        hour = when.strftime('%H')
        when = when.date()
        print("Hour =", hour, "when =", when)

        with sqlite3.connect(self.db) as conn:
            self._write_keyboard(conn, keyboard, when, hour)
            self._write_mouse(conn, mouse, when, hour)
            self._write_mouse_distance(conn, distance, when, hour)

    def clear_current_hour(self):
        """Zero the last hour
        """
        with sqlite3.connect(self.db) as conn:
            when = datetime.now()
            hour = when.strftime('%H')
            when = when.date()
            params = {'when': when, 'hour': hour}
            conn.execute('delete from keyboard where day = :when and hour = :hour', params)
            conn.execute('delete from mouse where day = :when and hour = :hour', params)
            conn.execute('delete from mouse_distance where day = :when and hour = :hour', params)

    def clear_current_day(self):
        """Zero the current day
        """
        with sqlite3.connect(self.db) as conn:
            when = datetime.now().date()
            params = {'when': when}
            conn.execute('delete from keyboard where day = :when', params)
            conn.execute('delete from mouse where day = :when', params)
            conn.execute('delete from mouse_distance where day = :when', params)

    def clear_all(self):
        """Zero everything (removes database)
        """
        os.remove(self.db)

    def print_stats(self):
        with sqlite3.connect(self.db) as conn:
            top5_keys = 'select id, sum(count) from keyboard group by id order by 2 desc limit 5'
            cursor = conn.execute(top5_keys)
            row = cursor.fetchall()
            print("Top 5 Keys:", row)

            when = datetime.now()
            hour = when.strftime('%H')
            when = when.date()
            total_mouse_this_hour = '''
            select x, y from mouse_distance
            where day = :when and hour = :hour'''
            cursor = conn.execute(total_mouse_this_hour, {'when': when, 'hour': hour})
            row = cursor.fetchone()

            screen_px, screen_mm = get_screen()
            mm_px_x = screen_mm.x / screen_px.x
            mm_px_y = screen_mm.y / screen_px.y

            inch_per_foot = 12
            foot_per_meter = 1 / 0.3048
            meter_per_mm = 0.001
            inch_per_mm = inch_per_foot * foot_per_meter * meter_per_mm
            # IN FT M_ MM
            # FT M_ MM PX

            in_px_x = mm_px_x * inch_per_mm
            in_px_y = mm_px_y * inch_per_mm

            x_px, y_px = row
            mouse_distance_m = ((x_px * mm_px_x * meter_per_mm)**2 + (y_px * mm_px_y * meter_per_mm)**2)**0.5
            print("Mouse distance during current hour: %.1f meters" % (mouse_distance_m))

            mouse_buttons = 'select id, sum(count) from mouse group by id order by count desc limit 5'
            cursor = conn.execute(mouse_buttons)
            row = cursor.fetchall()
            print("Mouse buttons:", row)


def is_mouse(event):
    return event.type.startswith('EV_MOV', 'EV_REL')


class KbdCounter(object):
    def __init__(self, options):
        self.storepath = os.path.expanduser(options.storepath)

        self.set_thishour()
        self.set_nextsave()

        # map of (KEY_I, M): K, where M = modifier state, K = count
        self.keyboard_events = Counter()
        # map of (BTN_LEFT, M): count
        self.mouse_events = Counter()

        self.mouse_distance_x = 0
        self.mouse_distance_y = 0
        self.wheel_up = 0
        self.wheel_down = 0

    def set_thishour(self):
        self.thishour = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.nexthour = self.thishour + timedelta(hours=1)
        self.thishour_count = 0

    def set_nextsave(self):
        save_every = 300 # 5 minutes
        now = time.time()
        self.nextsave = now + min((self.nexthour - datetime.now()).seconds + 1, save_every)

    def save(self):
        self.set_nextsave()
        storage = Storage(self.storepath)
        try:
            storage.write_data(self.keyboard_events, self.mouse_events, self.thishour, (self.mouse_distance_x, self.mouse_distance_y))
            self.keyboard_events.clear()
            self.mouse_events.clear()
            self.mouse_distance_x = 0
            self.mouse_distance_y = 0
        except sqlite3.OperationalError as e:
            print("Error saving data", e)

    def run(self):
        events = XEvents()
        events.start()
        while not events.listening():
            # Wait for init
            time.sleep(1)

        last_mov = None

        try:
            modifier_state = 0

            while events.listening():
                evt = events.next_event()
                if not evt:
                    time.sleep(0.5)
                    continue

                # read modifier state
                if evt.type == 'EV_KEY' and evt.code in MODIFIERS.keys():
                    if evt.value:
                        modifier_state |= MODIFIERS[evt.code]
                    else:
                        modifier_state &= ~MODIFIERS[evt.code]

                # Key press (evt.value == 1) or release (evt.value == 0)
                if evt.type == 'EV_KEY' and evt.value == 1:
                    if evt.code.startswith('KEY'):
                        if evt.code == 'KEY_DUNNO':
                            idx = (evt.scancode, modifier_state)
                        else:
                            idx = (evt.code, modifier_state)
                        self.keyboard_events[idx] += 1

                    if evt.code.startswith('BTN'):
                        self.mouse_events[(evt.code, modifier_state)] += 1

                if evt.type == 'EV_MOV':
                    # EV_MOV's value is a tuple with the current mouse coordinates.
                    # To track movement, we need to compare with the last position
                    x, y = evt.value
                    if last_mov:
                        self.mouse_distance_x += abs(x - last_mov[0])
                        self.mouse_distance_y += abs(y - last_mov[1])

                    last_mov = x, y

                # Scrolling
                if evt.type == 'EV_REL':
                    if evt.code == 'REL_WHEEL':
                        if evt.value > 0:
                            self.mouse_events[('WHEEL_UP', modifier_state)] += evt.value
                        if evt.value < 0:
                            self.mouse_events[('WHEEL_DOWN', modifier_state)] += -evt.value

                if evt.code == 'REL_WHEEL' or (evt.type == 'EV_KEY' and evt.value == 1 and evt.code not in MODIFIERS.keys(
                )):
                    print("type %s value %s code %s scancode %s" % (evt.type, evt.value, evt.code, evt.scancode),
                          end=' ')
                    print("S:%d C:%d A:%d M:%d S:%d" % (modifier_state & MODIFIERS['KEY_SHIFT_L'], modifier_state & MODIFIERS['KEY_CONTROL_L'], modifier_state
                                                        & MODIFIERS['KEY_ALT_L'], modifier_state & MODIFIERS['KEY_META_L'], modifier_state & MODIFIERS['KEY_SUPER_L']))

                if time.time() > self.nextsave:
                    print("Mouse:", self.mouse_distance_x, self.mouse_distance_y)
                    self.save()

                    if datetime.now().hour != self.thishour.hour:
                        self.set_thishour()

        except KeyboardInterrupt:
            events.stop_listening()
            self.save()


def generate_heatmap(data):
    layout_name = kl.LayoutName.QWERTY
    pygame.init()

    grey = pygame.Color('grey')
    # set the keyboard position and color info
    keyboard_info = kl.KeyboardInfo(position=(0, 0), padding=2, color=~grey)
    # set the letter key color, padding, and margin info in px
    key_info = kl.KeyInfo(
        margin=10,
        color=grey,
        txt_color=~grey,                                      # invert grey
        txt_font=pygame.font.SysFont('Arial', KEY_SIZE // 4),
        txt_padding=(KEY_SIZE // 6, KEY_SIZE // 10))
                                                              # set the letter key size info in px
    letter_key_size = (KEY_SIZE, KEY_SIZE)                    # width, height
    keyboard_layout = klp.KeyboardLayout(layout_name, keyboard_info, letter_key_size, key_info)
                                                              # set the pygame window to the size of the keyboard
    screen = pygame.display.set_mode((keyboard_layout.rect.width, keyboard_layout.rect.height))
    screen.fill(pygame.Color('black'))

    # draw the keyboard on the pygame screen
    keyboard_layout.draw(screen)
    pygame.display.update()

    key_positions = get_key_positions(keyboard_layout, layout_name)

    # loop until the user closes the pygame window
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                running = False

        # Clear the screen
        screen.fill(pygame.Color('black'))

        # Redraw the keyboard
        keyboard_layout.draw(screen)

        # Draw the heatmap on the keys
        draw_heatmap_on_keys(screen, keyboard_layout, data, key_positions)

        # Update the display
        pygame.display.update()

    pygame.quit()


def draw_heatmap_on_keys(screen, layout, data, key_positions):
    # Filter data to consider only KEY_ values
    data = data[data['id'].str.startswith('KEY_')]

    # Draw the heatmap on the keyboard layout
    for _, row in data.iterrows():
        key_id = row['id']
        count = row['total_count']

        # Get the key rect from the layout
        key_rect = key_positions[key_id]

        # Customize the heatmap's color and transparency (alpha) based on the count
        color = pygame.Color(0, 0, 255, int(255 * count / data['total_count'].max()))

        # Draw a translucent rectangle for each key with the appropriate color
        surf = pygame.Surface((key_rect.width, key_rect.height), pygame.SRCALPHA)
        surf.fill(color)
        screen.blit(surf, key_rect.topleft)

        # Add key count text
        font = pygame.font.SysFont('Arial', KEY_SIZE // 4)
        text_surface = font.render(str(int(count)), True, pygame.Color('white'))
        text_rect = text_surface.get_rect()
        text_rect.center = key_rect.center
        screen.blit(text_surface, text_rect)


def run():
    oparser = OptionParser()
    oparser.add_option("--storepath",
                       dest="storepath",
                       help="Filename into which number of keypresses per hour is written",
                       default="~/.kbdcounter.db")
    oparser.add_option("--report", dest='report', action="store_true", help="Print some statistics", default=False)
    oparser.add_option("--zero-hour",
                       dest='zero_hour',
                       action="store_true",
                       help="Zero data for the current hour",
                       default=False)
    oparser.add_option("--zero-day",
                       dest='zero_day',
                       action="store_true",
                       help="Zero data for the current day",
                       default=False)
    oparser.add_option("--zero-all",
                       dest='zero_all',
                       action="store_true",
                       help="Zero all data (erases database file)",
                       default=False)

    (options, args) = oparser.parse_args()

    options.storepath = os.path.expanduser(options.storepath)
    options.storepath = os.path.expandvars(options.storepath)

    # if options.report:
    query = "SELECT id, SUM(count) as total_count FROM keyboard GROUP BY id"
    data = fetch_data(query, options.storepath)
    generate_heatmap(data)
    # print (options.storepath)
    # storage = Storage(options.storepath)
    # storage.print_stats()
    return

    if options.zero_hour:
        Storage(options.storepath).clear_current_hour()
        print("Cleared")
        return

    if options.zero_day:
        Storage(options.storepath).clear_current_day()
        print("Cleared")
        return

    if options.zero_all:
        Storage(options.storepath).clear_all()
        print("Database deleted")
        return

    kc = KbdCounter(options)
    kc.run()

    print("And we're done")


if __name__ == '__main__':
    run()
