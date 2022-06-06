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
REQUIRED_CONFIRMATIONS = 1
PUBLISHED = config["networks"][network.show_active()]["publish"]

frTOKEN_NAME = config["networks"][network.show_active()]["frTokenName"]
frTOKEN_SYMBOL = config["networks"][network.show_active()]["frTokenSymbol"]
FRZ_SYMBOL = config["networks"][network.show_active()]["FRZ_SYMBOL"]
WASSET_ADDRESS = config["networks"][network.show_active()]["WASSET_ADDRESS"]
FRZ_DISTRIB_REWARDS_OVER = 7 * 86400
frToken_DISTRIB_REWARDS_OVER = 365 * 86400
MERKLE_TREE = "0xc54a775732dc2f2f2da0f6021b744201a2c185a37ff9b7abc607e85f39ba6af1"


def _tx_params():
    return {
        "from": DEPLOYER,
        "required_confs": REQUIRED_CONFIRMATIONS,
    }


def main():
    # Deploy frToken
    frContract = frToken.deploy(
        frTOKEN_NAME, frTOKEN_SYMBOL, _tx_params(), publish_source=PUBLISHED
    )

    # Deploy merkle tree
    merkle = MerkleDistributor.deploy(
        MERKLE_TREE,
        _tx_params(),
        publish_source=PUBLISHED,
    )

    # Deploy frToken staking contract
    frStaking = StakingRewards.deploy(
        DEPLOYER, frContract, _tx_params(), publish_source=PUBLISHED
    )

    # Deploy merkle tree
    frzToken = FRZtoken.deploy(
        merkle, frStaking, FRZ_SYMBOL, _tx_params(), publish_source=PUBLISHED
    )

    # Init Merkle contract & Staking contract
    merkle.initialize(frzToken, _tx_params())
    frStaking.addReward(frzToken, frzToken, frToken_DISTRIB_REWARDS_OVER, _tx_params())

    # Deploy FRZ staking contract
    stakingContract = MultiRewards.deploy(
        DEPLOYER, frzToken, _tx_params(), publish_source=PUBLISHED
    )

    # Deploy NFT contract
    nftContract = NonFungiblePositionManager.deploy(
        _tx_params(), publish_source=PUBLISHED
    )

    # Deploy TrueFreezeGovernor
    trueFreeze = TrueFreezeGovernor.deploy(
        WASSET_ADDRESS,
        frContract,
        nftContract,
        stakingContract,
        _tx_params(),
        publish_source=PUBLISHED,
    )

    # Set TrueFreeze admin

    frContract.setOnlyGovernor(trueFreeze.address, _tx_params())
    nftContract.setOnlyGovernor(trueFreeze.address, _tx_params())

    # Configure staking contract
    stakingContract.addReward(
        WASSET_ADDRESS, trueFreeze, FRZ_DISTRIB_REWARDS_OVER, _tx_params()
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
