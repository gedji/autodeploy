"""
Infrastructure Analyzer
Analyzes parsed deployment specifications and determines optimal resource configurations.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class InfrastructureAnalyzer:
    """Analyzes deployment specifications and optimizes resource configurations."""
    
    # Resource recommendations based on common patterns
    INSTANCE_RECOMMENDATIONS = {
        'nodejs': {
            'dev': 't3.micro',
            'staging': 't3.small', 
            'prod': 't3.medium'
        },
        'python': {
            'dev': 't3.micro',
            'staging': 't3.small',
            'prod': 't3.medium'
        },
        'docker': {
            'dev': 't3.small',
            'staging': 't3.medium',
            'prod': 't3.large'
        },
        'static': {
            'dev': 't3.nano',
            'staging': 't3.micro',
            'prod': 't3.small'
        }
    }
    
    SERVERLESS_RECOMMENDATIONS = {
        'memory': {
            'nodejs': 512,
            'python': 512,
            'static': 128
        },
        'timeout': {
            'api': 30,
            'worker': 300,
            'cron': 900
        }
    }
    
    def __init__(self):
        """Initialize the analyzer."""
        pass
    
    def analyze_deployment(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze deployment specification and provide optimized configuration.
        
        Args:
            spec: Parsed deployment specification
            
        Returns:
            Enhanced specification with optimized resource configurations
        """
        logger.info(f"Analyzing deployment: {spec}")
        
        # Create a copy to avoid modifying the original
        analyzed_spec = spec.copy()
        
        # Analyze based on infrastructure type
        if spec['infra_type'] == 'vm':
            analyzed_spec.update(self._analyze_vm_deployment(spec))
        elif spec['infra_type'] == 'serverless':
            analyzed_spec.update(self._analyze_serverless_deployment(spec))
        elif spec['infra_type'] == 'container':
            analyzed_spec.update(self._analyze_container_deployment(spec))
        
        # Add security recommendations
        analyzed_spec.update(self._analyze_security_requirements(spec))
        
        # Add monitoring and logging
        analyzed_spec.update(self._analyze_monitoring_requirements(spec))
        
        logger.info(f"Analysis complete: {analyzed_spec}")
        return analyzed_spec
    
    def _analyze_vm_deployment(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze VM deployment requirements."""
        framework = spec.get('framework', 'static')
        environment = spec.get('environment', 'dev')
        
        # Recommend instance type if not specified
        if 'instance_type' not in spec:
            instance_type = self.INSTANCE_RECOMMENDATIONS.get(framework, {}).get(
                environment, 't3.micro'
            )
            spec['instance_type'] = instance_type
        
        # Storage recommendations
        storage_size = self._get_storage_recommendation(framework, environment)
        
        # Network configuration
        network_config = self._get_network_configuration(spec)
        
        return {
            'storage_gb': storage_size,
            'network': network_config,
            'user_data_script': self._generate_user_data(framework),
            'key_pair_required': True
        }
    
    def _analyze_serverless_deployment(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze serverless deployment requirements."""
        framework = spec.get('framework', 'nodejs')
        
        # Memory recommendations
        memory = self.SERVERLESS_RECOMMENDATIONS['memory'].get(framework, 512)
        
        # Timeout based on function type
        function_type = spec.get('function_type', 'api')
        timeout = self.SERVERLESS_RECOMMENDATIONS['timeout'].get(function_type, 30)
        
        return {
            'memory_mb': memory,
            'timeout_seconds': timeout,
            'runtime': self._get_serverless_runtime(framework),
            'environment_variables': self._get_default_env_vars(spec),
            'iam_role_required': True
        }
    
    def _analyze_container_deployment(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze container deployment requirements."""
        # For container deployments, we'll use ECS or similar
        return {
            'container_cpu': 256,
            'container_memory': 512,
            'desired_count': 1 if spec.get('environment') == 'dev' else 2,
            'load_balancer_required': spec.get('environment') != 'dev',
            'auto_scaling_enabled': spec.get('environment') == 'prod'
        }
    
    def _analyze_security_requirements(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security requirements."""
        environment = spec.get('environment', 'dev')
        
        security_config = {
            'security_groups': {
                'ingress_rules': self._get_ingress_rules(spec),
                'egress_rules': [{'port': 'all', 'protocol': 'all', 'cidr': '0.0.0.0/0'}]
            },
            'encryption_at_rest': environment == 'prod',
            'backup_enabled': environment in ['staging', 'prod']
        }
        
        return {'security': security_config}
    
    def _analyze_monitoring_requirements(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze monitoring and logging requirements."""
        environment = spec.get('environment', 'dev')
        
        monitoring_config = {
            'cloudwatch_logs': True,
            'metrics_enabled': environment in ['staging', 'prod'],
            'alerting_enabled': environment == 'prod',
            'log_retention_days': 7 if environment == 'dev' else 30
        }
        
        return {'monitoring': monitoring_config}
    
    def _get_storage_recommendation(self, framework: str, environment: str) -> int:
        """Get storage size recommendation in GB."""
        base_sizes = {
            'nodejs': 20,
            'python': 20,
            'docker': 30,
            'static': 10
        }
        
        multipliers = {
            'dev': 1,
            'staging': 1.5,
            'prod': 2
        }
        
        base_size = base_sizes.get(framework, 20)
        multiplier = multipliers.get(environment, 1)
        
        return int(base_size * multiplier)
    
    def _get_network_configuration(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Get network configuration."""
        return {
            'vpc_required': True,
            'public_subnet': spec.get('infra_type') != 'serverless',
            'private_subnet': True,
            'nat_gateway': spec.get('environment') in ['staging', 'prod']
        }
    
    def _generate_user_data(self, framework: str) -> str:
        """Generate user data script for VM initialization."""
        scripts = {
            'nodejs': '''#!/bin/bash
yum update -y
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
yum install -y nodejs
npm install -g pm2
''',
            'python': '''#!/bin/bash
yum update -y
yum install -y python3 python3-pip
pip3 install --upgrade pip
''',
            'docker': '''#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user
''',
            'static': '''#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
'''
        }
        
        return scripts.get(framework, scripts['static'])
    
    def _get_serverless_runtime(self, framework: str) -> str:
        """Get appropriate serverless runtime."""
        runtimes = {
            'nodejs': 'nodejs18.x',
            'python': 'python3.11',
            'static': 'nodejs18.x'  # For static sites, we'll use a simple handler
        }
        
        return runtimes.get(framework, 'nodejs18.x')
    
    def _get_default_env_vars(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Get default environment variables."""
        return {
            'ENVIRONMENT': spec.get('environment', 'dev'),
            'REGION': spec.get('region', 'us-east-1'),
            'LOG_LEVEL': 'DEBUG' if spec.get('environment') == 'dev' else 'INFO'
        }
    
    def _get_ingress_rules(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get security group ingress rules."""
        framework = spec.get('framework', 'static')
        
        # Default rules based on framework
        if framework == 'static':
            return [
                {'port': 80, 'protocol': 'tcp', 'cidr': '0.0.0.0/0'},
                {'port': 443, 'protocol': 'tcp', 'cidr': '0.0.0.0/0'}
            ]
        elif framework in ['nodejs', 'python']:
            return [
                {'port': 22, 'protocol': 'tcp', 'cidr': '0.0.0.0/0'},  # SSH
                {'port': 80, 'protocol': 'tcp', 'cidr': '0.0.0.0/0'},
                {'port': 443, 'protocol': 'tcp', 'cidr': '0.0.0.0/0'},
                {'port': 3000, 'protocol': 'tcp', 'cidr': '0.0.0.0/0'}  # App port
            ]
        else:
            return [
                {'port': 22, 'protocol': 'tcp', 'cidr': '0.0.0.0/0'},
                {'port': 80, 'protocol': 'tcp', 'cidr': '0.0.0.0/0'},
                {'port': 443, 'protocol': 'tcp', 'cidr': '0.0.0.0/0'}
            ]


def analyze_deployment(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for analyzing deployments."""
    analyzer = InfrastructureAnalyzer()
    return analyzer.analyze_deployment(spec)