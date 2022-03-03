from brownie import (
    TrueFreezeGovernor,
    frToken,
    MockWETH,
    NonFungiblePositionManager,
    FRZtoken,
    MultiRewards,
)
from web3 import Web3


def deploy_wETH(admin):
    weth = MockWETH.deploy({"from": admin})
    return weth


def deploy_frToken(admin, name, symbol):
    frtoken = frToken.deploy(NAME, SYMBOL, {"from": admin})
    return frtoken


def deploy_NFTPosition(admin):
    nftPosition = NonFungiblePositionManager.deploy({"from": admin})
    return nftPosition


def deploy_FRZtoken(admin):
    FRZ_SUPPLY = Web3.toWei(1000000000, "Ether")
    frz = FRZtoken.deploy(FRZ_SUPPLY, {"from": admin})
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
    frtoken = deploy_frToken(admin, name, symbol)
    nft = deploy_NFTPosition(admin)
    frz = deploy_FRZtoken(admin)
    staking = deploy_stakingContract(admin, frz)
    freeze = deploy_freeze(admin, weth, frtoken, nft, staking)
    return weth, frtoken, nft, staking, frz, freeze


def setGovernor(admin, frtoken, nft, freeze):
    frtoken.setOnlyGovernor(freeze.address, {"from": admin})
    nft.setOnlyGovernor(freeze.address, {"from": admin})


def setStakingReward(admin, staking, freeze, frtoken, weth):
    DISTRIB_OVER = 7 * 24 * 3600
    staking.addReward(weth, freeze, DISTRIB_OVER, {"from": admin})
    staking.addReward(frtoken, freeze, DISTRIB_OVER, {"from": admin})


def deployAndParametrize(admin):
    (weth, frtoken, nft, staking, frz, freeze) = deploy_contracts(admin)
    setGovernor(admin, frtoken, nft, freeze)
    setStakingReward(admin, staking, freeze, frtoken, weth)
    return weth, frtoken, nft, staking, frz, freeze
