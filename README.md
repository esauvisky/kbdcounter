#    kdbcounter - a program for counting keyboard & mouse activity

This program keeps track of the number of input events that you make with your keyboard and mouse. 

Requires an X Windows environment such as Linux. (No Macintoshes or Windows, sorry). 

The results are are stored in a sqlite3 database file for later perusal.

Thanks to [Erik Forsberg](https://github.com/forsberg) for writing the original version. 

## Purpose

The purpose is to collect data on how you interact with your computer's input devices. It has no particular value above statistical curiosity. 

## Installation

This program uses Python, the sqlite3 module, and the Xlib module. If you are using an Ubuntu-derived system, your system python likely already has all the dependencies installed. 

If not, create a virtual environment: 

```
$ python -m virtualenv ~/kbdcounter_env
$ . ~/kbdcounter_env/bin/activate
$ pip install -r kbdcounter/requirements.txt
$ python kbdcounter.py
```

## Usage

### Run the program: 

`$ python kbdcounter.py`

### Report some statistics from the database

```
$ python kbdcounter.py --report
Top 5 Keys: [(u'KEY_SPACE', 337), (u'KEY_T', 200), 
(u'KEY_E', 199), (u'KEY_A', 153), (u'KEY_BACKSPACE', 152)]
Mouse distance during current hour: 19.2 meters
Mouse buttons: [(u'WHEEL_DOWN', 7614), (u'WHEEL_UP', 4546),
 (u'BTN_RIGHT', 35), (u'BTN_LEFT', 680), (u'BTN_MIDDLE', 2)]
```

*Mouse distance is the physical distance that the arrow on the screen has moved, based on the screen size reported by X11.*


Reporting is pretty rudimentary right now. More advanced reporting can be accomplished by using the SQLite database directly. 

#### Examples: 

Compute the all-time top five keys: 
```
$ sqlite3 ~/.kbdcounter.db "select id, sum(count) 
from keyboard group by id order by 2 desc limit 5"
KEY_SPACE|536
KEY_E|333
KEY_T|308
KEY_BACKSPACE|306
KEY_S|245
```

How many times did you type an upper-case letter? 
```
$ sqlite3 ~/.kbdcounter.db "select count(*) 
from keyboard where shift = 1 and id <> 'KEY_SHIFT_L'"
96
```

What's your favorite mouse button? 
```
sqlite3 ~/.kbdcounter.db "select id, sum(count) from mouse group by id order by 2 desc"
WHEEL_DOWN|7774
WHEEL_UP|4566
BTN_LEFT|743
BTN_RIGHT|35
BTN_MIDDLE|2
```

#### Schema

Data is stored in three tables.

Counts with modifier keys are stored separately, so a parenthesis (shift-9) shows as KEY_9 and shift=1, versus a just a number 9 shows as KEY_9 and shift=0. 

```
CREATE TABLE keyboard(
    id text,    -- The name of the key, or it's scancode if unknown
    count int,  -- Number of key down's (not ups)
    day date,   -- The day 
    hour int,   -- The hour
    shift int,  -- 1 if left or right shift was down
    ctrl int,   -- 1 if left or right control was down
    alt int,    -- 1 if left or right alt was down
    meta int,   -- 1 if left or right meta was down
    super int)  -- 1 if left or right super was down

CREATE TABLE mouse(
    id text,    -- The name of the button
    count int,  -- Number of clicks
    day date,   -- The day 
    hour int,   -- The hour
    shift int,  -- 1 if left or right shift was down
    ctrl int,   -- 1 if left or right control was down
    alt int,    -- 1 if left or right alt was down
    meta int,   -- 1 if left or right meta was down
    super int)  -- 1 if left or right super was down

CREATE TABLE mouse_distance(
    x int,      -- number of horizontal pixels moved
    y int,      -- number of vertical pixels moved
    dist real,  -- diagonal pixels moved [sqrt(x^2 + y^2)]
    day date,   -- the day
    hour int)   -- the hour
```

### Limitations

The program currently reports on events that it knows about, those from standard keyboards and mice. Events from other sources (e.g., tablets, buttons on the computer itself, maybe trackpads) may not be recognized, or may be confused with something else. 

It also records only raw input, and knows nothing of keyboard layouts. A "KEY_S" event may not necessarily mean that "S" was produced when you pressed that button. For example, "KEY_S" may correspond to "Σ" if you were using a Greek keyboard layout. 


## Security & Privacy

This program records _every keystroke_ that you make, **including passwords**, as well as mouse movement, scrolling, and button presses. It does not transmit this information anywhere, but it is stored in a sqlite database in your home directory. 

The information contained within the database is not a step-by-step record of everything entered, but an aggregation of entries made by hour. While I don't believe that this aggregation presents a direct security risk, it is technically possible to analyze the database to reconstruct (at least) the characters used in passwords. 

Although I can't imagine an attacker would use the database as an attack vector (indeed, if someone has access to the database file, then they already have access to your computer and could use more direct methods to obtain information), it is still a possibility.

**If you are uncomfortable with this, then do not use this software.** 



