#!/bin/bash

if [ -n "$VNC_PASSWORD" ]; then
    echo "Setting VNC password from environment variable..."
    mkdir -p /home/chrome/.vnc
    x11vnc -storepasswd "$VNC_PASSWORD" /home/chrome/.vnc/passwd
fi

# Check manifest
if [ -f "/home/chrome/extension/manifest.json" ]; then
    echo "✓ Extension manifest found"
    echo "Extension content:"
    find /home/chrome/extension/ -type f | head -20
else
    echo "✗ Extension manifest NOT found!"
    echo "Available files in extension directory:"
    find /home/chrome/extension/ -type f
    exit 1
fi

# Chrome profile
mkdir -p /home/chrome/chrome-profile
mkdir -p /home/chrome/chrome-profile/Default

cat > /home/chrome/chrome-profile/Default/Preferences << 'EOF'
{
  "extensions": {
    "settings": {
      "ibffcdnaaoagnnbemdielinlpjalhkhb": {
        "active_permissions": {
          "api": ["scripting", "activeTab", "downloads", "storage"],
          "explicit_host": ["https://*/*", "http://*/*", "http://localhost/*"],
          "manifest_permissions": [],
          "scriptable_host": []
        },
        "commands": {
          "_execute_action": {
            "was_assigned": true
          }
        },
        "service_worker_registration_info": {
          "version": "0.1.1"
        },
        "serviceworkerevents": ["runtime.onInstalled","storage.local.onChanged"],
        "creation_flags": 38,
        "enabled": true,
        "first_install_time": "13291366331567067",
        "from_webstore": false,
        "incognito_enabled": true,
        "last_update_time": "13291366331567067",
        "location": 4,
        "manifest": {
          "name": "Universal Scraper",
          "description": "Universal Scraper (UniScrap) extension. Able to work with RabbitMQ Web STOMP plugin and also start tasks manually through popup.",
          "version": "0.1.1",
          "manifest_version": 3,
          "icons": {
            "16": "icon/16.png",
            "32": "icon/32.png",
            "48": "icon/48.png",
            "96": "icon/96.png",
            "128": "icon/128.png"
          },
          "action": {
            "default_popup": "src/popup.html"
          },
          "permissions": ["scripting", "activeTab", "downloads", "storage"],
          "host_permissions": ["https://*/*", "http://*/*", "http://localhost/*"],
          "background": {
            "service_worker": "src/background.js"
          },
          "update_url": "http://cp.nyle.ai:8091/ext/update/uniscrap.xml",
          "content_security_policy": {
            "extension_pages": "script-src 'self' 'wasm-unsafe-eval' http://localhost:*; object-src 'self';"
          }
        },
        "path": "/home/chrome/extension",
        "state": 1,
        "was_installed_by_default": false,
        "withholding_permissions": false
      }
    },
    "ui": {
      "developer_mode": true
    }
  },
  "browser": {
    "has_seen_welcome_page": true
  },
  "profile": {
    "content_settings": {
      "exceptions": {
        "notification": {
          "https://*,*": {
            "setting": 2
          }
        }
      }
    },
    "exit_type": "Normal",
    "exited_cleanly": true
  }
}
EOF

export DISPLAY=:99
Xvfb "$DISPLAY" -screen 0 1920x1080x24 &

# Wait for Xvfb...
sleep 2

if [ -f /home/chrome/.vnc/passwd ]; then
    echo "Starting VNC with password..."
    x11vnc -forever -noxdamage -shared -rfbport 5900 -passwd /home/chrome/.vnc/passwd -display :99 &
else
    echo "Starting VNC without password..."
    x11vnc -forever -noxdamage -shared -rfbport 5900 -display :99 &
fi

google-chrome-stable \
    --disable-gpu \
    --disable-dev-shm-usage \
    --user-data-dir=/home/chrome/chrome-profile \
    --disable-default-apps \
    --no-first-run \
    --no-default-browser-check \
    --disable-sync \
    --enable-logging \
    --v=1 \
    --extension-metrics-opt-in=true \
    --enable-extension-activity-logging \
    --disable-features=ExtensionsManifestV2DeprecationWarning \
    --whitelisted-extension-id=ibffcdnaaoagnnbemdielinlpjalhkhb \
    --enable-experimental-extension-apis