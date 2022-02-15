//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract FRZtoken is ERC20 {
    constructor(uint256 _tokenSupply) public ERC20("FRZ", "FRZ") {
        _mint(msg.sender, _tokenSupply);
    }
}
