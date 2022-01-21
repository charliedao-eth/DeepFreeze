from brownie import accounts, exceptions
from scripts.deploy_functions import deploy_Factory_DeepFreeze
from web3 import Web3
from decimal import *
import pytest


def test_LockingParameters(admin, alice):
    hint = "Code"
    password = "Hello world"
    lockedAmount = 2
    daysToLock = 365
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    deposit = Web3.toWei(lockedAmount, "Ether")
    deepfreeze.deposit({"from": alice, "value": deposit})
    deepfreeze.lock(daysToLock, {"from": alice})
    freezeLock = Web3.fromWei(deepfreeze.getLockedAmount(), "Ether")
    #  print(f"{lockedAmount} ETH deposit, got {freezeLock} ETH in freezer")
    lockDays = deepfreeze.getTimeToLock()


# Test the computation of the reward
@pytest.mark.parametrize("lockedAmount", [1, 4, 5])
@pytest.mark.parametrize("nDaysToLock", [365, 730, 1095])
def test_calcLockReward(admin, alice, lockedAmount, nDaysToLock):
    hint = "Code"
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(admin, alice, hint, password)
    deposit = Web3.toWei(lockedAmount, "Ether")
    deepfreeze.deposit({"from": alice, "value": deposit})
    deepfreeze.lock(nDaysToLock, {"from": alice})
    frToken = Web3.fromWei(deepfreeze.getFrToken({"from": alice}), "Ether")
    thToken = (nDaysToLock * lockedAmount) / 365
    # print(
    #    f"Deposit {lockedAmount} ETh locked for {nDaysToLock}days , get {frToken} frETH"
    # )
    assert thToken == frToken
