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


def deploy_DeepFreeze(admin, weth, freth, nftPosition, frz, staking):
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
    deepfreeze = deploy_DeepFreeze(admin, weth, freth, nft, frz, staking)
    return weth, freth, nft, staking, deepfreeze


def deployAndSetAdmin(admin):
    (weth, freth, nft, frz, staking, deepfreeze) = deploy_contracts(admin)
    freth.setOnlyGovernor(deepfreeze.address)
    nft.setOnlyGovernor(deepfreeze.address)
    return weth, freth, nft, staking, deepfreeze
