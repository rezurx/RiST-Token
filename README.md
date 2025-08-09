# 🏅 Reputation-Splitting Tokens (RiST)

**Modular Credential Infrastructure for Web3 Identity, DAO Access, and Professional Verification**

> ⚠️ **Educational Project Disclaimer**
> This is an experimental project for educational purposes. RiSTs are not promoted for commercial use.
> Deployed on public blockchains but use at your own risk. No roadmap or support provided.

RiSTs are non-transferable, modular, and cryptographically-verifiable credentials designed to record on-chain reputation **by domain** without leaking private data or allowing any single authority to control everyone's score.

## 🏛️ RiST v1: Core Architecture

RiST v1 is designed for security, efficiency, and developer-friendliness by leveraging a streamlined, EVM-native stack. The primary goal is to deliver a robust and auditable system that is ready for real-world adoption.

*   **Blockchain Foundation:** Deployed on a single, cost-effective, and high-throughput EVM-compatible L2 network (e.g., Polygon, Base, Arbitrum) to ensure low transaction fees and fast confirmations.
*   **Smart Contracts:** All core logic, including token issuance, revocation, access control, and governance, is handled by on-chain Solidity smart contracts.
*   **Decentralized Storage:** On-chain contracts store a hash (CID) of the credential metadata. The full metadata JSON object is stored on a decentralized storage network like IPFS/Filecoin. This ensures data integrity and availability while minimizing on-chain data costs. We recommend using a pinning service like `web3.storage` or `nft.storage` for implementation.
*   **Focus on Simplicity:** The v1 architecture intentionally avoids cross-chain complexity to maximize security and minimize long-term maintenance overhead.

For the long-term vision of the project, which explores a more complex, multi-DLT architecture, please see our **[RiST2 Future Vision](RiST2_Future_Vision.md)** document.

## 🎯 Key Features

- **🔒 EIP-5114 Soulbound**: Compliant with soulbound token standard
- **🏷️ Domain-Specific**: Separate reputation contexts (ux_design, solidity_dev, etc.)
- **⚡ UUPS Upgradeable**: Proxy pattern with 7-day timelock for security
- **🔑 Holder-Approved Updates**: Metadata updates require holder signature
- **🎫 Ephemeral Access**: ERC-1155 chips for time-limited résumé access
- **🏛️ Registry System**: Centralized issuer and domain management
- **📊 Multi-Contract Queries**: Aggregate reputation across multiple contracts

## 🏗️ Contract Architecture

### Core Contracts

- **`ReputationSplittingToken.sol`** - Main RiST EIP-5114 implementation with UUPS proxy
- **`RSTRegistry.sol`** - Issuer whitelist and domain management
- **`ResumeAccessChip.sol`** - ERC-1155 ephemeral access tokens
- **`RiSTTimelock.sol`** - 7-day timelock for contract upgrades
- **`interfaces/IERC5114.sol`** - EIP-5114 soulbound token interface

### RiST Data Structure

```solidity
struct RiST {
    string domain;          // e.g. "ux_design", "solidity_dev"
    string issuer;          // org name or DID string
    string level;           // "L3", "Gold", etc.
    uint256 issuedAt;       // block timestamp
    uint256 validUntil;     // 0 = perpetual
    bool revoked;           // hard revocation flag
    string metadataURI;     // IPFS / HTTPS / Arweave pointer
    bytes32 contentHash;    // keccak256 of full off-chain JSON
}
```

## 📋 Quick Start

### Prerequisites

- Node.js 18+ (recommended)
- npm or yarn
- Git
- OpenZeppelin Contracts v5.0.1+

### Installation

```bash
git clone <your-repo-url>
cd ReputationSplittingToken
npm install
```

### Environment Setup

Create `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your actual values
```

Required environment variables:
```bash
PRIVATE_KEY=your_private_key_here
ALCHEMY_API_KEY=your_alchemy_api_key
BASESCAN_API_KEY=your_basescan_api_key
```

### Compile & Test

```bash
# Compile contracts (OpenZeppelin v5 compatible)
npm run compile

# Run test suite (21/23 tests passing)
npm run test

# Generate coverage report
npm run coverage
```

