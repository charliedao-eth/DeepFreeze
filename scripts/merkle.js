const ethers = require("ethers");
const { MerkleTree } = require('merkletreejs');
const keccak256 = require('keccak256')


const users = require('./airdrop_needs1e18_formatted.json');

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

const merkleJsonExport = users.map(function (user, index) {
    return Object.assign({}, user, {
        amount: user.amount.toString(),
        merkleProof: merkleTree.getHexProof(elements[index])
    })
});

console.log(JSON.stringify(merkleJsonExport));
