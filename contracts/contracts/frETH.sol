//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract frETH is ERC20, ERC20Burnable, Ownable {
    address public factoryAddress;

    constructor() public ERC20("FrozenETH", "frETH") {}

    // Modifier
    modifier onlyFactory() {
        require(msg.sender == factoryAddress, "Only Factory can call");
        _;
    }

    function setOnlyFactory(address _factoryAddress) public onlyOwner {
        factoryAddress = _factoryAddress;
    }

    function mint(address to, uint256 amount) public onlyFactory {
        _mint(to, amount);
    }

    function burn(address account_, uint256 amount_) public onlyFactory {
        _burn(account_, amount_);
    }
}
