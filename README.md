# 🚀 AutoDeploy - Intelligent Infrastructure Deployment

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![Terraform](https://img.shields.io/badge/terraform-1.5+-green.svg)](https://www.terraform.io/)
[![OpenAI](https://img.shields.io/badge/openai-gpt--4-orange.svg)](https://openai.com/)

AutoDeploy is an intelligent system that converts natural language instructions into deployable cloud infrastructure using OpenAI's GPT models and Terraform. It supports multiple deployment patterns including VMs, serverless functions, and containerized applications.

## ✨ Features

- 🧠 **Natural Language Processing**: Convert plain English to infrastructure code
- 🏗️ **Multi-Pattern Support**: VMs, Serverless, and Container deployments  
- 🔧 **Intelligent Analysis**: Automatic resource optimization and security recommendations
- 🐳 **Containerized**: Runs entirely in Docker for consistent, OS-agnostic operation
- 🔒 **LocalStack Integration**: Test deployments locally before going to production
- 📊 **Rich CLI**: Interactive and command-line modes with detailed feedback

## 🏗️ Architecture

```
autodeploy/
├── src/
│   ├── main.py              # CLI entry point and user interface
│   ├── parser.py            # OpenAI-powered instruction parsing  
│   ├── analyzer.py          # Infrastructure requirement analysis
│   ├── deployer.py          # Deployment orchestration
│   └── terraform/
│       ├── renderer.py      # Jinja2 template rendering
│       └── templates/       # Terraform configuration templates
├── docker-compose.yml       # Multi-service orchestration
├── Dockerfile              # Application container definition
└── requirements.txt        # Python dependencies
```

## 🚦 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (any OS)
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd autodeploy

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# Alternative: Set environment variable directly
export OPENAI_API_KEY="your-openai-api-key-here"

# On Windows PowerShell:
$env:OPENAI_API_KEY="your-openai-api-key-here"
```

### 2. Start Services

```bash
# Start all required services (LocalStack, Terraform, App)
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Deploy Infrastructure

```bash
# Simple VM deployment
docker-compose exec app python src/main.py "Deploy a Node.js app on AWS using EC2"

# Serverless deployment (dry-run)
docker-compose exec app python src/main.py --dry-run "Create a Python API using Lambda"

# Interactive mode
docker-compose exec app python src/main.py --interactive
```

## 📖 Usage Examples

### Command Line Mode

```bash
# Basic VM deployment
python src/main.py "Deploy a Python web app on AWS using EC2 in production"

# Serverless API with specific requirements  
python src/main.py "Create a Node.js serverless API on AWS with auto-scaling"

# Static website deployment
python src/main.py "Deploy a static website on AWS with CDN"

# Dry run (plan only, no deployment)
python src/main.py --dry-run "Deploy a Docker container on AWS using ECS"

# Use local Terraform instead of container
python src/main.py --local "Deploy a Python app on AWS"
```

### Interactive Mode

```bash
# Start interactive session
python src/main.py --interactive

# Example session:
📝 Enter instruction: Deploy a Node.js app on AWS using EC2
🔧 Deploy mode (plan/deploy) [plan]: deploy
🚀 Processing: Deploy a Node.js app on AWS using EC2
✅ Infrastructure deployed successfully!
🗑️ Destroy infrastructure? (y/n) [n]: y
```

### Supported Instructions

The system understands natural language instructions like:

- **Web Applications**: "Deploy a Node.js web app on AWS using EC2"
- **APIs**: "Create a Python REST API using Lambda with API Gateway"  
- **Static Sites**: "Deploy a static website on AWS with CloudFront"
- **Containers**: "Deploy a Docker application using ECS with load balancing"
- **Databases**: "Create a MySQL database on AWS RDS with backup enabled"

### Environment Specifications

Include environment details for optimized configurations:

- **Development**: "Deploy a Node.js app for development"
- **Staging**: "Create a staging environment for my Python API"  
- **Production**: "Deploy a production-ready React app with auto-scaling"

## 🛠️ Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional (for production use)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key  
AWS_ENDPOINT_URL=http://localhost:4566  # LocalStack for local testing
```

### Docker Compose Services

- **app**: Main AutoDeploy application
- **terraform**: HashiCorp Terraform for infrastructure provisioning
- **localstack**: Local AWS cloud stack for testing

### Terraform Templates

Customize deployment patterns by editing Jinja2 templates in `src/terraform/templates/`:

- `provider.tf.j2`: Cloud provider configuration
- `vm.tf.j2`: Virtual machine deployments
- `serverless.tf.j2`: Lambda and serverless configurations

## 🔧 Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run locally (without containers)
python src/main.py --local "your instruction here"
```

### Adding New Deployment Patterns

1. **Create Template**: Add new Jinja2 template in `src/terraform/templates/`
2. **Update Analyzer**: Add resource recommendations in `analyzer.py`
3. **Update Renderer**: Add rendering logic in `terraform/renderer.py`
4. **Test**: Verify with sample instructions

### Project Structure

```
autodeploy/
├── src/
│   ├── main.py              # CLI interface and user experience
│   ├── parser.py            # OpenAI integration for NLP
│   ├── analyzer.py          # Infrastructure analysis and optimization
│   ├── deployer.py          # Deployment orchestration and Terraform integration
│   └── terraform/
│       ├── renderer.py      # Template rendering engine
│       └── templates/       # Infrastructure-as-Code templates
│           ├── provider.tf.j2     # Cloud provider configuration
│           ├── vm.tf.j2           # Virtual machine templates
│           └── serverless.tf.j2   # Serverless deployment templates
├── docker-compose.yml       # Service orchestration
├── Dockerfile              # Application containerization
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🌍 Cross-Platform Compatibility

AutoDeploy is designed to work on any operating system:

- **Windows**: PowerShell, Command Prompt, WSL
- **macOS**: Terminal, iTerm2
- **Linux**: Any bash/zsh shell

All dependencies run in Docker containers, ensuring consistent behavior across platforms.

## 🔍 Troubleshooting

### Common Issues

**OpenAI API Key not found**
```bash
export OPENAI_API_KEY="your-key-here"
# Verify: echo $OPENAI_API_KEY
```

**Docker services not running**
```bash
docker-compose ps
docker-compose up -d
```

**Terraform initialization fails**
```bash
docker-compose exec terraform terraform init
```

**Port 4566 already in use**
```bash
# Stop conflicting LocalStack instances
docker stop $(docker ps -q --filter "publish=4566")
docker-compose up -d
```

### Debug Mode

```bash
# Enable verbose logging
python src/main.py --verbose "your instruction"

# Check logs
tail -f autodeploy.log
```

## 📋 Requirements

### System Requirements
- **OS**: Windows, macOS, or Linux
- **Docker**: Version 20.10+ with Docker Compose
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk**: 5GB free space

### External Dependencies
- **OpenAI API**: GPT-4 access required
- **Internet**: For pulling Docker images and API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check this README and inline code documentation

---

**Made with ❤️ for intelligent infrastructure deployment**