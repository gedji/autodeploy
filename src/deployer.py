"""
Infrastructure Deployer
Orchestrates the complete deployment pipeline from parsing to infrastructure provisioning.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .parser import InstructionParser
from .analyzer import InfrastructureAnalyzer
from .terraform.renderer import TerraformRenderer

logger = logging.getLogger(__name__)


class InfrastructureDeployer:
    """Orchestrates complete infrastructure deployment pipeline."""
    
    def __init__(self, working_dir: str = None):
        """
        Initialize the deployer.
        
        Args:
            working_dir: Working directory for Terraform operations
        """
        self.parser = InstructionParser()
        self.analyzer = InfrastructureAnalyzer()
        self.renderer = TerraformRenderer()
        
        if working_dir is None:
            working_dir = tempfile.mkdtemp(prefix='autodeploy_')
        
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Deployer initialized with working directory: {self.working_dir}")
    
    def deploy_from_instruction(self, instruction: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Complete deployment pipeline from natural language instruction.
        
        Args:
            instruction: Natural language deployment instruction
            dry_run: If True, only plan without applying changes
            
        Returns:
            Deployment result dictionary
        """
        logger.info(f"Starting deployment from instruction: {instruction}")
        
        try:
            # Step 1: Parse instruction
            logger.info("Step 1: Parsing instruction...")
            parsed_spec = self.parser.parse_instruction(instruction)
            logger.info(f"Parsed specification: {parsed_spec}")
            
            # Step 2: Analyze requirements
            logger.info("Step 2: Analyzing infrastructure requirements...")
            analyzed_spec = self.analyzer.analyze_deployment(parsed_spec)
            logger.info(f"Analyzed specification: {analyzed_spec}")
            
            # Step 3: Render Terraform configuration
            logger.info("Step 3: Rendering Terraform configuration...")
            terraform_files = self.renderer.render_configuration(
                analyzed_spec, 
                str(self.working_dir)
            )
            logger.info(f"Rendered {len(terraform_files)} Terraform files")
            
            # Step 4: Initialize Terraform
            logger.info("Step 4: Initializing Terraform...")
            self._run_terraform_init()
            
            # Step 5: Plan deployment
            logger.info("Step 5: Planning deployment...")
            plan_output = self._run_terraform_plan()
            
            result = {
                'status': 'planned',
                'instruction': instruction,
                'parsed_spec': parsed_spec,
                'analyzed_spec': analyzed_spec,
                'terraform_files': list(terraform_files.keys()),
                'working_dir': str(self.working_dir),
                'plan_output': plan_output
            }
            
            # Step 6: Apply if not dry run
            if not dry_run:
                logger.info("Step 6: Applying deployment...")
                apply_output = self._run_terraform_apply()
                result.update({
                    'status': 'deployed',
                    'apply_output': apply_output,
                    'outputs': self._get_terraform_outputs()
                })
            
            logger.info(f"Deployment completed successfully. Status: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'instruction': instruction,
                'working_dir': str(self.working_dir)
            }
    
    def destroy_infrastructure(self) -> Dict[str, Any]:
        """
        Destroy infrastructure in the working directory.
        
        Returns:
            Destruction result dictionary
        """
        logger.info(f"Destroying infrastructure in: {self.working_dir}")
        
        try:
            # Check if Terraform state exists
            state_file = self.working_dir / 'terraform.tfstate'
            if not state_file.exists():
                return {
                    'status': 'no_infrastructure',
                    'message': 'No Terraform state found, nothing to destroy'
                }
            
            # Run terraform destroy
            destroy_output = self._run_terraform_destroy()
            
            return {
                'status': 'destroyed',
                'destroy_output': destroy_output,
                'working_dir': str(self.working_dir)
            }
            
        except Exception as e:
            logger.error(f"Destruction failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'working_dir': str(self.working_dir)
            }
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """
        Get current deployment status and outputs.
        
        Returns:
            Status dictionary with current state information
        """
        try:
            # Check if Terraform state exists
            state_file = self.working_dir / 'terraform.tfstate'
            if not state_file.exists():
                return {
                    'status': 'not_deployed',
                    'message': 'No Terraform state found'
                }
            
            # Get Terraform outputs
            outputs = self._get_terraform_outputs()
            
            return {
                'status': 'deployed',
                'outputs': outputs,
                'working_dir': str(self.working_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _run_terraform_init(self) -> str:
        """Initialize Terraform in working directory."""
        return self._run_terraform_command(['init'])
    
    def _run_terraform_plan(self) -> str:
        """Run Terraform plan."""
        return self._run_terraform_command(['plan', '-no-color'])
    
    def _run_terraform_apply(self) -> str:
        """Apply Terraform configuration."""
        return self._run_terraform_command(['apply', '-auto-approve', '-no-color'])
    
    def _run_terraform_destroy(self) -> str:
        """Destroy Terraform infrastructure."""
        return self._run_terraform_command(['destroy', '-auto-approve', '-no-color'])
    
    def _get_terraform_outputs(self) -> Dict[str, Any]:
        """Get Terraform outputs as dictionary."""
        try:
            output = self._run_terraform_command(['output', '-json'])
            import json
            return json.loads(output) if output.strip() else {}
        except Exception as e:
            logger.warning(f"Failed to get Terraform outputs: {e}")
            return {}
    
    def _run_terraform_command(self, args: list, timeout: int = 300) -> str:
        """
        Run a Terraform command in the working directory.
        
        Args:
            args: Terraform command arguments
            timeout: Command timeout in seconds
            
        Returns:
            Command output
        """
        cmd = ['terraform'] + args
        
        # Set up environment variables for LocalStack
        env = os.environ.copy()
        env.update({
            'TF_VAR_aws_access_key': 'test',
            'TF_VAR_aws_secret_key': 'test',
            'TF_VAR_aws_endpoint_url': 'http://localhost:4566',
            'TF_VAR_region': 'us-east-1'
        })
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode != 0:
                logger.error(f"Terraform command failed: {output}")
                raise RuntimeError(f"Terraform command failed with exit code {result.returncode}: {output}")
            
            logger.debug(f"Command output: {output}")
            return output
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Terraform command timed out after {timeout} seconds")
        except FileNotFoundError:
            raise RuntimeError("Terraform not found. Please install Terraform and ensure it's in PATH")
    
    def cleanup(self):
        """Clean up working directory."""
        if self.working_dir.exists():
            shutil.rmtree(self.working_dir)
            logger.info(f"Cleaned up working directory: {self.working_dir}")


class ContainerizedDeployer(InfrastructureDeployer):
    """Deployer that uses containerized Terraform via Docker Compose."""
    
    def __init__(self, working_dir: str = None, compose_service: str = 'terraform'):
        """
        Initialize containerized deployer.
        
        Args:
            working_dir: Working directory for Terraform operations
            compose_service: Docker Compose service name for Terraform
        """
        super().__init__(working_dir)
        self.compose_service = compose_service
    
    def _run_terraform_command(self, args: list, timeout: int = 300) -> str:
        """
        Run Terraform command in Docker container.
        
        Args:
            args: Terraform command arguments
            timeout: Command timeout in seconds
            
        Returns:
            Command output
        """
        # Copy files to the container's working directory
        container_work_dir = f'/workspace/terraform'
        
        # Build docker-compose exec command
        docker_cmd = [
            'docker-compose', 'exec', '-T', self.compose_service,
            'terraform'
        ] + args
        
        # Set up environment variables
        env = os.environ.copy()
        env.update({
            'TF_VAR_aws_access_key': 'test',
            'TF_VAR_aws_secret_key': 'test',
            'TF_VAR_aws_endpoint_url': 'http://localstack:4566',
            'TF_VAR_region': 'us-east-1'
        })
        
        logger.info(f"Running containerized command: {' '.join(docker_cmd)}")
        
        try:
            # First, copy our files to the container's terraform directory
            self._sync_files_to_container()
            
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode != 0:
                logger.error(f"Containerized Terraform command failed: {output}")
                raise RuntimeError(f"Terraform command failed with exit code {result.returncode}: {output}")
            
            logger.debug(f"Command output: {output}")
            return output
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Terraform command timed out after {timeout} seconds")
        except FileNotFoundError:
            raise RuntimeError("Docker Compose not found. Please ensure Docker and Docker Compose are installed")
    
    def _sync_files_to_container(self):
        """Sync local files to container's terraform directory."""
        # Copy files from local working directory to container
        for tf_file in self.working_dir.glob('*.tf'):
            cmd = [
                'docker-compose', 'exec', '-T', self.compose_service,
                'sh', '-c', f'cat > /workspace/terraform/{tf_file.name}'
            ]
            
            with open(tf_file, 'r') as f:
                subprocess.run(cmd, input=f.read(), text=True, check=True)
        
        # Copy tfvars file if it exists
        tfvars_file = self.working_dir / 'terraform.tfvars'
        if tfvars_file.exists():
            cmd = [
                'docker-compose', 'exec', '-T', self.compose_service,
                'sh', '-c', 'cat > /workspace/terraform/terraform.tfvars'
            ]
            
            with open(tfvars_file, 'r') as f:
                subprocess.run(cmd, input=f.read(), text=True, check=True)


def deploy_from_instruction(instruction: str, dry_run: bool = False, use_container: bool = True) -> Dict[str, Any]:
    """
    Convenience function for deploying from natural language instruction.
    
    Args:
        instruction: Natural language deployment instruction
        dry_run: If True, only plan without applying changes
        use_container: If True, use containerized Terraform
        
    Returns:
        Deployment result dictionary
    """
    if use_container:
        deployer = ContainerizedDeployer()
    else:
        deployer = InfrastructureDeployer()
    
    try:
        return deployer.deploy_from_instruction(instruction, dry_run)
    finally:
        # Clean up unless it's a dry run (user might want to inspect)
        if not dry_run:
            deployer.cleanup()