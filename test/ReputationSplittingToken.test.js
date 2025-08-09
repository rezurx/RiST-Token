const { expect } = require("chai");
const { ethers, upgrades } = require("hardhat");

describe("ReputationSplittingToken", function () {
  let rist, registry, timelock, accessChip;
  let admin, issuer, holder, other;
  let ISSUER_ROLE, ADMIN_ROLE, UPGRADER_ROLE;

  beforeEach(async function () {
    [admin, issuer, holder, other] = await ethers.getSigners();

    // Deploy timelock
    const RiSTTimelock = await ethers.getContractFactory("RiSTTimelock");
    timelock = await RiSTTimelock.deploy(
      604800, // 7 days
      [admin.address],
      [admin.address],
      ethers.ZeroAddress
    );
    await timelock.waitForDeployment();

    // Deploy registry
    const RSTRegistry = await ethers.getContractFactory("RSTRegistry");
    registry = await RSTRegistry.deploy(admin.address);
    await registry.waitForDeployment();

    // Deploy RiST as UUPS proxy
    const ReputationSplittingToken = await ethers.getContractFactory("ReputationSplittingToken");
    rist = await upgrades.deployProxy(
      ReputationSplittingToken,
      ["Reputation Splitting Token", "RiST", admin.address],
      { kind: "uups", initializer: "initialize" }
    );
    await rist.waitForDeployment();

    // Deploy access chip
    const ResumeAccessChip = await ethers.getContractFactory("ResumeAccessChip");
    accessChip = await ResumeAccessChip.deploy("https://api.test.xyz/chips/{id}");
    await accessChip.waitForDeployment();

    // Get role constants
    ISSUER_ROLE = await rist.ISSUER_ROLE();
    ADMIN_ROLE = await rist.ADMIN_ROLE();
    UPGRADER_ROLE = await rist.UPGRADER_ROLE();

    // Setup initial configuration
    await rist.connect(admin).grantRole(UPGRADER_ROLE, timelock.address);
    await rist.connect(admin).setIssuerWhitelist(issuer.address, true);
    await registry.connect(admin).approveDomain("test_domain");
  });

  describe("Initialization", function () {
    it("Should initialize correctly", async function () {
      expect(await rist.name()).to.equal("Reputation Splitting Token");
      expect(await rist.symbol()).to.equal("RiST");
      expect(await rist.hasRole(ADMIN_ROLE, admin.address)).to.be.true;
      expect(await rist.hasRole(UPGRADER_ROLE, timelock.address)).to.be.true;
    });

    it("Should implement EIP-5114 interface", async function () {
      const EIP5114_INTERFACE_ID = "0x0489b56f"; // EIP-5114 interface ID
      expect(await rist.supportsInterface(EIP5114_INTERFACE_ID)).to.be.true;
    });
  });

  describe("RiST Minting", function () {
    it("Should mint RiST with correct data", async function () {
      const ristData = {
        domain: "test_domain",
        issuer: "Test Issuer",
        level: "L3",
        issuedAt: 0, // Will be set by contract
        validUntil: 0, // Perpetual
        revoked: false,
        metadataURI: "ipfs://test-metadata",
        contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test content"))
      };

      await expect(rist.connect(issuer).mintRiST(holder.address, ristData))
        .to.emit(rist, "RiSTIssued")
        .withArgs(0, holder.address, "test_domain")
        .to.emit(rist, "Issued")
        .withArgs(issuer.address, holder.address, 0);

      const mintedRiST = await rist.getRiST(0);
      expect(mintedRiST.domain).to.equal("test_domain");
      expect(mintedRiST.issuer).to.equal("Test Issuer");
      expect(mintedRiST.level).to.equal("L3");
      expect(mintedRiST.metadataURI).to.equal("ipfs://test-metadata");
      expect(mintedRiST.contentHash).to.equal(ristData.contentHash);
      expect(mintedRiST.revoked).to.be.false;
    });

    it("Should reject minting from non-whitelisted issuer", async function () {
      const ristData = {
        domain: "test_domain",
        issuer: "Test Issuer",
        level: "L3",
        issuedAt: 0,
        validUntil: 0,
        revoked: false,
        metadataURI: "ipfs://test-metadata",
        contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test content"))
      };

      await expect(rist.connect(other).mintRiST(holder.address, ristData))
        .to.be.revertedWithCustomError(rist, "IssuerNotWhitelisted");
    });

    it("Should reject minting with empty domain", async function () {
      const ristData = {
        domain: "",
        issuer: "Test Issuer",
        level: "L3",
        issuedAt: 0,
        validUntil: 0,
        revoked: false,
        metadataURI: "ipfs://test-metadata",
        contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test content"))
      };

      await expect(rist.connect(issuer).mintRiST(holder.address, ristData))
        .to.be.revertedWithCustomError(rist, "EmptyDomain");
    });
  });

  describe("Soulbound Behavior", function () {
    beforeEach(async function () {
      const ristData = {
        domain: "test_domain",
        issuer: "Test Issuer",
        level: "L3",
        issuedAt: 0,
        validUntil: 0,
        revoked: false,
        metadataURI: "ipfs://test-metadata",
        contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test content"))
      };
      await rist.connect(issuer).mintRiST(holder.address, ristData);
    });

    it("Should prevent transfers", async function () {
      await expect(rist.connect(holder).transferFrom(holder.address, other.address, 0))
        .to.be.revertedWithCustomError(rist, "SoulboundTokenTransferAttempt");
    });

    it("Should prevent approvals", async function () {
      await expect(rist.connect(holder).approve(other.address, 0))
        .to.be.revertedWithCustomError(rist, "SoulboundTokenTransferAttempt");
    });

    it("Should prevent setApprovalForAll", async function () {
      await expect(rist.connect(holder).setApprovalForAll(other.address, true))
        .to.be.revertedWithCustomError(rist, "SoulboundTokenTransferAttempt");
    });

    it("Should return true for isSoulbound", async function () {
      expect(await rist.isSoulbound(0)).to.be.true;
    });
  });

  describe("RiST Revocation", function () {
    beforeEach(async function () {
      const ristData = {
        domain: "test_domain",
        issuer: "Test Issuer",
        level: "L3",
        issuedAt: 0,
        validUntil: 0,
        revoked: false,
        metadataURI: "ipfs://test-metadata",
        contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test content"))
      };
      await rist.connect(issuer).mintRiST(holder.address, ristData);
    });

    it("Should allow issuer to revoke", async function () {
      await expect(rist.connect(issuer).revokeRiST(0))
        .to.emit(rist, "RiSTRevoked")
        .withArgs(0, issuer.address);

      const ristData = await rist.getRiST(0);
      expect(ristData.revoked).to.be.true;
      expect(await rist.isValid(0)).to.be.false;
    });

    it("Should allow admin to revoke", async function () {
      await expect(rist.connect(admin).revokeRiST(0))
        .to.emit(rist, "RiSTRevoked")
        .withArgs(0, admin.address);

      const ristData = await rist.getRiST(0);
      expect(ristData.revoked).to.be.true;
    });

    it("Should reject revocation from unauthorized user", async function () {
      await expect(rist.connect(other).revokeRiST(0))
        .to.be.revertedWithCustomError(rist, "NotAuthorized");
    });

    it("Should reject double revocation", async function () {
      await rist.connect(issuer).revokeRiST(0);
      await expect(rist.connect(issuer).revokeRiST(0))
        .to.be.revertedWithCustomError(rist, "TokenAlreadyRevoked");
    });
  });

  describe("Metadata Updates", function () {
    let tokenId;

    beforeEach(async function () {
      const ristData = {
        domain: "test_domain",
        issuer: "Test Issuer",
        level: "L3",
        issuedAt: 0,
        validUntil: 0,
        revoked: false,
        metadataURI: "ipfs://test-metadata",
        contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test content"))
      };
      await rist.connect(issuer).mintRiST(holder.address, ristData);
      tokenId = 0;
    });

    it("Should update metadata with valid holder signature", async function () {
      const newURI = "ipfs://new-metadata";
      const newHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("new content"));
      const nonce = await rist.nonces(holder.address);

      // Create EIP-712 signature
      const domain = {
        name: "ReputationSplittingToken",
        version: "1",
        chainId: await ethers.provider.getNetwork().then(n => n.chainId),
        verifyingContract: await rist.getAddress()
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
        tokenId: tokenId,
        metadataURI: newURI,
        contentHash: newHash,
        nonce: nonce
      };

      const signature = await holder._signTypedData(domain, types, value);

      await expect(rist.connect(issuer).updateMetadata(tokenId, newURI, newHash, signature))
        .to.emit(rist, "MetadataUpdated")
        .withArgs(tokenId, newURI);

      const updatedRiST = await rist.getRiST(tokenId);
      expect(updatedRiST.metadataURI).to.equal(newURI);
      expect(updatedRiST.contentHash).to.equal(newHash);
    });

    it("Should reject metadata update with invalid signature", async function () {
      const newURI = "ipfs://new-metadata";
      const newHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("new content"));
      const invalidSignature = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234";

      await expect(rist.connect(issuer).updateMetadata(tokenId, newURI, newHash, invalidSignature))
        .to.be.revertedWithCustomError(rist, "InvalidSignature");
    });
  });

  describe("Domain Queries", function () {
    beforeEach(async function () {
      // Mint multiple RiSTs in different domains
      const ristData1 = {
        domain: "test_domain",
        issuer: "Test Issuer",
        level: "L3",
        issuedAt: 0,
        validUntil: 0,
        revoked: false,
        metadataURI: "ipfs://test-metadata-1",
        contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test content 1"))
      };
      
      const ristData2 = {
        domain: "test_domain",
        issuer: "Test Issuer",
        level: "L2",
        issuedAt: 0,
        validUntil: Math.floor(Date.now() / 1000) + 86400, // 1 day from now
        revoked: false,
        metadataURI: "ipfs://test-metadata-2",
        contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test content 2"))
      };

      await registry.connect(admin).approveDomain("other_domain");
      const ristData3 = {
        domain: "other_domain",
        issuer: "Test Issuer",
        level: "L1",
        issuedAt: 0,
        validUntil: 0,
        revoked: false,
        metadataURI: "ipfs://test-metadata-3",
        contentHash: ethers.utils.keccak256(ethers.utils.toUtf8Bytes("test content 3"))
      };

      await rist.connect(issuer).mintRiST(holder.address, ristData1);
      await rist.connect(issuer).mintRiST(holder.address, ristData2);
      await rist.connect(issuer).mintRiST(holder.address, ristData3);
    });

    it("Should return valid RiSTs by domain", async function () {
      const validRiSTs = await rist.getValidRiSTsByDomain(holder.address, "test_domain");
      expect(validRiSTs.length).to.equal(2);
      expect(validRiSTs[0]).to.equal(0);
      expect(validRiSTs[1]).to.equal(1);
    });

    it("Should exclude revoked RiSTs", async function () {
      await rist.connect(issuer).revokeRiST(0);
      const validRiSTs = await rist.getValidRiSTsByDomain(holder.address, "test_domain");
      expect(validRiSTs.length).to.equal(1);
      expect(validRiSTs[0]).to.equal(1);
    });
  });

  describe("Upgradeability", function () {
    it("Should allow upgrade through timelock", async function () {
      // This test verifies the upgrade mechanism is in place
      // In a real scenario, you would deploy a new implementation
      expect(await rist.hasRole(UPGRADER_ROLE, timelock.address)).to.be.true;
    });

    it("Should reject upgrade from non-upgrader", async function () {
      const ReputationSplittingTokenV2 = await ethers.getContractFactory("ReputationSplittingToken");
      const newImplementation = await ReputationSplittingTokenV2.deploy();
      await newImplementation.deployed();

      // This should fail because other doesn't have UPGRADER_ROLE
      await expect(rist.connect(other).upgradeTo(newImplementation.address))
        .to.be.reverted;
    });
  });
});

