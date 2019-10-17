import atexit
import clockify
import configparser
from ctypes import Structure, windll, c_uint, sizeof, byref
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import json
import signal
import sys
import threading
import wx.adv
import wx


config = configparser.ConfigParser()
config.read('config.ini')

LOOP_TIME = int(config['idleless'].get('CheckRateMinutes', 3)) * 60  # seconds
IDLE_THRESHOLD = int(config['idleless'].get('IdleThresholdMinutes', 15)) * 60  # seconds

TRAY_TOOLTIP = 'Clockify Idleless'
TRAY_ICON = 'Clockify.ico'

CACHE_FILE = 'cache.json'
CACHE = {}


def load_cache():
    try:
        with open(CACHE_FILE) as json_file:
            json_dict = json.load(json_file)
            for key, value in json_dict.items():
                CACHE[key] = value
    except FileNotFoundError:
        pass


def dump_cache():
    with open(CACHE_FILE, 'w') as json_file:
        json.dump(CACHE, json_file)


def start_timer():
    if is_timer_running():
        return

    print('▶ Start timer')
    current_time_entry = clockify.get_new_time_entry()
    response = clockify.send_time_entry(current_time_entry)
    CACHE['current_time_entry'] = current_time_entry
    CACHE['current_time_entry_id'] = response['id']
    CACHE['start_timestamp'] = datetime.timestamp(datetime.now(timezone.utc))
    CACHE['last_active_timestamp'] = datetime.timestamp(datetime.now())
    return current_time_entry


def stop_timer(end_datetime=None):
    if not is_timer_running():
        return

    if not end_datetime:
        end_datetime = datetime.now(timezone.utc)

    print('■ Stop timer: {}'.format(end_datetime))
    CACHE['current_time_entry']['end'] = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    response = clockify.send_time_entry(CACHE['current_time_entry'], CACHE['current_time_entry_id'])
    del CACHE['current_time_entry']
    del CACHE['current_time_entry_id']
    del CACHE['last_active_timestamp']
    del CACHE['start_timestamp']
    return response


def exit_app():
    stop_timer()
    dump_cache()
    CACHE['exit'] = True
    print('Exiting... Have a nice day!')


def is_timer_running():
    return 'current_time_entry' in CACHE


def idle_check():
    if CACHE.get('exit', False):
        return

    t = threading.Timer(LOOP_TIME, idle_check)
    t.daemon = True
    t.start()

    now_timestamp = datetime.timestamp(datetime.now(timezone.utc))
    if is_timer_running():
        time_diff = now_timestamp - CACHE['last_active_timestamp']
        if time_diff > max(LOOP_TIME, IDLE_THRESHOLD) * 2:
            print('Process slept/suspended/stopped')
            stop_timer(datetime.fromtimestamp(CACHE['last_active_timestamp'], timezone.utc))
        elif datetime.now().day > datetime.fromtimestamp(CACHE['start_timestamp']).day:
            print('We crossed midnight')
            stop_timer()

    idle_duration = get_idle_duration()
    if idle_duration > IDLE_THRESHOLD:
        print('Idle for {}'.format(idle_duration))
        stop_timer()
    else:
        # TODO: check if a task is in progress online
        start_timer()

        # let's keep the file updated in case of a unexpected shutdown or sleep happens
        CACHE['last_active_timestamp'] = now_timestamp
    dump_cache()


class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]


def get_idle_duration():
    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = sizeof(last_input_info)
    windll.user32.GetLastInputInfo(byref(last_input_info))
    millis = windll.kernel32.GetTickCount() - last_input_info.dwTime
    return millis / 1000.0


#
# UI - Tray Icon
#
def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Duration', self.on_duration)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print ('Tray icon was left-clicked.')

    def on_duration(self, event):
        print ('Duration pressed')
        duration = datetime.timestamp(datetime.now(timezone.utc)) - CACHE['start_timestamp']
        duration = str(timedelta(seconds=round(duration)))
        wx.MessageBox("Time entry duration: {}.".format(duration),
                            "Clockify Duration", wx.OK | wx.ICON_INFORMATION)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()


class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True


def main():
    load_cache()
    idle_check()
    app = App(False)
    app.MainLoop()


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)
    print('Exiting gracefully')
    exit_app()
    sys.exit(1)


if __name__ == '__main__':
    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    atexit.register(exit_app)
    main()
