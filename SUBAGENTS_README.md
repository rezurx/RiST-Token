# 🤖 Blockchain Subagents for ReputationSplittingToken

This project now includes a comprehensive subagent orchestration system specifically designed for blockchain development with Claude Code.

## ✨ What's Included

### 🔍 **Intelligent Project Analysis**
The system automatically detected this as a **Blockchain/Smart Contract** project with:
- **Languages**: Python, JavaScript, Solidity
- **Frameworks**: Hardhat, Ethers.js, OpenZeppelin 
- **Tools**: Hardhat
- **Complexity**: 3/10 (Moderate)

### 🤖 **Specialized Blockchain Subagents**

#### Core Development Agents
- **`solidity-developer`** - Solidity smart contract development and optimization
- **`smart-contract-auditor`** ⚡ *PROACTIVE* - Security vulnerability scanning
- **`gas-optimizer`** - Gas usage analysis and optimization
- **`hardhat-specialist`** - Hardhat environment and testing setup
- **`openzeppelin-specialist`** - OpenZeppelin patterns and upgrade mechanisms

#### Additional Available Agents
- **`deployment-manager`** - Multi-network deployment and verification
- **`protocol-architect`** - Protocol design and tokenomics
- **`web3-frontend-developer`** - Web3 frontend integration
- **`defi-specialist`** - DeFi protocol development
- **`wallet-integration-expert`** - Wallet connection and UX

## 🚀 How to Use

### Quick Start
The following subagents are already configured for this project:
- `solidity-developer`
- `smart-contract-auditor` (proactive)
- `gas-optimizer`
- `hardhat-specialist`
- `openzeppelin-specialist`

### Using Subagents in Claude Code

**Example Usage:**
```
Use the solidity-developer to help me optimize the ReputationSplittingToken contract for gas efficiency.

Use the smart-contract-auditor to review the RSTRegistry contract for security vulnerabilities.

Use the hardhat-specialist to set up comprehensive testing for all contracts.
```

**The `smart-contract-auditor` is proactive** - it will automatically review code changes without being asked.

### Available Commands

```bash
# Analyze project and get recommendations
python3 claude_subagent_manager.py analyze

# List all available subagents
python3 claude_subagent_manager.py list

# Create new subagents from templates
python3 claude_subagent_manager.py create --template <name>

# Interactive management UI
python3 claude_subagent_manager.py ui
```

### Available Templates

**Blockchain-Specific:**
- `solidity-developer`
- `smart-contract-auditor` 
- `gas-optimizer`
- `deployment-manager`
- `protocol-architect`
- `hardhat-specialist`
- `openzeppelin-specialist`
- `web3-frontend-developer`
- `defi-specialist`
- `wallet-integration-expert`

**General Development:**
- `code-reviewer`
- `test-runner`
- `documentation-generator`
- `python-specialist`
- `javascript-specialist`

## 📋 Project-Specific Capabilities

These subagents are specifically configured for:

### 🔐 **Security Focus**
- EIP-5114 soulbound token compliance
- UUPS proxy pattern security
- Access control vulnerabilities
- Upgrade safety analysis
- Signature-based metadata updates

### ⛽ **Gas Optimization**
- Storage layout optimization
- Function selector optimization
- Batch operations for multiple tokens
- Event emission optimization

### 🏗️ **Architecture**
- Multi-contract system coordination
- Registry pattern implementation
- Timelock upgrade mechanisms
- Cross-contract reputation queries

### 🧪 **Testing & Deployment**
- Hardhat test suite optimization
- Multi-network deployment scripts
- Contract verification automation
- Upgrade testing procedures

## 🛠️ Management Tools

### Dependencies
```bash
# Install in virtual environment
python3 -m venv subagent-env
source subagent-env/bin/activate
pip install -r requirements.txt
```

### Project Structure
```
.claude/
└── agents/
    ├── solidity-developer.md
    ├── smart-contract-auditor.md
    ├── gas-optimizer.md
    ├── hardhat-specialist.md
    └── openzeppelin-specialist.md
```

## 💡 Tips for Maximum Effectiveness

1. **Be Specific**: "Use the gas-optimizer to reduce storage costs in the RiST struct"
2. **Combine Agents**: Use multiple agents for comprehensive analysis
3. **Leverage Proactive Agents**: The security auditor will automatically review changes
4. **Ask for Explanations**: Agents can explain blockchain concepts and patterns
5. **Request Comparisons**: Ask agents to compare different implementation approaches

## 🔧 Advanced Configuration

### Custom Subagents
Create project-specific subagents for:
- Custom ERC standards
- Specific integration patterns  
- Protocol-specific security checks
- Domain-specific optimization rules

### Environment Variables
Configure network endpoints, API keys, and tool paths in your environment or `.env` file.

---

**Ready to build secure, efficient smart contracts with AI assistance! 🚀**

*The subagent system adapts to your development workflow and learns from your project patterns.*