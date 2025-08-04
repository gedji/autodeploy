#!/bin/bash
# AutoDeploy Repository Cleanup Script
# Removes temporary files, logs, and build artifacts

echo "Starting AutoDeploy repository cleanup..."

# Remove Python cache files
if [ -d "__pycache__" ]; then
    echo "Removing Python cache files..."
    rm -rf __pycache__
fi

# Remove any .pyc files
if ls *.pyc 1> /dev/null 2>&1; then
    echo "Removing compiled Python files..."
    find . -name "*.pyc" -delete
fi

# Remove log files
if ls *.log 1> /dev/null 2>&1; then
    echo "Removing log files..."
    rm -f *.log
fi

# Remove Terraform state files (keep for reference but clean working directory)
if [ -d ".terraform" ]; then
    echo "Cleaning Terraform working directory..."
    rm -rf .terraform
fi

if ls *.tfstate 1> /dev/null 2>&1; then
    echo "Removing Terraform state files..."
    rm -f *.tfstate
fi

if ls *.tfstate.backup 1> /dev/null 2>&1; then
    echo "Removing Terraform backup files..."
    rm -f *.tfstate.backup
fi

# Remove temporary directories
if [ -d "temp" ]; then
    echo "Removing temporary directory..."
    rm -rf temp
fi

if [ -d "working_dir" ]; then
    echo "Removing working directory..."
    rm -rf working_dir
fi

# Remove build artifacts
if [ -d "build" ]; then
    echo "Removing build directory..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "Removing distribution directory..."
    rm -rf dist
fi

if ls *.egg-info 1> /dev/null 2>&1; then
    echo "Removing egg-info directories..."
    rm -rf *.egg-info
fi

echo "Cleanup completed successfully!"
echo "Repository is now clean and ready for development."
