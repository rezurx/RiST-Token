// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "./ReputationSplittingToken.sol";

/**
 * @title RSTRegistry
 * @dev Enhanced registry for managing multiple RiST contracts and issuers
 * Provides centralized querying and issuer management
 */
contract RSTRegistry is AccessControl, Pausable {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant REGISTRY_MANAGER_ROLE = keccak256("REGISTRY_MANAGER_ROLE");
    
    struct IssuerInfo {
        string name;            // Issuer organization name
        string did;             // DID string if available
        bool active;            // Whether issuer is active
        uint256 registeredAt;   // Registration timestamp
        string metadataURI;     // IPFS/HTTPS link to issuer metadata
    }
    
    struct ContractInfo {
        address contractAddress;
        string name;
        string version;
        bool active;
        uint256 registeredAt;
    }
    
    mapping(address => bool) public registeredContracts;
    mapping(address => ContractInfo) public contractInfo;
    mapping(address => IssuerInfo) public issuerInfo;
    
    address[] public ristContracts;
    address[] public registeredIssuers;
    
    // Domain management
    mapping(string => bool) public approvedDomains;
    string[] public domainList;
    
    event ContractRegistered(
        address indexed contractAddress,
        string name,
        string version
    );
    
    event ContractDeregistered(address indexed contractAddress);
    
    event IssuerRegistered(
        address indexed issuer,
        string name,
        string did
    );
    
    event IssuerUpdated(
        address indexed issuer,
        string name,
        string did,
        bool active
    );
    
    event DomainApproved(string domain);
    event DomainRevoked(string domain);
    
    error ContractAlreadyRegistered();
    error ContractNotRegistered();
    error IssuerAlreadyRegistered();
    error IssuerNotRegistered();
    error DomainAlreadyApproved();
    error DomainNotApproved();
    error ZeroAddress();
    error EmptyString();
    
    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(REGISTRY_MANAGER_ROLE, admin);
    }
    
    /**
     * @dev Register a RiST contract
     */
    function registerContract(
        address contractAddress,
        string calldata name,
        string calldata version
    ) external onlyRole(REGISTRY_MANAGER_ROLE) {
        if (contractAddress == address(0)) revert ZeroAddress();
        if (bytes(name).length == 0) revert EmptyString();
        if (registeredContracts[contractAddress]) revert ContractAlreadyRegistered();
        
        registeredContracts[contractAddress] = true;
        contractInfo[contractAddress] = ContractInfo({
            contractAddress: contractAddress,
            name: name,
            version: version,
            active: true,
            registeredAt: block.timestamp
        });
        
        ristContracts.push(contractAddress);
        
        emit ContractRegistered(contractAddress, name, version);
    }
    
    /**
     * @dev Deregister a RiST contract
     */
    function deregisterContract(address contractAddress) external onlyRole(REGISTRY_MANAGER_ROLE) {
        if (!registeredContracts[contractAddress]) revert ContractNotRegistered();
        
        registeredContracts[contractAddress] = false;
        contractInfo[contractAddress].active = false;
        
        emit ContractDeregistered(contractAddress);
    }
    
    /**
     * @dev Register an issuer
     */
    function registerIssuer(
        address issuer,
        string calldata name,
        string calldata did,
        string calldata metadataURI
    ) external onlyRole(ADMIN_ROLE) {
        if (issuer == address(0)) revert ZeroAddress();
        if (bytes(name).length == 0) revert EmptyString();
        if (issuerInfo[issuer].registeredAt > 0) revert IssuerAlreadyRegistered();
        
        issuerInfo[issuer] = IssuerInfo({
            name: name,
            did: did,
            active: true,
            registeredAt: block.timestamp,
            metadataURI: metadataURI
        });
        
        registeredIssuers.push(issuer);
        
        emit IssuerRegistered(issuer, name, did);
    }
    
    /**
     * @dev Update issuer information
     */
    function updateIssuer(
        address issuer,
        string calldata name,
        string calldata did,
        bool active,
        string calldata metadataURI
    ) external onlyRole(ADMIN_ROLE) {
        if (issuerInfo[issuer].registeredAt == 0) revert IssuerNotRegistered();
        
        issuerInfo[issuer].name = name;
        issuerInfo[issuer].did = did;
        issuerInfo[issuer].active = active;
        issuerInfo[issuer].metadataURI = metadataURI;
        
        emit IssuerUpdated(issuer, name, did, active);
    }
    
    /**
     * @dev Approve a domain for RiST issuance
     */
    function approveDomain(string calldata domain) external onlyRole(ADMIN_ROLE) {
        if (bytes(domain).length == 0) revert EmptyString();
        if (approvedDomains[domain]) revert DomainAlreadyApproved();
        
        approvedDomains[domain] = true;
        domainList.push(domain);
        
        emit DomainApproved(domain);
    }
    
    /**
     * @dev Revoke a domain
     */
    function revokeDomain(string calldata domain) external onlyRole(ADMIN_ROLE) {
        if (!approvedDomains[domain]) revert DomainNotApproved();
        
        approvedDomains[domain] = false;
        
        emit DomainRevoked(domain);
    }
    
    /**
     * @dev Get total reputation score across all registered contracts
     */
    function getTotalReputationScore(
        address holder,
        string calldata domain
    ) external view returns (uint256) {
        uint256 totalScore = 0;
        
        for (uint256 i = 0; i < ristContracts.length; i++) {
            address contractAddr = ristContracts[i];
            
            if (registeredContracts[contractAddr] && contractInfo[contractAddr].active) {
                try ReputationSplittingToken(contractAddr).getValidRiSTsByDomain(holder, domain) 
                    returns (uint256[] memory validTokens) {
                    totalScore += validTokens.length;
                } catch {
                    // Skip contracts that don't implement the interface properly
                    continue;
                }
            }
        }
        
        return totalScore;
    }
    
    /**
     * @dev Get all RiSTs for holder across all contracts
     */
    function getAllRiSTsForHolder(
        address holder,
        string calldata domain
    ) external view returns (uint256[] memory tokenIds, address[] memory contracts) {
        uint256 totalTokens = 0;
        
        // First pass: count total tokens
        for (uint256 i = 0; i < ristContracts.length; i++) {
            address contractAddr = ristContracts[i];
            
            if (registeredContracts[contractAddr] && contractInfo[contractAddr].active) {
                try ReputationSplittingToken(contractAddr).getValidRiSTsByDomain(holder, domain) 
                    returns (uint256[] memory validTokens) {
                    totalTokens += validTokens.length;
                } catch {
                    continue;
                }
            }
        }
        
        // Second pass: collect tokens
        tokenIds = new uint256[](totalTokens);
        contracts = new address[](totalTokens);
        uint256 index = 0;
        
        for (uint256 i = 0; i < ristContracts.length; i++) {
            address contractAddr = ristContracts[i];
            
            if (registeredContracts[contractAddr] && contractInfo[contractAddr].active) {
                try ReputationSplittingToken(contractAddr).getValidRiSTsByDomain(holder, domain) 
                    returns (uint256[] memory validTokens) {
                    for (uint256 j = 0; j < validTokens.length; j++) {
                        tokenIds[index] = validTokens[j];
                        contracts[index] = contractAddr;
                        index++;
                    }
                } catch {
                    continue;
                }
            }
        }
    }
    
    /**
     * @dev Get all registered contracts
     */
    function getRegisteredContracts() external view returns (address[] memory) {
        uint256 activeCount = 0;
        
        // Count active contracts
        for (uint256 i = 0; i < ristContracts.length; i++) {
            if (registeredContracts[ristContracts[i]] && contractInfo[ristContracts[i]].active) {
                activeCount++;
            }
        }
        
        // Collect active contracts
        address[] memory activeContracts = new address[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < ristContracts.length; i++) {
            if (registeredContracts[ristContracts[i]] && contractInfo[ristContracts[i]].active) {
                activeContracts[index] = ristContracts[i];
                index++;
            }
        }
        
        return activeContracts;
    }
    
    /**
     * @dev Get all registered issuers
     */
    function getRegisteredIssuers() external view returns (address[] memory) {
        uint256 activeCount = 0;
        
        // Count active issuers
        for (uint256 i = 0; i < registeredIssuers.length; i++) {
            if (issuerInfo[registeredIssuers[i]].active) {
                activeCount++;
            }
        }
        
        // Collect active issuers
        address[] memory activeIssuers = new address[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < registeredIssuers.length; i++) {
            if (issuerInfo[registeredIssuers[i]].active) {
                activeIssuers[index] = registeredIssuers[i];
                index++;
            }
        }
        
        return activeIssuers;
    }
    
    /**
     * @dev Get all approved domains
     */
    function getApprovedDomains() external view returns (string[] memory) {
        uint256 activeCount = 0;
        
        // Count active domains
        for (uint256 i = 0; i < domainList.length; i++) {
            if (approvedDomains[domainList[i]]) {
                activeCount++;
            }
        }
        
        // Collect active domains
        string[] memory activeDomains = new string[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < domainList.length; i++) {
            if (approvedDomains[domainList[i]]) {
                activeDomains[index] = domainList[i];
                index++;
            }
        }
        
        return activeDomains;
    }
    
    /**
     * @dev Emergency pause
     */
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }
}