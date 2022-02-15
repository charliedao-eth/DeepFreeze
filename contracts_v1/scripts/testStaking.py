from brownie import (
    FreezerGovernor,
    frETH,
    MockWETH,
    accounts,
    NFTPosition,
    FRZtoken,
    MultiRewards,
)
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


def deploy_FRZtoken(admin):
    frz = FRZtoken.deploy(1000000000 * 10 ** 18, {"from": admin})
    return frz


def deploy_stakingContract(admin, frz):
    staking = MultiRewards.deploy(admin, frz.address, {"from": admin})
    return staking


def deploy_DeepFreeze(admin, weth, freth, nftPosition, frz):
    deepfreeze = FreezerGovernor.deploy(weth, freth, nftPosition, frz, {"from": admin})
    return deepfreeze


admin = accounts[0]
user = accounts[1]
value = Web3.toWei(1, "Ether")

weth = deploy_wETH(admin)
freth = deploy_frETH(admin)
nft = deploy_NFTPosition(admin)
frz = deploy_FRZtoken(admin)
staking = deploy_stakingContract(admin, frz)
deepfreeze = deploy_DeepFreeze(admin, weth, freth, nft, staking)
staking.addReward(weth, deepfreeze, 60, {"from": admin})
staking.addReward(freth, deepfreeze, 60, {"from": admin})
frz.approve(staking, 100000, {"from": admin})
staking.stake(100000, {"from": admin})

freth.setOnlyGovernor(deepfreeze.address)
nft.setOnlyGovernor(deepfreeze.address)

weth.deposit({"from": user, "value": value})
weth.approve(deepfreeze.address, value, {"from": user})
tx = deepfreeze.lockWETH(value, 365 * 2, {"from": user})


chain.sleep(3600 * 24 * 300)
chain.mine()
penalty = deepfreeze.getUnlockCost(1)
freth.approve(deepfreeze, penalty, {"from": user})
tx2 = deepfreeze.withdrawWETH(1, {"from": user})