### Deploy to Testnet

```bash
# Deploy to Base Sepolia
npm run deploy:sepolia

# Verify contracts
npm run verify:sepolia
```

## 🚀 Usage Examples

### Basic RiST Minting

```javascript
const ReputationSplittingToken = await ethers.getContractFactory("ReputationSplittingToken");
const rist = await ReputationSplittingToken.attach(proxyAddress);

// Mint UX design credential
const ristData = {
  domain: "ux_design",
  issuer: "GitcoinDAO",
  level: "L3",
  issuedAt: 0, // Set by contract
  validUntil: 0, // Perpetual
  revoked: false,
  metadataURI: "ipfs://QmMetadataHash",
  contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("metadata json"))
};

await rist.mintRiST(holderAddress, ristData);
```

### Metadata Updates with Holder Signature

```javascript
// Holder creates EIP-712 signature for metadata update
const domain = {
  name: "ReputationSplittingToken",
  version: "1",
  chainId: 8453,
  verifyingContract: rist.address
};

const types = {
  MetadataUpdate: [
    { name: "tokenId", type: "uint256" },
    { name: "metadataURI", type: "string" },
    { name: "contentHash", type: "bytes32" },
    { name: "nonce", type: "uint256" }
  ]
};

const value = {
  tokenId: 0,
  metadataURI: "ipfs://QmNewMetadata",
  contentHash: newHash,
  nonce: await rist.nonces(holder.address)
};

const signature = await holder._signTypedData(domain, types, value);

// Issuer updates metadata with holder approval
await rist.updateMetadata(0, "ipfs://QmNewMetadata", newHash, signature);
```

### Ephemeral Access Chips

```javascript
const ResumeAccessChip = await ethers.getContractFactory("ResumeAccessChip");
const accessChip = await ResumeAccessChip.attach(chipAddress);

// Mint access chip for résumé viewing
const expiry = Math.floor(Date.now() / 1000) + 86400; // 24 hours
await accessChip.mintChip(
  holderAddress,
  expiry,          // expiration timestamp
  5,               // max views
  0,               // scope (0 = all RiSTs)
  "https://resume.example.com/holder123",
  1                // amount
);

// Burn chip to access résumé
await accessChip.burnAndVerifyAccess(chipId, viewerAddress);
```

### Registry Operations

```javascript
const RSTRegistry = await ethers.getContractFactory("RSTRegistry");
const registry = await RSTRegistry.attach(registryAddress);

// Register issuer
await registry.registerIssuer(
  issuerAddress,
  "Gitcoin DAO",
  "did:ethr:0x123...",
  "ipfs://QmIssuerMetadata"
);

// Approve domain
await registry.approveDomain("ux_design");

// Get total reputation across all contracts
const totalScore = await registry.getTotalReputationScore(holderAddress, "ux_design");
```

## ⚡ OpenZeppelin v5 Compatibility

This project has been fully updated for OpenZeppelin Contracts v5.0.1 compatibility:

- **Modern Hook Patterns**: Uses `_update` instead of deprecated `_beforeTokenTransfer`
- **Improved Gas Efficiency**: Manual counters instead of Counters utility
- **Enhanced Type Safety**: Proper interface overrides and ECDSA imports
- **Ethers v6 Compatible**: Updated test suite for latest ethers.js

## 🔐 Security Features

### EIP-5114 Soulbound Implementation

- All transfer functions revert with custom errors
- Implements `isSoulbound()` interface
- Emits `Issued` events as per specification

### UUPS Proxy with Timelock

- 7-day timelock for all upgrades
- Only timelock contract can authorize upgrades
- Prevents immediate malicious upgrades

### Signature-Based Metadata Updates

- Holder must sign EIP-712 message to approve updates
- Nonce-based replay protection
- Only whitelisted issuers can execute updates

### Comprehensive Access Control

- Role-based permissions (ADMIN, ISSUER, UPGRADER)
- Issuer whitelist system
- Domain approval system
- Emergency pause functionality

