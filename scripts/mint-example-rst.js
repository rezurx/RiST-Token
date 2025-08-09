// scripts/mint-example-rst.js
const hre = require("hardhat");
const fs = require('fs');
const path = require('path');

async function main() {
  console.log("🏅 Minting Example RiSTs...");

  // Load deployment info
  const deploymentFile = path.join(__dirname, '..', 'deployments', `${hre.network.name}-deployment.json`);
  if (!fs.existsSync(deploymentFile)) {
    console.error("❌ Deployment file not found. Please deploy contracts first.");
    console.log("Run: npm run deploy:sepolia");
    process.exit(1);
  }

  const deployment = JSON.parse(fs.readFileSync(deploymentFile, 'utf8'));
  const ristAddress = deployment.contracts.ReputationSplittingToken;
  const registryAddress = deployment.contracts.RSTRegistry;
  const accessChipAddress = deployment.contracts.ResumeAccessChip;

  const [deployer, holder1, holder2] = await hre.ethers.getSigners();
  console.log("Minting with account:", deployer.address);
  console.log("RiST Contract:", ristAddress);
  console.log("Registry Contract:", registryAddress);
  console.log("Access Chip Contract:", accessChipAddress);

  // Get contract instances
  const rist = await hre.ethers.getContractAt("ReputationSplittingToken", ristAddress);
  const registry = await hre.ethers.getContractAt("RSTRegistry", registryAddress);
  const accessChip = await hre.ethers.getContractAt("ResumeAccessChip", accessChipAddress);

  // Example RiST data for different domains
  const exampleRiSTs = [
    {
      holder: holder1.address,
      domain: "ux_design",
      issuer: "GitcoinDAO",
      level: "L3",
      validUntil: 0, // Never expires
      metadataURI: "ipfs://QmUXDesignL3MetadataHash",
      contentHash: hre.ethers.utils.keccak256(hre.ethers.utils.toUtf8Bytes(JSON.stringify({
        name: "UX Design Contributor – Gitcoin Q3 2024",
        description: "Verified contributor in Gitcoin's UX audit round",
        domain: "ux_design",
        level: "L3",
        skills: ["User Research", "Prototype Design", "Usability Testing"]
      })))
    },
    {
      holder: holder1.address,
      domain: "solidity_dev",
      issuer: "OpenZeppelin Academy",
      level: "L2",
      validUntil: Math.floor(Date.now() / 1000) + (365 * 24 * 60 * 60), // 1 year
      metadataURI: "ipfs://QmSolidityDevL2MetadataHash",
      contentHash: hre.ethers.utils.keccak256(hre.ethers.utils.toUtf8Bytes(JSON.stringify({
        name: "Solidity Developer L2",
        description: "Intermediate Solidity developer with DeFi experience",
        domain: "solidity_dev",
        level: "L2",
        skills: ["Smart Contracts", "DeFi Protocols", "Testing"]
      })))
    },
    {
      holder: holder2.address,
      domain: "governance",
      issuer: "Developer DAO",
      level: "L1",
      validUntil: 0,
      metadataURI: "ipfs://QmGovernanceL1MetadataHash",
      contentHash: hre.ethers.utils.keccak256(hre.ethers.utils.toUtf8Bytes(JSON.stringify({
        name: "DAO Governance Participant L1",
        description: "Active participant in DAO governance processes",
        domain: "governance",
        level: "L1",
        skills: ["Proposal Review", "Community Voting", "Discussion"]
      })))
    },
    {
      holder: holder2.address,
      domain: "community_management",
      issuer: "Discord Communities",
      level: "L2",
      validUntil: Math.floor(Date.now() / 1000) + (180 * 24 * 60 * 60), // 6 months
      metadataURI: "ipfs://QmCommunityMgmtL2MetadataHash",
      contentHash: hre.ethers.utils.keccak256(hre.ethers.utils.toUtf8Bytes(JSON.stringify({
        name: "Community Manager L2",
        description: "Experienced community moderator and event organizer",
        domain: "community_management",
        level: "L2",
        skills: ["Moderation", "Event Planning", "Conflict Resolution"]
      })))
    }
  ];

  console.log("\n🏭 Minting RiSTs...");
  
  for (let i = 0; i < exampleRiSTs.length; i++) {
    const ristData = exampleRiSTs[i];
    
    console.log(`\n${i + 1}. Minting ${ristData.domain} ${ristData.level} to ${ristData.holder}`);
    console.log(`   Issuer: ${ristData.issuer}`);
    
    try {
      const tx = await rist.mintRiST(ristData.holder, ristData);
      await tx.wait();
      
      console.log(`✅ Minted RiST with token ID ${i}`);
      console.log(`   Transaction: ${tx.hash}`);
      
    } catch (error) {
      console.error(`❌ Failed to mint RiST: ${error.message}`);
    }
  }

  // Demonstrate metadata update with holder signature
  console.log("\n🔄 Demonstrating Holder-Approved Metadata Update...");
  
  try {
    const tokenId = 0;
    const newURI = "ipfs://QmUpdatedMetadataHash";
    const newContentHash = hre.ethers.utils.keccak256(hre.ethers.utils.toUtf8Bytes("updated metadata"));
    
    // Create EIP-712 signature from holder
    const domain = {
      name: "ReputationSplittingToken",
      version: "1",
      chainId: await hre.ethers.provider.getNetwork().then(n => n.chainId),
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

    const nonce = await rist.nonces(holder1.address);
    const value = {
      tokenId: tokenId,
      metadataURI: newURI,
      contentHash: newContentHash,
      nonce: nonce
    };

    const signature = await holder1._signTypedData(domain, types, value);
    
    console.log("Updating metadata with holder signature...");
    const updateTx = await rist.updateMetadata(tokenId, newURI, newContentHash, signature);
    await updateTx.wait();
    
    console.log("✅ Metadata updated successfully");
    console.log(`   New URI: ${newURI}`);
    
  } catch (error) {
    console.error(`❌ Metadata update failed: ${error.message}`);
  }

  // Create ephemeral access chips
  console.log("\n🎫 Creating Ephemeral Access Chips...");
  
  const accessChips = [
    {
      holder: holder1.address,
      expiry: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours
      maxViews: 5,
      scopeTokenId: 0, // All RiSTs
      resumeURI: "https://resume.reputation.xyz/holder1",
      amount: 3
    },
    {
      holder: holder2.address,
      expiry: Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60), // 7 days
      maxViews: 10,
      scopeTokenId: 0,
      resumeURI: "https://resume.reputation.xyz/holder2",
      amount: 5
    }
  ];

  for (let i = 0; i < accessChips.length; i++) {
    const chip = accessChips[i];
    
    console.log(`\n${i + 1}. Creating access chip for ${chip.holder}`);
    console.log(`   Expiry: ${new Date(chip.expiry * 1000).toLocaleString()}`);
    console.log(`   Max Views: ${chip.maxViews}`);
    
    try {
      const tx = await accessChip.connect(deployer).mintChip(
        chip.holder,
        chip.expiry,
        chip.maxViews,
        chip.scopeTokenId,
        chip.resumeURI,
        chip.amount
      );
      await tx.wait();
      
      console.log(`✅ Access chip created with ID ${i}`);
      console.log(`   Transaction: ${tx.hash}`);
      
    } catch (error) {
      console.error(`❌ Failed to create access chip: ${error.message}`);
    }
  }

  // Query reputation scores through registry
  console.log("\n📊 Reputation Scores (via Registry):");
  console.log("=====================================");
  
  const domains = ["ux_design", "solidity_dev", "governance", "community_management"];
  const holders = [holder1.address, holder2.address];
  
  for (const holder of holders) {
    console.log(`\nHolder: ${holder}`);
    
    for (const domain of domains) {
      try {
        const totalScore = await registry.getTotalReputationScore(holder, domain);
        console.log(`  ${domain}: ${totalScore} RiSTs`);
      } catch (error) {
        console.log(`  ${domain}: Error querying - ${error.message}`);
      }
    }
  }

  // Demonstrate access chip usage
  console.log("\n🔥 Demonstrating Access Chip Burn...");
  
  try {
    console.log("Burning access chip for résumé viewing...");
    const chipId = 0;
    const viewer = holder2.address;
    
    const burnTx = await accessChip.connect(holder1).burnAndVerifyAccess(chipId, viewer);
    await burnTx.wait();
    
    console.log("✅ Access chip burned successfully");
    console.log(`   Viewer: ${viewer}`);
    
    // Check remaining chips
    const chipData = await accessChip.getChipData(chipId);
    console.log(`   Remaining views: ${chipData.maxViews - chipData.currentViews}`);
    
  } catch (error) {
    console.error(`❌ Access chip burn failed: ${error.message}`);
  }

  // Demonstrate revocation
  console.log("\n🔄 Demonstrating RiST Revocation...");
  
  try {
    console.log("Revoking token ID 0 (ux_design L3)...");
    const revokeTx = await rist.revokeRiST(0);
    await revokeTx.wait();
    console.log("✅ RiST revoked successfully");
    
    // Check validity
    const isValid = await rist.isValid(0);
    console.log(`   Is valid: ${isValid}`);
    
  } catch (error) {
    console.error(`❌ Revocation failed: ${error.message}`);
  }

  console.log("\n🎉 Example RiST Operations Complete!");
  console.log("=====================================");
  console.log(`Network: ${hre.network.name}`);
  console.log(`RiST Contract: ${ristAddress}`);
  console.log(`Registry Contract: ${registryAddress}`);
  console.log(`Access Chip Contract: ${accessChipAddress}`);
  console.log(`Total RiSTs minted: ${exampleRiSTs.length}`);
  console.log(`Unique domains: ${domains.length}`);
  console.log(`Unique holders: ${holders.length}`);
  
  console.log("\n📋 Next Steps:");
  console.log("1. Build issuer dashboard for easier minting");
  console.log("2. Create holder profile viewer with QR codes");
  console.log("3. Integrate with token-gating applications");
  console.log("4. Set up The Graph indexing for queries");
  console.log("5. Implement ZK-proof verification modules");
  
  console.log("\n🔗 Integration Examples:");
  console.log("- DAO governance: Require governance RiSTs for voting");
  console.log("- Job platforms: Verify skills with domain-specific RiSTs");
  console.log("- Event access: Use access chips for time-limited entry");
  console.log("- Professional networks: Showcase verified credentials");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Example operations failed:", error);
    process.exit(1);
  });