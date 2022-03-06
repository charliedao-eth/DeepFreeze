from brownie import accounts, exceptions, chain
from scripts.deploy_functions import deploy_contracts
from scripts.utils import calculateWithdrawCost

from web3 import Web3
import pytest

# Test onlyOwner can do
def test_onlyOwner(admin, alice):
    (weth, frtoken, nft, staking, frz, freeze, staking_frToken) = deploy_contracts(
        admin
    )
    with pytest.raises(exceptions.VirtualMachineError):
        frtoken.setOnlyGovernor(alice, {"from": alice})


# Test set onlyGovernance
def test_Governance(admin):
    (weth, frtoken, nft, staking, frz, freeze, staking_frToken) = deploy_contracts(
        admin
    )
    frtoken.setOnlyGovernor(freeze.address, {"from": admin})
    assert freeze.address == frtoken.governorAddress({"from": admin})


# Test mint token
def test_NotMint(admin, alice):
    (weth, frtoken, nft, staking, frz, freeze, staking_frToken) = deploy_contracts(
        admin
    )
    frtoken.setOnlyGovernor(freeze.address, {"from": admin})
    with pytest.raises(exceptions.VirtualMachineError):
        frtoken.mint(alice, 10000000, {"from": alice})


# Test mint token
def test_NotBurn(admin, alice):
    (weth, frtoken, nft, staking, frz, freeze, staking_frToken) = deploy_contracts(
        admin
    )
    frtoken.setOnlyGovernor(freeze.address, {"from": admin})
    with pytest.raises(exceptions.VirtualMachineError):
        frtoken.burn(alice, 10000000, {"from": alice})
