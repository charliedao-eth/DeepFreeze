//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

/// @title DeepFreeze
/// @author CharlieDAO

contract DeepFreeze {
    // Var declarations
    address payable public freezerOwner;
    string internal hint;
    bytes32 internal password;
    uint256 internal lockingDate;
    uint256 internal timeToLock;
    uint256 internal unlockingDate;
    uint256 internal lockedAmount;
    uint256 internal frToken;
    uint256 internal constant PROGRESS_THRESHOLD = 67;
    uint256 internal constant MIN_LOCK_DAYS = 7;
    uint256 internal constant MAX_LOCK_DAYS = 1100;
    uint256 internal constant N_DAYS = 365;

    enum Status {
        Open,
        Closed
    }

    enum PasswordSafe {
        yes,
        no
    }
    PasswordSafe private passwordSafe = PasswordSafe.yes;
    Status private status = Status.Open;

    // Events
    event FundDeposited(address indexed freezer, uint256 amount);
    event FundWithdrawed(address indexed freezer, address _to, uint256 amount);
    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );

    // Constructor

    constructor(
        address eoa,
        string memory _hint,
        bytes32 _password
    ) {
        freezerOwner = payable(eoa);
        hint = _hint;
        password = _password;
    }

    // Modifier
    modifier onlyOwner() {
        require(msg.sender == freezerOwner);
        _;
    }

    // Fallback function

    /// @notice Fallback function for deposit blockchain native assets
    function deposit() public payable {
        require(status == Status.Open);
        emit FundDeposited(address(this), msg.value);
    }

    // Public functions

    /// @notice Change the password
    function changePassword(string memory oldPassword, bytes32 newPassword)
        public
        onlyOwner
    {
        require(keccak256(abi.encodePacked(oldPassword)) == password); // Wrong password
        password = newPassword;
        passwordSafe = PasswordSafe.yes;
    }

    /// @notice Change the hint
    function changeHint(string memory _hint) public onlyOwner {
        hint = _hint;
    }

    /// @notice Change the ownership of the DeepFreeze, force to change the password when calling the function
    /// @dev Since the password is giving, user need to change the password for safety
    function transferOwnership(
        address newOwner,
        string memory oldPassword,
        bytes32 newPassword
    ) public onlyOwner {
        require(newOwner != address(0)); // Zero address
        passwordSafe = PasswordSafe.no;
        changePassword(oldPassword, newPassword);
        require(passwordSafe == PasswordSafe.yes);
        address oldOwner = freezerOwner;
        freezerOwner = payable(newOwner);
        emit OwnershipTransferred(oldOwner, newOwner);
    }

    /// @notice Lock the DeepFreeze, when locking users receive frAssets (i.e., 1 ETH lock 365 days mint 1 frETH)
    function lock(uint256 _timeToLock) public onlyOwner {
        require(address(this).balance != 0); // DeepFreeze empty
        require(status == Status.Open);
        require(_timeToLock > MIN_LOCK_DAYS && _timeToLock < MAX_LOCK_DAYS);
        status = Status.Closed;
        lockingDate = block.timestamp;
        timeToLock = (_timeToLock * 1 days);
        unlockingDate = lockingDate + timeToLock;
        lockedAmount = address(this).balance;
        frToken = calculate_frToken(lockedAmount, timeToLock);
        // Call Mint function here, probably an interface
    }

    /// @notice Wihtdraw the funds from the contract to owner address
    /// @dev Calling selfdestruct for gas refunding
    function withdraw(string memory _password) public onlyOwner {
        require(keccak256(abi.encodePacked(_password)) == password); // Wrong password
        require(address(this).balance != 0); // DeepFreeze empty
        address freezerAddress = address(this);
        emit FundWithdrawed(
            freezerAddress,
            freezerOwner,
            address(this).balance
        );
        selfdestruct(freezerOwner);
    }

    // Private function

    // View functions

    function getHint() public view onlyOwner returns (string memory) {
        return hint;
    }

    function getPassword() public view onlyOwner returns (bytes32) {
        return password;
    }

    /// @notice Get the locking date
    /// @return Return the block timestamp when the DeepFreeze have been locked
    function getLockingDate() public view returns (uint256) {
        return lockingDate;
    }

    /// @notice Get the number of UNIX-Timestamp when the contracts will unlock
    /// @return Return the number of UNIX-Timestamp when the contracts will unlock
    function getTimeToLock() public view returns (uint256) {
        return timeToLock;
    }

    /// @notice Get the timestamp where the DeepFreeze will be unlock
    /// @return Return the timestamp where the DeepFreeze will be unlock
    function getUnlockingDate() public view returns (uint256) {
        return unlockingDate;
    }

    /// @notice Get the amount of blockchain native assets locked in the DeepFreeze
    /// @return Return the amount of blockchain native assets locked in the DeepFreeze
    function getLockedAmount() public view returns (uint256) {
        return lockedAmount;
    }

    /// @notice Get the status of the DeepFreeze
    /// @return Return 1 if DeepFreeze is locked
    function getStatus() public view returns (Status) {
        return status;
    }

    /// @notice Get the number of UNIX-Timestamp when the contracts will unlock
    /// @return Return the number of UNIX-Timestamp when the contracts will unlock
    function getFrToken() public view returns (uint256) {
        return frToken;
    }

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

    // Pure function

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
}
