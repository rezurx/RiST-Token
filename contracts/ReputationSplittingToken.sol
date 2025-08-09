// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts-upgradeable/token/ERC721/ERC721Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/cryptography/EIP712Upgradeable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "./interfaces/IERC5114.sol";

/**
 * @title ReputationSplittingToken (RiST)
 * @dev Non-transferable, domain-specific reputation credentials
 * Implements EIP-5114 Soulbound Token Standard with UUPS upgradability
 */
contract ReputationSplittingToken is 
    ERC721Upgradeable,
    AccessControlUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable,
    EIP712Upgradeable,
    IERC5114
{
    using ECDSA for bytes32;

    bytes32 public constant ISSUER_ROLE = keccak256("ISSUER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");

    // EIP-712 type hash for metadata updates
    bytes32 private constant METADATA_UPDATE_TYPEHASH = 
        keccak256("MetadataUpdate(uint256 tokenId,string metadataURI,bytes32 contentHash,uint256 nonce)");

    uint256 private _tokenIdCounter;
    
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
    
    mapping(uint256 => RiST) public rists;
    mapping(address => mapping(string => uint256[])) public holdersByDomain;
    mapping(address => bool) public whitelistedIssuers;
    mapping(address => uint256) public nonces;

    // Events as per specification
    event RiSTIssued(uint256 indexed tokenId, address indexed to, string domain);
    event RiSTRevoked(uint256 indexed tokenId, address indexed revoker);
    event IssuerWhitelisted(address indexed issuer);
    event MetadataUpdated(uint256 indexed tokenId, string newURI);

    error SoulboundTokenTransferAttempt();
    error TokenNotExists();
    error NotAuthorized();
    error IssuerNotWhitelisted();
    error TokenAlreadyRevoked();
    error InvalidSignature();
    error ZeroAddress();
    error EmptyDomain();

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(
        string memory name,
        string memory symbol,
        address admin
    ) public initializer {
        __ERC721_init(name, symbol);
        __AccessControl_init();
        __Pausable_init();
        __UUPSUpgradeable_init();
        __EIP712_init("ReputationSplittingToken", "1");

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(UPGRADER_ROLE, admin);
    }

    /**
     * @dev Mint RiST to holder - only by whitelisted issuers
     */
    function mintRiST(
        address to,
        RiST calldata data
    ) external onlyRole(ISSUER_ROLE) whenNotPaused returns (uint256) {
        if (to == address(0)) revert ZeroAddress();
        if (!whitelistedIssuers[msg.sender]) revert IssuerNotWhitelisted();
        if (bytes(data.domain).length == 0) revert EmptyDomain();
        
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        
        _safeMint(to, tokenId);
        
        // Store RiST data with current timestamp
        rists[tokenId] = RiST({
            domain: data.domain,
            issuer: data.issuer,
            level: data.level,
            issuedAt: block.timestamp,
            validUntil: data.validUntil,
            revoked: false,
            metadataURI: data.metadataURI,
            contentHash: data.contentHash
        });
        
        holdersByDomain[to][data.domain].push(tokenId);
        
        emit RiSTIssued(tokenId, to, data.domain);
        emit Issued(msg.sender, to, tokenId);
        
        return tokenId;
    }

    /**
     * @dev Revoke RiST - only by original issuer or admin
     */
    function revokeRiST(uint256 tokenId) external {
        if (_ownerOf(tokenId) == address(0)) revert TokenNotExists();
        
        RiST storage rist = rists[tokenId];
        
        // Check authorization: must be issuer or admin
        bool isOriginalIssuer = keccak256(abi.encodePacked(rist.issuer)) == 
                               keccak256(abi.encodePacked(_getIssuerString(msg.sender)));
        bool isAdmin = hasRole(ADMIN_ROLE, msg.sender);
        
        if (!isOriginalIssuer && !isAdmin) revert NotAuthorized();
        if (rist.revoked) revert TokenAlreadyRevoked();
        
        rist.revoked = true;
        
        emit RiSTRevoked(tokenId, msg.sender);
    }

    /**
     * @dev Check if RiST is valid (not revoked, not expired)
     */
    function isValid(uint256 tokenId) public view returns (bool) {
        if (_ownerOf(tokenId) == address(0)) return false;
        
        RiST memory rist = rists[tokenId];
        
        if (rist.revoked) return false;
        if (rist.validUntil > 0 && block.timestamp > rist.validUntil) return false;
        
        return true;
    }

    /**
     * @dev Get RiST data
     */
    function getRiST(uint256 tokenId) public view returns (RiST memory) {
        if (_ownerOf(tokenId) == address(0)) revert TokenNotExists();
        return rists[tokenId];
    }

    /**
     * @dev Update metadata with holder approval signature
     */
    function updateMetadata(
        uint256 tokenId,
        string calldata newURI,
        bytes32 newHash,
        bytes calldata signature
    ) external onlyRole(ISSUER_ROLE) {
        if (_ownerOf(tokenId) == address(0)) revert TokenNotExists();
        
        address holder = ownerOf(tokenId);
        
        // Verify holder signature
        bytes32 structHash = keccak256(abi.encode(
            METADATA_UPDATE_TYPEHASH,
            tokenId,
            keccak256(bytes(newURI)),
            newHash,
            nonces[holder]++
        ));
        
        bytes32 hash = _hashTypedDataV4(structHash);
        address signer = hash.recover(signature);
        
        if (signer != holder) revert InvalidSignature();
        
        // Update metadata
        rists[tokenId].metadataURI = newURI;
        rists[tokenId].contentHash = newHash;
        
        emit MetadataUpdated(tokenId, newURI);
    }

    /**
     * @dev Get all valid RiSTs for holder in specific domain
     */
    function getValidRiSTsByDomain(
        address holder,
        string calldata domain
    ) external view returns (uint256[] memory) {
        uint256[] memory holderTokens = holdersByDomain[holder][domain];
        uint256[] memory validTokens = new uint256[](holderTokens.length);
        uint256 validCount = 0;
        
        for (uint256 i = 0; i < holderTokens.length; i++) {
            if (isValid(holderTokens[i])) {
                validTokens[validCount] = holderTokens[i];
                validCount++;
            }
        }
        
        // Resize array to actual valid count
        uint256[] memory result = new uint256[](validCount);
        for (uint256 i = 0; i < validCount; i++) {
            result[i] = validTokens[i];
        }
        
        return result;
    }

    /**
     * @dev Whitelist issuer
     */
    function setIssuerWhitelist(
        address issuer,
        bool whitelisted
    ) external onlyRole(ADMIN_ROLE) {
        whitelistedIssuers[issuer] = whitelisted;
        
        if (whitelisted) {
            _grantRole(ISSUER_ROLE, issuer);
        } else {
            _revokeRole(ISSUER_ROLE, issuer);
        }
        
        emit IssuerWhitelisted(issuer);
    }

    /**
     * @dev EIP-5114: Check if token is soulbound
     */
    function isSoulbound(uint256 tokenId) external view override returns (bool) {
        return _ownerOf(tokenId) != address(0);
    }

    /**
     * @dev Override transfer functions to make tokens soulbound
     */
    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal virtual override returns (address) {
        address from = _ownerOf(tokenId);
        
        if (from != address(0) && to != address(0)) {
            revert SoulboundTokenTransferAttempt();
        }
        
        return super._update(to, tokenId, auth);
    }

    /**
     * @dev Disable approve - soulbound tokens cannot be approved
     */
    function approve(address, uint256) public pure override(ERC721Upgradeable, IERC721) {
        revert SoulboundTokenTransferAttempt();
    }

    /**
     * @dev Disable setApprovalForAll - soulbound tokens cannot be approved
     */
    function setApprovalForAll(address, bool) public pure override(ERC721Upgradeable, IERC721) {
        revert SoulboundTokenTransferAttempt();
    }

    /**
     * @dev Override tokenURI to return RiST metadata
     */
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        if (_ownerOf(tokenId) == address(0)) revert TokenNotExists();
        return rists[tokenId].metadataURI;
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

    /**
     * @dev UUPS upgrade authorization
     */
    function _authorizeUpgrade(address newImplementation) internal override onlyRole(UPGRADER_ROLE) {}

    /**
     * @dev Helper function to get issuer string representation
     */
    function _getIssuerString(address addr) internal pure returns (string memory) {
        return string(abi.encodePacked(addr));
    }

    /**
     * @dev Support interfaces
     */
    function supportsInterface(bytes4 interfaceId)
        public view override(ERC721Upgradeable, AccessControlUpgradeable, IERC165) returns (bool) {
        return interfaceId == type(IERC5114).interfaceId || super.supportsInterface(interfaceId);
    }
}