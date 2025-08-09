#!/usr/bin/env python3
"""
Claude Code Project Analyzer & Subagent Manager

This tool automatically analyzes project structure and creates appropriate subagents
for use with Claude Code, plus provides a management UI for subagent operations.
"""

import os
import json
import yaml
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import shutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.tree import Tree
from rich.syntax import Syntax
import questionary

console = Console()

@dataclass
class ProjectAnalysis:
    """Results of project structure analysis"""
    project_type: str
    languages: List[str]
    frameworks: List[str]
    tools: List[str]
    architecture_patterns: List[str]
    suggested_subagents: List[str]
    complexity_score: int
    special_requirements: List[str]

@dataclass
class SubagentConfig:
    """Configuration for a Claude Code subagent"""
    name: str
    description: str
    tools: Optional[List[str]]
    system_prompt: str
    category: str = "custom"
    auto_invoke: bool = False

class ProjectAnalyzer:
    """Analyzes project structure to determine appropriate subagents"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.analysis = None
        
    def analyze_project(self) -> ProjectAnalysis:
        """Perform comprehensive project analysis"""
        console.print(f"[blue]Analyzing project: {self.project_path}[/blue]")
        
        languages = self._detect_languages()
        frameworks = self._detect_frameworks()
        tools = self._detect_tools()
        architecture = self._detect_architecture_patterns()
        project_type = self._determine_project_type(languages, frameworks)
        complexity = self._calculate_complexity()
        special_reqs = self._detect_special_requirements()
        suggested_agents = self._suggest_subagents(
            project_type, languages, frameworks, tools, architecture
        )
        
        self.analysis = ProjectAnalysis(
            project_type=project_type,
            languages=languages,
            frameworks=frameworks,
            tools=tools,
            architecture_patterns=architecture,
            suggested_subagents=suggested_agents,
            complexity_score=complexity,
            special_requirements=special_reqs
        )
        
        return self.analysis
    
    def _detect_languages(self) -> List[str]:
        """Detect programming languages used in the project"""
        languages = []
        
        # File extension mapping (including blockchain-specific)
        ext_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.sol': 'Solidity',
            '.vy': 'Vyper',
            '.move': 'Move',
            '.cairo': 'Cairo',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.cs': 'C#',
            '.vue': 'Vue.js',
            '.svelte': 'Svelte',
            '.dart': 'Dart',
            '.sh': 'Shell',
            '.sql': 'SQL',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.toml': 'TOML',
            '.dockerfile': 'Docker',
            '.tf': 'Terraform'
        }
        
        # Count files by extension
        ext_counts = {}
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and not self._is_ignored(file_path):
                ext = file_path.suffix.lower()
                if ext in ext_map:
                    ext_counts[ext] = ext_counts.get(ext, 0) + 1
        
        # Add languages with significant presence
        for ext, count in ext_counts.items():
            if count >= 3:  # Threshold for inclusion
                lang = ext_map[ext]
                if lang not in languages:
                    languages.append(lang)
        
        return languages
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks and libraries used"""
        frameworks = []
        
        # Check package.json for Node.js projects
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    # Framework detection patterns (including blockchain)
                    patterns = {
                        'React': ['react', '@types/react'],
                        'Next.js': ['next'],
                        'Vue.js': ['vue', '@vue/cli'],
                        'Angular': ['@angular/core'],
                        'Svelte': ['svelte'],
                        'Express': ['express'],
                        'Fastify': ['fastify'],
                        'NestJS': ['@nestjs/core'],
                        'Socket.io': ['socket.io'],
                        'Prisma': ['prisma', '@prisma/client'],
                        'TypeORM': ['typeorm'],
                        'Sequelize': ['sequelize'],
                        'Mongoose': ['mongoose'],
                        'Jest': ['jest'],
                        'Cypress': ['cypress'],
                        'Playwright': ['playwright'],
                        'Webpack': ['webpack'],
                        'Vite': ['vite'],
                        'Tailwind CSS': ['tailwindcss'],
                        'Material-UI': ['@mui/material', '@material-ui/core'],
                        'Chakra UI': ['@chakra-ui/react'],
                        'Styled Components': ['styled-components'],
                        'GraphQL': ['graphql', 'apollo-server'],
                        'tRPC': ['@trpc/server'],
                        'Hardhat': ['hardhat'],
                        'Truffle': ['truffle'],
                        'Foundry': ['@foundry-rs/hardhat-foundry'],
                        'Ethers.js': ['ethers'],
                        'Web3.js': ['web3'],
                        'Wagmi': ['wagmi'],
                        'Rainbow Kit': ['@rainbow-me/rainbowkit'],
                        'OpenZeppelin': ['@openzeppelin/contracts', '@openzeppelin/hardhat-upgrades'],
                        'Chainlink': ['@chainlink/contracts'],
                        'The Graph': ['@graphprotocol/graph-cli']
                    }
                    
                    for framework, indicators in patterns.items():
                        if any(dep in deps for dep in indicators):
                            frameworks.append(framework)
            except Exception:
                pass
        
        # Check requirements.txt for Python projects
        requirements = self.project_path / 'requirements.txt'
        if requirements.exists():
            try:
                with open(requirements) as f:
                    content = f.read().lower()
                    
                    python_patterns = {
                        'Django': ['django'],
                        'Flask': ['flask'],
                        'FastAPI': ['fastapi'],
                        'SQLAlchemy': ['sqlalchemy'],
                        'Pandas': ['pandas'],
                        'NumPy': ['numpy'],
                        'Scikit-learn': ['scikit-learn', 'sklearn'],
                        'TensorFlow': ['tensorflow'],
                        'PyTorch': ['torch', 'pytorch'],
                        'Streamlit': ['streamlit'],
                        'Celery': ['celery'],
                        'Pytest': ['pytest']
                    }
                    
                    for framework, indicators in python_patterns.items():
                        if any(indicator in content for indicator in indicators):
                            frameworks.append(framework)
            except Exception:
                pass
        
        # Check for other framework indicators
        if (self.project_path / 'Dockerfile').exists():
            frameworks.append('Docker')
        
        if (self.project_path / 'docker-compose.yml').exists():
            frameworks.append('Docker Compose')
        
        if (self.project_path / '.github' / 'workflows').exists():
            frameworks.append('GitHub Actions')
        
        return frameworks
    
    def _detect_tools(self) -> List[str]:
        """Detect development tools and build systems"""
        tools = []
        
        # Check for common tool configuration files (including blockchain)
        tool_files = {
            'ESLint': ['.eslintrc.js', '.eslintrc.json', '.eslintrc.yml'],
            'Prettier': ['.prettierrc', '.prettierrc.json', '.prettierrc.yml'],
            'TypeScript': ['tsconfig.json'],
            'Babel': ['.babelrc', 'babel.config.js'],
            'Webpack': ['webpack.config.js'],
            'Rollup': ['rollup.config.js'],
            'Vite': ['vite.config.js', 'vite.config.ts'],
            'Makefile': ['Makefile'],
            'CMake': ['CMakeLists.txt'],
            'Gradle': ['build.gradle', 'gradle.properties'],
            'Maven': ['pom.xml'],
            'Cargo': ['Cargo.toml'],
            'Poetry': ['pyproject.toml'],
            'Pipenv': ['Pipfile'],
            'Terraform': ['main.tf', '*.tf'],
            'Kubernetes': ['*.yaml', '*.yml'],
            'Helm': ['Chart.yaml'],
            'Hardhat': ['hardhat.config.js', 'hardhat.config.ts'],
            'Truffle': ['truffle-config.js', 'truffle.js'],
            'Foundry': ['foundry.toml', 'forge.toml'],
            'Brownie': ['brownie-config.yaml'],
            'Slither': ['.slither.json'],
            'Mythril': ['mythril.yaml'],
            'Solhint': ['.solhint.json', 'solhint.json']
        }
        
        for tool, files in tool_files.items():
            if any((self.project_path / file).exists() or 
                   list(self.project_path.glob(file)) for file in files):
                tools.append(tool)
        
        return tools
    
    def _detect_architecture_patterns(self) -> List[str]:
        """Detect architectural patterns in the project"""
        patterns = []
        
        # Check directory structure for patterns
        dirs = [d.name for d in self.project_path.iterdir() if d.is_dir()]
        
        # MVC pattern
        if any(d in dirs for d in ['models', 'views', 'controllers']):
            patterns.append('MVC')
        
        # Microservices
        if 'services' in dirs or len([d for d in dirs if 'service' in d.lower()]) > 1:
            patterns.append('Microservices')
        
        # Clean Architecture
        if any(d in dirs for d in ['domain', 'infrastructure', 'application']):
            patterns.append('Clean Architecture')
        
        # Monorepo
        if 'packages' in dirs or 'apps' in dirs:
            patterns.append('Monorepo')
        
        # API-first
        if any(d in dirs for d in ['api', 'routes', 'endpoints']):
            patterns.append('API-first')
        
        # Event-driven
        if any(d in dirs for d in ['events', 'handlers', 'subscribers']):
            patterns.append('Event-driven')
        
        return patterns
    
    def _determine_project_type(self, languages: List[str], frameworks: List[str]) -> str:
        """Determine the primary project type"""
        
        # Blockchain/Smart Contract indicators (highest priority)
        blockchain_frameworks = ['Hardhat', 'Truffle', 'Foundry', 'OpenZeppelin', 'Brownie']
        blockchain_languages = ['Solidity', 'Vyper', 'Move', 'Cairo']
        if (any(fw in frameworks for fw in blockchain_frameworks) or 
            any(lang in languages for lang in blockchain_languages) or
            (self.project_path / 'contracts').exists()):
            return 'Blockchain/Smart Contract'
        
        # DeFi/Web3 Application indicators
        web3_frameworks = ['Ethers.js', 'Web3.js', 'Wagmi', 'Rainbow Kit', 'The Graph']
        if any(fw in frameworks for fw in web3_frameworks):
            return 'DeFi/Web3 Application'
        
        # Web application indicators
        web_frameworks = ['React', 'Vue.js', 'Angular', 'Next.js', 'Express', 'Django', 'Flask']
        if any(fw in frameworks for fw in web_frameworks):
            return 'Web Application'
        
        # Mobile application indicators
        mobile_frameworks = ['React Native', 'Flutter', 'Ionic']
        if any(fw in frameworks for fw in mobile_frameworks) or 'Swift' in languages or 'Kotlin' in languages:
            return 'Mobile Application'
        
        # Data science indicators
        data_frameworks = ['Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch']
        if any(fw in frameworks for fw in data_frameworks):
            return 'Data Science'
        
        # API/Backend indicators
        api_frameworks = ['FastAPI', 'Express', 'NestJS', 'Flask', 'Django']
        if any(fw in frameworks for fw in api_frameworks):
            return 'Backend API'
        
        # Infrastructure indicators
        if 'Terraform' in frameworks or 'Kubernetes' in frameworks:
            return 'Infrastructure'
        
        # Library/Package indicators
        if any(lang in languages for lang in ['Python', 'JavaScript', 'TypeScript']) and not frameworks:
            return 'Library'
        
        return 'General Application'
    
    def _calculate_complexity(self) -> int:
        """Calculate project complexity score (1-10)"""
        complexity = 1
        
        # Add points for multiple languages
        complexity += min(len(self.analysis.languages if self.analysis else []), 3)
        
        # Add points for frameworks
        complexity += min(len(self.analysis.frameworks if self.analysis else []) // 2, 2)
        
        # Add points for architecture patterns
        complexity += min(len(self.analysis.architecture_patterns if self.analysis else []), 2)
        
        # Add points for project size (rough estimate)
        try:
            file_count = len(list(self.project_path.rglob('*')))
            if file_count > 1000:
                complexity += 2
            elif file_count > 500:
                complexity += 1
        except Exception:
            pass
        
        return min(complexity, 10)
    
    def _detect_special_requirements(self) -> List[str]:
        """Detect special requirements or considerations"""
        requirements = []
        
        # Security-sensitive indicators
        if any(f in str(self.project_path).lower() for f in ['auth', 'security', 'crypto']):
            requirements.append('Security-focused')
        
        # Performance-critical indicators
        if any(f in str(self.project_path).lower() for f in ['performance', 'optimization', 'high-performance']):
            requirements.append('Performance-critical')
        
        # Real-time indicators
        if 'Socket.io' in getattr(self.analysis, 'frameworks', []):
            requirements.append('Real-time')
        
        # Database-heavy indicators
        db_frameworks = ['Prisma', 'TypeORM', 'Sequelize', 'SQLAlchemy']
        if any(fw in getattr(self.analysis, 'frameworks', []) for fw in db_frameworks):
            requirements.append('Database-heavy')
        
        return requirements
    
    def _suggest_subagents(self, project_type: str, languages: List[str], 
                          frameworks: List[str], tools: List[str], 
                          architecture: List[str]) -> List[str]:
        """Suggest appropriate subagents based on analysis"""
        agents = []
        
        # Core agents for all projects
        agents.extend(['code-reviewer', 'test-runner', 'documentation-generator'])
        
        # Blockchain/Smart Contract specific agents
        if project_type == 'Blockchain/Smart Contract':
            agents.extend([
                'solidity-developer',
                'smart-contract-auditor', 
                'gas-optimizer',
                'deployment-manager',
                'protocol-architect'
            ])
            
            # Add specific tools-based agents
            if 'Hardhat' in frameworks:
                agents.append('hardhat-specialist')
            if 'OpenZeppelin' in frameworks:
                agents.append('openzeppelin-specialist')
            if any(tool in tools for tool in ['Slither', 'Mythril']):
                agents.append('security-analyzer')
                
        # DeFi/Web3 Application agents
        elif project_type == 'DeFi/Web3 Application':
            agents.extend([
                'web3-frontend-developer',
                'defi-specialist',
                'wallet-integration-expert',
                'smart-contract-auditor'
            ])
            
            if 'React' in frameworks:
                agents.append('react-specialist')
            if any(fw in frameworks for fw in ['Wagmi', 'Rainbow Kit']):
                agents.append('wallet-connector-specialist')
        
        # Language-specific agents
        if 'Solidity' in languages:
            agents.append('solidity-developer')
        if 'Python' in languages:
            agents.append('python-specialist')
        if any(lang in languages for lang in ['JavaScript', 'TypeScript']):
            agents.append('javascript-specialist')
        if 'React' in frameworks or 'React TypeScript' in languages:
            agents.append('react-specialist')
        
        # Project type specific agents (non-blockchain)
        if project_type == 'Web Application':
            agents.extend(['frontend-developer', 'backend-developer', 'ui-specialist'])
        elif project_type == 'Backend API':
            agents.extend(['api-architect', 'database-specialist', 'performance-optimizer'])
        elif project_type == 'Data Science':
            agents.extend(['data-analyst', 'ml-engineer', 'visualization-specialist'])
        elif project_type == 'Mobile Application':
            agents.extend(['mobile-developer', 'ui-specialist'])
        elif project_type == 'Infrastructure':
            agents.extend(['devops-specialist', 'security-auditor', 'cloud-architect'])
        
        # Framework-specific agents
        if 'Docker' in frameworks:
            agents.append('docker-specialist')
        if 'Kubernetes' in frameworks:
            agents.append('kubernetes-specialist')
        if any(fw in frameworks for fw in ['Jest', 'Cypress', 'Playwright']):
            agents.append('testing-specialist')
        if 'GraphQL' in frameworks:
            agents.append('graphql-specialist')
        
        # Architecture-specific agents
        if 'Microservices' in architecture:
            agents.append('microservices-architect')
        if 'Clean Architecture' in architecture:
            agents.append('architecture-reviewer')
        
        return list(set(agents))  # Remove duplicates
    
    def _is_ignored(self, file_path: Path) -> bool:
        """Check if file should be ignored in analysis"""
        ignored_dirs = {
            'node_modules', '.git', '__pycache__', '.venv', 'venv',
            'dist', 'build', '.next', 'coverage', '.pytest_cache'
        }
        
        for part in file_path.parts:
            if part in ignored_dirs or part.startswith('.'):
                return True
        
        return False

class SubagentManager:
    """Manages Claude Code subagents"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_agents_dir = self.project_path / '.claude' / 'agents'
        self.user_agents_dir = Path.home() / '.claude' / 'agents'
        
    def create_agent(self, config: SubagentConfig, scope: str = 'project') -> bool:
        """Create a new subagent"""
        agents_dir = self.project_agents_dir if scope == 'project' else self.user_agents_dir
        agents_dir.mkdir(parents=True, exist_ok=True)
        
        agent_file = agents_dir / f"{config.name}.md"
        
        # Prepare YAML frontmatter
        frontmatter = {
            'name': config.name,
            'description': config.description
        }
        
        if config.tools:
            frontmatter['tools'] = ', '.join(config.tools)
        
        # Create file content
        content = "---\n"
        content += yaml.dump(frontmatter, default_flow_style=False)
        content += "---\n\n"
        content += config.system_prompt
        
        try:
            with open(agent_file, 'w') as f:
                f.write(content)
            console.print(f"[green]✓ Created subagent: {config.name}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ Failed to create subagent: {e}[/red]")
            return False
    
    def list_agents(self) -> Dict[str, List[str]]:
        """List all available subagents"""
        agents = {'project': [], 'user': []}
        
        # List project agents
        if self.project_agents_dir.exists():
            for agent_file in self.project_agents_dir.glob('*.md'):
                agents['project'].append(agent_file.stem)
        
        # List user agents
        if self.user_agents_dir.exists():
            for agent_file in self.user_agents_dir.glob('*.md'):
                agents['user'].append(agent_file.stem)
        
        return agents
    
    def delete_agent(self, name: str, scope: str = 'project') -> bool:
        """Delete a subagent"""
        agents_dir = self.project_agents_dir if scope == 'project' else self.user_agents_dir
        agent_file = agents_dir / f"{name}.md"
        
        if agent_file.exists():
            try:
                agent_file.unlink()
                console.print(f"[green]✓ Deleted subagent: {name}[/green]")
                return True
            except Exception as e:
                console.print(f"[red]✗ Failed to delete subagent: {e}[/red]")
                return False
        else:
            console.print(f"[yellow]! Subagent not found: {name}[/yellow]")
            return False
    
    def get_agent_config(self, name: str, scope: str = 'project') -> Optional[SubagentConfig]:
        """Get configuration for a specific subagent"""
        agents_dir = self.project_agents_dir if scope == 'project' else self.user_agents_dir
        agent_file = agents_dir / f"{name}.md"
        
        if not agent_file.exists():
            return None
        
        try:
            with open(agent_file) as f:
                content = f.read()
            
            # Parse frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                return None
            
            frontmatter = yaml.safe_load(parts[1])
            system_prompt = parts[2].strip()
            
            tools = None
            if 'tools' in frontmatter:
                tools = [t.strip() for t in frontmatter['tools'].split(',')]
            
            return SubagentConfig(
                name=frontmatter['name'],
                description=frontmatter['description'],
                tools=tools,
                system_prompt=system_prompt
            )
        except Exception as e:
            console.print(f"[red]Error reading agent config: {e}[/red]")
            return None

class AgentTemplates:
    """Predefined agent templates"""
    
    @staticmethod
    def get_template(agent_type: str) -> Optional[SubagentConfig]:
        """Get a predefined agent template"""
        templates = {
            'code-reviewer': SubagentConfig(
                name='code-reviewer',
                description='Use PROACTIVELY to review code changes, check for bugs, performance issues, and best practices',
                tools=['Read', 'Write', 'Bash'],
                system_prompt="""You are an expert code reviewer with deep knowledge across multiple programming languages and frameworks.

When reviewing code:
1. Check for bugs, logical errors, and edge cases
2. Verify adherence to best practices and coding standards
3. Look for performance issues and optimization opportunities
4. Ensure proper error handling and security considerations
5. Suggest improvements for readability and maintainability
6. Check for proper testing coverage

Provide specific, actionable feedback with examples when possible. Focus on the most important issues first."""
            ),
            
            'test-runner': SubagentConfig(
                name='test-runner',
                description='Use PROACTIVELY to run tests, fix test failures, and improve test coverage',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a testing specialist focused on ensuring code quality through comprehensive testing.

Your responsibilities:
1. Run existing tests and analyze results
2. Fix failing tests and understand why they failed
3. Write new tests for uncovered code paths
4. Suggest testing strategies and frameworks
5. Ensure tests are maintainable and fast
6. Help set up CI/CD testing pipelines

Always run tests after making changes and explain test failures clearly."""
            ),
            
            'python-specialist': SubagentConfig(
                name='python-specialist',
                description='Use for Python-specific development tasks, optimization, and best practices',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a Python expert with deep knowledge of the language, ecosystem, and best practices.

Areas of expertise:
1. Python language features and idioms
2. Popular frameworks (Django, Flask, FastAPI, etc.)
3. Data science libraries (pandas, numpy, scikit-learn)
4. Performance optimization and profiling
5. Package management and virtual environments
6. Code style (PEP 8, black, isort)
7. Testing with pytest
8. Async programming

Write Pythonic code that follows best practices and is well-documented."""
            ),
            
            'react-specialist': SubagentConfig(
                name='react-specialist',
                description='Use for React development, components, hooks, and modern React patterns',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a React expert specializing in modern React development patterns and best practices.

Areas of expertise:
1. Functional components and hooks
2. State management (useState, useReducer, Context API)
3. Performance optimization (React.memo, useMemo, useCallback)
4. Modern React patterns and architecture
5. TypeScript integration
6. Testing React components
7. Next.js and server-side rendering
8. CSS-in-JS and styling solutions

Write clean, performant React code following current best practices."""
            ),
            
            'api-architect': SubagentConfig(
                name='api-architect',
                description='Use for designing REST APIs, GraphQL schemas, and backend architecture',
                tools=['Read', 'Write', 'Bash'],
                system_prompt="""You are an API design expert specializing in building scalable, maintainable backend systems.

Areas of expertise:
1. RESTful API design principles
2. GraphQL schema design and optimization
3. Database schema design and optimization
4. Authentication and authorization patterns
5. API versioning and backward compatibility
6. Performance optimization and caching
7. Error handling and status codes
8. API documentation and testing

Design APIs that are intuitive, well-documented, and follow industry standards."""
            ),
            
            'devops-specialist': SubagentConfig(
                name='devops-specialist',
                description='Use for Docker, Kubernetes, CI/CD, and infrastructure automation',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a DevOps engineer expert in infrastructure automation, containerization, and deployment pipelines.

Areas of expertise:
1. Docker containerization and optimization
2. Kubernetes orchestration and management
3. CI/CD pipeline design and implementation
4. Infrastructure as Code (Terraform, CloudFormation)
5. Monitoring and logging solutions
6. Security best practices
7. Cloud platforms (AWS, GCP, Azure)
8. Performance monitoring and optimization

Focus on automation, reliability, and security in all infrastructure decisions."""
            ),
            
            'security-auditor': SubagentConfig(
                name='security-auditor',
                description='Use PROACTIVELY to audit code for security vulnerabilities and compliance',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a security expert focused on identifying and fixing security vulnerabilities.

Security areas to check:
1. Input validation and sanitization
2. Authentication and authorization flaws
3. SQL injection and XSS vulnerabilities
4. Insecure direct object references
5. Security misconfiguration
6. Sensitive data exposure
7. Insufficient logging and monitoring
8. Using components with known vulnerabilities

Follow OWASP guidelines and provide specific remediation steps for any issues found."""
            ),
            
            'performance-optimizer': SubagentConfig(
                name='performance-optimizer',
                description='Use to analyze and optimize application performance',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a performance optimization expert focused on making applications faster and more efficient.

Areas of focus:
1. Code profiling and bottleneck identification
2. Database query optimization
3. Caching strategies and implementation
4. Frontend performance optimization
5. Memory usage and garbage collection
6. Network optimization and CDN usage
7. Bundle size optimization
8. Server-side rendering optimization

Provide specific, measurable performance improvements with benchmarks when possible."""
            ),
            
            'documentation-generator': SubagentConfig(
                name='documentation-generator',
                description='Use to create and maintain comprehensive project documentation',
                tools=['Read', 'Write'],
                system_prompt="""You are a technical documentation expert focused on creating clear, comprehensive documentation.

Documentation types:
1. README files with clear setup instructions
2. API documentation with examples
3. Code comments and docstrings
4. Architecture diagrams and explanations
5. User guides and tutorials
6. Contributing guidelines
7. Changelog maintenance
8. Troubleshooting guides

Write documentation that is clear, accurate, and helpful for both new and experienced developers."""
            ),
            
            # Blockchain-specific templates
            'solidity-developer': SubagentConfig(
                name='solidity-developer',
                description='Use for Solidity smart contract development, optimization, and best practices',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a Solidity expert specializing in secure, efficient smart contract development.

Areas of expertise:
1. Solidity language features and syntax
2. Smart contract design patterns
3. Gas optimization techniques
4. Security best practices (reentrancy, overflow/underflow, etc.)
5. ERC token standards (ERC-20, ERC-721, ERC-1155, ERC-5114)
6. OpenZeppelin contracts and patterns
7. Upgradeable contract patterns (proxy, diamond)
8. Event emission and error handling
9. Testing with Hardhat/Truffle/Foundry
10. Contract verification and deployment

Always prioritize security, gas efficiency, and code readability. Follow established patterns and include comprehensive NatSpec documentation."""
            ),
            
            'smart-contract-auditor': SubagentConfig(
                name='smart-contract-auditor',
                description='Use PROACTIVELY to audit smart contracts for security vulnerabilities',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a smart contract security auditor with expertise in identifying blockchain-specific vulnerabilities.

Security checks to perform:
1. Reentrancy attacks and state changes
2. Integer overflow/underflow vulnerabilities
3. Access control and privilege escalation
4. Front-running and MEV vulnerabilities
5. Gas limit issues and denial of service
6. Oracle manipulation and price feed attacks
7. Flash loan vulnerabilities
8. Upgradability risks and storage collisions
9. ERC standard compliance
10. Business logic flaws

Use static analysis tools (Slither, Mythril) and manual review. Provide specific remediation steps and severity ratings for each finding."""
            ),
            
            'gas-optimizer': SubagentConfig(
                name='gas-optimizer',
                description='Use to analyze and optimize smart contract gas usage',
                tools=['Bash', 'Read', 'Write'], 
                system_prompt="""You are a gas optimization specialist focused on reducing smart contract execution costs.

Optimization strategies:
1. Storage layout optimization (packing, slot usage)
2. Function selector optimization 
3. Loop optimization and gas-efficient algorithms
4. Eliminating unnecessary SLOAD/SSTORE operations
5. Using appropriate data types and structures
6. Optimizing external calls and delegatecalls
7. Event optimization for off-chain indexing
8. Batch operations and multicall patterns
9. Assembly optimization where appropriate
10. Proxy pattern gas considerations

Always measure before/after gas consumption and provide specific savings estimates. Balance optimization with code readability and security."""
            ),
            
            'deployment-manager': SubagentConfig(
                name='deployment-manager',
                description='Use for smart contract deployment, verification, and network management',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a deployment specialist expert in managing smart contract deployments across multiple networks.

Responsibilities:
1. Multi-network deployment strategies
2. Contract verification on block explorers
3. Deployment script creation and testing
4. Gas price optimization for deployments
5. Proxy deployment and upgrade management
6. Environment-specific configuration management
7. Deployment rollback and recovery procedures
8. Network compatibility and feature checks
9. Post-deployment testing and validation
10. Monitoring and alerting setup

Ensure deployments are secure, cost-effective, and properly verified. Always test on testnets before mainnet deployment."""
            ),
            
            'protocol-architect': SubagentConfig(
                name='protocol-architect',
                description='Use for designing protocol architecture, tokenomics, and system interactions',
                tools=['Read', 'Write', 'Bash'],
                system_prompt="""You are a protocol architect specializing in designing decentralized systems and tokenomics.

Design expertise:
1. Protocol architecture and component interactions
2. Tokenomics design and incentive mechanisms
3. Governance model design and implementation
4. Multi-contract system orchestration
5. Cross-chain compatibility and bridges
6. Scalability solutions and layer 2 integration
7. Economic security and attack resistance
8. User experience and protocol usability
9. Composability with other DeFi protocols
10. Upgrade paths and migration strategies

Focus on creating robust, scalable, and user-friendly protocols. Consider long-term sustainability and community governance."""
            ),
            
            'hardhat-specialist': SubagentConfig(
                name='hardhat-specialist',
                description='Use for Hardhat development environment setup, testing, and tooling',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a Hardhat expert specializing in development environment optimization and testing frameworks.

Areas of expertise:
1. Hardhat configuration and plugin management
2. Testing framework setup (Chai, Mocha, Ethers)
3. Deployment script creation and management
4. Network configuration for multiple chains
5. Gas reporting and optimization tools
6. Coverage reporting and analysis
7. Debugging and tracing transactions
8. Fork testing against mainnet
9. Custom task creation and automation
10. Integration with external tools and services

Create efficient development workflows that maximize productivity and code quality. Ensure comprehensive testing coverage."""
            ),
            
            'openzeppelin-specialist': SubagentConfig(
                name='openzeppelin-specialist',
                description='Use for OpenZeppelin contracts, security patterns, and upgrade mechanisms',
                tools=['Read', 'Write', 'Bash'],
                system_prompt="""You are an OpenZeppelin expert specializing in secure contract patterns and upgrade mechanisms.

Expertise areas:
1. OpenZeppelin contract library usage and customization
2. Access control patterns (Ownable, AccessControl, roles)
3. Token standards implementation (ERC-20, ERC-721, ERC-1155)
4. Upgrade patterns (Transparent, UUPS, Beacon proxies)
5. Security features (ReentrancyGuard, Pausable)
6. Governance contracts and voting mechanisms
7. Utilities (Multicall, EIP-712, cryptographic primitives)
8. Best practices for contract composition
9. Upgrade safety and storage layout management
10. Integration with Defender and other OpenZeppelin tools

Always use battle-tested OpenZeppelin patterns. Prioritize security and follow established upgrade best practices."""
            ),
            
            'web3-frontend-developer': SubagentConfig(
                name='web3-frontend-developer',
                description='Use for Web3 frontend development with wallet integration and blockchain interaction',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a Web3 frontend developer expert in building decentralized application interfaces.

Specializations:
1. Wallet connection and management (MetaMask, WalletConnect)
2. Web3 library integration (Ethers.js, Web3.js, Wagmi)
3. Smart contract interaction from frontend
4. Transaction handling and error management
5. Network switching and multi-chain support
6. ENS integration and address resolution
7. IPFS integration for decentralized storage
8. Real-time blockchain data updates
9. Gas estimation and transaction optimization
10. Mobile Web3 and responsive design

Create intuitive Web3 UX that abstracts blockchain complexity while maintaining transparency and user control."""
            ),
            
            'defi-specialist': SubagentConfig(
                name='defi-specialist',
                description='Use for DeFi protocol development, AMM design, and yield strategies',
                tools=['Read', 'Write', 'Bash'],
                system_prompt="""You are a DeFi specialist expert in decentralized finance protocols and mechanisms.

DeFi expertise:
1. AMM (Automated Market Maker) design and implementation
2. Liquidity mining and yield farming mechanisms
3. Lending and borrowing protocol development
4. Flash loan implementation and security
5. Oracle integration and price feed management
6. Governance token design and distribution
7. Cross-protocol composability (money legos)
8. Risk management and liquidation mechanisms
9. MEV protection and fair ordering
10. Economic modeling and tokenomics analysis

Design sustainable DeFi protocols with proper risk management, user incentives, and long-term value creation."""
            ),
            
            'wallet-integration-expert': SubagentConfig(
                name='wallet-integration-expert',
                description='Use for wallet integration, transaction management, and Web3 user experience',
                tools=['Bash', 'Read', 'Write'],
                system_prompt="""You are a wallet integration expert specializing in seamless Web3 user experiences.

Integration expertise:
1. Multi-wallet support (MetaMask, Coinbase, Rainbow, etc.)
2. WalletConnect protocol implementation
3. Transaction signing and verification flows
4. Network switching and chain management
5. Account abstraction and smart wallet integration
6. Mobile wallet deep linking and QR codes
7. Error handling and user feedback systems
8. Batch transactions and multicall optimization
9. Gasless transactions and meta-transactions
10. Security best practices for wallet interaction

Create frictionless wallet experiences that maintain security while providing excellent UX for both novice and expert users."""
            )
        }
        
        return templates.get(agent_type)

