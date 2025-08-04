"""
Natural Language Instruction Parser
Converts user instructions into structured deployment specifications using OpenAI.
"""

import json
import os
from typing import Dict, Any
from openai import OpenAI


class InstructionParser:
    """Parses natural language deployment instructions using OpenAI GPT."""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    def parse_instruction(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language instruction into structured deployment spec.
        
        Args:
            text: Natural language instruction describing infrastructure needs
            
        Returns:
            Dict containing parsed deployment specification
        """
        system_prompt = """
        You are an expert infrastructure engineer. Parse the user's instruction and extract:
        
        Required fields:
        - framework: Application framework (e.g., "nodejs", "python", "static", "docker")
        - cloud: Cloud provider ("aws", "gcp", "azure") 
        - infra_type: Infrastructure type ("vm", "serverless", "container")
        
        Optional fields:
        - region: Deployment region (default: "us-east-1")
        - instance_type: VM instance type (default: "t3.micro")
        - runtime: Runtime version (e.g., "nodejs18", "python3.11")
        - environment: Deployment environment ("dev", "staging", "prod")
        - scaling: Auto-scaling configuration
        - storage: Storage requirements
        - network: Network configuration
        
        Return ONLY valid JSON, no additional text or formatting.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,  # Low temperature for consistent parsing
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Handle potential JSON formatting issues
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
                
            parsed = json.loads(content)
            
            # Validate required fields
            required_fields = ['framework', 'cloud', 'infra_type']
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            
            # Set defaults
            parsed.setdefault('region', 'us-east-1')
            parsed.setdefault('environment', 'dev')
            
            return parsed
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse OpenAI response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing instruction: {e}")


def parse_instruction(text: str) -> Dict[str, Any]:
    """Convenience function for parsing instructions."""
    parser = InstructionParser()
    return parser.parse_instruction(text)