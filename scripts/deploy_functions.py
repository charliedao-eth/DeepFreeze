from brownie import (
    TrueFreezeGovernor,
    frToken,
    MockWETH,
    NonFungiblePositionManager,
    FRZtoken,
    MultiRewards,
    StakingRewards,
)
from web3 import Web3

NAME = "frETH"
SYMBOL = "frETH"


def deploy_wETH(admin):
    weth = MockWETH.deploy({"from": admin})
    return weth


def deploy_frToken(admin):
    frtoken = frToken.deploy(NAME, SYMBOL, {"from": admin})
    return frtoken


def deploy_staking_frToken(admin, frToken):
    staking_frToken = StakingRewards.deploy(admin, frToken, {"from": admin})
    return staking_frToken


def deploy_NFTPosition(admin):
    nftPosition = NonFungiblePositionManager.deploy({"from": admin})
    return nftPosition


def deploy_FRZtoken(admin, staking_frToken):
    frz = FRZtoken.deploy(admin, staking_frToken, "FRZ", {"from": admin})
    return frz


def deploy_stakingContract(admin, frz):
    staking = MultiRewards.deploy(admin, frz.address, {"from": admin})
    return staking


def deploy_freeze(admin, weth, frtoken, nftPosition, staking):
    freeze = TrueFreezeGovernor.deploy(
        weth, frtoken, nftPosition, staking, {"from": admin}
    )
    return freeze


def deploy_contracts(admin):
    weth = deploy_wETH(admin)
    frtoken = deploy_frToken(admin)
    nft = deploy_NFTPosition(admin)
    staking_frToken = deploy_staking_frToken(admin, frtoken)
    frz = deploy_FRZtoken(admin, staking_frToken)
    staking = deploy_stakingContract(admin, frz)
    freeze = deploy_freeze(admin, weth, frtoken, nft, staking)
    return weth, frtoken, nft, staking, frz, freeze, staking_frToken


def setGovernor(admin, frtoken, nft, freeze):
    frtoken.setOnlyGovernor(freeze.address, {"from": admin})
    nft.setOnlyGovernor(freeze.address, {"from": admin})


def setStakingReward(admin, staking, freeze, frtoken, weth, staking_frToken, frz):
    DISTRIB_OVER = 7 * 24 * 3600
    staking.addReward(weth, freeze, DISTRIB_OVER, {"from": admin})
    staking.addReward(frtoken, freeze, DISTRIB_OVER, {"from": admin})
    DISTRIB_OVER = 365 * 86400
    staking_frToken.addReward(frz, frz, DISTRIB_OVER, {"from": admin})


def deployAndParametrize(admin):
    (weth, frtoken, nft, staking, frz, freeze, staking_frToken) = deploy_contracts(
        admin
    )
    setGovernor(admin, frtoken, nft, freeze)
    setStakingReward(admin, staking, freeze, frtoken, weth, staking_frToken, frz)
    return weth, frtoken, nft, staking, frz, freeze, staking_frToken
