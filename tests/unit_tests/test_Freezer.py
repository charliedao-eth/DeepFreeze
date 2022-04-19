from brownie import accounts, exceptions, chain
from scripts.deploy_functions import deploy_contracts, deployAndParametrize
from scripts.utils import calculateWithdrawCost

from web3 import Web3
import pytest


# Test locking and minting of frETH and NFT
@pytest.mark.parametrize("amountToLock", [1, 4, 5])
@pytest.mark.parametrize("timeToLock", [30, 89, 365, 730, 1095])
def test_deposit(admin, alice, amountToLock, timeToLock):
    (
        WAsset,
        freth,
        nft,
        staking,
        frz,
        deepfreeze,
        staking_frToken,
    ) = deployAndParametrize(admin)
    amountToLock = Web3.toWei(amountToLock, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, timeToLock, {"from": alice})
    theoric_frEth = (timeToLock * amountToLock) / 365
    print(
        f"Delta between theoric and from contract is {abs(freth.balanceOf(alice) - theoric_frEth.as_integer_ratio()[0])} Gwei"
    )
    assert abs(freth.balanceOf(alice) - theoric_frEth.as_integer_ratio()[0]) < 200
    assert freth.totalSupply() == freth.balanceOf(alice)
    assert nft.balanceOf(alice) == 1
    assert nft.ownerOf(1) == alice
    assert WAsset.balanceOf(deepfreeze.address) == amountToLock


# Test locking and minting of frETH and NFT
@pytest.mark.parametrize("timeToLock", [1300, 1101])
def test_notLockingPeriod(admin, alice, timeToLock):
    (
        WAsset,
        freth,
        nft,
        staking,
        frz,
        deepfreeze,
        staking_frToken,
    ) = deployAndParametrize(admin)
    amountToLock = Web3.toWei(0.001, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    with pytest.raises(exceptions.VirtualMachineError):
        deepfreeze.lockWAsset(amountToLock, timeToLock, {"from": alice})


# Test position is correct
@pytest.mark.parametrize("amountToLock", [1, 4, 5])
@pytest.mark.parametrize("timeToLock", [30, 89, 409, 201])
def test_positionCorrect(admin, alice, amountToLock, timeToLock):
    (
        WAsset,
        freth,
        nft,
        staking,
        frz,
        deepfreeze,
        staking_frToken,
    ) = deployAndParametrize(admin)
    amountToLock = Web3.toWei(amountToLock, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, timeToLock, {"from": alice})
    theoric_frEth = timeToLock * amountToLock / 365
    (
        amountLocked,
        tokenMinted,
        timestampLock,
        timestampUnlock,
        isActive,
    ) = deepfreeze.getPositions(1)
    print(
        f"Delta between theoric and tokenMinted is {abs(freth.balanceOf(alice) - theoric_frEth.as_integer_ratio()[0])} Gwei"
    )
    assert amountLocked == amountToLock
    assert tokenMinted == freth.balanceOf(alice)
    assert abs(tokenMinted - theoric_frEth.as_integer_ratio()[0]) < 200
    assert (timestampUnlock - timestampLock) / (3600 * 24) == timeToLock
    assert isActive == True


# Test progress computation
def test_calculateProgress(admin, alice):
    (
        WAsset,
        freth,
        nft,
        staking,
        frz,
        deepfreeze,
        staking_frToken,
    ) = deployAndParametrize(admin)
    amountToLock = Web3.toWei(1, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, 500, {"from": alice})
    assert deepfreeze.getProgress(1) == 0
    chain.sleep(3600 * 24 * 125)
    chain.mine()
    assert deepfreeze.getProgress(1) == 25
    chain.sleep(3600 * 24 * 125)
    chain.mine()
    assert deepfreeze.getProgress(1) == 50
    chain.sleep(3600 * 24 * 125)
    chain.mine()
    assert deepfreeze.getProgress(1) == 75
    chain.sleep(3600 * 24 * 125)
    chain.mine()
    assert deepfreeze.getProgress(1) == 100


# Test unlocking cost
@pytest.mark.parametrize("amountToLock", [0.5, 0.03, 0.00001])
@pytest.mark.parametrize("timeToLock", [30, 89, 409, 201])
def test_unlockingCost(admin, alice, amountToLock, timeToLock):
    (
        WAsset,
        freth,
        nft,
        staking,
        frz,
        deepfreeze,
        staking_frToken,
    ) = deployAndParametrize(admin)
    amountToLock = Web3.toWei(amountToLock, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, timeToLock, {"from": alice})
    progress = deepfreeze.getProgress(1)
    (
        amountLocked,
        tokenMinted,
        timestampLock,
        timestampUnlock,
        isActive,
    ) = deepfreeze.getPositions(1)
    delta = abs(
        calculateWithdrawCost(progress, tokenMinted) - deepfreeze.getUnlockCost(1)
    )
    print(f"Delta at {progress} % between theoric and from contract {delta} Gwei")
    assert delta <= 200
    chain.sleep(3600 * 24 * round((timeToLock / 4)))
    chain.mine()
    progress = deepfreeze.getProgress(1)
    delta = abs(
        calculateWithdrawCost(progress, tokenMinted) - deepfreeze.getUnlockCost(1)
    )
    print(f"Delta at {progress} % between theoric and from contract {delta} Gwei")
    assert delta <= 200

    chain.sleep(3600 * 24 * round((timeToLock / 2)))
    chain.mine()
    progress = deepfreeze.getProgress(1)
    delta = abs(
        calculateWithdrawCost(progress, tokenMinted) - deepfreeze.getUnlockCost(1)
    )
    print(f"Delta at {progress} % between theoric and from contract {delta} Gwei")
    assert delta <= 200

    chain.sleep(3600 * 24 * round((timeToLock / 2)))
    chain.mine()
    progress = deepfreeze.getProgress(1)
    delta = abs(
        calculateWithdrawCost(progress, tokenMinted) - deepfreeze.getUnlockCost(1)
    )
    print(f"Delta at {progress} % between theoric and from contract {delta} Gwei")
    assert delta <= 200


# Test WAssetFees
@pytest.mark.parametrize("amountToLock", [0.5, 0.03, 0.00001])
def test_WAssetfees(admin, alice, amountToLock):
    (
        WAsset,
        freth,
        nft,
        staking,
        frz,
        deepfreeze,
        staking_frToken,
    ) = deployAndParametrize(admin)
    amountToLock = Web3.toWei(amountToLock, "Ether")
    WAsset.deposit({"from": alice, "value": amountToLock})
    WAsset.approve(deepfreeze.address, amountToLock, {"from": alice})
    deepfreeze.lockWAsset(amountToLock, 400, {"from": alice})
    assert deepfreeze.getWAssetFees(1) == (amountToLock * 0.0025).as_integer_ratio()[0]
    chain.sleep(3600 * 24 * 200)
    chain.mine()
    assert deepfreeze.getWAssetFees(1) == (amountToLock * 0.0025).as_integer_ratio()[0]
    chain.sleep(3600 * 24 * 200)
    chain.mine()
    assert deepfreeze.getWAssetFees(1) == 0
