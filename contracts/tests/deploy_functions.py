from brownie import DeepFreezeFactory, Contract
from web3 import Web3
import json

# Deploy the DeepFreezeFactory contract
def deploy_Factory(admin):
    factory = DeepFreezeFactory.deploy({"from": admin})
    return factory


# Create a DeepFreeze through a Factory call
def create_DeepFreeze(factory, user, hint, password):
    factory.createDeepFreeze(hint, Web3.keccak(text=password), {"from": user})


# Return a DeepFreeze object
def get_DeepFreezeContract(factory, admin, user, freezerID):
    deepfreeze_address = factory.userFreezer(user, freezerID, {"from": admin})
    with open("DeepFreeze_abi.json") as f:
        abi = json.load(f)
    deepfreeze = Contract.from_abi("deepfreeze", deepfreeze_address, abi)
    return deepfreeze


# Deploy the factory, create one freezer and return the DeepFreeze object
def deploy_Factory_DeepFreeze(admin, user, hint, password):
    factory = deploy_Factory(admin)
    create_DeepFreeze(factory, user, hint, password)
    deepfreeze = get_DeepFreezeContract(factory, admin, user, 0)
    return deepfreeze
