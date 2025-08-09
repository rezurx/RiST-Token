const { ethers, upgrades } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy timelock first (7 days = 604800 seconds)
  const TIMELOCK_DELAY = 604800; // 7 days in seconds
  
  console.log("\n1. Deploying RiSTTimelock...");
  const RiSTTimelock = await ethers.getContractFactory("RiSTTimelock");
  const timelock = await RiSTTimelock.deploy(
    TIMELOCK_DELAY,
    [deployer.address], // proposers
    [deployer.address], // executors
    ethers.constants.AddressZero // admin (set to zero for decentralization)
  );
  await timelock.deployed();
  console.log("RiSTTimelock deployed to:", timelock.address);

  // Deploy RSTRegistry
  console.log("\n2. Deploying RSTRegistry...");
  const RSTRegistry = await ethers.getContractFactory("RSTRegistry");
  const registry = await RSTRegistry.deploy(deployer.address);
  await registry.deployed();
  console.log("RSTRegistry deployed to:", registry.address);

  // Deploy ReputationSplittingToken as UUPS proxy
  console.log("\n3. Deploying ReputationSplittingToken (UUPS Proxy)...");
  const ReputationSplittingToken = await ethers.getContractFactory("ReputationSplittingToken");
  
  const rist = await upgrades.deployProxy(
    ReputationSplittingToken,
    [
      "Reputation Splitting Token",
      "RiST",
      deployer.address
    ],
    {
      kind: "uups",
      initializer: "initialize"
    }
  );
  await rist.deployed();
  console.log("ReputationSplittingToken proxy deployed to:", rist.address);

  // Deploy ResumeAccessChip
  console.log("\n4. Deploying ResumeAccessChip...");
  const ResumeAccessChip = await ethers.getContractFactory("ResumeAccessChip");
  const accessChip = await ResumeAccessChip.deploy("https://api.reputation.xyz/chips/{id}");
  await accessChip.deployed();
  console.log("ResumeAccessChip deployed to:", accessChip.address);

  // Setup initial configuration
  console.log("\n5. Setting up initial configuration...");
  
  // Grant timelock the upgrader role
  const UPGRADER_ROLE = await rist.UPGRADER_ROLE();
  await rist.grantRole(UPGRADER_ROLE, timelock.address);
  console.log("Granted UPGRADER_ROLE to timelock");

  // Register the RiST contract in the registry
  await registry.registerContract(
    rist.address,
    "ReputationSplittingToken",
    "1.0.0"
  );
  console.log("Registered RiST contract in registry");

  // Add some initial approved domains
  const initialDomains = [
    "ux_design",
    "solidity_dev",
    "frontend_dev",
    "backend_dev",
    "governance",
    "moderation",
    "content_creation",
    "community_management"
  ];

  console.log("\n6. Adding initial approved domains...");
  for (const domain of initialDomains) {
    await registry.approveDomain(domain);
    console.log(`Approved domain: ${domain}`);
  }

  // Register deployer as an initial issuer
  await registry.registerIssuer(
    deployer.address,
    "Initial Issuer",
    "", // No DID initially
    "https://metadata.reputation.xyz/issuers/initial"
  );
  console.log("Registered deployer as initial issuer");

  // Whitelist deployer in the RiST contract
  await rist.setIssuerWhitelist(deployer.address, true);
  console.log("Whitelisted deployer in RiST contract");

  console.log("\n🎉 Deployment completed successfully!");
  console.log("\nContract Addresses:");
  console.log("==================");
  console.log("RiSTTimelock:", timelock.address);
  console.log("RSTRegistry:", registry.address);
  console.log("ReputationSplittingToken:", rist.address);
  console.log("ResumeAccessChip:", accessChip.address);

  console.log("\nNext Steps:");
  console.log("==========");
  console.log("1. Verify contracts on block explorer");
  console.log("2. Transfer admin roles to appropriate multisig/DAO");
  console.log("3. Add more issuers via registry.registerIssuer()");
  console.log("4. Test minting RiSTs via rist.mintRiST()");
  console.log("5. Test access chip functionality");

  // Save deployment info
  const deploymentInfo = {
    network: network.name,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      RiSTTimelock: timelock.address,
      RSTRegistry: registry.address,
      ReputationSplittingToken: rist.address,
      ResumeAccessChip: accessChip.address
    },
    config: {
      timelockDelay: TIMELOCK_DELAY,
      initialDomains: initialDomains
    }
  };

  const fs = require("fs");
  const path = require("path");
  const deploymentPath = path.join(__dirname, "../deployments");
  
  if (!fs.existsSync(deploymentPath)) {
    fs.mkdirSync(deploymentPath, { recursive: true });
  }
  
  fs.writeFileSync(
    path.join(deploymentPath, `${network.name}-deployment.json`),
    JSON.stringify(deploymentInfo, null, 2)
  );
  
  console.log(`\nDeployment info saved to: deployments/${network.name}-deployment.json`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });