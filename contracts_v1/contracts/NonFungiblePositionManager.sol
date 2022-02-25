//SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./libraries/NFTDescriptor.sol";
import "./libraries/utils.sol";

interface IGovernor {
    function getPositions(uint256)
        external
        view
        returns (
            uint256,
            uint256,
            uint256,
            uint256,
            bool
        );
}

contract NonFungiblePositionManager is ERC721, Ownable {
    address public governorAddress;
    IGovernor private IGov;

    constructor() ERC721("TrueFreeze NFT positions", "TrueFreeze") {}

    // Modifier
    modifier onlyGovernor() {
        require(msg.sender == governorAddress, "Only Factory can call");
        _;
    }

    function setOnlyGovernor(address _governorAddress) external onlyOwner {
        governorAddress = _governorAddress;
        IGov = IGovernor(_governorAddress);
    }

    function mint(address _to, uint256 _tokenId) external onlyGovernor {
        _mint(_to, _tokenId);
    }

    function burn(uint256 _tokenId) external onlyGovernor {
        _burn(_tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721)
        returns (string memory)
    {
        require(_exists(tokenId));
        (
            uint256 _amountLocked,
            ,
            uint256 _lockingDate,
            uint256 _maturityDate,

        ) = IGov.getPositions(tokenId);

        return
            NFTDescriptor._constructTokenURI(
                _amountLocked,
                _lockingDate,
                _maturityDate
            );
    }

    // Internal
}
