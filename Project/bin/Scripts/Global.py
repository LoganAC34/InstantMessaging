import os
import pathlib
import queue
import sys


class GlobalVars(object):
    # TODO: Update version number
    # TODO: Update changelog
    # MAJOR version when you make incompatible API changes
    # MINOR version when you add functionality in a backwards compatible manner
    # PATCH version when you make backwards compatible bug fixes
    version_number = 'v2.4.5'

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
        my_data_dir = pathlib.Path.home() / 'AppData/Roaming' / "Local_Instant_Messenger"
        debug = False
    else:
        # we are running in a normal Python environment
        print('Not frozen')
        exe = os.path.abspath('./') + '\\'
        app_path = os.path.abspath('../../Testing/Local_Instant_Messenger.exe')
        my_data_dir = pathlib.Path(os.path.abspath('../Testing/Local_Instant_Messenger'))
        debug = True

    # Home directory
    if not os.path.isdir(my_data_dir):
        my_data_dir.mkdir(parents=True)

    # Pickle variable files
    pkl_sha = my_data_dir / 'sha.pkl'
    pkl_update = my_data_dir / 'update.pkl'
    plk_IP = my_data_dir / 'ip.pkl'
    lockfile = my_data_dir / 'program.lock'

    # Global Variables
    icon = os.path.join(exe, 'Resources', 'Local_Instant_Messenger.ico')
    maxCharacterLength = 256
    lineBreak = '\r'
    allowed_keys = [8, 127, 305, 312, 313, 314, 315, 316, 317, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 364,
                    364, 366, 367, 370, 375, 376, 377, 378, 379, 380, 381, 382, 384, 385, 387, 388, 390, 391, 392]

    cfgFile_path = os.path.join(my_data_dir, 'config.cfg')  # Config file
    pwl_path = os.path.join(my_data_dir, 'user_dictionary.txt')  # Personal dictionary

    # Server
    queue_to_server = queue.Queue()
    queue_from_server = queue.Queue()
