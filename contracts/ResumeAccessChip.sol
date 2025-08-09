// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title ResumeAccessChip
 * @dev ERC-1155 chips for time-limited or view-count-limited access to RiST résumés
 * Implements Ephemeral Rights Tokens (ERTs) as per specification
 */
contract ResumeAccessChip is ERC1155, Ownable, Pausable {
    uint256 private _chipIdCounter;
    
    struct ChipData {
        address minter;         // Who created this chip
        uint256 expiry;         // Expiration timestamp (0 = no expiry)
        uint256 maxViews;       // Maximum number of views (0 = unlimited)
        uint256 currentViews;   // Current view count
        uint256 scopeTokenId;   // Optional RiST tokenId scope (0 = all RiSTs)
        string resumeURI;       // URI to the résumé data
        bool burned;            // Chip burn status
    }
    
    mapping(uint256 => ChipData) public chips;
    mapping(address => uint256[]) public holderChips;
    
    event ChipMinted(
        address indexed minter,
        uint256 indexed chipId,
        uint256 expiry,
        uint256 maxViews,
        uint256 scopeTokenId
    );
    
    event ChipBurned(
        uint256 indexed chipId,
        address indexed burner,
        address indexed viewer
    );
    
    event ResumeViewed(
        uint256 indexed chipId,
        address indexed viewer,
        uint256 viewCount
    );
    
    error ChipExpired();
    error ChipExhausted();
    error ChipAlreadyBurned();
    error ChipNotExists();
    error NotAuthorized();
    error ZeroAddress();
    
    constructor(string memory _uri) ERC1155(_uri) Ownable(msg.sender) {}
    
    /**
     * @dev Mint access chip
     * @param to Address to mint chip to
     * @param expiry Expiration timestamp (0 = no expiry)
     * @param maxViews Maximum views (0 = unlimited)
     * @param scopeTokenId Optional RiST scope (0 = all RiSTs)
     * @param resumeURI URI to résumé data
     * @param amount Number of chips to mint
     */
    function mintChip(
        address to,
        uint256 expiry,
        uint256 maxViews,
        uint256 scopeTokenId,
        string calldata resumeURI,
        uint256 amount
    ) external whenNotPaused returns (uint256) {
        if (to == address(0)) revert ZeroAddress();
        
        uint256 chipId = _chipIdCounter;
        _chipIdCounter++;
        
        chips[chipId] = ChipData({
            minter: msg.sender,
            expiry: expiry,
            maxViews: maxViews,
            currentViews: 0,
            scopeTokenId: scopeTokenId,
            resumeURI: resumeURI,
            burned: false
        });
        
        holderChips[to].push(chipId);
        
        _mint(to, chipId, amount, "");
        
        emit ChipMinted(msg.sender, chipId, expiry, maxViews, scopeTokenId);
        
        return chipId;
    }
    
    /**
     * @dev Burn chip and verify access for résumé viewing
     * @param chipId The chip ID to burn
     * @param viewer Address of the viewer
     */
    function burnAndVerifyAccess(
        uint256 chipId,
        address viewer
    ) external returns (bool) {
        if (!_chipExists(chipId)) revert ChipNotExists();
        
        ChipData storage chip = chips[chipId];
        
        // Check if chip is already burned
        if (chip.burned) revert ChipAlreadyBurned();
        
        // Check expiry
        if (chip.expiry > 0 && block.timestamp > chip.expiry) {
            revert ChipExpired();
        }
        
        // Check view limit
        if (chip.maxViews > 0 && chip.currentViews >= chip.maxViews) {
            revert ChipExhausted();
        }
        
        // Authorization check: must be chip holder or minter
        if (balanceOf(msg.sender, chipId) == 0 && msg.sender != chip.minter) {
            revert NotAuthorized();
        }
        
        // Burn one chip
        _burn(msg.sender, chipId, 1);
        
        // Update view count
        chip.currentViews++;
        
        // Mark as burned if this was the last chip or view limit reached
        if (balanceOf(msg.sender, chipId) == 0 || 
            (chip.maxViews > 0 && chip.currentViews >= chip.maxViews)) {
            chip.burned = true;
        }
        
        emit ChipBurned(chipId, msg.sender, viewer);
        emit ResumeViewed(chipId, viewer, chip.currentViews);
        
        return true;
    }
    
    /**
     * @dev Check if chip is valid for viewing
     * @param chipId The chip ID to check
     */
    function isChipValid(uint256 chipId) external view returns (bool) {
        if (!_chipExists(chipId)) return false;
        
        ChipData memory chip = chips[chipId];
        
        // Check if burned
        if (chip.burned) return false;
        
        // Check expiry
        if (chip.expiry > 0 && block.timestamp > chip.expiry) return false;
        
        // Check view limit
        if (chip.maxViews > 0 && chip.currentViews >= chip.maxViews) return false;
        
        return true;
    }
    
    /**
     * @dev Get chip data
     * @param chipId The chip ID
     */
    function getChipData(uint256 chipId) external view returns (ChipData memory) {
        if (!_chipExists(chipId)) revert ChipNotExists();
        return chips[chipId];
    }
    
    /**
     * @dev Get all chips for a holder
     * @param holder The holder address
     */
    function getHolderChips(address holder) external view returns (uint256[] memory) {
        return holderChips[holder];
    }
    
    /**
     * @dev Get valid chips for a holder
     * @param holder The holder address
     */
    function getValidChips(address holder) external view returns (uint256[] memory) {
        uint256[] memory allChips = holderChips[holder];
        uint256[] memory validChips = new uint256[](allChips.length);
        uint256 validCount = 0;
        
        for (uint256 i = 0; i < allChips.length; i++) {
            if (this.isChipValid(allChips[i]) && balanceOf(holder, allChips[i]) > 0) {
                validChips[validCount] = allChips[i];
                validCount++;
            }
        }
        
        // Resize array
        uint256[] memory result = new uint256[](validCount);
        for (uint256 i = 0; i < validCount; i++) {
            result[i] = validChips[i];
        }
        
        return result;
    }
    
    /**
     * @dev Override URI to return chip-specific metadata
     */
    function uri(uint256 chipId) public view override returns (string memory) {
        if (!_chipExists(chipId)) revert ChipNotExists();
        return chips[chipId].resumeURI;
    }
    
    /**
     * @dev Check if chip exists
     */
    function _chipExists(uint256 chipId) internal view returns (bool) {
        return chips[chipId].minter != address(0);
    }
    
    /**
     * @dev Override _update to track chip movements
     */
    function _update(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts
    ) internal override {
        super._update(from, to, ids, amounts);
        
        // Update holder tracking when transferring
        if (from != address(0) && to != address(0)) {
            for (uint256 i = 0; i < ids.length; i++) {
                uint256 chipId = ids[i];
                
                // Add to new holder's list if not already there
                bool foundInNewHolder = false;
                for (uint256 j = 0; j < holderChips[to].length; j++) {
                    if (holderChips[to][j] == chipId) {
                        foundInNewHolder = true;
                        break;
                    }
                }
                if (!foundInNewHolder) {
                    holderChips[to].push(chipId);
                }
            }
        }
    }
    
    /**
     * @dev Emergency pause
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Set base URI
     */
    function setURI(string calldata newURI) external onlyOwner {
        _setURI(newURI);
    }
}