from brownie import accounts, exceptions, chain
from scripts.deploy_functions import deploy_contracts
from scripts.utils import calculateWithdrawCost

from web3 import Web3
import pytest

# Test onlyOwner can do
def test_onlyOwner(admin, alice):
    weth, freth, nft, staking, frz, deepfreeze = deploy_contracts(admin)
    with pytest.raises(exceptions.VirtualMachineError):
        freth.setOnlyGovernor(alice, {"from": alice})


# Test set onlyGovernance
def test_Governance(admin):
    weth, freth, nft, staking, frz, deepfreeze = deploy_contracts(admin)
    freth.setOnlyGovernor(deepfreeze.address, {"from": admin})
    assert deepfreeze.address == freth.governorAddress({"from": admin})


# Test mint token
def test_NotMint(admin, alice):
    weth, freth, nft, staking, frz, deepfreeze = deploy_contracts(admin)
    freth.setOnlyGovernor(deepfreeze.address, {"from": admin})
    with pytest.raises(exceptions.VirtualMachineError):
        freth.mint(alice, 10000000, {"from": alice})


# Test mint token
def test_NotBurn(admin, alice):
    weth, freth, nft, staking, frz, deepfreeze = deploy_contracts(admin)
    freth.setOnlyGovernor(deepfreeze.address, {"from": admin})
    with pytest.raises(exceptions.VirtualMachineError):
        freth.burn(alice, 10000000, {"from": alice})
