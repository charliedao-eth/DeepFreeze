from brownie import FRZtoken, accounts
from web3 import Web3


def deploy_token():
    token = FRZtoken.deploy({"from": accounts[0]})
    return token


def main():
    token = deploy_token()
    tokenToMint = []
    newSupply = []
    for i in range(100):
        oldSupply = Web3.fromWei(token.totalSupply(), "Ether")
        tokenToMint.append(Web3.fromWei(token.getTokenToMint(), "Ether"))
        token.mint({"from": accounts[0]})
        newSupply.append(Web3.fromWei(token.totalSupply(), "Ether"))

    for i in range(100):
        print(
            f"Year {i},new supply of {newSupply[i]/1000000} M tokenMinted : {tokenToMint[i]/ 1000000} M "
        )
