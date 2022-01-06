//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract DeepFreeze {
    // Var declarations
    address payable public FreezerOwner;
    string internal _hint;
    bytes32 internal _password;

    // Events
    event FundDeposited(address indexed freezer, uint256 amount);
    event FundWithdrawed(address indexed freezer, address _to, uint256 amount);

    // Constructor

    constructor(
        address eoa,
        string memory hint_,
        bytes32 password_
    ) {
        FreezerOwner = payable(eoa);
        _hint = hint_;
        _password = password_;
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

    function requestHint() public view onlyOwner returns (string memory) {
        return _hint;
    }

    function requestPassword() public view onlyOwner returns (bytes32) {
        return _password;
    }

    function deposit() public payable {
        emit FundDeposited(address(this), msg.value);
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
