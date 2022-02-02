from brownie import FreezerGovernor, frETH, MockWETH, accounts, NFTPosition
from web3 import Web3


def deploy_wETH(admin):
    weth = MockWETH.deploy({"from": admin})
    return weth


def deploy_frETH(admin):
    freth = frETH.deploy({"from": admin})
    return freth


def deploy_NFTPosition(admin):
    nftPosition = NFTPosition.deploy({"from": admin})
    return nftPosition


def deploy_DeepFreeze(admin, weth, freth, nftPosition):
    deepfreeze = FreezerGovernor.deploy(weth, freth, nftPosition, {"from": admin})
    return deepfreeze


admin = accounts[0]
user = accounts[1]
value = Web3.toWei(1, "Ether")

weth = deploy_wETH(admin)
freth = deploy_frETH(admin)
nft = deploy_NFTPosition(admin)
deepfreeze = deploy_DeepFreeze(admin, weth, freth, nft)
freth.setOnlyGovernor(deepfreeze.address)
nft.setOnlyGovernor(deepfreeze.address)

weth.deposit({"from": user, "value": value})
weth.approve(deepfreeze.address, value, {"from": user})
deepfreeze.lock(value, 365 * 2, {"from": user})
