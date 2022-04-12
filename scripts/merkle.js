const ethers = require("ethers");
const { MerkleTree } = require('merkletreejs');
const keccak256 = require('keccak256')


const users = [
    { index: 0, address: "0x96b6de62f4cCb4381937b8446D5F0aA7c153aC29", amount: 1000000000000000000000n },
    { index: 1, address: "0x39E856863e5F6f0654a0b87B12bc921DA23D06BB", amount: 2000000000000000000000n },
    { index: 2, address: "0x459d04Fc1e24f1699846b8B88a270bC68aA71f46", amount: 3000000000000000000000n },
];

// equal to MerkleDistributor.sol #keccak256(abi.encodePacked(account, amount));
const elements = users.map((x) =>
    ethers.utils.solidityKeccak256(["uint256", "address", "uint256"], [x.index, x.address, x.amount])
);

const merkleTree = new MerkleTree(elements, keccak256, { sort: true });

const root = merkleTree.getHexRoot();

const leaf = elements[0]; // To get the proof of the address change the idx of elements
const proof = merkleTree.getHexProof(leaf);
console.log(root);
console.log(proof)