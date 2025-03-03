from setuptools import setup

APP = ['main.py']  # Replace with your main script name
DATA_FILES = []         # List any additional files/folders (images, sounds, etc.)
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame', 'pyttsx3'],  # Include any packages your game uses
    # You can add more options like 'includes', 'excludes', etc.
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)