from brownie import (
    FreezerGovernor,
    frETH,
    MockWETH,
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
    FRZ_SUPPLY = Web3.toWei(1000000000, "Ether")
    frz = FRZtoken.deploy(FRZ_SUPPLY, {"from": admin})
    return frz


def deploy_stakingContract(admin, frz):
    staking = MultiRewards.deploy(admin, frz.address, {"from": admin})
    return staking


def deploy_DeepFreeze(admin, weth, freth, nftPosition, staking):
    deepfreeze = FreezerGovernor.deploy(
        weth, freth, nftPosition, staking, {"from": admin}
    )
    return deepfreeze


def deploy_contracts(admin):
    weth = deploy_wETH(admin)
    freth = deploy_frETH(admin)
    nft = deploy_NFTPosition(admin)
    frz = deploy_FRZtoken(admin)
    staking = deploy_stakingContract(admin, frz)
    deepfreeze = deploy_DeepFreeze(admin, weth, freth, nft, staking)
    return weth, freth, nft, staking, frz, deepfreeze


def setGovernor(admin, freth, nft, deepfreeze):
    freth.setOnlyGovernor(deepfreeze.address, {"from": admin})
    nft.setOnlyGovernor(deepfreeze.address, {"from": admin})


def setStakingReward(admin, staking, deepfreeze, freth, weth):
    DISTRIB_OVER = 7 * 24 * 3600
    staking.addReward(weth, deepfreeze, DISTRIB_OVER, {"from": admin})
    staking.addReward(freth, deepfreeze, DISTRIB_OVER, {"from": admin})


def deployAndParametrize(admin):
    (weth, freth, nft, staking, frz, deepfreeze) = deploy_contracts(admin)
    setGovernor(admin, freth, nft, deepfreeze)
    setStakingReward(admin, staking, deepfreeze, freth, weth)
    return weth, freth, nft, staking, frz, deepfreeze
