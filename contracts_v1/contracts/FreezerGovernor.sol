//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IfrETH is IERC20 {
    function mint(address, uint256) external;

    function burn(address, uint256) external;
}

interface INFT {
    function mint(
        address,
        uint256,
        uint256,
        uint256,
        uint256
    ) external;
}

contract FreezerGovernor is Ownable {
    uint256 internal constant N_DAYS = 365;
    uint256 internal constant PROGRESS_THRESHOLD = 67;
    uint256 internal constant MIN_LOCK_DAYS = 7;
    uint256 internal constant MAX_LOCK_DAYS = 1100;

    /// @dev The token ID position data
    mapping(uint256 => Position) private _positions;

    /// @dev The ID of the next token that will be minted. Skips 0
    uint176 private _nextId = 1;

    struct Position {
        uint256 amountLocked;
        uint256 tokenMinted;
        uint256 lockingDate;
        uint256 unlockingDate;
    }

    IfrETH public frETH;
    IERC20 public wETH;
    INFT public nftPosition;

    constructor(
        address _WETHaddress,
        address _frETH,
        address _NFTPosition
    ) {
        wETH = IERC20(_WETHaddress);
        frETH = IfrETH(_frETH);
        nftPosition = INFT(_NFTPosition);
    }

    // function lock Amount Duration onlyWeth
    function lock(uint256 _amount, uint256 _lockDuration) public {
        require(_amount > 0, "Amount must be more than 0");
        require(
            _lockDuration > MIN_LOCK_DAYS && _lockDuration < MAX_LOCK_DAYS,
            "Bad days input"
        );
        bool sent = wETH.transferFrom(msg.sender, address(this), _amount);
        require(sent, "Error in sending WETH");
        uint256 lockingDate = block.timestamp;
        uint256 unlockingDate = lockingDate + (_lockDuration * 1 days);
        uint256 tokenToMint = _calculate_frToken(
            _amount,
            (_lockDuration * 1 days)
        );
        _createPosition(
            _amount,
            tokenToMint,
            lockingDate,
            unlockingDate,
            _nextId
        );
        _mintToken(tokenToMint);
        nftPosition.mint(
            msg.sender,
            _nextId,
            _amount,
            lockingDate,
            unlockingDate
        );
        _nextId += 1;
    } // function create position

    // Internal functions

    function _createPosition(
        uint256 _amount,
        uint256 _tokenMinted,
        uint256 _lockingDate,
        uint256 _unlockingDate,
        uint256 tokenId
    ) private {
        _positions[tokenId] = Position({
            amountLocked: _amount,
            tokenMinted: _tokenMinted,
            lockingDate: _lockingDate,
            unlockingDate: _unlockingDate
        });
    }

    function _mintToken(uint256 _tokenToMint) private {
        frETH.mint(msg.sender, _tokenToMint);
    }

    // View functions

    function getPositions(uint256 tokenId)
        public
        view
        returns (
            uint256,
            uint256,
            uint256,
            uint256
        )
    {
        return (
            _positions[tokenId].amountLocked,
            _positions[tokenId].tokenMinted,
            _positions[tokenId].lockingDate,
            _positions[tokenId].unlockingDate
        );
    }

    function getProgress(uint256 tokenId) public view returns (uint256) {
        (, , uint256 _lockingDate, uint256 _unlockingDate) = getPositions(
            tokenId
        );
        return
            _calculateProgress(block.timestamp, _lockingDate, _unlockingDate);
    }

    function getUnlockCost(uint256 _tokenId) public view returns (uint256) {
        uint256 _progress = getProgress(_tokenId);
        (, uint256 _TokenMinted, , ) = getPositions(_tokenId);
        return _calculateWithdrawCost(_progress, _TokenMinted);
    }

    function getFees(uint256 _tokenId) public view returns (uint256) {
        (uint256 amountLocked, , , ) = getPositions(_tokenId);
        return _calculateFees(amountLocked);
    }

    // Pure functions

    /// @notice Get the amount of frAsset that will be minted
    /// @return Return the amount of frAsset that will be minted
    function _calculate_frToken(uint256 _lockedAmount, uint256 _timeToLock)
        internal
        pure
        returns (uint256)
    {
        uint256 token = (_timeToLock * _lockedAmount) / (N_DAYS * 1 days);
        return token;
    }

    function _calculateProgress(
        uint256 _nBlock,
        uint256 _lockingDate,
        uint256 _unlockingDate
    ) internal pure returns (uint256) {
        return
            (100 * (_nBlock - _lockingDate)) / (_unlockingDate - _lockingDate);
    }

    function _calculateWithdrawCost(uint256 _progress, uint256 _frToken)
        internal
        pure
        returns (uint256)
    {
        uint256 unlockCost;
        if (_progress >= 100) {
            unlockCost = 0;
        } else if (_progress < 67) {
            unlockCost =
                _frToken +
                ((((20 * _frToken) / 100) * (100 - ((_progress * 3) / 2))) /
                    100);
        } else {
            unlockCost = (_frToken * (100 - ((_progress - 67) * 3))) / 100;
        }
        return unlockCost;
    }

    function _calculateFees(uint256 _lockedAmount)
        internal
        pure
        returns (uint256)
    {
        return (_lockedAmount * 25) / 10000;
    }
}
