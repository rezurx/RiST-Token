# 🏅 Reputation-Splitting Tokens (RiST) v2.0

**Modular Credential Infrastructure for Web3 Identity, DAO Access, and Professional Verification**

> ⚠️ **Educational Project Disclaimer**
> RiSTs are experimental tokens for educational purposes. Not promoted for commercial use.
> Use at your own risk. See [DISCLAIMER.md](DISCLAIMER.md) for details.

RiSTs are non-transferable, modular, and cryptographically-verifiable credentials designed to record on-chain reputation **by domain** without leaking private data or allowing any single authority to control reputation scores.

## 🎯 Key Features v2.0

- **🔒 EIP-5114 Soulbound**: Standards-compliant soulbound token implementation
- **🏷️ Domain-Specific**: Separate reputation contexts (ux_design, solidity_dev, etc.)
- **⚡ UUPS Upgradeable**: Proxy pattern with 7-day timelock for security
- **🔑 Holder-Approved Updates**: Metadata updates require holder EIP-712 signatures
- **🎫 Ephemeral Access**: ERC-1155 chips for time-limited résumé access
- **🏛️ Registry System**: Centralized issuer and domain management
- **📊 Multi-Contract Queries**: Aggregate reputation across multiple contracts
- **🔐 Enhanced Security**: Comprehensive access control and emergency mechanisms

## 🏗️ Architecture v2.0

### Core Contracts

- **`ReputationSplittingToken.sol`** - Main RiST EIP-5114 implementation with UUPS proxy
- **`RSTRegistry.sol`** - Enhanced issuer whitelist and domain management
- **`ResumeAccessChip.sol`** - ERC-1155 ephemeral access tokens for résumé viewing
- **`RiSTTimelock.sol`** - 7-day timelock for secure contract upgrades
- **`interfaces/IERC5114.sol`** - EIP-5114 soulbound token interface

### Enhanced RiST Structure

```solidity
struct RiST {
    string domain;          // e.g. "ux_design", "solidity_dev"
    string issuer;          // org name or DID string (supports decentralized identity)
    string level;           // "L3", "Gold", etc.
    uint256 issuedAt;       // block timestamp (auto-set)
    uint256 validUntil;     // 0 = perpetual
    bool revoked;           // hard revocation flag
    string metadataURI;     // IPFS / HTTPS / Arweave pointer
    bytes32 contentHash;    // keccak256 of full off-chain JSON
}
```

## 📋 Quick Start

### Prerequisites

- Node.js 16+
- npm or yarn
- Git

### Installation

```bash
git clone <your-repo-url>
cd ReputationSplittingToken
npm install
```

### Environment Setup

Create `.env` file:

```bash
PRIVATE_KEY=your_private_key_here
ALCHEMY_API_KEY=your_alchemy_api_key
BASESCAN_API_KEY=your_basescan_api_key
```

### Compile & Test

```bash
npm run compile
npm run test
npm run coverage
```

### Deploy to Testnet

```bash
# Deploy to Base Sepolia
npm run deploy:sepolia

# Verify contracts
npm run verify:sepolia

# Mint example RiSTs
npm run mint:example
```

## 🚀 Usage Examples v2.0

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

### Holder-Approved Metadata Updates

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

// Create time-limited access chip
const expiry = Math.floor(Date.now() / 1000) + 86400; // 24 hours
await accessChip.mintChip(
  holderAddress,
  expiry,          // expiration timestamp
  5,               // max views
  0,               // scope (0 = all RiSTs)
  "https://resume.example.com/holder123",
  3                // amount of chips
);

// Burn chip to access résumé
await accessChip.burnAndVerifyAccess(chipId, viewerAddress);
```

### Registry Operations

```javascript
const RSTRegistry = await ethers.getContractFactory("RSTRegistry");
const registry = await RSTRegistry.attach(registryAddress);

// Register issuer with DID support
await registry.registerIssuer(
  issuerAddress,
  "Gitcoin DAO",
  "did:ethr:0x123...",
  "ipfs://QmIssuerMetadata"
);

// Approve domain for RiST issuance
await registry.approveDomain("ux_design");

// Get total reputation across all contracts
const totalScore = await registry.getTotalReputationScore(holderAddress, "ux_design");
```

## 🔐 Security Features v2.0

### EIP-5114 Soulbound Implementation

- All transfer functions revert with custom errors
- Implements `isSoulbound()` interface function
- Emits `Issued` events as per EIP-5114 specification
- Proper interface detection via `supportsInterface()`

### UUPS Proxy with 7-Day Timelock

- Upgrades require 7-day community review period
- Only timelock contract can authorize upgrades
- Prevents immediate malicious contract changes
- Transparent upgrade process with public proposals

### Signature-Based Metadata Updates

- Holder must sign EIP-712 message to approve metadata changes
- Nonce-based replay protection prevents signature reuse
- Only whitelisted issuers can execute updates
- Maintains holder sovereignty over their credentials

### Comprehensive Access Control

- Role-based permissions (ADMIN, ISSUER, UPGRADER)
- Issuer whitelist system prevents unauthorized minting
- Domain approval system for reputation categories
- Emergency pause functionality for critical issues

## 🎫 Ephemeral Access Tokens (ERTs)

### QR Résumé System

Generate time-limited or view-limited access to RiST-based résumés:

```javascript
// Create access chip for job interviews
const accessChip = await ResumeAccessChip.deploy("https://api.reputation.xyz/chips/{id}");

// Mint chip with specific constraints
await accessChip.mintChip(
  candidate.address,
  expiry,      // 24-hour expiry
  1,           // Single use
  0,           // All RiSTs
  "https://resume.reputation.xyz/candidate123",
  1            // One chip
);

