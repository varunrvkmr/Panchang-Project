cat > entrypoint.sh <<'EOF'
#!/bin/sh
set -e

# 1) write your token
ngrok config add-authtoken "${NGROK_AUTHTOKEN}"

# 2) hand off to the tunnel process
exec ngrok http web:5050
EOF

# make it executable
chmod +x entrypoint.sh
