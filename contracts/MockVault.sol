// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract MockVault {
    uint256 public health = 100;
    uint256 public lastAttackTimestamp;
    uint256 public constant WINDOW_SECONDS = 2;

    event AttackSimulated(address indexed attacker, uint256 newHealth, uint256 timestamp);
    event EmergencyActionExecuted(address indexed guardian, uint256 restoredHealth, uint256 timestamp);

    error TooHealthy();
    error TooLate();

    function simulateAttack(uint256 damage) external {
        if (damage == 0 || damage > health) {
            damage = 40;
        }

        health -= damage;
        lastAttackTimestamp = block.timestamp;

        emit AttackSimulated(msg.sender, health, block.timestamp);
    }

    function emergencyAction() external {
        if (health >= 80) revert TooHealthy();
        if (block.timestamp > lastAttackTimestamp + WINDOW_SECONDS) revert TooLate();

        health = 100;
        emit EmergencyActionExecuted(msg.sender, health, block.timestamp);
    }
}
