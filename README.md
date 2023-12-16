# Greenfield Python SDK

## Disclaimer
**The software and related documentation are under active development, all subject to potential future change without
notification and not ready for production use. The code and security audit have not been fully completed and not ready
for any bug bounty. We advise you to be careful and experiment on the network at your own risk. Stay safe out there.**

**Parts of the codebase might be broken or not up to date**

## Introduction

Greenfield Python SDK is a Python package for interacting with the Greenfield API. 

It provides an asynchronous client that can be used to interact with the Greenfield blockchain API and the Greenfield storage provider.

This SDK support latest Greenfield Mainnet version (v1.1.0).

For more information about the Greenfield Python SDK, please check the following website: [Greenfield Python SDK](https://docs.bnbchain.org/greenfield-python-sdk/)

## Installation

First you will need to `generate a shared library` to be able to use the object module.

The format is (`.so` or `.dll`), depending of the SO that you have.

To generate it go to the [data-redundancy-generator-bridge](https://github.com/bnb-chain/data-redundancy-generator-bridge) repository and follow the steps in the README.md file.


After that you will need to clone the greenfield-python-sdk. You can also download it instead.

```bash
git clone https://github.com/bnb-chain/greenfield-python-sdk
cd greenfield-python-sdk
```

Now copy the generated shared library output into `greenfield_python_sdk/go_library` folder. 

And finally 
    
```bash
pip install .
```


## Quickstart
```python
import asyncio

from greenfield_python_sdk.config import NetworkConfiguration, NetworkTestnet, KeyManager
from greenfield_python_sdk.greenfield_client import GreenfieldClient

async def main():
    network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
    key_manager = KeyManager(private_key="key")
    
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        # Get the account information
        account = await client.account.get_account(address=key_manager.address)

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- [x] Protobuf support
- [x] Asynchronous Greenfield blockchain API client
- [x] Asynchronous Greenfield storage provider API client
- [x] Asynchronous Greenfield mixed client

### Modules

- [x] Account
- [x] Basic
- [x] Challenge
- [x] CrossChain
- [x] Distribution
- [x] Feegrant
- [x] Group
- [x] Object
- [x] Payment
- [x] Proposal
- [x] Storage Provider
- [x] Validator (Limited functionality)
- [x] Virtual Group

## Prerequisites

To use the Greenfield Python SDK, you need to have the following:

- Python 3.9 or later
- Please include the `generated shared library` (`.so` or `.dll`) from the [data-redundancy-generator-bridge](https://github.com/bnb-chain/data-redundancy-generator-bridge) repository into the `greenfield_python_sdk/go_library` folder. These files are necessary for adding an object to a storage provider.


## Testing

To run the tests, use the following command:

```bash
make test-unit
make test-e2e
```

If you want to create transactions and upload objects as part of the tests, you will need to export a private_key with funds as an environment variable:

```bash
export private_key=...
```


```bash
make test-e2e-complete
```

You can also test the creation of validators by using a local greenfield node.

```bash
export host=http://localhost
export port=26750
export chain_id=9000

make test-e2e-local
```

## Development

To use the library you need to install its dependencies.
For that, we recomend to use poetry.

```bash
poetry install
```

or if you have `make` installed

```bash
make install
```

### Building protofiles

To be able to build the protofiles, you need to install the following:

- Install buf: [Buf installation link](https://buf.build/docs/installation)
- Install betterproto: `pip install betterproto` or with `poetry add betterproto`

And then run the following command:

```bash
make build
```

#### Notes

In the generated proto code, you will find the following:

- QueryStub is a service stub for handling query requests. In general, queries are read-only operations that fetch data from the blockchain without changing the state. For example, you might use a query to get the current state of a particular account, retrieve data from a smart contract, or fetch the parameters of a module.

- MsgStub is a service stub for handling message requests. Messages, on the other hand, are used to perform state-changing operations, such as sending tokens from one account to another, interacting with a smart contract, or updating the parameters of a module. These operations typically involve transactions that need to be signed and submitted to the network.

Basically GET and POST requests.

In reallity, we use the Tendermint RPC endpoint instead of using GRPC.

### Updating Greenfield version

To update the Greenfield version, you need to update the proto files by importing them from the Greenfield and the greenfield-cosmos-sdk repositories.

`https://github.com/bnb-chain/greenfield/tree/master/proto` (greenfield folder)

`https://github.com/bnb-chain/greenfield-cosmos-sdk/tree/master/proto` (amino, cosmos and tendermint folders)


Move those into the `proto` folder and then run the following command:

```bash
make build
```

And finally, update the `greenfield_python_sdk/config.py` file with the new Greenfield version. `GREENFIELD_VERSION`

## Reference

- [Greenfield](https://github.com/bnb-chain/greenfield): the greenfield blockchain
- [Greenfield-Cosmos-SDK](https://github.com/bnb-chain/greenfield-cosmos-sdk): the cosmos sdk forked by Greenfield
  
- [Greenfield-Contract](https://github.com/bnb-chain/greenfield-contracts): the cross chain contract for Greenfield that deployed on BSC network.
- [Greenfield-Tendermint](https://github.com/bnb-chain/greenfield-tendermint): the consensus layer of Greenfield blockchain.
- [Greenfield-Storage-Provider](https://github.com/bnb-chain/greenfield-storage-provider): the storage service infrastructures provided by either organizations or individuals.
- [Greenfield-Relayer](https://github.com/bnb-chain/greenfield-relayer): the service that relay cross chain package to both chains.
- [Greenfield-Cmd](https://github.com/bnb-chain/greenfield-cmd): the most powerful command line to interact with Greenfield system.
- [Awesome Cosmos](https://github.com/cosmos/awesome-cosmos): Collection of Cosmos related resources which also fits Greenfield.
