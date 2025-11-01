#!/bin/bash

echo "🔄 Migrating to Python 3.12..."
echo ""

# Check if Python 3.12 is installed
# We use the full path we found: /usr/bin/python3.12
if ! [ -x "/usr/bin/python3.12" ]; then
    echo "❌ Python 3.12 not found at /usr/bin/python3.12. Please install it."
    # We will try to install it just in case
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3.12-dev
else
    echo "✅ Python 3.12 found at /usr/bin/python3.12"
fi

# Deactivate current environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo ""
    echo "Deactivating current virtual environment..."
    deactivate
fi

# Backup old venv
if [ -d "codebasejac-env" ]; then
    echo ""
    echo "Backing up old virtual environment..."
    mv codebasejac-env venv-backup-$(date +%Y%M%d-%H%M%S)
fi

# Create new virtual environment with Python 3.12 (using the full path)
echo ""
echo "Creating new 'codebasejac-env' with Python 3.12..."
/usr/bin/python3.12 -m venv codebasejac-env

# Activate new environment
echo "Activating 'codebasejac-env'..."
source codebasejac-env/bin/activate

# Verify Python version
echo ""
echo "New virtual environment Python version:"
python --version

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install root/backend dependencies
echo ""
echo "Installing backend dependencies from ./requirements.txt..."
pip install -r requirements.txt

# Install frontend dependencies
if [ -d "frontend" ]; then
    echo ""
    echo "Installing frontend dependencies from ./frontend/requirements.txt..."
    pip install -r frontend/requirements.txt
fi

echo ""
echo "✅ Migration complete!"
echo ""
echo "Your 'codebasejac-env' environment is now using Python 3.12"
echo "To activate in the future, run: source codebasejac-env/bin/activate"

