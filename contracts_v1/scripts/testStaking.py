from scripts.deploy_functions import deployAndParametrize
from web3 import Web3


admin = accounts[0]
user = accounts[1]
value = Web3.toWei(1, "Ether")

weth, freth, nft, staking, frz, deepfreeze = deployAndParametrize(admin)


frz.approve(staking, 100000, {"from": admin})
staking.stake(100000, {"from": admin})

weth.deposit({"from": user, "value": value})
weth.approve(deepfreeze.address, value, {"from": user})
tx = deepfreeze.lockWETH(value, 365, {"from": user})


chain.sleep(3600 * 24 * 300)
chain.mine()
penalty = deepfreeze.getUnlockCost(1)
freth.approve(deepfreeze, penalty, {"from": user})
tx2 = deepfreeze.withdrawWETH(1, {"from": user})

# check how tokenURI evolve when withdraw
