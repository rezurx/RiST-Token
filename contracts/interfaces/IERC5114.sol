// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

/**
 * @title EIP-5114 Soulbound Token Standard
 * @dev Interface for soulbound tokens that cannot be transferred
 */
interface IERC5114 is IERC721 {
    /**
     * @dev Emitted when a soulbound token is issued.
     * @param from The issuer of the token
     * @param to The recipient of the token
     * @param tokenId The token ID
     */
    event Issued(address indexed from, address indexed to, uint256 indexed tokenId);

    /**
     * @dev Returns true if the token is soulbound (non-transferable)
     * @param tokenId The token ID to check
     * @return True if the token is soulbound
     */
    function isSoulbound(uint256 tokenId) external view returns (bool);
}