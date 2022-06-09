const ethers = require("ethers");
const { MerkleTree } = require('merkletreejs');
const keccak256 = require('keccak256')
const fs = require('fs');


const users = require('./airdrop_has1e18_strings.json');

// equal to MerkleDistributor.sol #keccak256(abi.encodePacked(account, amount));
const elements = users.map((x) =>
    ethers.utils.solidityKeccak256(["uint256", "address", "uint256"], [x.index, x.address, x.amount])
);

var merkleTree = new MerkleTree(elements, keccak256, { sort: true });

var root = merkleTree.getHexRoot();

var leaf = elements[1]; // To get the proof of the address change the idx of elements
var proof = merkleTree.getHexProof(leaf);
console.log(root);
console.log(proof)

var merkleJsonExport = users.map(function (user, index) {
    const userObj = Object.assign({}, user, {
        amount: user.amount.toString(),
        merkleProof: merkleTree.getHexProof(elements[index])
    })
    console.log(userObj);
    return userObj;
});
merkleJsonExport = JSON.stringify(merkleJsonExport);


try {
    fs.writeFileSync('./users_export.json', merkleJsonExport);
    // file written successfully
    console.log("done");
} catch (err) {
    console.error(err);
}