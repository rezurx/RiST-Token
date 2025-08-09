// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/governance/TimelockController.sol";

/**
 * @title RiSTTimelock
 * @dev 7-day timelock for RiST contract upgrades
 */
contract RiSTTimelock is TimelockController {
    /**
     * @dev Constructor for RiSTTimelock
     * @param minDelay Minimum delay for operations (7 days = 604800 seconds)
     * @param proposers Array of addresses that can propose operations
     * @param executors Array of addresses that can execute operations
     * @param admin Address that can manage the timelock (should be address(0) for full decentralization)
     */
    constructor(
        uint256 minDelay,
        address[] memory proposers,
        address[] memory executors,
        address admin
    ) TimelockController(minDelay, proposers, executors, admin) {}
}