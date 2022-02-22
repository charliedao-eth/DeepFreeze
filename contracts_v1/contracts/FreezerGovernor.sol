//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

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

    function burn(uint256) external;

    function ownerOf(uint256) external returns (address);
}

interface IStaking {
    function notifyRewardAmount(address, uint256) external;
}

contract FreezerGovernor is Ownable, ReentrancyGuard {
    uint256 internal constant N_DAYS = 365;
    uint256 internal constant MIN_LOCK_DAYS = 7;
    uint256 internal constant MAX_LOCK_DAYS = 1100;
    uint256 internal constant MAX_UINT = 2**256 - 1;

    /// @dev The token ID position data
    mapping(uint256 => Position) private _positions;

    /// @dev The ID of the next token that will be minted. Skips 0
    uint256 private _nextId = 1;

    struct Position {
        uint256 amountLocked;
        uint256 tokenMinted;
        uint256 lockingDate;
        uint256 maturityDate;
        bool active;
    }

    event lockedWETH(
        address indexed minter,
        uint256 tokenId,
        uint256 amounntLocked,
        uint256 lockingDate,
        uint256 maturityDate
    );

    event withdrawedWETH(
        address indexed withdrawer,
        uint256 tokenId,
        uint256 amountWithdrawed,
        uint256 WethPenalty,
        uint256 frPenalty
    );

    IfrETH private immutable frETH;
    IERC20 private immutable wETH;
    INFT private immutable nftPosition;
    IStaking private immutable stakingContract;

    constructor(
        address _WETHaddress,
        address _frETH,
        address _NFTPosition,
        address _stakingAddress
    ) {
        wETH = IERC20(_WETHaddress);
        frETH = IfrETH(_frETH);
        nftPosition = INFT(_NFTPosition);
        stakingContract = IStaking(_stakingAddress);
        wETH.approve(_stakingAddress, MAX_UINT);
        frETH.approve(_stakingAddress, MAX_UINT);
    }

    // function lock Amount Duration onlyWeth
    function lockWETH(uint256 _amount, uint256 _lockDuration)
        external
        nonReentrant
    {
        require(_amount > 0, "Amount must be more than 0");
        require(
            _lockDuration >= MIN_LOCK_DAYS && _lockDuration <= MAX_LOCK_DAYS,
            "Bad days input"
        );
        bool sent = wETH.transferFrom(msg.sender, address(this), _amount);
        require(sent, "Error in sending WETH");
        uint256 lockingDate = block.timestamp;
        uint256 maturityDate = lockingDate + (_lockDuration * 1 days);
        uint256 tokenToMint = _calculate_frToken(
            _amount,
            (_lockDuration * 1 days)
        );
        _createPosition(
            _amount,
            tokenToMint,
            lockingDate,
            maturityDate,
            _nextId
        );
        _mintToken(tokenToMint);
        nftPosition.mint(
            msg.sender,
            _nextId,
            _amount,
            lockingDate,
            maturityDate
        );

        emit lockedWETH(
            msg.sender,
            _nextId,
            _amount,
            lockingDate,
            maturityDate
        );

        _nextId += 1;
    }

    function withdrawWETH(uint256 _tokenId) external nonReentrant {
        require(
            msg.sender == nftPosition.ownerOf(_tokenId),
            "Not the owner of tokenId"
        );
        require(
            _positions[_tokenId].active = true,
            "Position already withdrawed"
        );

        (
            uint256 amountLocked,
            uint256 tokenMinted,
            uint256 lockingDate,
            uint256 maturityDate,
            bool active
        ) = getPositions(_tokenId);
        uint256 feesToPay = getWethFees(_tokenId);
        _positions[_tokenId].active = false;
        _positions[_tokenId].amountLocked = 0;

        nftPosition.burn(_tokenId);
        uint256 progress = getProgress(_tokenId);
        if (progress >= 100) {
            wETH.approve(msg.sender, amountLocked);
            wETH.transfer(msg.sender, amountLocked);
            emit withdrawedWETH(msg.sender, _tokenId, amountLocked, 0, 0);
        } else if (progress < 100) {
            uint256 sendToUser = amountLocked - feesToPay;
            wETH.approve(msg.sender, sendToUser);
            wETH.transfer(msg.sender, sendToUser);
            stakingContract.notifyRewardAmount(address(wETH), feesToPay);

            uint256 frPenalty = getUnlockCost(_tokenId);
            frETH.transferFrom(msg.sender, address(this), frPenalty);

            if (progress <= 67) {
                (uint256 toSend, uint256 toBurn) = _calculateBurnAndSend(
                    tokenMinted,
                    frPenalty
                );
                frETH.burn(address(this), toBurn);
                stakingContract.notifyRewardAmount(address(frETH), toSend);
            } else {
                frETH.burn(address(this), frPenalty);
            }
            emit withdrawedWETH(
                msg.sender,
                _tokenId,
                amountLocked,
                feesToPay,
                frPenalty
            );
        }
    }

    // Internal functions

    function _createPosition(
        uint256 _amount,
        uint256 _tokenMinted,
        uint256 _lockingDate,
        uint256 _maturityDate,
        uint256 tokenId
    ) private {
        _positions[tokenId] = Position({
            amountLocked: _amount,
            tokenMinted: _tokenMinted,
            lockingDate: _lockingDate,
            maturityDate: _maturityDate,
            active: true
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
            uint256,
            bool
        )
    {
        return (
            _positions[tokenId].amountLocked,
            _positions[tokenId].tokenMinted,
            _positions[tokenId].lockingDate,
            _positions[tokenId].maturityDate,
            _positions[tokenId].active
        );
    }

    function getProgress(uint256 tokenId) public view returns (uint256) {
        (, , uint256 _lockingDate, uint256 _maturityDate, ) = getPositions(
            tokenId
        );
        return _calculateProgress(block.timestamp, _lockingDate, _maturityDate);
    }

    function getUnlockCost(uint256 _tokenId) public view returns (uint256) {
        uint256 _progress = getProgress(_tokenId);
        (, uint256 _TokenMinted, , , ) = getPositions(_tokenId);
        return _calculateWithdrawCost(_progress, _TokenMinted);
    }

    function getWethFees(uint256 _tokenId) public view returns (uint256) {
        (uint256 amountLocked, , , , ) = getPositions(_tokenId);
        uint256 progress = getProgress(_tokenId);
        if (progress >= 100) {
            return 0;
        } else {
            return _calculateWethFees(amountLocked);
        }
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
        uint256 _maturityDate
    ) internal pure returns (uint256) {
        return
            (100 * (_nBlock - _lockingDate)) / (_maturityDate - _lockingDate);
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

    function _calculateWethFees(uint256 _lockedAmount)
        internal
        pure
        returns (uint256)
    {
        return (_lockedAmount * 25) / 10000;
    }

    function _calculateBurnAndSend(uint256 _tokenMinted, uint256 _penaltyPaid)
        internal
        pure
        returns (uint256, uint256)
    {
        uint256 toSend = (_penaltyPaid - _tokenMinted) / 2;
        uint256 toBurn = _tokenMinted + (_penaltyPaid - _tokenMinted) / 2;
        return (toSend, toBurn);
    }
}
