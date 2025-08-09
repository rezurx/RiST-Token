#!/usr/bin/env python3
"""
Blockchain Agent Registry System
Manages agent capabilities, metadata, and discovery for blockchain development tasks
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import inspect

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Types of tasks that can be performed by blockchain agents"""
    SMART_CONTRACT_DEVELOPMENT = "smart_contract_development"
    SECURITY_AUDIT = "security_audit"
    DEPLOYMENT_MANAGEMENT = "deployment_management"
    TESTING_AUTOMATION = "testing_automation"
    GAS_OPTIMIZATION = "gas_optimization"
    DOCUMENTATION_GENERATION = "documentation_generation"
    INTEGRATION_TESTING = "integration_testing"
    PROTOCOL_ANALYSIS = "protocol_analysis"

class AgentCapability(Enum):
    """Specific capabilities that blockchain agents can provide"""
    SOLIDITY_DEVELOPMENT = "solidity_development"
    CONTRACT_VERIFICATION = "contract_verification"
    SECURITY_SCANNING = "security_scanning"
    GAS_ANALYSIS = "gas_analysis"
    TEST_GENERATION = "test_generation"
    DEPLOYMENT_SCRIPTING = "deployment_scripting"
    DOCUMENTATION_WRITING = "documentation_writing"
    CODE_OPTIMIZATION = "code_optimization"
    INTERFACE_DESIGN = "interface_design"
    UPGRADABILITY_ANALYSIS = "upgradability_analysis"
    TOKENOMICS_ANALYSIS = "tokenomics_analysis"
    CROSS_CHAIN_SUPPORT = "cross_chain_support"

class ExecutionMode(Enum):
    """How agents can be executed"""
    SYNCHRONOUS = "sync"
    ASYNCHRONOUS = "async"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"

@dataclass
class ResourceRequirements:
    """Resource requirements for agent execution"""
    api_calls_per_execution: int = 0
    memory_usage_mb: int = 50
    execution_time_seconds: int = 10
    requires_internet: bool = True
    requires_database: bool = False
    rate_limit_per_minute: int = 60
    cost_estimate_usd: float = 0.0

@dataclass
class AgentMetadata:
    """Comprehensive metadata about a blockchain agent"""
    name: str
    description: str
    version: str
    author: str
    created_date: str
    last_updated: str
    
    # Capabilities
    task_types: List[TaskType]
    capabilities: List[AgentCapability]
    supported_networks: List[str]
    
    # Execution
    execution_modes: List[ExecutionMode]
    resource_requirements: ResourceRequirements
    
    # Dependencies
    required_config_keys: List[str]
    optional_config_keys: List[str]
    python_dependencies: List[str]
    
    # Performance
    average_execution_time: float = 0.0
    success_rate: float = 1.0
    error_rate: float = 0.0
    
    # Quality metrics
    accuracy_score: float = 0.0
    reliability_score: float = 1.0
    user_rating: float = 5.0

@dataclass 
class AgentInstance:
    """Runtime instance of a blockchain agent"""
    metadata: AgentMetadata
    agent_class: type
    instance: Any = None
    is_initialized: bool = False
    last_used: Optional[datetime] = None
    usage_count: int = 0
    current_load: int = 0
    max_concurrent_tasks: int = 3

