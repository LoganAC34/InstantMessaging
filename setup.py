import os
import shutil

import PyInstaller.__main__

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_name = dir_path.split('\\')[-1]
dst = 'C:/Temp/' + dir_name + '/'
try:
    shutil.rmtree(dst)
except FileNotFoundError:
    pass
shutil.copytree(dir_path + '/Files/', dst)

# Main script
PyInstaller.__main__.run([
    dst + 'Local_Instant_Messenger.py',
    '--distpath', dir_path,
    '-F',
    '--noconsole',
    #'--hidden-import', 'PYTHONCOM',
    #'--debug=imports',
    #'--add-data', dst + 'db_template.db;.',
])

shutil.rmtree(dst)

