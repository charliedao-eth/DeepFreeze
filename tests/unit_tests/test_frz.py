from brownie import accounts, exceptions, chain
from scripts.deploy_functions import deploy_contracts, deployAndParametrize
from scripts.utils import calculateWithdrawCost

from web3 import Web3
import pytest


def test_Init(admin):
    (
        WAsset,
        freth,
        nft,
        staking,
        frz,
        deepfreeze,
        staking_frToken,
    ) = deployAndParametrize(admin)
    assert frz.balanceOf(admin) == frz.totalSupply()


def test_mint(admin):
    (
        WAsset,
        freth,
        nft,
        staking,
        frz,
        deepfreeze,
        staking_frToken,
    ) = deployAndParametrize(admin)
    nToken = frz.getTokenToMint()
    frz.mint({"from": admin})
    assert frz.balanceOf(staking_frToken) == nToken
