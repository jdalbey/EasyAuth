#!/bin/bash

# Check if VENV_PATH is provided via command line argument
# e.g.:  build.sh /home/user/Py-venvs/EasyAuth/
if [ -z "$1" ]; then
  echo "Error: VENV_PATH is required."
  exit 1
else
  export VENV_PATH="$1"
fi

# Set the PYINSTALLER_PATH if it's not already set
if [ -z "$PYINSTALLER_PATH" ]; then
  export PYINSTALLER_PATH=$VENV_PATH"venv/bin"
fi

# Check if the version info file exists
if [ ! -f "assets/version_info.txt" ]; then
    echo "Error: assets/version_info.txt does not exist"
    exit 1
fi

# Display current content
echo "Version info $(cat assets/version_info.txt)"
echo "Update? "
read new_version

# Update only if input is not empty
if [ -n "$new_version" ]; then
    echo "$new_version" > assets/version_info.txt
    echo -n "New version accepted: "
    cat assets/version_info.txt
else
    echo Using $(cat assets/version_info.txt)
fi

# Check if PYINSTALLER_PATH is set
if [ -z "$PYINSTALLER_PATH" ]; then
    echo "Error: PYINSTALLER_PATH environment variable is not set"
    exit 1
fi

# Check if the directory exists
if [ ! -d "$PYINSTALLER_PATH" ]; then
    echo "Error: Directory $PYINSTALLER_PATH does not exist"
    exit 1
fi

# Create tmp file for current date
echo "   "$(date) > /tmp/build_date.txt

"$PYINSTALLER_PATH/pyinstaller" -y \
    --clean \
    --hidden-import "_cffi_backend" \
    --hidden-import 'html.parser' \
    --add-data "assets:assets" \
    --add-data "docs/Quick Start Guide.md:assets" \
    --add-data "/tmp/build_date.txt:assets" \
    --onefile \
    src/main.py

