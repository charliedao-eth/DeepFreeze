from brownie import FreezerGovernor, frETH, MockWETH, accounts, NFTPosition, FRZstaking
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


def deploy_FRZstaking(admin):
    frz = FRZstaking.deploy({"from": admin})
    return frz


def deploy_DeepFreeze(admin, weth, freth, nftPosition, frz):
    deepfreeze = FreezerGovernor.deploy(weth, freth, nftPosition, frz, {"from": admin})
    return deepfreeze


admin = accounts[0]
user = accounts[1]
value = Web3.toWei(1, "Ether")

weth = deploy_wETH(admin)
freth = deploy_frETH(admin)
nft = deploy_NFTPosition(admin)
frz = deploy_FRZstaking(admin)
deepfreeze = deploy_DeepFreeze(admin, weth, freth, nft, frz)
freth.setOnlyGovernor(deepfreeze.address)
nft.setOnlyGovernor(deepfreeze.address)

weth.deposit({"from": user, "value": value})
weth.approve(deepfreeze.address, value, {"from": user})
tx = deepfreeze.lockWETH(value, 365 * 2, {"from": user})

chain.sleep(3600 * 24 * 800)
chain.mine()
penalty = deepfreeze.getUnlockCost(1)
freth.approve(deepfreeze, penalty, {"from": user})
tx2 = deepfreeze.withdrawWETH(1, {"from": user})
