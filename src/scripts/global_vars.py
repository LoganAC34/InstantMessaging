import os
import pathlib
import queue
import sys
from fontTools import ttLib

class GlobalVars(object):
    # TODO: update version number
    # Update changelog!!!
    APP_NAME = 'Local Instant Messenger'
    APP_NAME_UNDERSCORE = APP_NAME.replace(' ', '_')
    PUBLISHER = 'OrangeByte'
    VERSION = 'v4.1.1'
    PYTHON_BUILD_VERSION = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
    GITHUB_REPO_LINK = 'https://github.com/LoganAC34/InstantMessaging'
    AUTHOR = 'LoganAC34'
    AUTHOR_LINK = 'https://github.com/LoganAC34'
    # MAJOR version when you make incompatible API changes
    # MINOR version when you add functionality in a backwards compatible manner
    # PATCH version when you make backwards compatible bug fixes

    # Relative and exe paths
    # Get exe location
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        print('Frozen')
        # noinspection PyProtectedMember
        exe = sys._MEIPASS + '\\'
        app_path = sys.executable
        my_data_dir = pathlib.Path.home() / 'AppData/Roaming' / APP_NAME_UNDERSCORE
        debug = False
    else:
        # we are running in a normal Python environment
        print('Not frozen')
        exe = os.path.abspath('./') + '\\'
        app_path = os.path.abspath(f'../Testing/{APP_NAME_UNDERSCORE}.exe')
        my_data_dir = pathlib.Path(os.path.abspath(f'../Testing/{APP_NAME_UNDERSCORE}'))
        debug = True

    path_resources = os.path.join(exe, 'resources')

    with open(os.path.join(path_resources, 'build_date.txt')) as f:
        BUILD_DATE = f.read().strip()

    # Home directory
    if not os.path.isdir(my_data_dir):
        my_data_dir.mkdir(parents=True)


    # Pickle variable files
    pkl_sha = my_data_dir / 'sha.pkl'
    pkl_update = my_data_dir / 'update.pkl'
    plk_IP = my_data_dir / 'ip.pkl'
    lockfile = my_data_dir / 'program.lock'

    # Global Variables
    program_icon = os.path.join(path_resources, 'Local_Instant_Messenger.ico')
    program_image = os.path.join(path_resources, 'vector-chat-icon-png_302635.png')
    company_logo = os.path.join(path_resources, 'OrangeByte_Logo.png')
    emoji_font = os.path.join(path_resources, 'NotoColorEmoji.ttf')  # https://github.com/googlefonts/noto-emoji/tree/main?tab=readme-ov-file
    emoji_font_name = ttLib.TTFont(emoji_font)['name'].getDebugName(1)
    maxCharacterLength = 256
    lineBreak = '\r'
    allowed_keys = [8, 127, 305, 312, 313, 314, 315, 316, 317, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 364,
                    364, 366, 367, 370, 375, 376, 377, 378, 379, 380, 381, 382, 384, 385, 387, 388, 390, 391, 392]

    cfgFile_path = os.path.join(my_data_dir, 'config.cfg')  # Config file
    pwl_path = os.path.join(my_data_dir, 'user_dictionary.txt')  # Personal dictionary

    emoji_directory = pathlib.Path(os.path.join(my_data_dir, "emojis"))
    if not os.path.isdir(emoji_directory):
        emoji_directory.mkdir(parents=True)

    # Server
    queue_server_and_app = queue.Queue()

    # Chat log HTML template
    edge_webview_installer = os.path.join(path_resources, 'MicrosoftEdgeWebview2Setup.exe')
    html_template_path = os.path.join(path_resources, 'message_log_template.html')
    html_template_code = open(html_template_path).read()
