@echo off
REM AutoDeploy Setup Script for Windows

echo 🚀 AutoDeploy Setup Script
echo ==========================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Copy environment file if it doesn't exist
if not exist .env (
    echo 📄 Creating .env file from template...
    copy .env.example .env
    echo ✅ .env file created. Please edit it and add your OpenAI API key.
) else (
    echo ✅ .env file already exists.
)

REM Check if OpenAI API key is set
findstr "your-openai-api-key-here" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Please edit .env and replace 'your-openai-api-key-here' with your actual OpenAI API key.
    exit /b 1
)

REM Start services
echo 🐳 Starting Docker services...
docker-compose up -d

REM Wait a moment for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Services are running!
    echo.
    echo 🎉 Setup complete! You can now use AutoDeploy:
    echo.
    echo Examples:
    echo   docker-compose exec app python src/main.py "Deploy a Node.js app on AWS"
    echo   docker-compose exec app python src/main.py --interactive
    echo   docker-compose exec app python src/main.py --dry-run "Create a Python API"
    echo.
) else (
    echo ❌ Some services failed to start. Please check the logs:
    echo   docker-compose logs
)