class BlockchainAgentRegistry:
    """
    Central registry for managing all available blockchain development agents
    Provides discovery, metadata management, and instance tracking
    """
    
    def __init__(self):
        self._agents: Dict[str, AgentInstance] = {}
        self._task_type_index: Dict[TaskType, List[str]] = {}
        self._capability_index: Dict[AgentCapability, List[str]] = {}
        self._network_index: Dict[str, List[str]] = {}
        self._performance_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize built-in blockchain agents
        self._register_builtin_agents()
    
    def _register_builtin_agents(self):
        """Register all built-in specialized blockchain agents"""
        
        # Smart Contract Security Agent
        self.register_agent(
            agent_name="smart_contract_security_agent",
            metadata=AgentMetadata(
                name="Smart Contract Security Agent",
                description="Comprehensive security auditing for Solidity smart contracts",
                version="1.0.0",
                author="RiST System",
                created_date="2025-08-08",
                last_updated="2025-08-08",
                task_types=[TaskType.SECURITY_AUDIT, TaskType.SMART_CONTRACT_DEVELOPMENT],
                capabilities=[
                    AgentCapability.SECURITY_SCANNING,
                    AgentCapability.CONTRACT_VERIFICATION,
                    AgentCapability.CODE_OPTIMIZATION,
                    AgentCapability.UPGRADABILITY_ANALYSIS
                ],
                supported_networks=["ethereum", "polygon", "base", "arbitrum", "optimism"],
                execution_modes=[ExecutionMode.ASYNCHRONOUS, ExecutionMode.PARALLEL],
                resource_requirements=ResourceRequirements(
                    api_calls_per_execution=8,
                    memory_usage_mb=150,
                    execution_time_seconds=30,
                    requires_internet=True,
                    cost_estimate_usd=0.05
                ),
                required_config_keys=["rpc_urls", "etherscan_api_keys"],
                optional_config_keys=["security_thresholds", "audit_depth"],
                python_dependencies=["web3", "slither-analyzer", "mythril", "requests"]
            ),
            agent_class_path="blockchain_agents.smart_contract_security_agent.SmartContractSecurityAgent"
        )
        
        # Gas Optimization Agent
        self.register_agent(
            agent_name="gas_optimization_agent", 
            metadata=AgentMetadata(
                name="Gas Optimization Agent",
                description="Analyzes and optimizes smart contract gas usage",
                version="1.0.0",
                author="RiST System",
                created_date="2025-08-08",
                last_updated="2025-08-08",
                task_types=[TaskType.GAS_OPTIMIZATION, TaskType.SMART_CONTRACT_DEVELOPMENT],
                capabilities=[
                    AgentCapability.GAS_ANALYSIS,
                    AgentCapability.CODE_OPTIMIZATION,
                    AgentCapability.SOLIDITY_DEVELOPMENT
                ],
                supported_networks=["ethereum", "polygon", "base", "arbitrum"],
                execution_modes=[ExecutionMode.ASYNCHRONOUS, ExecutionMode.SEQUENTIAL],
                resource_requirements=ResourceRequirements(
                    api_calls_per_execution=3,
                    memory_usage_mb=80,
                    execution_time_seconds=20,
                    requires_internet=False,
                    requires_database=True
                ),
                required_config_keys=["hardhat_config", "contract_paths"],
                optional_config_keys=["optimization_level", "gas_price_targets"],
                python_dependencies=["subprocess", "json", "pathlib"]
            ),
            agent_class_path="blockchain_agents.gas_optimization_agent.GasOptimizationAgent"
        )
        
        # Test Generation Agent
        self.register_agent(
            agent_name="test_generation_agent",
            metadata=AgentMetadata(
                name="Smart Contract Test Generation Agent", 
                description="Automatically generates comprehensive test suites for smart contracts",
                version="1.0.0",
                author="RiST System",
                created_date="2025-08-08",
                last_updated="2025-08-08",
                task_types=[TaskType.TESTING_AUTOMATION, TaskType.SMART_CONTRACT_DEVELOPMENT],
                capabilities=[
                    AgentCapability.TEST_GENERATION,
                    AgentCapability.SOLIDITY_DEVELOPMENT,
                    AgentCapability.SECURITY_SCANNING
                ],
                supported_networks=["ethereum", "polygon", "base", "arbitrum", "hardhat"],
                execution_modes=[ExecutionMode.ASYNCHRONOUS, ExecutionMode.PARALLEL],
                resource_requirements=ResourceRequirements(
                    api_calls_per_execution=5,
                    memory_usage_mb=120,
                    execution_time_seconds=45,
                    requires_internet=True,
                    cost_estimate_usd=0.03
                ),
                required_config_keys=["contract_paths", "test_framework"],
                optional_config_keys=["test_coverage_targets", "test_types"],
                python_dependencies=["anthropic", "pathlib", "json"]
            ),
            agent_class_path="blockchain_agents.test_generation_agent.TestGenerationAgent"
        )
        
        # Deployment Management Agent
        self.register_agent(
            agent_name="deployment_management_agent",
            metadata=AgentMetadata(
                name="Deployment Management Agent",
                description="Manages smart contract deployments across multiple networks",
                version="1.0.0",
                author="RiST System", 
                created_date="2025-08-08",
                last_updated="2025-08-08",
                task_types=[TaskType.DEPLOYMENT_MANAGEMENT, TaskType.INTEGRATION_TESTING],
                capabilities=[
                    AgentCapability.DEPLOYMENT_SCRIPTING,
                    AgentCapability.CONTRACT_VERIFICATION,
                    AgentCapability.CROSS_CHAIN_SUPPORT
                ],
                supported_networks=["ethereum", "polygon", "base", "arbitrum", "optimism"],
                execution_modes=[ExecutionMode.ASYNCHRONOUS, ExecutionMode.SEQUENTIAL],
                resource_requirements=ResourceRequirements(
                    api_calls_per_execution=10,
                    memory_usage_mb=100,
                    execution_time_seconds=60,
                    requires_internet=True,
                    cost_estimate_usd=0.08
                ),
                required_config_keys=["private_keys", "rpc_urls", "etherscan_api_keys"],
                optional_config_keys=["deployment_order", "verification_delay"],
                python_dependencies=["web3", "requests", "subprocess"]
            ),
            agent_class_path="blockchain_agents.deployment_management_agent.DeploymentManagementAgent"
        )
        
        # Documentation Generation Agent
        self.register_agent(
            agent_name="documentation_generation_agent",
            metadata=AgentMetadata(
                name="Documentation Generation Agent",
                description="Generates comprehensive documentation for smart contracts and protocols",
                version="1.0.0",
                author="RiST System",
                created_date="2025-08-08",
                last_updated="2025-08-08",
                task_types=[TaskType.DOCUMENTATION_GENERATION, TaskType.PROTOCOL_ANALYSIS],
                capabilities=[
                    AgentCapability.DOCUMENTATION_WRITING,
                    AgentCapability.INTERFACE_DESIGN,
                    AgentCapability.TOKENOMICS_ANALYSIS
                ],
                supported_networks=["all"],
                execution_modes=[ExecutionMode.ASYNCHRONOUS],
                resource_requirements=ResourceRequirements(
                    api_calls_per_execution=12,
                    memory_usage_mb=90,
                    execution_time_seconds=40,
                    requires_internet=True,
                    cost_estimate_usd=0.06
                ),
                required_config_keys=["anthropic_api_key", "contract_paths"],
                optional_config_keys=["documentation_style", "output_formats"],
                python_dependencies=["anthropic", "markdown", "pathlib"]
            ),
            agent_class_path="blockchain_agents.documentation_generation_agent.DocumentationGenerationAgent"
        )
        
        logger.info("Registered 5 built-in specialized blockchain agents")
    
    def register_agent(self, agent_name: str, metadata: AgentMetadata, agent_class_path: str):
        """Register a new blockchain agent in the registry"""
        
        # Import agent class dynamically
        module_name, class_name = agent_class_path.split('.')[-2:]
        try:
            module = __import__(agent_class_path.rsplit('.', 1)[0], fromlist=[class_name])
            agent_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not import {agent_class_path}: {e}")
            agent_class = None
        
        # Create agent instance record
        agent_instance = AgentInstance(
            metadata=metadata,
            agent_class=agent_class
        )
        
        # Store in main registry
        self._agents[agent_name] = agent_instance
        
        # Update indices for fast lookup
        self._update_indices(agent_name, metadata)
        
        logger.info(f"Registered blockchain agent: {agent_name}")
    
    def _update_indices(self, agent_name: str, metadata: AgentMetadata):
        """Update lookup indices for fast agent discovery"""
        
        # Task type index
        for task_type in metadata.task_types:
            if task_type not in self._task_type_index:
                self._task_type_index[task_type] = []
            self._task_type_index[task_type].append(agent_name)
        
        # Capability index
        for capability in metadata.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            self._capability_index[capability].append(agent_name)
        
        # Network index
        for network in metadata.supported_networks:
            if network not in self._network_index:
                self._network_index[network] = []
            self._network_index[network].append(agent_name)
    
    def get_agents_by_task_type(self, task_type: TaskType) -> List[str]:
        """Get all agents that can handle a specific task type"""
        return self._task_type_index.get(task_type, [])
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[str]:
        """Get all agents that have a specific capability"""
        return self._capability_index.get(capability, [])
    
    def get_agents_by_network(self, network: str) -> List[str]:
        """Get all agents that support a specific blockchain network"""
        return self._network_index.get(network, [])
    
    def find_agents(self, 
                   task_types: Optional[List[TaskType]] = None,
                   capabilities: Optional[List[AgentCapability]] = None,
                   networks: Optional[List[str]] = None,
                   execution_mode: Optional[ExecutionMode] = None,
                   max_execution_time: Optional[int] = None,
                   max_cost: Optional[float] = None) -> List[str]:
        """
        Find blockchain agents matching multiple criteria
        Returns intersection of all criteria
        """
        candidate_sets = []
        
        # Filter by task types
        if task_types:
            task_candidates = set()
            for task_type in task_types:
                task_candidates.update(self.get_agents_by_task_type(task_type))
            candidate_sets.append(task_candidates)
        
        # Filter by capabilities
        if capabilities:
            capability_candidates = set()
            for capability in capabilities:
                capability_candidates.update(self.get_agents_by_capability(capability))
            candidate_sets.append(capability_candidates)
        
        # Filter by networks
        if networks:
            network_candidates = set()
            for network in networks:
                network_candidates.update(self.get_agents_by_network(network))
            candidate_sets.append(network_candidates)
        
        # If no criteria specified, return all agents
        if not candidate_sets:
            candidates = set(self._agents.keys())
        else:
            # Get intersection of all criteria
            candidates = candidate_sets[0]
            for candidate_set in candidate_sets[1:]:
                candidates = candidates.intersection(candidate_set)
        
        # Apply additional filters
        filtered_agents = []
        for agent_name in candidates:
            agent = self._agents[agent_name]
            metadata = agent.metadata
            
            # Check execution mode
            if execution_mode and execution_mode not in metadata.execution_modes:
                continue
            
            # Check execution time
            if max_execution_time and metadata.resource_requirements.execution_time_seconds > max_execution_time:
                continue
            
            # Check cost
            if max_cost and metadata.resource_requirements.cost_estimate_usd > max_cost:
                continue
            
            filtered_agents.append(agent_name)
        
        return filtered_agents
    
    def get_agent_metadata(self, agent_name: str) -> Optional[AgentMetadata]:
        """Get metadata for a specific agent"""
        agent = self._agents.get(agent_name)
        return agent.metadata if agent else None
    
    def get_agent_instance(self, agent_name: str) -> Optional[AgentInstance]:
        """Get full agent instance"""
        return self._agents.get(agent_name)
    
    def is_agent_available(self, agent_name: str) -> bool:
        """Check if agent is available for execution"""
        agent = self._agents.get(agent_name)
        if not agent:
            return False
        
        # Check if agent can handle more concurrent tasks
        return agent.current_load < agent.max_concurrent_tasks
    
    def update_agent_performance(self, agent_name: str, execution_time: float, success: bool):
        """Update agent performance metrics"""
        agent = self._agents.get(agent_name)
        if not agent:
            return
        
        # Update usage statistics
        agent.usage_count += 1
        agent.last_used = datetime.now()
        
        # Update performance metrics
        metadata = agent.metadata
        
        # Running average for execution time
        if metadata.average_execution_time == 0:
            metadata.average_execution_time = execution_time
        else:
            metadata.average_execution_time = (
                (metadata.average_execution_time * (agent.usage_count - 1) + execution_time) 
                / agent.usage_count
            )
        
        # Update success/error rates
        if success:
            metadata.success_rate = (
                (metadata.success_rate * (agent.usage_count - 1) + 1.0) 
                / agent.usage_count
            )
        else:
            metadata.error_rate = (
                (metadata.error_rate * (agent.usage_count - 1) + 1.0) 
                / agent.usage_count
            )
        
        # Update reliability score based on success rate
        metadata.reliability_score = metadata.success_rate
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        total_agents = len(self._agents)
        
        # Count by task type
        task_type_counts = {}
        for task_type, agents in self._task_type_index.items():
            task_type_counts[task_type.value] = len(agents)
        
        # Count by capability
        capability_counts = {}
        for capability, agents in self._capability_index.items():
            capability_counts[capability.value] = len(agents)
        
        # Agent usage stats
        total_usage = sum(agent.usage_count for agent in self._agents.values())
        avg_performance = sum(agent.metadata.reliability_score for agent in self._agents.values()) / total_agents if total_agents > 0 else 0
        
        return {
            "total_agents": total_agents,
            "task_type_distribution": task_type_counts,
            "capability_distribution": capability_counts,
            "total_executions": total_usage,
            "average_reliability": avg_performance,
            "available_agents": sum(1 for agent in self._agents.values() if self.is_agent_available(agent.metadata.name.replace(" ", "_").lower())),
            "network_support": {network: len(agents) for network, agents in self._network_index.items()}
        }
    
    def list_all_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents with basic info"""
        agents_list = []
        for agent_name, agent_instance in self._agents.items():
            metadata = agent_instance.metadata
            agents_list.append({
                "name": agent_name,
                "display_name": metadata.name,
                "description": metadata.description,
                "version": metadata.version,
                "task_types": [tt.value for tt in metadata.task_types],
                "capabilities": [cap.value for cap in metadata.capabilities],
                "supported_networks": metadata.supported_networks,
                "execution_modes": [mode.value for mode in metadata.execution_modes],
                "average_execution_time": metadata.average_execution_time,
                "reliability_score": metadata.reliability_score,
                "usage_count": agent_instance.usage_count,
                "is_available": self.is_agent_available(agent_name)
            })
        
        return sorted(agents_list, key=lambda x: x["reliability_score"], reverse=True)

# Global registry instance
_blockchain_agent_registry = BlockchainAgentRegistry()

def get_blockchain_agent_registry() -> BlockchainAgentRegistry:
    """Get the global blockchain agent registry instance"""
    return _blockchain_agent_registry

# Convenience functions for common operations
def find_agents_for_task(task_type: TaskType, network: Optional[str] = None) -> List[str]:
    """Find the best agents for a specific blockchain task type"""
    registry = get_blockchain_agent_registry()
    criteria = {"task_types": [task_type]}
    if network:
        criteria["networks"] = [network]
    return registry.find_agents(**criteria)

def get_best_agent_for_capability(capability: AgentCapability) -> Optional[str]:
    """Get the highest-rated agent for a specific blockchain capability"""
    registry = get_blockchain_agent_registry()
    candidates = registry.get_agents_by_capability(capability)
    
    if not candidates:
        return None
    
    # Return agent with highest reliability score
    best_agent = None
    best_score = 0
    
    for agent_name in candidates:
        metadata = registry.get_agent_metadata(agent_name)
        if metadata and metadata.reliability_score > best_score:
            best_score = metadata.reliability_score
            best_agent = agent_name
    
    return best_agent

if __name__ == "__main__":
    # Demo blockchain registry usage
    registry = get_blockchain_agent_registry()
    
    print("=== Blockchain Agent Registry Demo ===")
    print(f"Total registered agents: {len(registry._agents)}")
    
    print("\nAgents by task type:")
    for task_type in TaskType:
        agents = registry.get_agents_by_task_type(task_type)
        print(f"  {task_type.value}: {agents}")
    
    print("\nFind agents for smart contract development:")
    dev_agents = find_agents_for_task(TaskType.SMART_CONTRACT_DEVELOPMENT)
    print(f"  {dev_agents}")
    
    print("\nBest agent for security scanning:")
    security_agent = get_best_agent_for_capability(AgentCapability.SECURITY_SCANNING)
    print(f"  {security_agent}")
    
    print("\nRegistry statistics:")
    stats = registry.get_registry_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")