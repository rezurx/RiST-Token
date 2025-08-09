// test/RSTToken.test.js
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("RSTToken", function () {
  let rstToken;
  let owner, issuer, holder, unauthorizedUser;
  let registry;

  beforeEach(async function () {
    [owner, issuer, holder, unauthorizedUser] = await ethers.getSigners();

    // Deploy RST Token
    const RSTToken = await ethers.getContractFactory("RSTToken");
    rstToken = await RSTToken.deploy();
    await rstToken.deployed();

    // Deploy Registry
    const RSTRegistry = await ethers.getContractFactory("RSTRegistry");
    registry = await RSTRegistry.deploy();
    await registry.deployed();

    // Approve issuer
    await rstToken.setIssuerApproval(issuer.address, true);
  });

  describe("Deployment", function () {
    it("Should set the correct name and symbol", async function () {
      expect(await rstToken.name()).to.equal("Reputation Splitting Token");
      expect(await rstToken.symbol()).to.equal("RST");
    });

    it("Should grant admin role to deployer", async function () {
      const adminRole = await rstToken.ADMIN_ROLE();
      expect(await rstToken.hasRole(adminRole, owner.address)).to.be.true;
    });
  });

  describe("Issuer Management", function () {
    it("Should approve issuers correctly", async function () {
      expect(await rstToken.approvedIssuers(issuer.address)).to.be.true;
      
      const issuerRole = await rstToken.ISSUER_ROLE();
      expect(await rstToken.hasRole(issuerRole, issuer.address)).to.be.true;
    });

    it("Should revoke issuer approval", async function () {
      await rstToken.setIssuerApproval(issuer.address, false);
      
      expect(await rstToken.approvedIssuers(issuer.address)).to.be.false;
      
      const issuerRole = await rstToken.ISSUER_ROLE();
      expect(await rstToken.hasRole(issuerRole, issuer.address)).to.be.false;
    });

    it("Should reject issuer approval from non-admin", async function () {
      await expect(
        rstToken.connect(unauthorizedUser).setIssuerApproval(holder.address, true)
      ).to.be.reverted;
    });
  });

  describe("RST Minting", function () {
    it("Should mint RST successfully", async function () {
      const domain = "governance";
      const level = "L2";
      const validUntil = 0; // Never expires
      const metadataURI = "ipfs://QmExample";

      await expect(
        rstToken.connect(issuer).mintRST(
          holder.address,
          domain,
          level,
          validUntil,
          metadataURI
        )
      ).to.emit(rstToken, "RSTMinted")
        .withArgs(holder.address, issuer.address, 0, domain, level);

      expect(await rstToken.ownerOf(0)).to.equal(holder.address);
      expect(await rstToken.balanceOf(holder.address)).to.equal(1);
    });

    it("Should store metadata correctly", async function () {
      const domain = "development";
      const level = "L3";
      const validUntil = Math.floor(Date.now() / 1000) + 86400; // 1 day
      const metadataURI = "ipfs://QmExample";

      await rstToken.connect(issuer).mintRST(
        holder.address,
        domain,
        level,
        validUntil,
        metadataURI
      );

      const metadata = await rstToken.rstMetadata(0);
      expect(metadata.domain).to.equal(domain);
      expect(metadata.level).to.equal(level);
      expect(metadata.issuer).to.equal(issuer.address);
      expect(metadata.validUntil).to.equal(validUntil);
      expect(metadata.revoked).to.be.false;
      expect(metadata.metadataURI).to.equal(metadataURI);
    });

    it("Should reject minting from non-issuer", async function () {
      await expect(
        rstToken.connect(unauthorizedUser).mintRST(
          holder.address,
          "governance",
          "L1",
          0,
          "ipfs://QmExample"
        )
      ).to.be.reverted;
    });

    it("Should reject minting to zero address", async function () {
      await expect(
        rstToken.connect(issuer).mintRST(
          ethers.constants.AddressZero,
          "governance",
          "L1", 
          0,
          "ipfs://QmExample"
        )
      ).to.be.revertedWith("Cannot mint to zero address");
    });

    it("Should reject empty domain", async function () {
      await expect(
        rstToken.connect(issuer).mintRST(
          holder.address,
          "",
          "L1",
          0,
          "ipfs://QmExample"
        )
      ).to.be.revertedWith("Domain cannot be empty");
    });
  });

  describe("RST Validation", function () {
    beforeEach(async function () {
      // Mint a valid RST
      await rstToken.connect(issuer).mintRST(
        holder.address,
        "governance",
        "L2",
        0,
        "ipfs://QmExample"
      );
    });

    it("Should validate non-expired, non-revoked RST", async function () {
      expect(await rstToken.isValidRST(0)).to.be.true;
    });

    it("Should invalidate revoked RST", async function () {
      await rstToken.connect(issuer).revokeRST(0);
      expect(await rstToken.isValidRST(0)).to.be.false;
    });

    it("Should invalidate expired RST", async function () {
      // Mint an expired RST
      const pastTimestamp = Math.floor(Date.now() / 1000) - 86400; // 1 day ago
      
      await rstToken.connect(issuer).mintRST(
        holder.address,
        "governance",
        "L1",
        pastTimestamp,
        "ipfs://QmExpired"
      );

      expect(await rstToken.isValidRST(1)).to.be.false;
    });
  });

  describe("RST Revocation", function () {
    beforeEach(async function () {
      await rstToken.connect(issuer).mintRST(
        holder.address,
        "governance",
        "L2",
        0,
        "ipfs://QmExample"
      );
    });

    it("Should allow issuer to revoke", async function () {
      await expect(rstToken.connect(issuer).revokeRST(0))
        .to.emit(rstToken, "RSTRevoked")
        .withArgs(0, issuer.address);

      const metadata = await rstToken.rstMetadata(0);
      expect(metadata.revoked).to.be.true;
    });

    it("Should allow admin to revoke", async function () {
      await expect(rstToken.connect(owner).revokeRST(0))
        .to.emit(rstToken, "RSTRevoked")
        .withArgs(0, owner.address);

      const metadata = await rstToken.rstMetadata(0);
      expect(metadata.revoked).to.be.true;
    });

    it("Should reject revocation from unauthorized user", async function () {
      await expect(
        rstToken.connect(unauthorizedUser).revokeRST(0)
      ).to.be.revertedWith("Not authorized to revoke");
    });

    it("Should reject double revocation", async function () {
      await rstToken.connect(issuer).revokeRST(0);
      
      await expect(
        rstToken.connect(issuer).revokeRST(0)
      ).to.be.revertedWith("Already revoked");
    });
  });

  describe("Reputation Scoring", function () {
    beforeEach(async function () {
      // Mint multiple RSTs in same domain
      await rstToken.connect(issuer).mintRST(
        holder.address,
        "governance",
        "L1",
        0,
        "ipfs://QmExample1"
      );
      
      await rstToken.connect(issuer).mintRST(
        holder.address,
        "governance", 
        "L2",
        0,
        "ipfs://QmExample2"
      );

      // Mint RST in different domain
      