from brownie import accounts, network, config
import json

abi_file = "./build/contracts/DeepFreeze.json"
with open(abi_file) as f:
    tmp = json.load(f)
freezer_abi = tmp["abi"]


LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "ganache",
    "hardhat",
    "local-ganache",
    "mainnet-fork",
]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])
