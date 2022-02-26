//SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./libraries/NFTDescriptor.sol";
import "./libraries/utils.sol";
import "../interfaces/ITrueFreezeGovernor.sol";

/// @title NonFungiblePositionManager contract
/// @author chalex.eth - CharlieDAO
/// @notice Represent position as a NFT

contract NonFungiblePositionManager is ERC721, Ownable {
    address public governorAddress;

    /* ------------------ Constructor --------------*/

    constructor() ERC721("TrueFreeze NFT positions", "TrueFreeze") {}

    /* ------------------ Modifier --------------*/
    modifier onlyGovernor() {
        require(msg.sender == governorAddress, "Only Factory can call");
        _;
    }

    /* ----------- External functions --------------*/

    function setOnlyGovernor(address _governorAddress) external onlyOwner {
        governorAddress = _governorAddress;
    }

    function mint(address _to, uint256 _tokenId) external onlyGovernor {
        _mint(_to, _tokenId);
    }

    function burn(uint256 _tokenId) external onlyGovernor {
        _burn(_tokenId);
    }

    /* ----------- View functions --------------*/

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

        ) = ITrueFreezeGovernor(governorAddress).getPositions(tokenId);

        return
            NFTDescriptor._constructTokenURI(
                _amountLocked,
                _lockingDate,
                _maturityDate
            );
    }
}
