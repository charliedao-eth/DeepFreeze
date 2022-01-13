//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "./DeepFreeze.sol";

/// @title DeepFreezeFactory
/// @author CharlieDAO

interface IDeepFreeze {
    function getLockedAmount() external view returns (uint256);

    function getLockingDate() external view returns (uint256);

    function getTimeToLock() external view returns (uint256);

    function getStatus() external view returns (uint256);

    function freezerOwner() external view returns (address);
}

interface IERC20 {
    function mint(address, uint256) external;
}

contract DeepFreezeFactory {
    address public creatorOwner;
    address[] public userAddress;
    address public frETH;
    DeepFreeze[] public deployedDeepFreeze;
    uint256 internal constant N_DAYS = 365;
    uint256 internal constant PROGRESS_THRESHOLD = 67;
    mapping(address => DeepFreeze[]) public userToDeepFreeze;
    mapping(address => uint256) internal frTokenMinted;
    event FreezerDeployed(address from, address freezerAddress);

    constructor(address _frETH) {
        creatorOwner = msg.sender;
        frETH = _frETH;
    }

    function createDeepFreeze(string memory hint_, bytes32 password_) public {
        DeepFreeze new_freezer_address = new DeepFreeze(
            address(this),
            msg.sender,
            hint_,
            password_
        );
        userAddress.push(msg.sender);
        userToDeepFreeze[msg.sender].push(new_freezer_address);
        deployedDeepFreeze.push(new_freezer_address);
        emit FreezerDeployed(msg.sender, address(new_freezer_address));
    }

    function isDeepFreeze(address _deepFreezeAddress)
        public
        view
        returns (bool)
    {
        for (uint256 idx = 0; idx < deployedDeepFreeze.length; idx++) {
            if (address(deployedDeepFreeze[idx]) == _deepFreezeAddress) {
                return true;
            }
        }
        return false;
    }

    function rewardLocking(address _deepFreezeAddress) public {
        require(
            isDeepFreeze(_deepFreezeAddress),
            "Caller is not a registered DeepFreeze"
        );
        uint256 status = IDeepFreeze(_deepFreezeAddress).getStatus();
        require(status == 1, "DeepFreeze not locked");
        uint256 lockedAmount = IDeepFreeze(_deepFreezeAddress)
            .getLockedAmount();
        uint256 timeToLock = IDeepFreeze(_deepFreezeAddress).getTimeToLock();
        uint256 frTokenToMint = calculate_frToken(lockedAmount, timeToLock);
        address _freezerOwner = IDeepFreeze(_deepFreezeAddress).freezerOwner();
        IERC20(frETH).mint(_freezerOwner, frTokenToMint);
        frTokenMinted[_deepFreezeAddress] = frTokenToMint;
    }

    // View functions

    function getFrTokenMinted(address _deepFreezeAddress)
        public
        view
        returns (uint256)
    {
        return frTokenMinted[_deepFreezeAddress];
    }

    // Pure functions

    /// @notice Get the amount of frAsset that will be minted
    /// @return Return the amount of frAsset that will be minted
    function calculate_frToken(uint256 _lockedAmount, uint256 _timeToLock)
        internal
        pure
        returns (uint256)
    {
        uint256 token = (_timeToLock * _lockedAmount) / (N_DAYS * 1 days);
        return token;
    }
}

/*
/// @notice Get the cost for unlocking the DeepFreeze
    /// @return Return 0 if wait the locking period, pay a penalty if not waitting 67 % of the time, make partial profit if wait between 67 % and 100%
    function getUnlockCost() public view returns (uint256) {
        uint256 progress = calculateProgress(
            block.timestamp,
            lockingDate,
            timeToLock
        );
        return calculateWithdrawCost(progress, frToken);
    }

    function calculateProgress(
        uint256 _nBlock,
        uint256 _lockingDate,
        uint256 _timeToLock
    ) internal pure returns (uint256) {
        return (100 * (_nBlock - _lockingDate)) / _timeToLock;
    }

    function calculateWithdrawCost(uint256 _progress, uint256 _frToken)
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
    */
