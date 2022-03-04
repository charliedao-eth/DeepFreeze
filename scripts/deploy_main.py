from brownie import (
    TrueFreezeGovernor,
    frToken,
    NonFungiblePositionManager,
    FRZtoken,
    MultiRewards,
    accounts,
    config,
    network,
)
from web3 import Web3

DEPLOYER = accounts.add(config["wallets"]["from_key"])
REQUIRED_CONFIRMATIONS = 4

TOKEN_NAME = "frETH"
TOKEN_SYMBOL = "frETH"
FRZ_SUPPLY = Web3.toWei(1000000000, "Ether")
WETH_ADDRESS = config["networks"][network.show_active()]["WETH_ADDRESS"]
DISTRIB_REWARDS_OVER = 7 * 86400


def _tx_params():
    return {
        "from": DEPLOYER,
        "required_confs": REQUIRED_CONFIRMATIONS,
    }


def main():
    # First deploy contracts
    frContract = frToken.deploy(
        TOKEN_NAME, TOKEN_SYMBOL, _tx_params(), publish_source=True
    )
    nftContract = NonFungiblePositionManager.deploy(_tx_params(), publish_source=True)
    frzToken = FRZtoken.deploy(
        FRZ_SUPPLY, _tx_params(), publish_source=True
    )  # Will change when tokenomic apply
    stakingContract = MultiRewards.deploy(
        DEPLOYER, frzToken, _tx_params(), publish_source=True
    )
    trueFreeze = TrueFreezeGovernor.deploy(
        WETH_ADDRESS,
        frContract,
        nftContract,
        stakingContract,
        _tx_params(),
        publish_source=True,
    )

    # Set TrueFreeze admin
    frContract.setOnlyGovernor(trueFreeze.address, _tx_params())
    nftContract.setOnlyGovernor(trueFreeze.address, _tx_params())

    # Configure staking contract
    stakingContract.addReward(
        WETH_ADDRESS, trueFreeze, DISTRIB_REWARDS_OVER, _tx_params()
    )
    stakingContract.addReward(
        frContract, trueFreeze, DISTRIB_REWARDS_OVER, _tx_params()
    )

    print(f"frToken deployed at {frContract}")
    print(f"NonFungiblePositionManager deployed at {nftContract}")
    print(f"FRZ deployed at {frzToken}")
    print(f"Staking contract deployed at {stakingContract}")
    print(f"TrueFreezeGovernor deployed at {trueFreeze}")
