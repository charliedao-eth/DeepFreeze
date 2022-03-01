from brownie import accounts, exceptions, chain
from scripts.deploy_functions import deploy_contracts, deployAndParametrize
from scripts.utils import calculateWithdrawCost
import brownie

from web3 import Web3
import pytest

# Test onlyOwner can do
def test_onlyOwner(admin, alice):
    WAsset, freth, nft, staking, frz, deepfreeze = deploy_contracts(admin)
    with pytest.raises(exceptions.VirtualMachineError):
        nft.setOnlyGovernor(alice, {"from": alice})


# Test set onlyGovernance
def test_Governance(admin):
    WAsset, freth, nft, staking, frz, deepfreeze = deploy_contracts(admin)
    nft.setOnlyGovernor(deepfreeze.address, {"from": admin})
    assert deepfreeze.address == nft.governorAddress({"from": admin})


# Test mint token
def test_NotMint(admin, alice):
    WAsset, freth, nft, staking, frz, deepfreeze = deploy_contracts(admin)
    nft.setOnlyGovernor(deepfreeze.address, {"from": admin})
    with pytest.raises(exceptions.VirtualMachineError):
        nft.mint(alice, 1, {"from": alice})


# Test mint token
def test_NotBurn(admin, alice):
    WAsset, freth, nft, staking, frz, deepfreeze = deployAndParametrize(admin)
    amountToLock = Web3.toWei(1, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, 500, {"from": alice})
    with pytest.raises(exceptions.VirtualMachineError):
        nft.burn(1, {"from": alice})


# Test ownership of token
def test_Ownership(admin, alice, bob):
    WAsset, freth, nft, staking, frz, deepfreeze = deployAndParametrize(admin)
    amountToLock = Web3.toWei(1, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, 500, {"from": alice})
    assert nft.ownerOf(1) == alice
    assert nft.ownerOf(1) != bob
