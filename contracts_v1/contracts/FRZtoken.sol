//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @title FRZ token
/// @author chalex.eth - CharlieDAO
/// @notice FRZ token ERC20 contract
contract FRZtoken is ERC20 {
    /* ------------------ Constructor --------------*/

    constructor(uint256 _tokenSupply) public ERC20("FRZ", "FRZ") {
        _mint(msg.sender, _tokenSupply);
    }
}
