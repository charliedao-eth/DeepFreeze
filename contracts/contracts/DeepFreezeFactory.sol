//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;
import "./DeepFreeze.sol";

contract DeepFreezeFactory {
    address public creatorOwner;
    address[] public userAddress;
    DeepFreeze[] public deployedDeepFreeze;
    mapping(address => DeepFreeze[]) public userToDeepFreeze;
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
        userAddress.push(msg.sender);
        userToDeepFreeze[msg.sender].push(new_freezer_address);
        deployedDeepFreeze.push(new_freezer_address);
        emit FreezerDeployed(msg.sender, address(new_freezer_address));
    }
}
