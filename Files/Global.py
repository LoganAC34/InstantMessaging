import os
import pathlib
import sys


class GlobalVars(object):
    # Relative and exe paths
    try:
        # we are running in a bundle
        # noinspection PyProtectedMember
        exe = sys._MEIPASS + '\\'
        relative = os.path.dirname(sys.executable) + '\\'
    except AttributeError:
        # we are running in a normal Python environment
        exe = os.path.dirname(os.path.abspath(__file__)) + '\\'
        relative = '\\'.join(exe.split('\\')[:-2]) + '\\'

    # Get exe location
    if getattr(sys, 'frozen', False):
        app_path = sys.executable
    else:
        app_path = fr"{pathlib.Path.home()}\Downloads\Local_Instant_Messenger.exe"  # os.path.abspath(__file__)

    # Home directory
    my_data_dir = pathlib.Path.home() / 'AppData/Roaming' / "Local_Instant_Messenger"
    try:
        my_data_dir.mkdir(parents=True)
    except FileExistsError:
        pass

    # Pickle variable files
    pkl_sha = my_data_dir / 'sha.pkl'
    pkl_update = my_data_dir / 'update.pkl'
    plk_IP = my_data_dir / 'ip.pkl'

    # Global Variables
    icon = exe + 'Local_Instant_Messenger.ico'
    debug = False

    # Config file -------------------------------------------------
    cfgFile_path = os.path.join(my_data_dir, 'config.cfg')