class CLIInterface:
    """Command-line interface for the subagent manager"""
    
    def __init__(self):
        self.current_path = os.getcwd()
        
    def run(self):
        """Main CLI entry point"""
        parser = argparse.ArgumentParser(
            description="Claude Code Project Analyzer & Subagent Manager"
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze project structure')
        analyze_parser.add_argument('--path', default='.', help='Project path to analyze')
        analyze_parser.add_argument('--create-agents', action='store_true', 
                                   help='Automatically create suggested subagents')
        
        # Create command
        create_parser = subparsers.add_parser('create', help='Create a new subagent')
        create_parser.add_argument('--interactive', action='store_true', 
                                  help='Interactive subagent creation')
        create_parser.add_argument('--template', help='Use a predefined template')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List all subagents')
        
        # UI command
        ui_parser = subparsers.add_parser('ui', help='Launch interactive UI')
        
        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a subagent')
        delete_parser.add_argument('name', help='Name of subagent to delete')
        delete_parser.add_argument('--scope', choices=['project', 'user'], 
                                  default='project', help='Subagent scope')
        
        args = parser.parse_args()
        
        if args.command == 'analyze':
            self.analyze_project(args.path, args.create_agents)
        elif args.command == 'create':
            if args.interactive:
                self.interactive_create()
            elif args.template:
                self.create_from_template(args.template)
            else:
                console.print("[red]Please specify --interactive or --template[/red]")
        elif args.command == 'list':
            self.list_agents()
        elif args.command == 'ui':
            self.launch_ui()
        elif args.command == 'delete':
            self.delete_agent(args.name, args.scope)
        else:
            parser.print_help()
    
    def analyze_project(self, path: str, create_agents: bool = False):
        """Analyze project and optionally create agents"""
        analyzer = ProjectAnalyzer(path)
        analysis = analyzer.analyze_project()
        
        # Display analysis results
        self.display_analysis_results(analysis)
        
        if create_agents:
            self.auto_create_agents(analysis, path)
    
    def display_analysis_results(self, analysis: ProjectAnalysis):
        """Display project analysis results in a formatted way"""
        console.print("\n[bold blue]🔍 Project Analysis Results[/bold blue]")
        
        # Create analysis table
        table = Table(title="Project Overview")
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Project Type", analysis.project_type)
        table.add_row("Complexity Score", f"{analysis.complexity_score}/10")
        table.add_row("Languages", ", ".join(analysis.languages))
        table.add_row("Frameworks", ", ".join(analysis.frameworks))
        table.add_row("Tools", ", ".join(analysis.tools))
        table.add_row("Architecture Patterns", ", ".join(analysis.architecture_patterns))
        table.add_row("Special Requirements", ", ".join(analysis.special_requirements))
        
        console.print(table)
        
        # Display suggested subagents
        console.print("\n[bold yellow]🤖 Suggested Subagents[/bold yellow]")
        agents_tree = Tree("Recommended Subagents")
        
        # Group agents by category
        core_agents = ['code-reviewer', 'test-runner', 'documentation-generator']
        specialized_agents = [a for a in analysis.suggested_subagents if a not in core_agents]
        
        core_branch = agents_tree.add("Core Agents")
        for agent in core_agents:
            if agent in analysis.suggested_subagents:
                core_branch.add(f"✓ {agent}")
        
        if specialized_agents:
            spec_branch = agents_tree.add("Specialized Agents")
            for agent in specialized_agents:
                spec_branch.add(f"• {agent}")
        
        console.print(agents_tree)
    
    def auto_create_agents(self, analysis: ProjectAnalysis, path: str):
        """Automatically create suggested subagents"""
        manager = SubagentManager(path)
        
        console.print("\n[bold green]🚀 Creating Suggested Subagents[/bold green]")
        
        created_count = 0
        for agent_name in analysis.suggested_subagents:
            template = AgentTemplates.get_template(agent_name)
            if template:
                if manager.create_agent(template):
                    created_count += 1
            else:
                console.print(f"[yellow]! No template available for: {agent_name}[/yellow]")
        
        console.print(f"\n[green]✓ Created {created_count} subagents successfully![/green]")
    
    def interactive_create(self):
        """Interactive subagent creation wizard"""
        console.print("[bold blue]🧙 Interactive Subagent Creation Wizard[/bold blue]\n")
        
        # Basic information
        name = questionary.text(
            "What should we name this subagent?",
            validate=lambda x: len(x) > 0 and x.replace('-', '').replace('_', '').isalnum()
        ).ask()
        
        description = questionary.text(
            "Describe when this subagent should be used:",
            validate=lambda x: len(x) > 10
        ).ask()
        
        # Category selection
        category = questionary.select(
            "What category does this subagent belong to?",
            choices=[
                "Development",
                "Testing",
                "Security",
                "Performance",
                "Documentation",
                "DevOps",
                "Architecture",
                "Custom"
            ]
        ).ask()
        
        # Tool selection
        available_tools = [
            "Bash", "Read", "Write", "Edit", "Search", "Browser",
            "Git", "Docker", "Kubernetes", "AWS", "Database"
        ]
        
        tools = questionary.checkbox(
            "Select tools this subagent should have access to:",
            choices=available_tools
        ).ask()
        
        # Auto-invoke option
        auto_invoke = questionary.confirm(
            "Should this subagent be invoked automatically when relevant?"
        ).ask()
        
        # System prompt
        console.print("\n[yellow]Now, let's create the system prompt for your subagent.[/yellow]")
        console.print("This defines the subagent's personality, expertise, and behavior.")
        
        use_template = questionary.confirm(
            "Would you like to start with a template and customize it?"
        ).ask()
        
        if use_template:
            prompt_template = self.get_prompt_template(category)
            console.print(f"\n[dim]{prompt_template}[/dim]")
            
            system_prompt = questionary.text(
                "Edit the template above or provide your own system prompt:",
                default=prompt_template,
                multiline=True
            ).ask()
        else:
            system_prompt = questionary.text(
                "Enter the system prompt for your subagent:",
                multiline=True,
                validate=lambda x: len(x) > 50
            ).ask()
        
        # Scope selection
        scope = questionary.select(
            "Where should this subagent be available?",
            choices=[
                questionary.Choice("This project only", "project"),
                questionary.Choice("All my projects", "user")
            ]
        ).ask()
        
        # Create the subagent
        config = SubagentConfig(
            name=name,
            description=description + (" PROACTIVELY" if auto_invoke else ""),
            tools=tools if tools else None,
            system_prompt=system_prompt,
            category=category,
            auto_invoke=auto_invoke
        )
        
        manager = SubagentManager(self.current_path)
        
        # Show preview
        self.show_agent_preview(config)
        
        if questionary.confirm("Create this subagent?").ask():
            if manager.create_agent(config, scope):
                console.print(f"\n[green]🎉 Successfully created subagent '{name}'![/green]")
                console.print(f"You can now use it by saying: 'Use the {name} subagent to...'")
            else:
                console.print(f"[red]Failed to create subagent '{name}'[/red]")
    
    def get_prompt_template(self, category: str) -> str:
        """Get a template system prompt based on category"""
        templates = {
            "Development": """You are a software development expert specializing in writing high-quality, maintainable code.

Your responsibilities:
1. Write clean, readable code following best practices
2. Implement features according to requirements
3. Ensure proper error handling and edge case coverage
4. Follow established coding standards and patterns
5. Optimize for performance when necessary

Always explain your approach and provide well-commented code.""",
            
            "Testing": """You are a testing specialist focused on ensuring code quality and reliability.

Your responsibilities:
1. Write comprehensive test suites with good coverage
2. Create unit, integration, and end-to-end tests
3. Debug and fix failing tests
4. Suggest testing strategies and improvements
5. Ensure tests are maintainable and fast

Focus on testing the most critical paths and edge cases first.""",
            
            "Security": """You are a security expert focused on identifying and preventing security vulnerabilities.

Your responsibilities:
1. Conduct security audits and code reviews
2. Identify common vulnerabilities (OWASP Top 10)
3. Implement secure coding practices
4. Suggest security improvements and mitigations
5. Ensure compliance with security standards

Always provide specific remediation steps for security issues.""",
            
            "Performance": """You are a performance optimization expert focused on making applications faster and more efficient.

Your responsibilities:
1. Profile code to identify performance bottlenecks
2. Optimize algorithms and data structures
3. Implement caching strategies
4. Optimize database queries and network calls
5. Monitor and measure performance improvements

Provide concrete metrics and benchmarks when possible.""",
            
            "Documentation": """You are a technical documentation expert focused on creating clear, comprehensive documentation.

Your responsibilities:
1. Write clear, accurate documentation
2. Create API documentation with examples
3. Maintain README files and guides
4. Document architecture and design decisions
5. Ensure documentation stays up-to-date

Write for your target audience and include practical examples.""",
            
            "DevOps": """You are a DevOps engineer expert in infrastructure automation and deployment.

Your responsibilities:
1. Design and implement CI/CD pipelines
2. Manage containerization and orchestration
3. Automate infrastructure provisioning
4. Monitor system health and performance
5. Implement security and backup strategies

Focus on automation, reliability, and scalability.""",
            
            "Architecture": """You are a software architect focused on designing scalable, maintainable systems.

Your responsibilities:
1. Design system architecture and components
2. Make technology and framework decisions
3. Ensure scalability and performance
4. Define coding standards and patterns
5. Review architectural decisions

Consider long-term maintainability and team capabilities."""
        }
        
        return templates.get(category, "You are an expert assistant specializing in this domain.")
    
    def show_agent_preview(self, config: SubagentConfig):
        """Show a preview of the subagent configuration"""
        console.print("\n[bold]📋 Subagent Preview[/bold]")
        
        preview_table = Table()
        preview_table.add_column("Property", style="cyan")
        preview_table.add_column("Value", style="white")
        
        preview_table.add_row("Name", config.name)
        preview_table.add_row("Description", config.description)
        preview_table.add_row("Tools", ", ".join(config.tools) if config.tools else "All available tools")
        preview_table.add_row("Auto-invoke", "Yes" if config.auto_invoke else "No")
        
        console.print(preview_table)
        
        # Show system prompt
        console.print(f"\n[bold]System Prompt:[/bold]")
        syntax = Syntax(config.system_prompt, "markdown", theme="monokai", line_numbers=False)
        console.print(Panel(syntax, title="System Prompt", border_style="blue"))
    
    def create_from_template(self, template_name: str):
        """Create subagent from a predefined template"""
        template = AgentTemplates.get_template(template_name)
        if not template:
            console.print(f"[red]Template '{template_name}' not found[/red]")
            available_templates = [
                'code-reviewer', 'test-runner', 'python-specialist', 'react-specialist',
                'api-architect', 'devops-specialist', 'security-auditor', 
                'performance-optimizer', 'documentation-generator',
                'solidity-developer', 'smart-contract-auditor', 'gas-optimizer',
                'deployment-manager', 'protocol-architect', 'hardhat-specialist',
                'openzeppelin-specialist', 'web3-frontend-developer', 'defi-specialist',
                'wallet-integration-expert'
            ]
            console.print(f"Available templates: {', '.join(available_templates)}")
            return
        
        scope = questionary.select(
            f"Where should the '{template_name}' subagent be available?",
            choices=[
                questionary.Choice("This project only", "project"),
                questionary.Choice("All my projects", "user")
            ]
        ).ask()
        
        manager = SubagentManager(self.current_path)
        
        if manager.create_agent(template, scope):
            console.print(f"[green]✓ Created '{template_name}' subagent successfully![/green]")
        else:
            console.print(f"[red]✗ Failed to create '{template_name}' subagent[/red]")
    
    def list_agents(self):
        """List all available subagents"""
        manager = SubagentManager(self.current_path)
        agents = manager.list_agents()
        
        console.print("\n[bold blue]📋 Available Subagents[/bold blue]")
        
        if agents['project'] or agents['user']:
            table = Table()
            table.add_column("Name", style="cyan")
            table.add_column("Scope", style="yellow")
            table.add_column("Description", style="white")
            
            # Add project agents
            for agent_name in agents['project']:
                config = manager.get_agent_config(agent_name, 'project')
                description = config.description[:60] + "..." if config and len(config.description) > 60 else (config.description if config else "No description")
                table.add_row(agent_name, "Project", description)
            
            # Add user agents (only if not overridden by project)
            for agent_name in agents['user']:
                if agent_name not in agents['project']:
                    config = manager.get_agent_config(agent_name, 'user')
                    description = config.description[:60] + "..." if config and len(config.description) > 60 else (config.description if config else "No description")
                    table.add_row(agent_name, "User", description)
            
            console.print(table)
        else:
            console.print("[yellow]No subagents found. Use 'create' command to add some![/yellow]")
    
    def delete_agent(self, name: str, scope: str):
        """Delete a subagent"""
        manager = SubagentManager(self.current_path)
        
        if questionary.confirm(f"Are you sure you want to delete the '{name}' subagent?").ask():
            manager.delete_agent(name, scope)
    
    def launch_ui(self):
        """Launch interactive management UI"""
        while True:
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    "🔍 Analyze current project",
                    "🤖 Create new subagent",
                    "📋 List all subagents",
                    "✏️  Edit existing subagent",
                    "🗑️  Delete subagent",
                    "📊 View project stats",
                    "❌ Exit"
                ]
            ).ask()
            
            if choice.startswith("🔍"):
                self.analyze_project(self.current_path, False)
                
                if questionary.confirm("Would you like to create the suggested subagents?").ask():
                    self.auto_create_agents_interactive()
                    
            elif choice.startswith("🤖"):
                self.interactive_create()
                
            elif choice.startswith("📋"):
                self.list_agents()
                
            elif choice.startswith("✏️"):
                self.edit_agent_interactive()
                
            elif choice.startswith("🗑️"):
                self.delete_agent_interactive()
                
            elif choice.startswith("📊"):
                self.show_project_stats()
                
            elif choice.startswith("❌"):
                console.print("[blue]👋 Goodbye![/blue]")
                break
            
            console.print()  # Add spacing
    
    def auto_create_agents_interactive(self):
        """Interactive version of auto-creating agents"""
        analyzer = ProjectAnalyzer(self.current_path)
        analysis = analyzer.analyze_project()
        
        # Let user select which agents to create
        agent_choices = []
        for agent in analysis.suggested_subagents:
            template = AgentTemplates.get_template(agent)
            if template:
                agent_choices.append(questionary.Choice(
                    f"{agent} - {template.description[:60]}...",
                    agent
                ))
        
        if not agent_choices:
            console.print("[yellow]No predefined templates available for suggested agents[/yellow]")
            return
        
        selected_agents = questionary.checkbox(
            "Select which subagents to create:",
            choices=agent_choices
        ).ask()
        
        if selected_agents:
            manager = SubagentManager(self.current_path)
            created_count = 0
            
            for agent_name in selected_agents:
                template = AgentTemplates.get_template(agent_name)
                if template and manager.create_agent(template):
                    created_count += 1
            
            console.print(f"[green]✓ Created {created_count} subagents![/green]")
    
    def edit_agent_interactive(self):
        """Interactive agent editing"""
        manager = SubagentManager(self.current_path)
        agents = manager.list_agents()
        
        all_agents = []
        for scope in ['project', 'user']:
            for agent in agents[scope]:
                all_agents.append(f"{agent} ({scope})")
        
        if not all_agents:
            console.print("[yellow]No subagents available to edit[/yellow]")
            return
        
        selected = questionary.select(
            "Which subagent would you like to edit?",
            choices=all_agents
        ).ask()
        
        agent_name, scope = selected.rsplit(' (', 1)
        scope = scope.rstrip(')')
        
        config = manager.get_agent_config(agent_name, scope)
        if not config:
            console.print(f"[red]Could not load configuration for {agent_name}[/red]")
            return
        
        # Show current config
        self.show_agent_preview(config)
        
        # Edit options
        edit_choice = questionary.select(
            "What would you like to edit?",
            choices=[
                "Description",
                "Tools",
                "System Prompt",
                "Cancel"
            ]
        ).ask()
        
        if edit_choice == "Description":
            new_description = questionary.text(
                "New description:",
                default=config.description
            ).ask()
            config.description = new_description
            
        elif edit_choice == "Tools":
            available_tools = ["Bash", "Read", "Write", "Edit", "Search", "Browser", "Git", "Docker"]
            current_tools = config.tools or []
            
            new_tools = questionary.checkbox(
                "Select tools:",
                choices=available_tools,
                default=current_tools
            ).ask()
            config.tools = new_tools if new_tools else None
            
        elif edit_choice == "System Prompt":
            new_prompt = questionary.text(
                "New system prompt:",
                default=config.system_prompt,
                multiline=True
            ).ask()
            config.system_prompt = new_prompt
            
        elif edit_choice == "Cancel":
            return
        
        # Save changes
        if manager.create_agent(config, scope):
            console.print(f"[green]✓ Updated {agent_name} successfully![/green]")
        else:
            console.print(f"[red]✗ Failed to update {agent_name}[/red]")
    
    def delete_agent_interactive(self):
        """Interactive agent deletion"""
        manager = SubagentManager(self.current_path)
        agents = manager.list_agents()
        
        all_agents = []
        for scope in ['project', 'user']:
            for agent in agents[scope]:
                all_agents.append(f"{agent} ({scope})")
        
        if not all_agents:
            console.print("[yellow]No subagents available to delete[/yellow]")
            return
        
        selected = questionary.select(
            "Which subagent would you like to delete?",
            choices=all_agents + ["Cancel"]
        ).ask()
        
        if selected == "Cancel":
            return
        
        agent_name, scope = selected.rsplit(' (', 1)
        scope = scope.rstrip(')')
        
        if questionary.confirm(f"Are you sure you want to delete '{agent_name}'?").ask():
            manager.delete_agent(agent_name, scope)
    
    def show_project_stats(self):
        """Show project statistics and insights"""
        analyzer = ProjectAnalyzer(self.current_path)
        analysis = analyzer.analyze_project()
        manager = SubagentManager(self.current_path)
        agents = manager.list_agents()
        
        console.print("\n[bold blue]📊 Project Statistics[/bold blue]")
        
        # Basic stats
        stats_table = Table(title="Overview")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        total_agents = len(agents['project']) + len(agents['user'])
        coverage_score = min(total_agents * 10, 100)  # Simple coverage metric
        
        stats_table.add_row("Project Complexity", f"{analysis.complexity_score}/10")
        stats_table.add_row("Active Subagents", str(total_agents))
        stats_table.add_row("Coverage Score", f"{coverage_score}%")
        stats_table.add_row("Suggested Agents", str(len(analysis.suggested_subagents)))
        
        console.print(stats_table)
        
        # Recommendations
        missing_agents = set(analysis.suggested_subagents) - set(agents['project']) - set(agents['user'])
        if missing_agents:
            console.print(f"\n[yellow]💡 Consider adding these subagents:[/yellow]")
            for agent in missing_agents:
                console.print(f"  • {agent}")


def main():
    """Main entry point"""
    try:
        cli = CLIInterface()
        cli.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()