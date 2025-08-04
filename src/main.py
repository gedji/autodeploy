#!/usr/bin/env python3
"""
AutoDeploy - Intelligent Infrastructure Deployment System

A command-line tool that converts natural language instructions into deployable
cloud infrastructure using OpenAI's GPT models and Terraform.

Usage:
    python main.py "Deploy a Node.js app on AWS using EC2"
    python main.py --dry-run "Create a serverless Python API on AWS"
    python main.py --local "Deploy a static website on AWS"
"""

import sys
import argparse
import logging
import json
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from deployer import deploy_from_instruction, ContainerizedDeployer, InfrastructureDeployer
except ImportError:
    from .deployer import deploy_from_instruction, ContainerizedDeployer, InfrastructureDeployer


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('autodeploy.log')
        ]
    )


def print_banner():
    """Print application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                        🚀 AutoDeploy                        ║
    ║              Intelligent Infrastructure Deployment           ║
    ║                                                              ║
    ║  Convert natural language into deployable cloud infrastructure ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_result(result: dict, verbose: bool = False):
    """Print deployment result in a formatted way."""
    status = result.get('status', 'unknown')
    
    print(f"\n{'='*60}")
    print(f"🎯 DEPLOYMENT RESULT: {status.upper()}")
    print(f"{'='*60}")
    
    if status == 'failed':
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    if status == 'planned':
        print("📋 Deployment planned successfully!")
        print(f"   Working directory: {result.get('working_dir', 'Unknown')}")
        print(f"   Terraform files: {', '.join(result.get('terraform_files', []))}")
        
        if verbose and 'plan_output' in result:
            print("\n📄 Terraform Plan Output:")
            print("-" * 40)
            print(result['plan_output'])
    
    elif status == 'deployed':
        print("✅ Infrastructure deployed successfully!")
        print(f"   Working directory: {result.get('working_dir', 'Unknown')}")
        
        outputs = result.get('outputs', {})
        if outputs:
            print("\n🔗 Deployment Outputs:")
            for key, value in outputs.items():
                if isinstance(value, dict) and 'value' in value:
                    print(f"   {key}: {value['value']}")
                else:
                    print(f"   {key}: {value}")
        
        if verbose and 'apply_output' in result:
            print("\n📄 Terraform Apply Output:")
            print("-" * 40)
            print(result['apply_output'])
    
    # Show parsed and analyzed specs if verbose
    if verbose:
        if 'parsed_spec' in result:
            print("\n🔍 Parsed Specification:")
            print(json.dumps(result['parsed_spec'], indent=2))
        
        if 'analyzed_spec' in result:
            print("\n📊 Analyzed Specification:")
            print(json.dumps(result['analyzed_spec'], indent=2, default=str))


def interactive_mode():
    """Run in interactive mode for multiple deployments."""
    print("\n🎮 Interactive Mode - Enter deployment instructions (or 'quit' to exit)")
    print("Examples:")
    print("  - Deploy a Node.js app on AWS using EC2")
    print("  - Create a serverless Python API with Lambda")
    print("  - Deploy a static website on AWS")
    print()
    
    deployer = None
    
    try:
        while True:
            instruction = input("\n📝 Enter instruction: ").strip()
            
            if instruction.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not instruction:
                continue
            
            # Ask for deployment mode
            mode = input("🔧 Deploy mode (plan/deploy) [plan]: ").strip().lower()
            dry_run = mode != 'deploy'
            
            # Use containerized deployer for consistency
            if deployer is None:
                deployer = ContainerizedDeployer()
            
            print(f"\n🚀 Processing: {instruction}")
            result = deployer.deploy_from_instruction(instruction, dry_run=dry_run)
            
            print_result(result, verbose=True)
            
            if result['status'] == 'deployed':
                destroy = input("\n🗑️  Destroy infrastructure? (y/n) [n]: ").strip().lower()
                if destroy == 'y':
                    print("🗑️ Destroying infrastructure...")
                    destroy_result = deployer.destroy_infrastructure()
                    if destroy_result['status'] == 'destroyed':
                        print("✅ Infrastructure destroyed successfully!")
                    else:
                        print(f"❌ Failed to destroy: {destroy_result.get('error', 'Unknown error')}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    
    finally:
        if deployer:
            deployer.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AutoDeploy - Convert natural language to cloud infrastructure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Deploy a Node.js app on AWS using EC2"
  %(prog)s --dry-run "Create a serverless Python API on AWS"
  %(prog)s --local "Deploy a static website without containers"
  %(prog)s --interactive
        """
    )
    
    parser.add_argument(
        'instruction',
        nargs='?',
        help='Natural language deployment instruction'
    )
    
    parser.add_argument(
        '--dry-run', '--plan',
        action='store_true',
        help='Only plan the deployment without applying changes'
    )
    
    parser.add_argument(
        '--local',
        action='store_true',
        help='Use local Terraform instead of containerized version'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--destroy',
        metavar='WORKING_DIR',
        help='Destroy infrastructure in the specified working directory'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Print banner
    print_banner()
    
    # Handle destroy operation
    if args.destroy:
        if args.local:
            deployer = InfrastructureDeployer(args.destroy)
        else:
            deployer = ContainerizedDeployer(args.destroy)
        
        print(f"🗑️ Destroying infrastructure in: {args.destroy}")
        result = deployer.destroy_infrastructure()
        
        if result['status'] == 'destroyed':
            print("✅ Infrastructure destroyed successfully!")
        else:
            print(f"❌ Failed to destroy: {result.get('error', 'Unknown error')}")
        
        return
    
    # Handle interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Require instruction for non-interactive mode
    if not args.instruction:
        parser.print_help()
        print("\n❌ Error: Please provide an instruction or use --interactive mode")
        sys.exit(1)
    
    # Validate environment
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Deploy from instruction
    print(f"🚀 Processing instruction: {args.instruction}")
    
    use_container = not args.local
    result = deploy_from_instruction(
        args.instruction,
        dry_run=args.dry_run,
        use_container=use_container
    )
    
    print_result(result, args.verbose)
    
    # Exit with appropriate code
    if result['status'] == 'failed':
        sys.exit(1)


if __name__ == '__main__':
    main()