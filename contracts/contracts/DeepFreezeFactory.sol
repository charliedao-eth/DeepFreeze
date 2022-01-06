//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;
import "./DeepFreeze.sol";

contract DeepFreezeFactory {
    address public creatorOwner;
    DeepFreeze[] public deployedFreezer;
    mapping(address => DeepFreeze[]) public userFreezer;
    event FreezerDeployed(address from, address freezerAddress);

    constructor() {
        creatorOwner = msg.sender;
    }

    function createDeepFreeze(string memory hint_, bytes32 password_) public {
        DeepFreeze new_freezer_address = new DeepFreeze(
            msg.sender,
            hint_,
            password_
        );
        userFreezer[msg.sender].push(new_freezer_address);
        deployedFreezer.push(new_freezer_address);
        emit FreezerDeployed(msg.sender, address(new_freezer_address));
    }
}
