import cx_Freeze as cx
import platform
import os

base = None
include_files = [('contin-exe','contin-exe')]
target_name = 'DLS Analyzer'
#if platform.system() == "Windows":
    #base = "Win32GUI"
target_name = 'dls.exe'
PYTHON_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_DIR, 'tcl', 'tk8.6')
include_files += [
    (os.path.join(PYTHON_DIR, 'DLLs', 'tcl86t.dll'), ''),
    (os.path.join(PYTHON_DIR, 'DLLs', 'tk86t.dll'), '')
]


shortcut_data = [
    # (Type, Folder, Name, ?, Target exe, arguments, description, hotkey, icon, icon index, show cmd, Working dir)
    ('DesktopShortcut', 'DesktopFolder', 'DLS Analyzer', 'TARGETDIR',
     '[TARGETDIR]' + target_name, None,
     'Laser Tecniques', None,
     None, None, None, 'TARGETDIR'),
    ('MenuShortcut', 'ProgramMenuFolder', 'DLS Analyzer', 'TARGETDIR',
     '[TARGETDIR]' + target_name, None,
     'Laser Tecniques', None,
     None, None, None, 'TARGETDIR'),
]

cx.setup(
    name='DLS Analyzer',
    version='1.0',
    author='Elí A. Flores',
    author_email='eli1998flores@gmail.com',
    description='Optical Tecniques',
    #packages=['src', 'contin-exe'],
    executables=[
        cx.Executable(
            'app.py',
            base=base,
            target_name=target_name,
            icon='app.ico'
        )
    ],
    options={
        'build_exe': {
            'packages': ['serial', 'matplotlib', 'sklearn'],
            'includes': ['serial.tools', 'sklearn.preprocessing'],
            'include_files': include_files,
            'excludes': ['PyQt4', 'PyQt5', 'PySide', 'PySide6', 'IPython', 'jupyter_client','jupyter_core', 'ipykernel','ipython_genutils']
        },

        'bdist_msi': {
            # can be generated in powershell: "{"+[System.Guid]::NewGuid().ToString().ToUpper()+"}"
            'upgrade_code': '{2AE0AF4E-7A53-4827-9E62-9EB6CAE7FEE3}',
            'data': {'Shortcut': shortcut_data},
            'install_icon': 'app.ico'
        },
        'bdist_mac': {
            # Sets the application name
            'bundle_name': 'DLS Analyzer',
            'iconfile': 'app.icns'
        }
    }
)