from scripts.deploy_functions import deploy_Factory_DeepFreeze
from brownie import accounts, chain
from web3 import Web3


def deploy(lockedAmount, nDaysToLock):
    hint = "Code"
    password = "Hello world"
    deepfreeze = deploy_Factory_DeepFreeze(accounts[0], accounts[1], hint, password)
    deposit = Web3.toWei(lockedAmount, "Ether")
    deepfreeze.deposit({"from": accounts[1], "value": deposit})
    deepfreeze.lock(nDaysToLock, {"from": accounts[1]})
    return deepfreeze


def cost(deepfreeze):
    return deepfreeze.getUnlockCost({"from": accounts[0]}) / (10 ** 18)


def main():
    lockedAmount = 3
    nDaysToLock = 365
    deepfreeze = deploy(lockedAmount, nDaysToLock)
    print(f"Locking {lockedAmount} ETH for {nDaysToLock} days")
    p = []
    i = 0
    price = cost(deepfreeze)
    print(f"Days 0 unlocking cost {price} frETH")
    steps = 15
    while i < 400:
        chain.sleep(3600 * 24 * steps)
        chain.mine()
        price = cost(deepfreeze)
        p.append(price)
        i += steps
        print(f"Days {i} unlocking cost {price} frETH")
