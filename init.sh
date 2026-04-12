#!/usr/bin/env bash
set -euo pipefail

echo "========================================="
echo " Codespace Environment Setup"
echo "========================================="

# -------------------------------------------
# 1. GitHub Copilot CLI (standalone binary via npm)
# -------------------------------------------
echo ""
echo "[1/3] Installing GitHub Copilot CLI..."
npm install -g @github/copilot
echo "  -> Done."

# -------------------------------------------
# 2. Azure CLI
# -------------------------------------------
echo ""
echo "[2/3] Installing Azure CLI..."
if command -v az &>/dev/null; then
    echo "  -> Azure CLI already installed ($(az version --output tsv --query '"azure-cli"' 2>/dev/null || echo 'unknown'))."
else
    sudo rm -f /etc/apt/sources.list.d/yarn.list
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi
echo "  -> Done."

# -------------------------------------------
# 3. uv (Python Package Manager)
# -------------------------------------------
echo ""
echo "[3/3] Installing uv..."
if command -v uv &>/dev/null; then
    echo "  -> uv already installed ($(uv --version 2>/dev/null || echo 'unknown')). Upgrading..."
    uv self update || true
else
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
echo "  -> Done."

# -------------------------------------------
# Summary
# -------------------------------------------
echo ""
echo "========================================="
echo " Setup Complete!"
echo "========================================="
echo ""
echo "Installed versions:"
echo "  copilot    : $(copilot --version 2>/dev/null || echo 'run: copilot --version')"
echo "  az         : $(az version --output tsv --query '"azure-cli"' 2>/dev/null || echo 'run: az --version')"
echo "  uv         : $(uv --version 2>/dev/null || echo 'run: uv --version')"
echo ""
