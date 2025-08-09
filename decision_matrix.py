#!/usr/bin/env python3
"""
Decision Matrix for Blockchain Agent Selection
Intelligent selection and coordination of agents for smart contract development tasks
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from agent_registry import (
    BlockchainAgentRegistry, TaskType, AgentCapability, AgentMetadata,
    ExecutionMode
)

logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """Complexity levels for blockchain tasks"""
    SIMPLE = "simple"        # Single contract, basic functionality
    MODERATE = "moderate"    # Multiple contracts, standard patterns
    COMPLEX = "complex"      # Advanced patterns, cross-contract interactions
    CRITICAL = "critical"    # Protocol-level, high-value, security-critical

class TaskUrgency(Enum):
    """Urgency levels for blockchain development"""
    LOW = "low"              # Quality over speed, thorough analysis
    MEDIUM = "medium"        # Balanced approach
    HIGH = "high"            # Fast delivery, minimum viable security
    EMERGENCY = "emergency"  # Immediate response, critical fixes

@dataclass
class TaskContext:
    """Context information for blockchain development tasks"""
    task_id: str
    task_description: str
    task_type: TaskType
    complexity: TaskComplexity
    urgency: TaskUrgency
    
    # Requirements
    required_capabilities: List[AgentCapability]
    preferred_capabilities: List[AgentCapability]
    target_networks: List[str]
    
    # Constraints
    max_execution_time_seconds: Optional[int] = None
    max_cost_usd: Optional[float] = None
    allow_parallel_execution: bool = True
    
    # Context-specific data
    contract_paths: List[str] = None
    existing_deployments: Dict[str, str] = None
    security_requirements: List[str] = None

@dataclass
class AgentSelectionResult:
    """Result of the agent selection process"""
    selected_agents: List[str]
    execution_groups: List[List[str]]  # Groups for parallel execution
    total_estimated_cost: float
    total_estimated_time: float
    confidence_score: float
    selection_reasoning: str
    
    # Risk assessment
    risk_level: str
    mitigation_strategies: List[str]
    
    # Performance predictions
    expected_success_rate: float
    fallback_agents: List[str]

class BlockchainDecisionMatrix:
    """
    Decision matrix for intelligent blockchain agent selection
    Optimizes for security, efficiency, and reliability in smart contract development
    """
    
    def __init__(self, agent_registry: BlockchainAgentRegistry):
        self.registry = agent_registry
        
        # Scoring weights - optimized for blockchain development priorities
        self.weights = {
            "security_match": 0.35,      # Highest priority for blockchain
            "capability_match": 0.25,
            "reliability": 0.20,
            "performance": 0.10,
            "cost_efficiency": 0.10
        }
        
        # Network priority scores (based on maturity and tooling)
        self.network_priorities = {
            "ethereum": 1.0,
            "base": 0.95,
            "polygon": 0.9,
            "arbitrum": 0.9,
            "optimism": 0.85,
            "hardhat": 0.8,  # Local development
            "sepolia": 0.7,  # Testnet
        }
        
        # Task complexity requirements
        self.complexity_requirements = {
            TaskComplexity.SIMPLE: {
                "min_agents": 1,
                "max_agents": 2,
                "security_weight": 0.7,
                "speed_weight": 0.3
            },
            TaskComplexity.MODERATE: {
                "min_agents": 2,
                "max_agents": 3,
                "security_weight": 0.8,
                "speed_weight": 0.2
            },
            TaskComplexity.COMPLEX: {
                "min_agents": 3,
                "max_agents": 5,
                "security_weight": 0.9,
                "speed_weight": 0.1
            },
            TaskComplexity.CRITICAL: {
                "min_agents": 4,
                "max_agents": 6,
                "security_weight": 1.0,
                "speed_weight": 0.0
            }
        }
        
        # Urgency modifiers
        self.urgency_modifiers = {
            TaskUrgency.LOW: {
                "thoroughness_bonus": 0.2,
                "speed_penalty": 0.0,
                "agent_count_multiplier": 1.2
            },
            TaskUrgency.MEDIUM: {
                "thoroughness_bonus": 0.1,
                "speed_penalty": 0.0,
                "agent_count_multiplier": 1.0
            },
            TaskUrgency.HIGH: {
                "thoroughness_bonus": 0.0,
                "speed_penalty": 0.1,
                "agent_count_multiplier": 0.8
            },
            TaskUrgency.EMERGENCY: {
                "thoroughness_bonus": 0.0,
                "speed_penalty": 0.2,
                "agent_count_multiplier": 0.6
            }
        }
    
    async def select_agents(self, context: TaskContext) -> AgentSelectionResult:
        """
        Select optimal agents for blockchain development task
        """
        logger.info(f"Selecting agents for {context.task_type.value} task: {context.task_description}")
        
        # Step 1: Find candidate agents
        candidates = self._find_candidate_agents(context)
        
        if not candidates:
            raise ValueError(f"No suitable agents found for task {context.task_type}")
        
        # Step 2: Score each candidate agent
        scored_agents = await self._score_agents(candidates, context)
        
        # Step 3: Determine optimal agent count and selection
        selected_agents = self._select_optimal_agents(scored_agents, context)
        
        # Step 4: Create execution plan
        execution_groups = self._create_execution_plan(selected_agents, context)
        
        # Step 5: Calculate estimates and risk assessment
        estimates = self._calculate_estimates(selected_agents, context)
        risk_assessment = self._assess_risks(selected_agents, context)
        
        # Step 6: Generate reasoning
        reasoning = self._generate_selection_reasoning(selected_agents, context, scored_agents)
        
        return AgentSelectionResult(
            selected_agents=selected_agents,
            execution_groups=execution_groups,
            total_estimated_cost=estimates["cost"],
            total_estimated_time=estimates["time"],
            confidence_score=estimates["confidence"],
            selection_reasoning=reasoning,
            risk_level=risk_assessment["level"],
            mitigation_strategies=risk_assessment["mitigations"],
            expected_success_rate=estimates["success_rate"],
            fallback_agents=scored_agents[len(selected_agents):len(selected_agents)+2]
        )
    
    def _find_candidate_agents(self, context: TaskContext) -> List[str]:
        """Find agents that match the basic requirements"""
        candidates = self.registry.find_agents(
            task_types=[context.task_type],
            capabilities=context.required_capabilities,
            networks=context.target_networks,
            max_execution_time=context.max_execution_time_seconds,
            max_cost=context.max_cost_usd
        )
        
        # Include agents with preferred capabilities
        if context.preferred_capabilities:
            preferred_candidates = self.registry.find_agents(
                capabilities=context.preferred_capabilities,
                networks=context.target_networks
            )
            candidates.extend([c for c in preferred_candidates if c not in candidates])
        
        logger.info(f"Found {len(candidates)} candidate agents: {candidates}")
        return candidates
    
    async def _score_agents(self, candidates: List[str], context: TaskContext) -> List[Tuple[str, float]]:
        """Score each candidate agent for the specific task"""
        scored_agents = []
        
        for agent_name in candidates:
            metadata = self.registry.get_agent_metadata(agent_name)
            if not metadata:
                continue
            
            # Calculate component scores
            security_score = self._calculate_security_score(metadata, context)
            capability_score = self._calculate_capability_score(metadata, context)
            reliability_score = metadata.reliability_score
            performance_score = self._calculate_performance_score(metadata, context)
            cost_score = self._calculate_cost_score(metadata, context)
            
            # Apply complexity and urgency modifiers
            complexity_bonus = self._get_complexity_bonus(metadata, context)
            urgency_modifier = self._get_urgency_modifier(metadata, context)
            
            # Calculate weighted total score
            total_score = (
                self.weights["security_match"] * security_score +
                self.weights["capability_match"] * capability_score +
                self.weights["reliability"] * reliability_score +
                self.weights["performance"] * performance_score +
                self.weights["cost_efficiency"] * cost_score +
                complexity_bonus +
                urgency_modifier
            )
            
            scored_agents.append((agent_name, total_score))
            
            logger.debug(f"Agent {agent_name} scored {total_score:.3f} (sec:{security_score:.2f}, cap:{capability_score:.2f}, rel:{reliability_score:.2f})")
        
        # Sort by score (descending)
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return scored_agents
    
    def _calculate_security_score(self, metadata: AgentMetadata, context: TaskContext) -> float:
        """Calculate security-focused score for blockchain tasks"""
        score = 0.0
        
        # Security capability bonus
        security_capabilities = [
            AgentCapability.SECURITY_SCANNING,
            AgentCapability.CONTRACT_VERIFICATION,
            AgentCapability.UPGRADABILITY_ANALYSIS
        ]
        
        for cap in security_capabilities:
            if cap in metadata.capabilities:
                score += 0.3
        
        # Task-specific security scoring
        if context.task_type in [TaskType.SECURITY_AUDIT, TaskType.SMART_CONTRACT_DEVELOPMENT]:
            if AgentCapability.SECURITY_SCANNING in metadata.capabilities:
                score += 0.4
        
        # Network maturity bonus
        for network in context.target_networks:
            if network in metadata.supported_networks:
                network_bonus = self.network_priorities.get(network, 0.5)
                score += network_bonus * 0.1
        
        return min(score, 1.0)
    
    def _calculate_capability_score(self, metadata: AgentMetadata, context: TaskContext) -> float:
        """Calculate capability match score"""
        required_caps = set(context.required_capabilities)
        preferred_caps = set(context.preferred_capabilities or [])
        agent_caps = set(metadata.capabilities)
        
        # Required capabilities (must have all)
        required_match = len(required_caps.intersection(agent_caps)) / len(required_caps) if required_caps else 1.0
        
        # Preferred capabilities (bonus for having them)
        preferred_match = len(preferred_caps.intersection(agent_caps)) / len(preferred_caps) if preferred_caps else 0.0
        
        # Task type match
        task_match = 1.0 if context.task_type in metadata.task_types else 0.5
        
        return (required_match * 0.6 + preferred_match * 0.2 + task_match * 0.2)
    
    def _calculate_performance_score(self, metadata: AgentMetadata, context: TaskContext) -> float:
        """Calculate performance-based score"""
        # Base performance from metadata
        base_score = metadata.success_rate * 0.6 + (1.0 - metadata.error_rate) * 0.4
        
        # Execution time penalty for urgent tasks
        if context.urgency in [TaskUrgency.HIGH, TaskUrgency.EMERGENCY]:
            time_penalty = min(metadata.resource_requirements.execution_time_seconds / 60.0, 0.3)
            base_score -= time_penalty
        
        return max(base_score, 0.0)
    
    def _calculate_cost_score(self, metadata: AgentMetadata, context: TaskContext) -> float:
        """Calculate cost efficiency score"""
        max_budget = context.max_cost_usd or 1.0
        agent_cost = metadata.resource_requirements.cost_estimate_usd
        
        if agent_cost == 0:
            return 1.0
        
        # Normalize cost (lower cost = higher score)
        cost_ratio = agent_cost / max_budget
        return max(1.0 - cost_ratio, 0.0)
    
    def _get_complexity_bonus(self, metadata: AgentMetadata, context: TaskContext) -> float:
        """Get bonus based on complexity requirements"""
        complexity_req = self.complexity_requirements[context.complexity]
        
        # Bonus for security-focused agents in complex tasks
        if context.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
            if AgentCapability.SECURITY_SCANNING in metadata.capabilities:
                return 0.1
        
        return 0.0
    
    def _get_urgency_modifier(self, metadata: AgentMetadata, context: TaskContext) -> float:
        """Get modifier based on urgency requirements"""
        modifier = self.urgency_modifiers[context.urgency]
        
        # Fast agents get bonus for urgent tasks
        if context.urgency in [TaskUrgency.HIGH, TaskUrgency.EMERGENCY]:
            if metadata.resource_requirements.execution_time_seconds < 30:
                return modifier["speed_penalty"]  # Actually a bonus in this context
        
        # Thorough agents get bonus for low urgency
        if context.urgency == TaskUrgency.LOW:
            if AgentCapability.SECURITY_SCANNING in metadata.capabilities:
                return modifier["thoroughness_bonus"]
        
        return 0.0
    
    def _select_optimal_agents(self, scored_agents: List[Tuple[str, float]], context: TaskContext) -> List[str]:
        """Select the optimal number and combination of agents"""
        complexity_req = self.complexity_requirements[context.complexity]
        urgency_modifier = self.urgency_modifiers[context.urgency]
        
        # Calculate optimal agent count
        base_count = complexity_req["min_agents"]
        max_count = complexity_req["max_agents"]
        
        # Apply urgency modifier
        target_count = int(base_count * urgency_modifier["agent_count_multiplier"])
        target_count = max(1, min(target_count, max_count, len(scored_agents)))
        
        # Select top-scored agents
        selected = [agent for agent, score in scored_agents[:target_count]]
        
        # Ensure diversity for complex tasks
        if context.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
            selected = self._ensure_agent_diversity(selected, scored_agents, context)
        
        logger.info(f"Selected {len(selected)} agents: {selected}")
        return selected
    
    def _ensure_agent_diversity(self, selected: List[str], scored_agents: List[Tuple[str, float]], context: TaskContext) -> List[str]:
        """Ensure diversity in agent capabilities for complex tasks"""
        # Get capabilities of selected agents
        selected_caps = set()
        for agent_name in selected:
            metadata = self.registry.get_agent_metadata(agent_name)
            if metadata:
                selected_caps.update(metadata.capabilities)
        
        # Check if we need additional capabilities
        critical_caps = [
            AgentCapability.SECURITY_SCANNING,
            AgentCapability.GAS_ANALYSIS,
            AgentCapability.TEST_GENERATION
        ]
        
        missing_caps = [cap for cap in critical_caps if cap not in selected_caps]
        
        # Add agents to cover missing capabilities
        for agent_name, score in scored_agents[len(selected):]:
            if not missing_caps:
                break
            
            metadata = self.registry.get_agent_metadata(agent_name)
            if metadata:
                agent_caps = set(metadata.capabilities)
                if any(cap in agent_caps for cap in missing_caps):
                    selected.append(agent_name)
                    selected_caps.update(agent_caps)
                    missing_caps = [cap for cap in missing_caps if cap not in selected_caps]
        
        return selected
    
    def _create_execution_plan(self, selected_agents: List[str], context: TaskContext) -> List[List[str]]:
        """Create execution plan with proper sequencing"""
        if not context.allow_parallel_execution:
            return [[agent] for agent in selected_agents]
        
        # Group agents by execution phase
        security_agents = []
        development_agents = []
        testing_agents = []
        deployment_agents = []
        
        for agent_name in selected_agents:
            metadata = self.registry.get_agent_metadata(agent_name)
            if not metadata:
                continue
            
            # Categorize by primary capability
            if AgentCapability.SECURITY_SCANNING in metadata.capabilities:
                security_agents.append(agent_name)
            elif AgentCapability.SOLIDITY_DEVELOPMENT in metadata.capabilities:
                development_agents.append(agent_name)
            elif AgentCapability.TEST_GENERATION in metadata.capabilities:
                testing_agents.append(agent_name)
            elif AgentCapability.DEPLOYMENT_SCRIPTING in metadata.capabilities:
                deployment_agents.append(agent_name)
            else:
                development_agents.append(agent_name)  # Default group
        
        # Create execution phases
        execution_plan = []
        if security_agents:
            execution_plan.append(security_agents)
        if development_agents:
            execution_plan.append(development_agents)
        if testing_agents:
            execution_plan.append(testing_agents)
        if deployment_agents:
            execution_plan.append(deployment_agents)
        
        return execution_plan or [selected_agents]  # Fallback to single group
    
    def _calculate_estimates(self, selected_agents: List[str], context: TaskContext) -> Dict[str, float]:
        """Calculate cost, time, and confidence estimates"""
        total_cost = 0.0
        max_time = 0.0
        success_rates = []
        
        for agent_name in selected_agents:
            metadata = self.registry.get_agent_metadata(agent_name)
            if metadata:
                total_cost += metadata.resource_requirements.cost_estimate_usd
                max_time = max(max_time, metadata.resource_requirements.execution_time_seconds)
                success_rates.append(metadata.success_rate)
        
        # Calculate confidence based on agent reliability
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.5
        
        # Confidence bonus for multiple agents
        multi_agent_bonus = min(len(selected_agents) * 0.1, 0.3)
        confidence = min(avg_success_rate + multi_agent_bonus, 1.0)
        
        return {
            "cost": total_cost,
            "time": max_time,
            "confidence": confidence,
            "success_rate": avg_success_rate
        }
    
    def _assess_risks(self, selected_agents: List[str], context: TaskContext) -> Dict[str, Any]:
        """Assess risks and generate mitigation strategies"""
        risk_factors = []
        mitigations = []
        
        # Check for single points of failure
        if len(selected_agents) == 1:
            risk_factors.append("Single agent dependency")
            mitigations.append("Consider adding backup agents for critical tasks")
        
        # Check security coverage
        security_agents = [
            agent for agent in selected_agents
            if self.registry.get_agent_metadata(agent) and 
            AgentCapability.SECURITY_SCANNING in self.registry.get_agent_metadata(agent).capabilities
        ]
        
        if not security_agents and context.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
            risk_factors.append("No security-focused agents selected")
            mitigations.append("Add security audit agent for comprehensive analysis")
        
        # Determine overall risk level
        if len(risk_factors) == 0:
            risk_level = "LOW"
        elif len(risk_factors) <= 2:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            "level": risk_level,
            "factors": risk_factors,
            "mitigations": mitigations
        }
    
    def _generate_selection_reasoning(self, selected_agents: List[str], context: TaskContext, 
                                    scored_agents: List[Tuple[str, float]]) -> str:
        """Generate human-readable reasoning for agent selection"""
        reasoning_parts = []
        
        # Basic selection info
        reasoning_parts.append(f"Selected {len(selected_agents)} agents for {context.complexity.value} {context.task_type.value} task")
        
        # Top agent info
        if scored_agents:
            top_agent, top_score = scored_agents[0]
            reasoning_parts.append(f"Primary agent: {top_agent} (score: {top_score:.2f})")
        
        # Capability coverage
        all_caps = set()
        for agent_name in selected_agents:
            metadata = self.registry.get_agent_metadata(agent_name)
            if metadata:
                all_caps.update(metadata.capabilities)
        
        key_caps = [cap.value.replace("_", " ") for cap in all_caps if cap in context.required_capabilities]
        if key_caps:
            reasoning_parts.append(f"Covers key capabilities: {', '.join(key_caps)}")
        
        # Urgency consideration
        if context.urgency in [TaskUrgency.HIGH, TaskUrgency.EMERGENCY]:
            reasoning_parts.append("Optimized for speed due to high urgency")
        elif context.urgency == TaskUrgency.LOW:
            reasoning_parts.append("Optimized for thoroughness and quality")
        
        return ". ".join(reasoning_parts)

if __name__ == "__main__":
    # Demo decision matrix
    from agent_registry import get_blockchain_agent_registry
    
    async def demo_decision_matrix():
        registry = get_blockchain_agent_registry()
        decision_matrix = BlockchainDecisionMatrix(registry)
        
        # Create test task context
        context = TaskContext(
            task_id="demo_task_001",
            task_description="Security audit for RiST smart contracts",
            task_type=TaskType.SECURITY_AUDIT,
            complexity=TaskComplexity.COMPLEX,
            urgency=TaskUrgency.MEDIUM,
            required_capabilities=[AgentCapability.SECURITY_SCANNING],
            preferred_capabilities=[AgentCapability.GAS_ANALYSIS],
            target_networks=["ethereum", "base"],
            max_cost_usd=0.20
        )
        
        # Select agents
        result = await decision_matrix.select_agents(context)
        
        print("=== Agent Selection Result ===")
        print(f"Selected agents: {result.selected_agents}")
        print(f"Execution plan: {result.execution_groups}")
        print(f"Estimated cost: ${result.total_estimated_cost:.3f}")
        print(f"Estimated time: {result.total_estimated_time}s")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Risk level: {result.risk_level}")
        print(f"Reasoning: {result.selection_reasoning}")
        
        if result.mitigation_strategies:
            print(f"Mitigations: {', '.join(result.mitigation_strategies)}")
    
    # Run demo
    asyncio.run(demo_decision_matrix())