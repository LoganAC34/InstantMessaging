import os
import pathlib
import queue
import sys


class GlobalVars(object):
    # Relative and exe paths
    """
    try:
        # we are running in a bundle
        # noinspection PyProtectedMember
        exe = sys._MEIPASS + '\\'
        relative = os.path.dirname(sys.executable) + '\\'
    except AttributeError:
        # we are running in a normal Python environment
        exe = os.path.dirname(os.path.abspath(__file__)) + '\\'
        relative = '\\'.join(exe.split('\\')[:-2]) + '\\'
    """

    # Get exe location
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        print('Frozen')
        # noinspection PyProtectedMember
        exe = sys._MEIPASS + '\\'
        app_path = sys.executable
        debug = False
    else:
        # we are running in a normal Python environment
        print('Not frozen')
        exe = os.path.abspath('./') + '\\'
        app_path = os.path.abspath('../../Testing/Local_Instant_Messenger.exe')
        debug = True

    # Home directory
    my_data_dir = pathlib.Path.home() / 'AppData/Roaming' / "Local_Instant_Messenger"
    if not os.path.isdir(my_data_dir):
        my_data_dir.mkdir(parents=True)

    # Pickle variable files
    pkl_sha = my_data_dir / 'sha.pkl'
    pkl_update = my_data_dir / 'update.pkl'
    plk_IP = my_data_dir / 'ip.pkl'

    # Global Variables
    icon = exe + 'Local_Instant_Messenger.ico'
    maxCharacterLength = 256
    lineBreak = '\r'

    cfgFile_path = os.path.join(my_data_dir, 'config.cfg')  # Config file
    pwl_path = os.path.join(my_data_dir, 'user_dictionary.txt')  # Personal dictionary

    # Server
    queue_to_server = queue.Queue()
    queue_from_server = queue.Queue()