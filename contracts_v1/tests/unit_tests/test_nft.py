from brownie import accounts, exceptions, chain
from scripts.deploy_functions import deploy_contracts, deployAndSetAdmin
from scripts.utils import calculateWithdrawCost

from web3 import Web3
import pytest

# Test onlyOwner can do
def test_onlyOwner(admin, alice):
    weth, freth, nft, frz, deepfreeze = deploy_contracts(admin)
    with pytest.raises(exceptions.VirtualMachineError):
        nft.setOnlyGovernor(alice, {"from": alice})


# Test set onlyGovernance
def test_Governance(admin):
    weth, freth, nft, frz, deepfreeze = deploy_contracts(admin)
    nft.setOnlyGovernor(deepfreeze.address, {"from": admin})
    assert deepfreeze.address == nft.governorAddress({"from": admin})


# Test mint token
def test_NotMint(admin, alice):
    weth, freth, nft, frz, deepfreeze = deploy_contracts(admin)
    nft.setOnlyGovernor(deepfreeze.address, {"from": admin})
    with pytest.raises(exceptions.VirtualMachineError):
        nft.mint(alice, 1, 1, 1, 1, {"from": alice})


# Test mint token
def test_NotBurn(admin, alice):
    weth, freth, nft, frz, deepfreeze = deployAndSetAdmin(admin)
    amountToLock = Web3.toWei(1, "Ether")
    weth.deposit({"from": alice, "value": amountToLock})
    weth.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWETH(amountToLock, 500, {"from": alice})
    with pytest.raises(exceptions.VirtualMachineError):
        nft.burn(1, {"from": alice})
