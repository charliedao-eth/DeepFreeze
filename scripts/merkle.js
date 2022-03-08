const ethers = require("ethers");
const { MerkleTree } = require('merkletreejs');
const keccak256 = require('keccak256')


const users = [
    { index: 0, address: "0x66aB6D9362d4F35596279692F0251Db635165871", amount: 10 },
    { index: 1, address: "0x33A4622B82D4c04a53e170c638B944ce27cffce3", amount: 15 },
    { index: 2, address: "0x0063046686E46Dc6F15918b61AE2B121458534a5", amount: 20 },
    { index: 3, address: "0x21b42413bA931038f35e7A5224FaDb065d297Ba3", amount: 30 },
];

// equal to MerkleDistributor.sol #keccak256(abi.encodePacked(account, amount));
const elements = users.map((x) =>
    ethers.utils.solidityKeccak256(["uint256", "address", "uint256"], [x.index, x.address, x.amount])
);

const merkleTree = new MerkleTree(elements, keccak256, { sort: true });

const root = merkleTree.getHexRoot();

const leaf = elements[1];
const proof = merkleTree.getHexProof(leaf);
console.log(root);
console.log(proof)