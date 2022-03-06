from brownie import (
    TrueFreezeGovernor,
    frToken,
    NonFungiblePositionManager,
    FRZtoken,
    MultiRewards,
    StakingRewards,
    accounts,
    config,
    network,
    MockWETH,
)
from web3 import Web3

DEPLOYER = accounts[0]
REQUIRED_CONFIRMATIONS = 4

TOKEN_NAME = "frETH"
TOKEN_SYMBOL = "frETH"
FRZ_SUPPLY = Web3.toWei(1000000000, "Ether")
DISTRIB_REWARDS_OVER = 7 * 86400


def _tx_params():
    return {
        "from": DEPLOYER,
    }

    # First deploy contracts


WETH = MockWETH.deploy({"from": accounts[0]})
frContract = frToken.deploy(TOKEN_NAME, TOKEN_SYMBOL, _tx_params())
nftContract = NonFungiblePositionManager.deploy(_tx_params())
frStaking = StakingRewards.deploy(DEPLOYER, frContract, _tx_params())
frzToken = FRZtoken.deploy(
    accounts[0], frStaking, _tx_params()
)  # Will change when tokenomic apply
frStaking.addReward(frzToken, frStaking, 365 * 86400, _tx_params())
stakingContract = MultiRewards.deploy(DEPLOYER, frzToken, _tx_params())
trueFreeze = TrueFreezeGovernor.deploy(
    WETH,
    frContract,
    nftContract,
    stakingContract,
    _tx_params(),
)

# Set TrueFreeze admin
frContract.setOnlyGovernor(trueFreeze.address, _tx_params())
nftContract.setOnlyGovernor(trueFreeze.address, _tx_params())

# Configure staking contract
stakingContract.addReward(WETH, trueFreeze, DISTRIB_REWARDS_OVER, _tx_params())
stakingContract.addReward(frContract, trueFreeze, DISTRIB_REWARDS_OVER, _tx_params())

user = accounts[1]
value = 100000000000000000
WETH.deposit({"from": user, "value": value})
WETH.approve(trueFreeze.address, value, {"from": user})
tx = trueFreeze.lockWAsset(value, 365 * 2, {"from": user})

from brownie import chain

chain.sleep(180 * 86400)
chain.mine()
frzToken.mint({"from": accounts[0]})
