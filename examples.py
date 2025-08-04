#!/usr/bin/env python3
"""
AutoDeploy Example Script

This script demonstrates various AutoDeploy capabilities with example deployments.
Run this to see the system in action with different deployment scenarios.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from deployer import deploy_from_instruction

def run_example(instruction: str, description: str, dry_run: bool = True):
    """Run a single deployment example."""
    print(f"\n{'='*80}")
    print(f"🎯 EXAMPLE: {description}")
    print(f"📝 Instruction: {instruction}")
    print(f"🔧 Mode: {'Dry Run (Plan Only)' if dry_run else 'Full Deployment'}")
    print(f"{'='*80}")
    
    try:
        result = deploy_from_instruction(instruction, dry_run=dry_run, use_container=True)
        
        if result['status'] == 'planned':
            print("✅ Planning successful!")
            print(f"📋 Generated files: {', '.join(result.get('terraform_files', []))}")
        elif result['status'] == 'deployed':
            print("🚀 Deployment successful!")
            outputs = result.get('outputs', {})
            if outputs:
                print("🔗 Outputs:")
                for key, value in outputs.items():
                    if isinstance(value, dict) and 'value' in value:
                        print(f"   {key}: {value['value']}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run example deployment scenarios."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🚀 AutoDeploy Examples                   ║
    ║                                                              ║
    ║  Demonstrating various deployment scenarios and capabilities ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check prerequisites
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: Please set OPENAI_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Example scenarios
    examples = [
        {
            'instruction': "Deploy a Node.js web application on AWS using EC2 for development",
            'description': "Simple VM Deployment - Development Environment"
        },
        {
            'instruction': "Create a Python REST API using AWS Lambda with API Gateway for production",
            'description': "Serverless API - Production Ready"
        },
        {
            'instruction': "Deploy a static website on AWS with CloudFront CDN for staging",
            'description': "Static Site with CDN - Staging Environment"
        },
        {
            'instruction': "Deploy a Docker containerized app using ECS with load balancing for production",
            'description': "Container Deployment - Auto-scaling Production"
        },
        {
            'instruction': "Create a MySQL database on AWS RDS with automated backups",
            'description': "Database Deployment - High Availability"
        }
    ]
    
    # Run examples
    for i, example in enumerate(examples, 1):
        print(f"\n🔄 Running Example {i}/{len(examples)}...")
        run_example(
            example['instruction'],
            example['description'],
            dry_run=True  # Always dry run for examples
        )
        
        if i < len(examples):
            input("\n⏸️  Press Enter to continue to next example...")
    
    print(f"\n{'='*80}")
    print("🎉 All examples completed!")
    print("💡 To run actual deployments, use:")
    print("   python src/main.py 'your instruction here'")
    print("   python src/main.py --interactive")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
