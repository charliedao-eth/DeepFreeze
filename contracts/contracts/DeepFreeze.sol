//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract DeepFreeze {
    // Var declarations
    address payable public FreezerOwner;
    string internal _hint;
    bytes32 internal _password;
    uint256 public _lockDate;
    uint256 public _timeToLock;

    enum STATUS {
        Open,
        Closed
    }
    STATUS public Status;

    enum PASSWORD_SAFE {
        yes,
        no
    }
    PASSWORD_SAFE private PasswordSafe = PASSWORD_SAFE.yes;

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
        string memory hint_,
        bytes32 password_
    ) {
        FreezerOwner = payable(eoa);
        _hint = hint_;
        _password = password_;
        Status = STATUS.Open;
    }

    // Modifier
    modifier onlyOwner() {
        require(
            msg.sender == FreezerOwner,
            "Only the freezer owner can do that!"
        );
        _;
    }

    // Functions

    function changePassword(string memory oldPassword, bytes32 newPassword)
        public
        onlyOwner
    {
        require(keccak256(abi.encodePacked(oldPassword)) == _password); // Wrong password
        _password = newPassword;
        PasswordSafe = PASSWORD_SAFE.yes;
    }

    function transferOwnership(
        address newOwner,
        string memory oldPassword,
        bytes32 newPassword
    ) public onlyOwner {
        require(newOwner != address(0)); // Zero address
        PasswordSafe = PASSWORD_SAFE.no;
        changePassword(oldPassword, newPassword);
        require(PasswordSafe == PASSWORD_SAFE.yes);
        address oldOwner = FreezerOwner;
        FreezerOwner = payable(newOwner);
        emit OwnershipTransferred(oldOwner, newOwner);
    }

    function requestHint() public view onlyOwner returns (string memory) {
        return _hint;
    }

    function requestPassword() public view onlyOwner returns (bytes32) {
        return _password;
    }

    function deposit() public payable {
        emit FundDeposited(address(this), msg.value);
    }

    function lock(uint256 timeToLock_) public onlyOwner {
        require(balance != 0);
        require(Status == STATUS.Open);
        _lockDate = block.timestamp;
        _timeToLock = timeToLock_;
        // continue
    }

    function withdraw(string memory password_) public onlyOwner {
        require(keccak256(abi.encodePacked(password_)) == _password); // Wrong password
        uint256 balance = address(this).balance;
        require(balance != 0); // DeepFreeze empty
        address freezerAddress = address(this);
        emit FundWithdrawed(freezerAddress, FreezerOwner, balance);
        selfdestruct(FreezerOwner);
    }
}
