//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract DeepFreeze {
    // Var declarations
    address payable public freezerOwner;
    string internal hint;
    bytes32 internal password;
    uint256 internal lockingDate;
    uint256 internal timeToLock;
    uint256 internal unlockingDate;
    uint256 internal lockedAmount;
    uint256 constant PROGRESS_THRESHOLD = 67;
    uint256 public constant MIN_LOCK_DAYS = 7;
    uint256 public constant MAX_LOCK_DAYS = 1100;

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

    function deposit() public payable {
        require(status == Status.Open);
        emit FundDeposited(address(this), msg.value);
    }

    // Public functions

    function changePassword(string memory oldPassword, bytes32 newPassword)
        public
        onlyOwner
    {
        require(keccak256(abi.encodePacked(oldPassword)) == password); // Wrong password
        password = newPassword;
        passwordSafe = PasswordSafe.yes;
    }

    function changeHint(string memory _hint) public onlyOwner {
        hint = _hint;
    }

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

    function lock(uint256 _timeToLock) public onlyOwner {
        require(address(this).balance != 0); // DeepFreeze empty
        require(status == Status.Open);
        require(_timeToLock > MIN_LOCK_DAYS && _timeToLock < MAX_LOCK_DAYS);
        status = Status.Closed;
        lockingDate = block.timestamp;
        timeToLock = (_timeToLock * 1 days);
        unlockingDate = lockingDate + timeToLock;
        uint256 lockedAmount = address(this).balance;
        // Call Mint function here, probably an interface
    }

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

    function getLockingDate() public view returns (uint256) {
        return lockingDate;
    }

    function getUnlockingDate() public view returns (uint256) {
        return unlockingDate;
    }

    function getLockedAmount() public view returns (uint256) {
        return lockedAmount;
    }

    function getStatus() public view returns (Status) {
        return status;
    }

    function calculateUnlockCost() public view returns (uint256) {
        uint256 unlockCost;
        uint256 progress = calculateProgress(
            block.timestamp,
            lockingDate,
            timeToLock
        );
        if (progress >= 100) {
            unlockCost = 0;
        } else if (progress <= PROGRESS_THRESHOLD) {
            // continue
        }
        return unlockCost;
    }

    // Pure function
    function calculateProgress(
        uint256 _nBlock,
        uint256 _lockingDate,
        uint256 _timeToLock
    ) internal pure returns (uint256) {
        return (100 * (_nBlock - _lockingDate)) / _timeToLock;
    }
}
