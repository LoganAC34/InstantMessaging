import os
import shutil
import subprocess
import sys
from datetime import date

import PyInstaller.__main__

dir_PyCharm = os.path.abspath('.')
dir_path = os.path.abspath('src')
build = os.path.join(dir_PyCharm, 'build\\')

dir_name = os.path.basename(os.path.abspath('.'))
dst = os.path.join('C:/Temp', dir_name)
if os.path.isdir(dst):
    shutil.rmtree(dst)
shutil.copytree(dir_path, dst)

# Create file with build date
with open(os.path.join(dir_path, 'resources/build_date.txt'), 'w') as f:
    f.write(date.today().strftime('%B {}, %Y'.format(date.today().day)))

# Update script
PyInstaller.__main__.run([
    os.path.join(dst, r'scripts/update.py'),
    '--workpath', build,
    '--specpath', build,
    '--distpath', os.path.join(dst, 'scripts'),
    '--noconsole',
    '-F'
])

# Main script
PyInstaller.__main__.run([
    os.path.join(dst, 'main.py'),
    '-n', 'Local_Instant_Messenger',
    '--workpath', build,
    '--specpath', build,
    '--distpath', dir_PyCharm,
    '-F',
    '--noconsole',  # Comment out for console to appear when running app
    '--icon', os.path.join(dir_path, 'resources', 'Local_Instant_Messenger.ico'),
    '--hidden-import', 'wx.adv',
    '--hidden-import', 'wx.xml',
    # '--add-data', f'{sys.prefix}/Lib/site-packages/wx/WebView2Loader.dll.lib;./wx',  # Don't need?
    # '--add-data', f'{sys.prefix}/Lib/site-packages/wx/WebView2LoaderStatic.lib;./wx', # Don't need?
    '--add-data', f'{sys.prefix}/Lib/site-packages/wx/WebView2Loader.dll;./wx',  # Otherwise the chat window doesn't show
    '--add-data', f'{sys.prefix}/Lib/site-packages/enchant;./enchant',  # Otherwise enchant errors
    '--add-data', f'{sys.prefix}/Lib/site-packages/emoji;./emoji',  # Otherwise emoji errors
    # '--debug=imports',
    '--add-data', rf'{dst};.'
])

shutil.rmtree(dst)

pigar_script = (f'cd {dir_PyCharm} '
                f'&& {sys.executable} -m pigar generate --question-answer no')
subprocess.run(pigar_script, cwd=dir_PyCharm, shell=True)
