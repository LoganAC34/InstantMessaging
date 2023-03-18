import os
import shutil

import PyInstaller.__main__

dir_PyCharm = os.path.abspath('../')
dir_path = os.path.abspath('./bin')
build = os.path.join(dir_PyCharm, 'build\\')

dir_name = os.path.basename(os.path.abspath('../'))
dst = os.path.join('C:/Temp', dir_name)
if os.path.isdir(dst):
    shutil.rmtree(dst)
shutil.copytree(dir_path, dst)

# Update script
PyInstaller.__main__.run([
    os.path.join(dst, r'Scripts/Update.py'),
    '--workpath', build,
    '--specpath', build,
    '--distpath', os.path.join(dst, 'Scripts'),
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
    '--noconsole',
    '--icon', os.path.join(dir_path, 'Local_Instant_Messenger.ico'),
    '--hidden-import', 'wx.adv',
    '--hidden-import', 'wx.xml',
    '--debug=imports',
    '--add-data', rf'{dir_path};.'
])

shutil.rmtree(dst)
