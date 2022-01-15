//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

/// @title DeepFreeze
/// @author CharlieDAO

interface IFactory {
    function rewardLocking(address) external;

    function earlyWithdraw(address) external;
}

contract DeepFreeze {
    // Var declarations
    address payable public freezerOwner;
    address public factoryAddress;
    string internal hint;
    bytes32 internal password;
    uint256 internal lockingDate;
    uint256 internal timeToLock;
    uint256 internal unlockingDate;
    uint256 internal lockedAmount;
    uint256 internal constant MIN_LOCK_DAYS = 7;
    uint256 internal constant MAX_LOCK_DAYS = 1100;

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
    event FundLocked(
        address indexed freezer,
        uint256 amount,
        uint256 lockPeriod
    );
    event FundWithdrawed(address indexed freezer, address _to, uint256 amount);
    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );

    // Constructor

    constructor(
        address _factoryAddress,
        address eoa,
        string memory _hint,
        bytes32 _password
    ) {
        factoryAddress = _factoryAddress;
        freezerOwner = payable(eoa);
        hint = _hint;
        password = _password;
    }

    // Modifier
    modifier onlyOwner() {
        require(msg.sender == freezerOwner, "Only owner can do that");
        _;
    }

    modifier onlyFactory() {
        require(msg.sender == factoryAddress, "Only Factory can call");
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
        require(
            keccak256(abi.encodePacked(oldPassword)) == password,
            "Wrong password"
        );
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
        require(newOwner != address(0), "Zero address");
        passwordSafe = PasswordSafe.no;
        changePassword(oldPassword, newPassword);
        require(passwordSafe == PasswordSafe.yes);
        address oldOwner = freezerOwner;
        freezerOwner = payable(newOwner);
        emit OwnershipTransferred(oldOwner, newOwner);
    }

    /// @notice Lock the DeepFreeze, when locking users receive frAssets (i.e., 1 ETH lock 365 days mint 1 frETH)
    function lock(uint256 _timeToLock) public onlyOwner {
        require(address(this).balance != 0, "DeepFreeze empty");
        require(status == Status.Open, "DeepFreeze already closed");
        require(
            _timeToLock > MIN_LOCK_DAYS && _timeToLock < MAX_LOCK_DAYS,
            "Bad days input"
        );
        status = Status.Closed;
        lockingDate = block.timestamp;
        timeToLock = (_timeToLock * 1 days);
        unlockingDate = lockingDate + timeToLock;
        lockedAmount = address(this).balance;
        IFactory(factoryAddress).rewardLocking(address(this));
        emit FundLocked(address(this), lockedAmount, timeToLock);
    }

    /// @notice Wihtdraw the funds from the contract to owner address
    /// @dev Calling selfdestruct for gas refunding
    function withdraw(string memory _password) public onlyOwner {
        require(
            keccak256(abi.encodePacked(_password)) == password,
            "Wrong password"
        );
        require(address(this).balance != 0, "DeepFreeze empty");
        if (block.timestamp >= getUnlockingDate()) {
            address freezerAddress = address(this);
            emit FundWithdrawed(
                freezerAddress,
                freezerOwner,
                address(this).balance
            );
            selfdestruct(freezerOwner);
        } else {
            IFactory(factoryAddress).earlyWithdraw(address(this));
        }
    }

    function earlyWithdraw(address _stakingFRZ, uint256 _fees)
        public
        payable
        onlyFactory
    {
        (bool sent, ) = payable(_stakingFRZ).call{value: _fees}("");
        require(sent, "Failed to send Ether");
        selfdestruct(freezerOwner);
    }

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
}
