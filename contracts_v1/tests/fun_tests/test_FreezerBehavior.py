from brownie import accounts, exceptions, chain
from scripts.deploy_functions import deploy_contracts, deployAndParametrize
from scripts.utils import calculateWithdrawCost
import brownie

from web3 import Web3
import pytest

# Test when withdraw after maturity
@pytest.mark.parametrize("amountToLock", [0.001, 0.231, 0.321, 1.293])
def test_fullProcess(admin, alice, amountToLock):
    WAsset, freth, nft, staking, frz, deepfreeze = deployAndParametrize(admin)
    amountToLock = Web3.toWei(amountToLock, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, 400, {"from": alice})
    assert freth.totalSupply() == freth.balanceOf(alice)
    assert nft.balanceOf(alice) == 1
    assert nft.ownerOf(1) == alice
    assert WAsset.balanceOf(deepfreeze.address) == amountToLock
    chain.sleep(3600 * 24 * 401)
    chain.mine()
    deepfreeze.withdrawWAsset(1, {"from": alice})
    assert WAsset.balanceOf(deepfreeze.address) == 0
    assert WAsset.balanceOf(alice) == amountToLock
    assert freth.balanceOf(alice) == freth.totalSupply()
    assert nft.balanceOf(alice) == 0
    with brownie.reverts():
        nft.ownerOf(1)


# Test lock send to bob and bob withdraw
def test_SendNFT(admin, alice, bob):
    WAsset, freth, nft, staking, frz, deepfreeze = deployAndParametrize(admin)
    amountToLock = Web3.toWei(0.01, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, 400, {"from": alice})
    nft.approve(bob, 1, {"from": alice})
    nft.transferFrom(alice, bob, 1, {"from": alice})
    assert nft.balanceOf(alice) == 0
    assert nft.balanceOf(bob) == 1
    assert nft.ownerOf(1) == bob
    chain.sleep(3600 * 24 * 401)
    chain.mine()
    deepfreeze.withdrawWAsset(1, {"from": bob})
    assert WAsset.balanceOf(deepfreeze.address) == 0
    assert WAsset.balanceOf(bob) == amountToLock
    assert WAsset.balanceOf(alice) == 0
    assert freth.balanceOf(alice) == freth.totalSupply()
    assert nft.balanceOf(alice) == 0
    assert nft.balanceOf(bob) == 0


# Test malicious user reedem
def test_reedem(admin, alice, bob):
    WAsset, freth, nft, staking, frz, deepfreeze = deployAndParametrize(admin)
    amountToLock = Web3.toWei(0.01, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, 400, {"from": alice})
    chain.sleep(3600 * 24 * 401)
    chain.mine()
    with brownie.reverts("Not the owner of tokenId"):
        deepfreeze.withdrawWAsset(1, {"from": bob})
