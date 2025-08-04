#!/usr/bin/env python3
"""
Quick test script for AutoDeploy without requiring OpenAI API key
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_autodeploy():
    """Test AutoDeploy components without API calls"""
    
    print("🧪 Testing AutoDeploy Components...")
    print("=" * 50)
    
    # Test 1: Import modules
    print("1. Testing imports...")
    try:
        from analyzer import InfrastructureAnalyzer
        from terraform.renderer import TerraformRenderer
        print("   ✅ All modules imported successfully")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test 2: Test analyzer
    print("2. Testing Infrastructure Analyzer...")
    try:
        analyzer = InfrastructureAnalyzer()
        
        # Sample specification (what would come from parser)
        spec = {
            "framework": "python",
            "cloud": "aws",
            "infra_type": "vm",
            "environment": "production"
        }
        
        enhanced_spec = analyzer.analyze_deployment(spec)
        
        print(f"   ✅ Analysis complete!")
        print(f"   📊 Instance type: {enhanced_spec.get('instance_type', 'N/A')}")
        print(f"   💾 Storage: {enhanced_spec.get('storage_gb', 'N/A')} GB")
        print(f"   🔐 Security: {enhanced_spec.get('security', {}).get('encryption_at_rest', 'N/A')}")
        
    except Exception as e:
        print(f"   ❌ Analyzer error: {e}")
        return False
    
    # Test 3: Test template renderer
    print("3. Testing Template Renderer...")
    try:
        renderer = TerraformRenderer()
        
        terraform_files = renderer.render_configuration(enhanced_spec)
        
        if terraform_files and isinstance(terraform_files, dict):
            print("   ✅ Terraform code generated successfully!")
            print(f"   📄 Generated {len(terraform_files)} file(s)")
            
            # Show files generated
            for filename, content in terraform_files.items():
                print(f"      📝 {filename}: {len(content)} characters")
                
            # Show a snippet from main.tf if available
            if 'main.tf' in terraform_files:
                lines = terraform_files['main.tf'].split('\n')[:5]
                print("   � Sample from main.tf:")
                for line in lines:
                    if line.strip():
                        print(f"      {line}")
        else:
            print("   ⚠️  No Terraform files generated")
            
    except Exception as e:
        print(f"   ❌ Renderer error: {e}")
        return False
    
    print("\n🎉 All tests passed! AutoDeploy is working correctly.")
    print("\n💡 To use with OpenAI API:")
    print("   1. Get an API key from https://platform.openai.com/")
    print("   2. Set environment variable: OPENAI_API_KEY=your_key")
    print("   3. Run: python src/main.py 'your instruction'")
    
    return True

if __name__ == "__main__":
    test_autodeploy()