## 📊 Metadata Standard

Off-chain JSON metadata stored on IPFS:

```json
{
  "name": "UX Design Contributor – Gitcoin Q3 2024",
  "description": "Issued to a verified contributor in Gitcoin's UX audit round (Q3 2024).",
  "image": "ipfs://QmImageHash",
  "vc_jwt": "eyJ...",
  "attributes": [
    { "trait_type": "Domain", "value": "ux_design" },
    { "trait_type": "Level", "value": "L3" },
    { "trait_type": "Issuer", "value": "GitcoinDAO" },
    { "trait_type": "Issued At", "value": "2024-09-15" },
    { "trait_type": "Expiration", "value": "2025-09-15" }
  ]
}
```

## 🧪 Testing

Comprehensive test suite covering:

- EIP-5114 compliance
- Soulbound behavior
- UUPS upgradability
- Metadata updates with signatures
- Access chip functionality
- Registry operations
- Error conditions

```bash
npm run test                    # Run all tests
npm run test:coverage          # Generate coverage report
npm run test:gas              # Gas usage analysis
```

## 🚀 Deployment Architecture

1. **RiSTTimelock** - 7-day timelock for upgrades
2. **RSTRegistry** - Issuer and domain management
3. **ReputationSplittingToken** - UUPS proxy with implementation
4. **ResumeAccessChip** - ERC-1155 ephemeral access tokens

All contracts deployed with proper role assignments and initial configuration.

## 🎯 Integration Examples

### DAO Governance

```solidity
contract MyDAO {
    IReputationSplittingToken public rist;
    
    modifier requireGovernanceRep(uint256 minTokens) {
        uint256[] memory tokens = rist.getValidRiSTsByDomain(msg.sender, "governance");
        require(tokens.length >= minTokens, "Insufficient reputation");
        _;
    }
    
    function vote(uint256 proposalId) external requireGovernanceRep(1) {
        // Only governance RiST holders can vote
    }
}
```

### QR Résumé System

```javascript
// Generate QR code for résumé access
const qrData = {
  holderAddress: "0x123...",
  accessChipId: 42,
  resumeURL: "https://qr.reputation.xyz/@holder123"
};

const qr = QRCode.create(JSON.stringify(qrData));
```

## 📖 Technical Specification

This implementation follows the complete technical specification document, including:

- EIP-5114 soulbound token standard
- UUPS proxy pattern with timelock
- Domain-scoped reputation system
- Ephemeral access tokens (ERTs)
- Holder-approved metadata updates
- Comprehensive registry system

## 🤖 AI Development Assistant

This project includes a comprehensive **blockchain-specific subagent system** for Claude Code that provides specialized AI assistance for:

- **Solidity Development** - Smart contract optimization and best practices
- **Security Auditing** - Automated vulnerability detection and analysis  
- **Gas Optimization** - Cost reduction and efficiency improvements
- **Testing & Deployment** - Hardhat workflow optimization
- **OpenZeppelin Integration** - Secure pattern implementation

**Quick Start:**
```bash
# Analyze project and see available AI agents
python3 claude_subagent_manager.py analyze

# Use specialized agents in Claude Code
"Use the solidity-developer to optimize this contract"
"Use the smart-contract-auditor to review for vulnerabilities"
```

📖 **[Full Subagents Documentation](SUBAGENTS_README.md)**

## 🛠️ Development

### Project Structure

```
contracts/
├── ReputationSplittingToken.sol    # Main RiST contract
├── RSTRegistry.sol                 # Registry system
├── ResumeAccessChip.sol           # ERC-1155 access chips
├── RiSTTimelock.sol               # 7-day timelock
└── interfaces/
    └── IERC5114.sol               # EIP-5114 interface

scripts/
├── deploy.js                      # Deployment script
└── mint-example-rst.js           # Example minting

test/
└── ReputationSplittingToken.test.js  # Comprehensive tests
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenZeppelin for secure contract foundations
- EIP-5114 for soulbound token standards
- Base ecosystem for L2 infrastructure
- Community feedback and testing

---

**Built for the decentralized future 🌐**