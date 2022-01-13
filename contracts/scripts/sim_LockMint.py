from scripts.deploy_functions import create_DeepFreeze, get_DeepFreezeContract
from web3 import Web3
from brownie import accounts, frETH, DeepFreezeFactory


def main():
    token = frETH.deploy({"from": accounts[0]})
    factory = DeepFreezeFactory.deploy(token.address, {"from": accounts[0]})
    token.setOnlyFactory(factory.address, {"from": accounts[0]})
    create_DeepFreeze(factory, accounts[1], "hello", "hello")
    deepfreeze = get_DeepFreezeContract(factory, accounts[0], accounts[1], 0)
