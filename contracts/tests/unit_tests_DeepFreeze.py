from brownie import accounts, exceptions
from deploy_functions import deploy_Factory_DeepFreeze
from web3 import Web3
import pytest

# Check owner of the DeepFreeze
@pytest.mark.parametrize("userId", [1, 3, 5])
def test_isOwner(admin, userId):
    hint = "Coding"
    password = "Hello world"
    user = accounts[userId]
    deepfreeze = deploy_Factory_DeepFreeze(admin, user, hint, password)
    assert user == deepfreeze.FreezerOwner()


# Test onlyOwner
def test_onlyOwner_canRequestHint(admin, alice, bob):
    hint = "Code"
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    with pytest.raises(exceptions.VirtualMachineError):
        deepfreeze.requestHint({"from": bob})


# Test onlyOwner
def test_onlyOwner_canRequestPassword(admin, alice, bob):
    hint = "Code"
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    with pytest.raises(exceptions.VirtualMachineError):
        deepfreeze.requestPassword({"from": bob})


# Test Hint
@pytest.mark.parametrize("hint", ["hello", "world", "1234"])
def test_isHintCorrect(admin, alice, hint):
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    assert hint == deepfreeze.requestHint({"from": alice})


# Test password
@pytest.mark.parametrize("password", ["hello", "world", "1234"])
def test_isPasswordCorrect(admin, alice, password):
    hint = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    assert Web3.keccak(text=password) == deepfreeze.requestPassword({"from": alice})


# Test deposit
@pytest.mark.parametrize("amount", [0.1, 10, 0.001, 0.000001])
def test_deposit(admin, alice, amount):
    hint = "Code"
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    deepfreeze.deposit({"from": alice, "value": Web3.toWei(amount, "Ether")})
    assert Web3.toWei(amount, "Ether") == deepfreeze.balance()


# Test only owner can withdraw
def test_withdraw_onlyOwner(admin, alice, bob):
    hint = "Code"
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    deepfreeze.deposit({"from": alice, "value": Web3.toWei(1, "Ether")})
    with pytest.raises(exceptions.VirtualMachineError):
        deepfreeze.withdraw(password, {"from": bob})


# Test bad password
@pytest.mark.parametrize("password", ["hello", "940904mlkmde dedw", "123edsmdkma3#"])
def test_withdraw_badPassword(admin, alice, password):
    hint = "Code"
    badPassword = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    deepfreeze.deposit({"from": alice, "value": Web3.toWei(1, "Ether")})
    with pytest.raises(exceptions.VirtualMachineError):
        deepfreeze.withdraw(badPassword, {"from": alice})


# Test withdraw different amount
@pytest.mark.parametrize("amount", [0.1, 10, 0.001, 0.000001])
def test_withdraw_amount(admin, alice, amount):
    initialBalance = alice.balance()
    hint = "Code"
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    deepfreeze.deposit({"from": alice, "value": Web3.toWei(amount, "Ether")})
    deepfreeze.withdraw(password, {"from": alice})
    assert alice.balance() == initialBalance


# Test withdraw different password
@pytest.mark.parametrize("password", ["hello", "940904mlkmde dedw", "123edsmdkma3#"])
def test_withdraw_password(admin, alice, password):
    hint = "Code"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    deepfreeze.deposit({"from": alice, "value": Web3.toWei(1, "Ether")})
    deepfreeze.withdraw(password, {"from": alice})


# Test changePassword
def test_changePassword(admin, alice):
    hint = "Code"
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    oldPassword = password
    newPassword = "Future of France"
    deepfreeze.changePassword(
        oldPassword, Web3.keccak(text=newPassword), {"from": alice}
    )
    assert Web3.keccak(text=newPassword) == deepfreeze.requestPassword({"from": alice})


# Test onlyOwner can changePassword
def test_onlyOwner_changePassword(admin, alice, bob):
    hint = "Code"
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    oldPassword = password
    newPassword = "Future of France"
    with pytest.raises(exceptions.VirtualMachineError):
        deepfreeze.changePassword(
            oldPassword, Web3.keccak(text=newPassword), {"from": bob}
        )


# Test TransferOwnership
def test_transferOwnership(admin, alice, bob):
    hint = "Code"
    password = "Hello world"
    newPassword = Web3.keccak(text="Future of France")
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    deepfreeze.transferOwnership(bob, password, newPassword, {"from": alice})
    assert bob == deepfreeze.FreezerOwner()
    assert newPassword == deepfreeze.requestPassword({"from": bob})


# Test onlyOwner canDo
def test_onlyOwnerTransferOwnership(admin, alice, bob):
    hint = "Code"
    password = "Hello world"
    newPassword = Web3.keccak(text="Future of France")
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    with pytest.raises(exceptions.VirtualMachineError):
        deepfreeze.transferOwnership(bob, password, newPassword, {"from": bob})
