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

## 🚦 Quick Start (No DevOps Experience Required!)

### 📋 What You Need

1. **A computer** with internet connection (Windows, Mac, or Linux)
2. **Docker Desktop** ([Download here](https://www.docker.com/products/docker-desktop/)) - This is like a "virtual computer" that runs our app
3. **OpenAI Account** ([Sign up here](https://platform.openai.com/)) - For AI-powered text understanding

### 🎯 Step-by-Step Setup (5 minutes)

#### Step 1: Install Docker Desktop
1. Download Docker Desktop from the link above
2. Install it (may require restart)
3. Open Docker Desktop - wait for it to start completely

#### Step 2: Get Your OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Go to "API Keys" section
4. Click "Create new secret key"
5. **Copy this key** - you'll need it soon!

#### Step 3: Download AutoDeploy
```bash
# Clone the repository
git clone <repository-url>
cd autodeploy

# Copy the example environment file
cp .env.example .env
```

#### Step 4: Add Your API Key
Open the `.env` file in any text editor and replace `your-openai-api-key-here` with your actual API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

#### Step 5: Start AutoDeploy
```bash
# Start the application (this downloads and starts everything automatically)
docker-compose up -d

# Wait about 30 seconds, then test if it's working
docker-compose ps
```

You should see 3 services running: `app`, `terraform`, and `localstack`.

## 🎮 Test Different Scenarios (Fun Part!)

### 🌐 Scenario 1: Deploy a Website

**What you're doing**: Creating a complete web server for a Node.js website

```bash
docker-compose exec app python src/main.py "Deploy a Node.js website on AWS using EC2 for production"
```

**What happens**: AutoDeploy will:
- Understand you want a Node.js website
- Choose the right server size for production
- Set up security (firewalls, etc.)
- Create monitoring and backups
- Generate all the infrastructure code

### 🚀 Scenario 2: Build a Serverless API

**What you're doing**: Creating an API that automatically scales up/down based on usage

```bash
docker-compose exec app python src/main.py "Create a Python REST API using AWS Lambda with auto-scaling"
```

**What happens**: AutoDeploy will:
- Set up serverless functions (no servers to manage!)
- Configure automatic scaling
- Add API gateway for requests
- Set up logging and monitoring

### 🐳 Scenario 3: Deploy a Containerized App

**What you're doing**: Deploying a Docker application with load balancing

```bash
docker-compose exec app python src/main.py "Deploy a Docker application on AWS ECS with load balancer"
```

**What happens**: AutoDeploy will:
- Set up container orchestration
- Configure load balancing for high availability
- Add health checks
- Set up auto-scaling

### 🧪 Scenario 4: Test Mode (Safe Practice)

**What you're doing**: Planning deployment without actually creating anything

```bash
docker-compose exec app python src/main.py --dry-run "Deploy a React website with CDN"
```

**What happens**: AutoDeploy will:
- Show you exactly what would be created
- Display cost estimates
- Generate all configuration files
- **But won't create any real infrastructure**

### 💬 Scenario 5: Interactive Mode (Ask Questions)

**What you're doing**: Having a conversation with AutoDeploy

```bash
docker-compose exec app python src/main.py --interactive
```

**Example conversation**:
```
📝 Enter instruction: I want to deploy a blog website
🤖 AutoDeploy: Great! What technology is your blog built with?
📝 Enter instruction: WordPress
🤖 AutoDeploy: Excellent! What environment? (development/staging/production)
📝 Enter instruction: Production with high availability
🚀 Processing your request...
```

## 🎯 More Test Scenarios

### For E-commerce
```bash
docker-compose exec app python src/main.py "Deploy a production e-commerce site with database and payment processing"
```

### For Mobile App Backend
```bash
docker-compose exec app python src/main.py "Create a mobile app backend API with user authentication"
```

### For Data Analytics
```bash
docker-compose exec app python src/main.py "Set up a data analytics platform with Python and database"
```

### For Static Website
```bash
docker-compose exec app python src/main.py "Deploy a static portfolio website with global CDN"
```

## 🎪 Understanding the Output

When you run a command, AutoDeploy will show you:

1. **🔍 Parsing**: Understanding your request
2. **🧠 Analysis**: Optimizing for your needs
3. **📝 Generation**: Creating infrastructure code
4. **🚀 Planning**: Showing what will be created
5. **✅ Results**: Summary of generated resources

### Example Output Explanation:
```
✅ Generated Infrastructure:
📄 provider.tf: Cloud provider setup (AWS)
📄 vm.tf: Virtual machine configuration
📄 network.tf: Networking and security
📄 security.tf: Firewalls and access control
📄 variables.tf: Customizable settings
📄 outputs.tf: Important information after deployment
```

## 🛡️ Safety Features

- **🏠 Local Testing**: Everything runs on your computer first using "LocalStack" (fake AWS)
- **🔍 Dry Run Mode**: See what would happen without doing it
- **🗑️ Easy Cleanup**: Remove everything with one command
- **🔒 Secure**: Your API keys stay on your computer

## ❓ What Each File Does (Simple Explanation)

- **provider.tf**: Tells AWS "this is us, let us create things"
- **vm.tf**: Creates virtual computers in the cloud
- **network.tf**: Sets up internet connections and security
- **security.tf**: Creates digital locks and access controls
- **variables.tf**: Settings you can change later
- **outputs.tf**: Important info like website addresses

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

## 🔍 Troubleshooting (Don't Panic!)

### 😅 "I'm getting an error about OpenAI API key"
**Solution**: 
1. Make sure you copied your API key correctly
2. Check that `.env` file has: `OPENAI_API_KEY=sk-your-key-here`
3. No spaces around the `=` sign

### 🐳 "Docker is not running" 
**Solution**:
1. Open Docker Desktop application
2. Wait for the whale icon to stop spinning
3. Try your command again

### 💸 "I'm worried about costs"
**Don't worry!** 
- AutoDeploy runs locally first (no AWS costs)
- Use `--dry-run` to see plans without creating anything
- OpenAI API costs are typically under $1 for testing

### ⏰ "It's taking forever"
**This is normal for first time**:
- Docker downloads images (one-time, ~5-10 minutes)
- Subsequent runs are much faster (30 seconds)

### 🤔 "I don't understand the output"
**That's okay!** The important parts:
- ✅ Green checkmarks = Success
- ❌ Red X = Something went wrong
- 📄 File names = Infrastructure components created

### 🆘 Still Stuck?
1. **Check if Docker is running**: `docker-compose ps`
2. **Restart everything**: `docker-compose down && docker-compose up -d`
3. **Check logs**: `docker-compose logs app`

## 🎓 Learning More

### 🤓 What is Infrastructure as Code?
Think of it like **LEGO instructions** for cloud computers:
- Instead of clicking buttons manually
- You write down the steps
- The computer follows your instructions perfectly every time

### 🧠 How Does the AI Part Work?
1. **You speak human**: "I want a website for my bakery"
2. **AI translates**: Understands you need web server, database, security
3. **System creates**: Generates the technical instructions
4. **Computer builds**: Follows the instructions to create your infrastructure

### 🔒 Is This Safe?
**Yes!** Here's why:
- Everything runs locally first (LocalStack = fake AWS)
- You can see exactly what will be created before it happens
- Easy to delete everything when you're done testing
- Your API keys never leave your computer

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
- **🎮 Testing Guide**: See `TESTING_GUIDE.md` for step-by-step testing scenarios
- **🚀 Technical Details**: See `SOLUTION.md` for technical implementation details

---

**Made with ❤️ for intelligent infrastructure deployment**