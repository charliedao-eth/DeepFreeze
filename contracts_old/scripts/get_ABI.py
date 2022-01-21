from brownie import DeepFreeze, DeepFreezeFactory
import json


# ABI for DeepFreezeFactory
def abi_DeepFreezeFactory():
    abi_file = "./build/contracts/DeepFreezeFactory.json"
    with open(abi_file, "r") as f:
        tmp = json.load(f)
    DeepFreezeFactory_abi = tmp["abi"]
    with open("DeepFreezeFactory_abi.json", "w") as output:
        json.dump(DeepFreezeFactory_abi, output)


# ABI for DeepFreeze
def abi_DeepFreeze():
    abi_file = "./build/contracts/DeepFreeze.json"
    with open(abi_file) as f:
        tmp = json.load(f)
    DeepFreeze_abi = tmp["abi"]
    with open("DeepFreeze_abi.json", "w") as output:
        json.dump(DeepFreeze_abi, output)


def main():
    abi_DeepFreezeFactory()
    abi_DeepFreeze()