describe("RSTRegistry", function () {
  let registry, rist;
  let admin, issuer, other;

  beforeEach(async function () {
    [admin, issuer, other] = await ethers.getSigners();

    // Deploy registry
    const RSTRegistry = await ethers.getContractFactory("RSTRegistry");
    registry = await RSTRegistry.deploy(admin.address);
    await registry.waitForDeployment();

    // Deploy RiST for testing
    const ReputationSplittingToken = await ethers.getContractFactory("ReputationSplittingToken");
    rist = await upgrades.deployProxy(
      ReputationSplittingToken,
      ["Test RiST", "TEST", admin.address],
      { kind: "uups", initializer: "initialize" }
    );
    await rist.waitForDeployment();
  });

  describe("Contract Registration", function () {
    it("Should register contract successfully", async function () {
      await expect(registry.connect(admin).registerContract(await rist.getAddress(), "TestRiST", "1.0.0"))
        .to.emit(registry, "ContractRegistered")
        .withArgs(await rist.getAddress(), "TestRiST", "1.0.0");

      expect(await registry.registeredContracts(await rist.getAddress())).to.be.true;
    });

    it("Should reject duplicate registration", async function () {
      await registry.connect(admin).registerContract(await rist.getAddress(), "TestRiST", "1.0.0");
      await expect(registry.connect(admin).registerContract(await rist.getAddress(), "TestRiST", "1.0.0"))
        .to.be.revertedWithCustomError(registry, "ContractAlreadyRegistered");
    });

    it("Should reject registration from non-admin", async function () {
      await expect(registry.connect(other).registerContract(await rist.getAddress(), "TestRiST", "1.0.0"))
        .to.be.reverted;
    });
  });

  describe("Issuer Management", function () {
    it("Should register issuer successfully", async function () {
      await expect(registry.connect(admin).registerIssuer(issuer.address, "Test Issuer", "did:example:123", "ipfs://metadata"))
        .to.emit(registry, "IssuerRegistered")
        .withArgs(issuer.address, "Test Issuer", "did:example:123");

      const issuerInfo = await registry.issuerInfo(issuer.address);
      expect(issuerInfo.name).to.equal("Test Issuer");
      expect(issuerInfo.did).to.equal("did:example:123");
      expect(issuerInfo.active).to.be.true;
    });

    it("Should update issuer info", async function () {
      await registry.connect(admin).registerIssuer(issuer.address, "Test Issuer", "did:example:123", "ipfs://metadata");
      
      await expect(registry.connect(admin).updateIssuer(issuer.address, "Updated Issuer", "did:example:456", false, "ipfs://new-metadata"))
        .to.emit(registry, "IssuerUpdated")
        .withArgs(issuer.address, "Updated Issuer", "did:example:456", false);

      const issuerInfo = await registry.issuerInfo(issuer.address);
      expect(issuerInfo.name).to.equal("Updated Issuer");
      expect(issuerInfo.did).to.equal("did:example:456");
      expect(issuerInfo.active).to.be.false;
    });
  });

  describe("Domain Management", function () {
    it("Should approve domain successfully", async function () {
      await expect(registry.connect(admin).approveDomain("test_domain"))
        .to.emit(registry, "DomainApproved")
        .withArgs("test_domain");

      expect(await registry.approvedDomains("test_domain")).to.be.true;
    });

    it("Should revoke domain", async function () {
      await registry.connect(admin).approveDomain("test_domain");
      
      await expect(registry.connect(admin).revokeDomain("test_domain"))
        .to.emit(registry, "DomainRevoked")
        .withArgs("test_domain");

      expect(await registry.approvedDomains("test_domain")).to.be.false;
    });

    it("Should get approved domains", async function () {
      await registry.connect(admin).approveDomain("domain1");
      await registry.connect(admin).approveDomain("domain2");
      await registry.connect(admin).approveDomain("domain3");
      await registry.connect(admin).revokeDomain("domain2");

      const approvedDomains = await registry.getApprovedDomains();
      expect(approvedDomains.length).to.equal(2);
      expect(approvedDomains[0]).to.equal("domain1");
      expect(approvedDomains[1]).to.equal("domain3");
    });
  });
});

