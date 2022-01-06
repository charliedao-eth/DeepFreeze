from brownie import DeepFreezeFactory, Contract
from scripts.helpful_scripts import get_account
from web3 import Web3
from sys import exit
import json

HINT = "Hello"
ETH = Web3.toWei(0.1, "Ether")


def createFreezer():
    if len(DeepFreezeFactory) == 0:
        print("You need to deploy the contract first")
        exit(0)
    factory = DeepFreezeFactory[-1]
    factory.createDeepFreeze(HINT, Web3.keccak(text="Toto"), {"from": get_account()})
    return factory.userFreezer(get_account(), 0, {"from": get_account()})


def send_Fund(freezer):
    freezer.deposit({"from": get_account(), "value": ETH})
    print(
        f"Send {Web3.fromWei(freezer.balance(),'Ether')} ETH, balance of {freezer.address} : {Web3.fromWei(freezer.balance(),'Ether')} ETH"
    )


def withdraw_Fund(freezer):
    freezer.withdraw("Toto", {"from": get_account()})
    print(
        f"Withdrawing fund, balance of {freezer.address} : {Web3.fromWei(freezer.balance(),'Ether')} ETH"
    )


def main():
    freezer_address = createFreezer()
    with open("DeepFreeze_abi.json") as f:
        abi = json.load(f)
    freezer = Contract.from_abi("freezer", freezer_address, abi)
    send_Fund(freezer)
    # withdraw_Fund(freezer)
