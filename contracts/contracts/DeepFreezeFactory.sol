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

    function earlyWithdraw(address, uint256) external;
}

interface IERC20 {
    function balanceOf(address) external view returns (uint256);

    function mint(address, uint256) external;

    function burn(address, uint256) external;
}

contract DeepFreezeFactory {
    address public creatorOwner;
    address[] public userAddress;
    address public frETH;
    address public stakingFRZ;
    DeepFreeze[] public deployedDeepFreeze;
    uint256 internal constant N_DAYS = 365;
    uint256 internal constant PROGRESS_THRESHOLD = 67;
    mapping(address => DeepFreeze[]) public userToDeepFreeze;
    mapping(address => uint256) internal frTokenMinted;
    event FreezerDeployed(address from, address freezerAddress);

    constructor(address _frETH, address _stakingFRZ) {
        creatorOwner = msg.sender;
        frETH = _frETH;
        stakingFRZ = _stakingFRZ;
    }

    function createDeepFreeze(string memory _hint, bytes32 _password) public {
        DeepFreeze new_freezer_address = new DeepFreeze(
            address(this),
            msg.sender,
            _hint,
            _password
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
        uint256 frTokenToMint = _calculate_frToken(lockedAmount, timeToLock);
        address _freezerOwner = IDeepFreeze(_deepFreezeAddress).freezerOwner();
        IERC20(frETH).mint(_freezerOwner, frTokenToMint);
        frTokenMinted[_deepFreezeAddress] = frTokenToMint;
    }

    function earlyWithdraw(address _deepFreezeAddress) public {
        address _freezerOwner = IDeepFreeze(_deepFreezeAddress).freezerOwner();
        uint256 _status = IDeepFreeze(_deepFreezeAddress).getStatus();
        uint256 _cost = getUnlockCost(_deepFreezeAddress);
        uint256 _fees = getFees(_deepFreezeAddress);
        require(
            isDeepFreeze(_deepFreezeAddress),
            "Caller is not a registered DeepFreeze"
        );
        require(_status == 1, "DeepFreeze not locked");
        require(_cost > 0, "This is not an early withdraw");
        require(
            IERC20(frETH).balanceOf(_freezerOwner) >= _cost,
            "Not enough frETH"
        );
        IERC20(frETH).burn(_freezerOwner, _cost);
        IERC20(frETH).mint(stakingFRZ, (_cost * 50) / 100);
        IDeepFreeze(_deepFreezeAddress).earlyWithdraw(stakingFRZ, _fees);
    }

    // View functions

    function getFrTokenMinted(address _deepFreezeAddress)
        public
        view
        returns (uint256)
    {
        return frTokenMinted[_deepFreezeAddress];
    }

    function getProgress(address _deepFreezeAddress)
        public
        view
        returns (uint256)
    {
        uint256 _lockingDate = IDeepFreeze(_deepFreezeAddress).getLockingDate();
        uint256 _timeToLock = IDeepFreeze(_deepFreezeAddress).getTimeToLock();
        return _calculateProgress(block.timestamp, _lockingDate, _timeToLock);
    }

    function getUnlockCost(address _deepFreezeAddress)
        public
        view
        returns (uint256)
    {
        uint256 _progress = getProgress(_deepFreezeAddress);
        uint256 _frTokenMinted = frTokenMinted[_deepFreezeAddress];
        return _calculateWithdrawCost(_progress, _frTokenMinted);
    }

    function getFees(address _deepFreezeAddress) public view returns (uint256) {
        uint256 _lockedAmount = IDeepFreeze(_deepFreezeAddress)
            .getLockedAmount();
        return _calculateFees(_lockedAmount);
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
        uint256 _timeToLock
    ) internal pure returns (uint256) {
        return (100 * (_nBlock - _lockingDate)) / _timeToLock;
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