describe("ResumeAccessChip", function () {
  let accessChip;
  let owner, minter, viewer, other;

  beforeEach(async function () {
    [owner, minter, viewer, other] = await ethers.getSigners();

    const ResumeAccessChip = await ethers.getContractFactory("ResumeAccessChip");
    accessChip = await ResumeAccessChip.deploy("https://api.test.xyz/chips/{id}");
    await accessChip.waitForDeployment();
  });

  describe("Chip Minting", function () {
    it("Should mint chip successfully", async function () {
      const expiry = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
      const maxViews = 5;
      const scopeTokenId = 0;
      const resumeURI = "https://resume.test.xyz/user1";
      const amount = 3;

      await expect(accessChip.connect(minter).mintChip(
        minter.address,
        expiry,
        maxViews,
        scopeTokenId,
        resumeURI,
        amount
      ))
        .to.emit(accessChip, "ChipMinted")
        .withArgs(minter.address, 0, expiry, maxViews, scopeTokenId);

      const chipData = await accessChip.getChipData(0);
      expect(chipData.minter).to.equal(minter.address);
      expect(chipData.expiry).to.equal(expiry);
      expect(chipData.maxViews).to.equal(maxViews);
      expect(chipData.scopeTokenId).to.equal(scopeTokenId);
      expect(chipData.resumeURI).to.equal(resumeURI);
      expect(chipData.currentViews).to.equal(0);
      expect(chipData.burned).to.be.false;

      expect(await accessChip.balanceOf(minter.address, 0)).to.equal(amount);
    });

    it("Should reject minting to zero address", async function () {
      await expect(accessChip.connect(minter).mintChip(
        ethers.ZeroAddress,
        0,
        5,
        0,
        "https://resume.test.xyz/user1",
        1
      ))
        .to.be.revertedWithCustomError(accessChip, "ZeroAddress");
    });
  });

  describe("Chip Burning and Access", function () {
    let chipId;

    beforeEach(async function () {
      const expiry = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
      const maxViews = 3;
      const scopeTokenId = 0;
      const resumeURI = "https://resume.test.xyz/user1";
      const amount = 2;

      await accessChip.connect(minter).mintChip(
        minter.address,
        expiry,
        maxViews,
        scopeTokenId,
        resumeURI,
        amount
      );
      chipId = 0;
    });

    it("Should burn chip and grant access", async function () {
      await expect(accessChip.connect(minter).burnAndVerifyAccess(chipId, viewer.address))
        .to.emit(accessChip, "ChipBurned")
        .withArgs(chipId, minter.address, viewer.address)
        .to.emit(accessChip, "ResumeViewed")
        .withArgs(chipId, viewer.address, 1);

      const chipData = await accessChip.getChipData(chipId);
      expect(chipData.currentViews).to.equal(1);
      expect(await accessChip.balanceOf(minter.address, chipId)).to.equal(1);
    });

    it("Should mark chip as burned when exhausted", async function () {
      // Burn all chips
      await accessChip.connect(minter).burnAndVerifyAccess(chipId, viewer.address);
      await accessChip.connect(minter).burnAndVerifyAccess(chipId, viewer.address);

      const chipData = await accessChip.getChipData(chipId);
      expect(chipData.burned).to.be.true;
      expect(await accessChip.balanceOf(minter.address, chipId)).to.equal(0);
    });

    it("Should reject burning expired chip", async function () {
      // Create chip with past expiry
      const pastExpiry = Math.floor(Date.now() / 1000) - 86400; // 1 day ago
      await accessChip.connect(minter).mintChip(
        minter.address,
        pastExpiry,
        5,
        0,
        "https://resume.test.xyz/user1",
        1
      );

      await expect(accessChip.connect(minter).burnAndVerifyAccess(1, viewer.address))
        .to.be.revertedWithCustomError(accessChip, "ChipExpired");
    });

    it("Should reject burning when view limit exceeded", async function () {
      // Create a new chip for this test
      const expiry = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
      const scopeTokenId = 0;
      const resumeURI = "https://resume.test.xyz/user1";
      const amount = 2;
      
      await accessChip.connect(minter).mintChip(
        minter.address,
        expiry,
        3, // maxViews = 3
        scopeTokenId,
        resumeURI,
        amount
      );
      const newChipId = 1;
      
      // Burn until view limit reached
      await accessChip.connect(minter).burnAndVerifyAccess(newChipId, viewer.address);
      await accessChip.connect(minter).burnAndVerifyAccess(newChipId, viewer.address);
      await accessChip.connect(minter).burnAndVerifyAccess(newChipId, other.address);

      await expect(accessChip.connect(minter).burnAndVerifyAccess(newChipId, viewer.address))
        .to.be.revertedWithCustomError(accessChip, "ChipExhausted");
    });
  });

  describe("Chip Validation", function () {
    it("Should validate active chips", async function () {
      const expiry = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
      await accessChip.connect(minter).mintChip(
        minter.address,
        expiry,
        5,
        0,
        "https://resume.test.xyz/user1",
        1
      );

      expect(await accessChip.isChipValid(0)).to.be.true;
    });

    it("Should invalidate expired chips", async function () {
      const pastExpiry = Math.floor(Date.now() / 1000) - 86400; // 1 day ago
      await accessChip.connect(minter).mintChip(
        minter.address,
        pastExpiry,
        5,
        0,
        "https://resume.test.xyz/user1",
        1
      );

      expect(await accessChip.isChipValid(0)).to.be.false;
    });

    it("Should get valid chips for holder", async function () {
      const futureExpiry = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
      const pastExpiry = Math.floor(Date.now() / 1000) - 86400; // 1 day ago

      await accessChip.connect(minter).mintChip(minter.address, futureExpiry, 5, 0, "https://resume1.test.xyz", 1);
      await accessChip.connect(minter).mintChip(minter.address, pastExpiry, 5, 0, "https://resume2.test.xyz", 1);
      await accessChip.connect(minter).mintChip(minter.address, 0, 5, 0, "https://resume3.test.xyz", 1); // No expiry

      const validChips = await accessChip.getValidChips(minter.address);
      expect(validChips.length).to.equal(2);
      expect(validChips[0]).to.equal(0);
      expect(validChips[1]).to.equal(2);
    });
  });
});