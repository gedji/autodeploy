@echo off
REM AutoDeploy Repository Cleanup Script
REM Removes temporary files, logs, and build artifacts

echo Starting AutoDeploy repository cleanup...

REM Remove Python cache files
if exist __pycache__ (
    echo Removing Python cache files...
    rmdir /s /q __pycache__
)

REM Remove any .pyc files
if exist *.pyc (
    echo Removing compiled Python files...
    del /s *.pyc
)

REM Remove log files
if exist *.log (
    echo Removing log files...
    del *.log
)

REM Remove Terraform state files (keep for reference but clean working directory)
if exist .terraform (
    echo Cleaning Terraform working directory...
    rmdir /s /q .terraform
)

if exist *.tfstate (
    echo Removing Terraform state files...
    del *.tfstate
)

if exist *.tfstate.backup (
    echo Removing Terraform backup files...
    del *.tfstate.backup
)

REM Remove temporary directories
if exist temp (
    echo Removing temporary directory...
    rmdir /s /q temp
)

if exist working_dir (
    echo Removing working directory...
    rmdir /s /q working_dir
)

REM Remove build artifacts
if exist build (
    echo Removing build directory...
    rmdir /s /q build
)

if exist dist (
    echo Removing distribution directory...
    rmdir /s /q dist
)

if exist *.egg-info (
    echo Removing egg-info directories...
    for /d %%i in (*.egg-info) do rmdir /s /q "%%i"
)

echo Cleanup completed successfully!
echo Repository is now clean and ready for development.
