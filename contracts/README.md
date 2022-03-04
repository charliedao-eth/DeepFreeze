# TrueFreeze Contracts

This repository is the set of smart contracts that are used for the TrueFreeze protocol.
It contains the requirements, code, deployment scripts, and tests necessary for the
core protocol.

## Requirements

To run the project you need:

- Python 3.8 local development environment and Node.js 10.x development environment for Ganache.
- Brownie local environment setup. See instructions for how to install it
  [here](https://eth-brownie.readthedocs.io/en/stable/install.html).
- Local env variables for [Etherscan API](https://etherscan.io/apis) and
  [Infura](https://infura.io/) (`ETHERSCAN_TOKEN`, `WEB3_INFURA_PROJECT_ID`,`PRIVATE_KEY`).
- Local Ganache environment installed with `npm install -g ganache`.

Compile the Smart Contracts:

```bash
brownie compile 
```

## Running the Tests

The [test suite](tests) contains common tests for all Curve pools, as well as unique per-pool tests. To run the entire suite:

```bash
brownie test
```

## Deployment

To deploy the contract : 

```bash
brownie run ./scripts/deploy_main.py --network yourNetwork (rinkeby/kovan ...)
```

