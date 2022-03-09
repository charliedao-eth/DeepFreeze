from brownie import (
    TrueFreezeGovernor,
    frToken,
    NonFungiblePositionManager,
    FRZtoken,
    MultiRewards,
    StakingRewards,
    MerkleDistributor,
    accounts,
    config,
    network,
)
from web3 import Web3

DEPLOYER = accounts.add(config["wallets"]["from_key"])
REQUIRED_CONFIRMATIONS = 4

TOKEN_NAME = "frETH"
TOKEN_SYMBOL = "frETH"
WETH_ADDRESS = config["networks"][network.show_active()]["WETH_ADDRESS"]
FRZ_DISTRIB_REWARDS_OVER = 7 * 86400
frToken_DISTRIB_REWARDS_OVER = 365 * 86400


def _tx_params():
    return {
        "from": DEPLOYER,
        "required_confs": REQUIRED_CONFIRMATIONS,
    }


def main():
    # Deploy frToken
    frContract = frToken.deploy(
        TOKEN_NAME, TOKEN_SYMBOL, _tx_params(), publish_source=True
    )

    # Deploy merkle tree
    merkle = MerkleDistributor.deploy(
        "0x37e5906e14199d5bed9cd6052ba795e68e8025ba46a4b2f7f4d92a31fde66411",
        _tx_params(),
        publish_source=True,
    )

    # Deploy frToken staking contract
    frStaking = StakingRewards.deploy(
        DEPLOYER, frContract, _tx_params(), publish_source=True
    )

    # Deploy merkle tree
    frzToken = FRZtoken.deploy(merkle, frStaking, _tx_params(), publish_source=True)

    # Init Merkle contract & Staking contract
    merkle.initialize(frContract, _tx_params())
    frStaking.addReward(frzToken, frzToken, frToken_DISTRIB_REWARDS_OVER, _tx_params())

    # Deploy FRZ staking contract
    stakingContract = MultiRewards.deploy(
        DEPLOYER, frzToken, _tx_params(), publish_source=True
    )

    # Deploy NFT contract
    nftContract = NonFungiblePositionManager.deploy(_tx_params(), publish_source=True)

    # Deploy TrueFreezeGovernor
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
        WETH_ADDRESS, trueFreeze, FRZ_DISTRIB_REWARDS_OVER, _tx_params()
    )
    stakingContract.addReward(
        frContract, trueFreeze, FRZ_DISTRIB_REWARDS_OVER, _tx_params()
    )

    print(f"frToken deployed at {frContract}")
    print(f"FRZ deployed at {frzToken}")
    print(f"Merkle tree deployed at {merkle}")
    print(f"NonFungiblePositionManager deployed at {nftContract}")
    print(f"frToken Staking contract deployed at {frStaking}")
    print(f"FRZ Staking contract deployed at {stakingContract}")
    print(f"TrueFreezeGovernor deployed at {trueFreeze}")
