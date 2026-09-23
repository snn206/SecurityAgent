#!/bin/bash
# Install/update all security tools in the Kali sandbox
set -e

TOOLS=(nmap gobuster sqlmap nikto whois curl)

echo "[+] Updating package lists..."
apt-get update -qq

for tool in "${TOOLS[@]}"; do
    echo "[+] Installing/updating: $tool"
    apt-get install -y --no-install-recommends "$tool" 2>/dev/null || true
done

echo "[+] All tools installed."
