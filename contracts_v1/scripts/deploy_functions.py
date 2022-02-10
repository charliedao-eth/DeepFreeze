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


def deploy_contracts(admin):
    weth = deploy_wETH(admin)
    freth = deploy_frETH(admin)
    nft = deploy_NFTPosition(admin)
    frz = deploy_FRZstaking(admin)
    deepfreeze = deploy_DeepFreeze(admin, weth, freth, nft, frz)
    return weth, freth, nft, frz, deepfreeze


def deployAndSetAdmin(admin):
    (weth, freth, nft, frz, deepfreeze) = deploy_contracts(admin)
    freth.setOnlyGovernor(deepfreeze.address)
    nft.setOnlyGovernor(deepfreeze.address)
    return weth, freth, nft, frz, deepfreeze
