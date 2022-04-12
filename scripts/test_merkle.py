from brownie import FRZtoken, MerkleDistributor
from scripts.deploy_main import DEPLOYER

merkle = MerkleDistributor.deploy(
    "0x2823d7df030bc8e00ae6a7b9891c14720a60c3d97d2d639ce68249f57783768a",
    {"from": accounts[0]},
)
token = FRZtoken.deploy(merkle, accounts[6], "FRZ", {"from": accounts[0]})
merkle.initialize(token, {"from": accounts[0]})

proof = [
    "0x3c60e097c59a73bdfc01ec9b48e4931ff32d2fce7d11ece3e97487cfaa600bcf",
    "0xd999846254f1dce87979409b2ce6aa0e4d0106304f9fbf3861f902551b08a226",
]
tx = merkle.claim(
    0,
    "0x96b6de62f4cCb4381937b8446D5F0aA7c153aC29",
    1000000000000000000000,
    proof,
    {"from": DEPLOYER},
)
