// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NFTPosition is ERC721URIStorage, Ownable {
    address public governorAddress;

    constructor() ERC721("Freezer", "Freezer") {}

    // Modifier
    modifier onlyGovernor() {
        require(msg.sender == governorAddress, "Only Factory can call");
        _;
    }

    function setOnlyGovernor(address _governorAddress) external onlyOwner {
        governorAddress = _governorAddress;
    }

    function mint(
        address _to,
        uint256 _tokenId,
        uint256 _amountLocked,
        uint256 _lockingDate,
        uint256 _maturityDate
    ) external onlyGovernor {
        _safeMint(_to, _tokenId);
    }

    function burn(uint256 _tokenId) external onlyGovernor {
        _burn(_tokenId);
    }
}
