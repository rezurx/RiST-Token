const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Skimpy", function () {
  let skimpy;
  let owner;
  let addr1;
  let addr2;

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();
    
    const Skimpy = await ethers.getContractFactory("Skimpy");
    skimpy = await Skimpy.deploy();
    await skimpy.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should have correct name and symbol", async function () {
      expect(await skimpy.name()).to.equal("Skimpy");
      expect(await skimpy.symbol()).to.equal("SKMP");
    });

    it("Should mint 1,000,000 SKMP to deployer", async function () {
      const totalSupply = await skimpy.totalSupply();
      const ownerBalance = await skimpy.balanceOf(owner.address);
      
      expect(totalSupply).to.equal(ethers.parseEther("1000000"));
      expect(ownerBalance).to.equal(totalSupply);
    });

    it("Should have 18 decimals", async function () {
      expect(await skimpy.decimals()).to.equal(18);
    });
  });

  describe("Transfers", function () {
    it("Should transfer tokens between accounts", async function () {
      const transferAmount = ethers.parseEther("100");
      
      await skimpy.transfer(addr1.address, transferAmount);
      expect(await skimpy.balanceOf(addr1.address)).to.equal(transferAmount);
      
      const ownerBalance = await skimpy.balanceOf(owner.address);
      expect(ownerBalance).to.equal(ethers.parseEther("999900"));
    });

    it("Should fail if sender doesn't have enough tokens", async function () {
      const initialOwnerBalance = await skimpy.balanceOf(owner.address);
      
      await expect(
        skimpy.connect(addr1).transfer(owner.address, 1)
      ).to.be.revertedWithCustomError(skimpy, "ERC20InsufficientBalance");
      
      expect(await skimpy.balanceOf(owner.address)).to.equal(initialOwnerBalance);
    });
  });
});