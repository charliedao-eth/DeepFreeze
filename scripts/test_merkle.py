from brownie import FRZtoken, MerkleDistributor

merkle = MerkleDistributor.deploy(
    "0x37e5906e14199d5bed9cd6052ba795e68e8025ba46a4b2f7f4d92a31fde66411",
    {"from": accounts[0]},
)
token = FRZtoken.deploy(merkle, accounts[6], {"from": accounts[0]})
merkle.initialize(token, {"from": accounts[0]})

proof = [
    "0xc9c20ecb5de271fc871e09dfd5cbb8e96f10f37481f4a201bde8964ae39da423",
    "0x606212bf954a7fa9cbfb5441ff569117b57ee0c5d1dafbcb4ddd3ec60cce7dfd",
]
merkle.claim(1, accounts[1].address, 15, proof, {"from": accounts[1]})
