#!/usr/bin/env bash
# exit on error
set -o errexit

# Where Chrome will be downloaded and cached between builds
STORAGE_DIR=/opt/render/project/.render/chrome
CHROME_URL=https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

echo "=== Setting up Google Chrome ==="

if [[ ! -d "$STORAGE_DIR/opt/google/chrome" ]]; then
  echo "...Downloading and extracting Google Chrome"
  mkdir -p "$STORAGE_DIR"
  wget -O "$STORAGE_DIR/chrome.deb" "$CHROME_URL"
  dpkg -x "$STORAGE_DIR/chrome.deb" "$STORAGE_DIR"
  rm "$STORAGE_DIR/chrome.deb"
else
  echo "...Using cached Chrome from $STORAGE_DIR"
fi

echo "=== Chrome setup complete ==="

# Optional: install Python dependencies if needed
pip install -r requirements.txt

# Reminder: in your Render **Start Command**, you'll need to add this to PATH:
# export PATH=$PATH:/opt/render/project/.render/chrome/opt/google/chrome && python app.py
