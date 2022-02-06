//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract frETH is ERC20, ERC20Burnable, Ownable {
    address public governorAddress;

    constructor() public ERC20("FrozenETH", "frETH") {}

    // Modifier
    modifier onlyGovernor() {
        require(msg.sender == governorAddress, "Only Factory can call");
        _;
    }

    function setOnlyGovernor(address _governorAddress) external onlyOwner {
        governorAddress = _governorAddress;
    }

    function mint(address to, uint256 amount) external onlyGovernor {
        _mint(to, amount);
    }

    function burn(address account_, uint256 amount_) external onlyGovernor {
        _burn(account_, amount_);
    }
}