// Recruiter burns chip to access résumé
await accessChip.burnAndVerifyAccess(chipId, recruiter.address);
```

### Access Chip Features

- **Time-limited**: Automatic expiration
- **View-limited**: Maximum view count
- **Scope-limited**: Specific RiST tokens only
- **Transferable**: Can be shared or gifted
- **Auditable**: On-chain access trail

## 📊 Metadata Standard v2.0

Enhanced JSON metadata with W3C VC support:

```json
{
  "name": "UX Design Contributor – Gitcoin Q3 2024",
  "description": "Verified contributor in Gitcoin's UX audit round (Q3 2024).",
  "image": "ipfs://QmImageHash",
  "vc_jwt": "eyJ...",
  "attributes": [
    { "trait_type": "Domain", "value": "ux_design" },
    { "trait_type": "Level", "value": "L3" },
    { "trait_type": "Issuer", "value": "GitcoinDAO" },
    { "trait_type": "Issued At", "value": "2024-09-15" },
    { "trait_type": "Expiration", "value": "2025-09-15" }
  ],
  "properties": {
    "domain": "ux_design",
    "level": "L3",
    "contentHash": "0x...",
    "evidence_uri": "ipfs://QmEvidenceHash"
  }
}
```

## 🧪 Testing v2.0

Comprehensive test suite covering:

- EIP-5114 compliance verification
- Soulbound behavior enforcement
- UUPS proxy upgradability
- Metadata updates with EIP-712 signatures
- Access chip functionality
- Registry operations and governance
- Error conditions and edge cases

```bash
npm run test                    # Run all tests
npm run test:coverage          # Generate coverage report
npm run test:gas              # Gas usage analysis
```

## 🎯 Integration Examples v2.0

### DAO Governance with RiSTs

```solidity
contract EnhancedDAO {
    IReputationSplittingToken public rist;
    
    modifier requireGovernanceRep(uint256 minTokens) {
        uint256[] memory tokens = rist.getValidRiSTsByDomain(msg.sender, "governance");
        require(tokens.length >= minTokens, "Insufficient reputation");
        _;
    }
    
    function vote(uint256 proposalId) external requireGovernanceRep(1) {
        // Only governance RiST holders can vote
        _castVote(proposalId, msg.sender);
    }
    
    function createProposal(string memory description) external requireGovernanceRep(2) {
        // L2+ governance contributors can create proposals
        _createProposal(description, msg.sender);
    }
}
```

### Professional Verification Platform

```javascript
class ProfessionalVerifier {
  constructor(ristAddress, registryAddress) {
    this.rist = new ethers.Contract(ristAddress, RiSTABI, provider);
    this.registry = new ethers.Contract(registryAddress, RegistryABI, provider);
  }
  
  async verifySkills(candidateAddress, requiredSkills) {
    const verifiedSkills = {};
    
    for (const skill of requiredSkills) {
      const tokens = await this.rist.getValidRiSTsByDomain(candidateAddress, skill);
      verifiedSkills[skill] = {
        count: tokens.length,
        levels: await this.getSkillLevels(tokens)
      };
    }
    
    return verifiedSkills;
  }
  
  async generateQRResume(candidateAddress, viewerAddress) {
    // Create ephemeral access chip
    const accessChip = await this.getAccessChip();
    const chipId = await accessChip.mintChip(
      candidateAddress,
      Math.floor(Date.now() / 1000) + 3600, // 1 hour
      1, // Single use
      0, // All RiSTs
      `https://resume.platform.com/${candidateAddress}`,
      1
    );
    
    return {
      qrCode: await QRCode.toDataURL(JSON.stringify({ chipId, viewer: viewerAddress })),
      expiry: Math.floor(Date.now() / 1000) + 3600
    };
  }
}
```

## 🔗 Advanced Features

### Zero-Knowledge Proofs (Planned)

```solidity
interface IZKRiSTVerifier {
    function verifyReputation(
        bytes32 proof,
        string memory domain,
        uint256 minLevel
    ) external view returns (bool);
}
```

### Cross-Chain Attestation (Planned)

```solidity
interface ILayerZeroRiST {
    function attestRiST(
        uint16 dstChainId,
        address holder,
        uint256 tokenId
    ) external payable;
}
```

## 🛠️ Development

### Project Structure

```
contracts/
├── ReputationSplittingToken.sol    # Main RiST contract (UUPS proxy)
├── RSTRegistry.sol                 # Enhanced registry system
├── ResumeAccessChip.sol           # ERC-1155 ephemeral access tokens
├── RiSTTimelock.sol               # 7-day upgrade timelock
└── interfaces/
    └── IERC5114.sol               # EIP-5114 soulbound interface

scripts/
├── deploy.js                      # UUPS proxy deployment
└── mint-example-rst.js           # Comprehensive example operations

test/
└── ReputationSplittingToken.test.js  # Full test suite
```

### Gas Optimization

| Operation | Gas Cost | Notes |
|-----------|----------|-------|
| Mint RiST | ~150,000 | Includes storage and events |
| Update Metadata | ~80,000 | With signature verification |
| Revoke RiST | ~45,000 | Storage update only |
| Mint Access Chip | ~120,000 | ERC-1155 batch mint |
| Burn Access Chip | ~65,000 | With verification logic |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenZeppelin for secure contract foundations and upgrade patterns
- EIP-5114 for soulbound token standards
- Base ecosystem for L2 infrastructure
- Ethereum community for identity and reputation research

---

**Built for the decentralized future 🌐**

*Version 2.0 - Technical Specification Implementation Complete*