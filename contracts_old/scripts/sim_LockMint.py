from scripts.deploy_functions import create_DeepFreeze, get_DeepFreezeContract
from web3 import Web3
from brownie import accounts, frETH, DeepFreezeFactory, FRZstaking, chain


token = frETH.deploy({"from": accounts[0]})
staking = FRZstaking.deploy({"from": accounts[0]})
factory = DeepFreezeFactory.deploy(
    token.address, staking.address, {"from": accounts[0]}
)
token.setOnlyFactory(factory.address, {"from": accounts[0]})
create_DeepFreeze(factory, accounts[1], "hello", "hello")
deepfreeze = get_DeepFreezeContract(factory, accounts[0], accounts[1], 0)
deepfreeze.deposit({"from": accounts[1], "value": Web3.toWei(2, "Ether")})
deepfreeze.lock(365, {"from": accounts[1]})

chain.sleep(3600 * 24 * 300)
chain.mine()
deepfreeze.withdraw("hello", {"from": accounts[1]})
