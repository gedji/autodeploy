#!/bin/bash
# AutoDeploy Setup Script

echo "🚀 AutoDeploy Setup Script"
echo "=========================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker and Docker Compose first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it and add your OpenAI API key."
else
    echo "✅ .env file already exists."
fi

# Check if OpenAI API key is set
if [ -f .env ]; then
    if grep -q "your-openai-api-key-here" .env; then
        echo "⚠️  Please edit .env and replace 'your-openai-api-key-here' with your actual OpenAI API key."
        exit 1
    fi
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🎉 Setup complete! You can now use AutoDeploy:"
    echo ""
    echo "Examples:"
    echo "  docker-compose exec app python src/main.py \"Deploy a Node.js app on AWS\""
    echo "  docker-compose exec app python src/main.py --interactive"
    echo "  docker-compose exec app python src/main.py --dry-run \"Create a Python API\""
    echo ""
else
    echo "❌ Some services failed to start. Please check the logs:"
    echo "  docker-compose logs"
fi
