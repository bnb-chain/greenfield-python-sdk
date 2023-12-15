# Getting Started with the Greenfield Python SDK

BNB Greenfield is a revolutionary blockchain and storage platform that aims to transform the data economy by decentralizing data management and ownership. Greenfield sets itself apart by allowing Ethereum-compatible addresses to manage both data and token assets, linking data permissions and management logic onto BNB Smart Chain (BSC), and providing developers with similar API primitives and performance as existing Web2 cloud storage.

This tutorial will guide you through the Greenfield Python SDK, a software development kit specifically designed to interact with the BNB Greenfield platform using Python.

For more information about Greenfield, please visit the [official website](https://docs.bnbchain.org/greenfield-docs).

## What is the Greenfield Python SDK?

The Greenfield Python SDK is a Python library that facilitates interaction with the BNB Greenfield platform. With this SDK, developers can create applications that interact with Greenfield's decentralized storage and blockchain. It provides functions to interact with storage providers, manage data objects, handle account configurations, and more.

## Setting up the Environment

Before using the Greenfield Python SDK, ensure Python 3.9 or later is installed on your system. You can check your Python version by running the following command in your terminal:

```bash
python --version
```

If Python is not installed or you have an older version, you can download the latest version from the [official Python website](https://www.python.org/downloads/).

To install the Greenfield Python SDK, go to the [SDK repo](https://github.com/bnb-chain/greenfield-python-sdk) and clone or download it. 

To be able to handle the creation of objects, you need to include the `data-redundancy-generator-bridge` library. You will need to build it, and generate a `.so` or `.dll` file (depending on your OS). 

To build this library go to the [data-redundancy-generator-bridge repository](https://github.com/bnb-chain/data-redundancy-generator-bridge) and clone or download it.


After that follow the steps in the README.md file to generate the library. Note that you need to have go installed.

Finally, copy the generated `data-redundancy-generator-bridge` library output into the `greenfield_python_sdk/go_library` folder and install the SDK with pip.

```bash
cd greenfield-python-sdk
pip install .
```

This command installs the Greenfield Python SDK and its dependencies.

## Using the Greenfield Python SDK

Now that you have the SDK installed, let's walk through an example of how you can use it to interact with Greenfield.

We will start by creating a simple Python script that uses the Greenfield Python SDK to create a bucket and add an object to it, and then delete the object and the bucket.

You can find the full code for this example in the `examples` folder or at the bottom of the post. It also contains an image that you can use to test the example.

To view the image that you are going to upload, you can go to https://dcellar.io/ and search for the bucket name `demobucket` and the object name `demoimage.png`. 

To be able to see the bucket you need to connect with your own wallet using Metamask or Trust Wallet. 

### Example walthrough

First, import the required modules from the Greenfield Python SDK:

```python
import asyncio
import io

from greenfield_python_sdk.config import NetworkConfiguration, NetworkTestnet, get_account_configuration
from greenfield_python_sdk.greenfield_client import GreenfieldClient
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.bucket import CreateBucketOptions
from greenfield_python_sdk.models.object import CreateObjectOptions, PutObjectOptions
from greenfield_python_sdk.protos.greenfield.storage import VisibilityType
```

Next, initialize the Greenfield client with your private key. You have two options for doing this, exporting your private key in the terminal or hardcoding it in code. 

We recomend to do the following (export):

```bash
export private_key="your private key"
```

And then in your code:

```python
config = get_account_configuration()
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
key_manager = KeyManager(private_key=config.private_key)
    
async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
    await client.async_init()
```

In the above snippet, `get_account_configuration()` retrieves your account's configuration, including the private key. The `KeyManager` class is used to manage your private key. Finally, a `GreenfieldClient` instance is created with the network configuration of testnet and a key manager.

Now, let's create a bucket on Greenfield. A bucket is a logical unit of storage where you can store data objects:

```python
bucket_name = "demobucket"

# Get a Storage Provider
sp = await client.blockchain_client.get_active_sps()

# Create Bucket
tx_hash = await client.bucket.create_bucket(
    bucket_name,
    primary_sp_address=sp[0]["operator_address"],
    opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
)
await client.basic.wait_for_tx(hash=tx_hash)
```

In this snippet, we first query for an available (in service) storage provider and then retrieve the first one on the list. We then create a bucket with `create_bucket()`, providing the bucket name, the address of a primary storage provider, and other options.

Note that we use the wait_for_tx() method because the Greenfield Python SDK is asynchronous, requiring us to wait for the transaction to be completed before continuing.

**Notes:** 
- If the bucket already exists, this will fail.
- This example uses the `get_active_sps()` method to get the storage providers owned by BNB Chain on Testnet. It is recommended to use the `client.blockchain_client.sp.get_first_in_service_storage_provider()` method to get the first storage provider that is in service on the Mainnet.

Next, let's add an object to our bucket:

```python
object_name = "demoimage.png"

# Create Object
with open('./examples/img.png', 'rb') as f:
    file = f.read()
content = io.BytesIO(file)

tx_hash = await client.object.create_object(
    bucket_name,
    object_name,
    reader=content,
    opts=CreateObjectOptions(content_type="image/png"),
)
await client.basic.wait_for_tx(hash=tx_hash)

# Put Object
await client.object.put_object(
    bucket_name=bucket_name,
    object_name=object_name,
    object_size=content.getbuffer().nbytes,
    reader=content.getvalue(),
    opts=PutObjectOptions(content_type="image/png")
)

await asyncio.sleep(5)
```

In this example, we read an image file (`img.png`) and use the `create_object()` method to create a transaction with the storage provider. We then add this object to our bucket with the `put_object()` function. It is recommended to add a delay after using the function `put_object()` to ensure it's sealed on the storage provider's side.

The image can be seen at https://dcellar.io/ by searching for the bucket name `demobucket` and the object name `demoimage.png`.

You will need to use the same account that you used as the private key.

Finally, let's delete the object and the bucket:

```python
# Delete Object
tx_hash = await client.object.delete_object(
    bucket_name=bucket_name,
    object_name=object_name,
)
await client.basic.wait_for_tx(hash=tx_hash)

# Delete Bucket
tx_hash = await client.bucket.delete_bucket(
    bucket_name=bucket_name
)
await client.basic.wait_for_tx(hash=tx_hash)
```

At the end of the script, add the following to execute the main function using asyncio:

```python
if __name__ == "__main__":
    asyncio.run(main())

```

And that's it! You have successfully created a bucket, added an object to it, and deleted the object and the bucket.

To run the script, use the following command:

```bash
python examples/demo.py
```

## Full code

The following is the full code for the above example, you can also find it in the `examples` folder:


```python
import asyncio
import io

from greenfield_python_sdk.config import NetworkConfiguration, NetworkTestnet, get_account_configuration
from greenfield_python_sdk.greenfield_client import GreenfieldClient
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.bucket import CreateBucketOptions
from greenfield_python_sdk.models.object import CreateObjectOptions, PutObjectOptions
from greenfield_python_sdk.protos.greenfield.storage import VisibilityType

config = get_account_configuration()


async def main():
    network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
    key_manager = KeyManager(private_key=config.private_key)
    
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        bucket_name = "demobucket"
        object_name = "demoimage.png"

        # Get a Storage Provider
        sp = await client.blockchain_client.get_active_sps()

        # Create Bucket
        tx_hash = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sp[0]["operator_address"],
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        await client.basic.wait_for_tx(hash=tx_hash)

        # Create Object
        with open('./examples/img.png', 'rb') as f:
            file = f.read()
        content = io.BytesIO(file)

        tx_hash = await client.object.create_object(
            bucket_name,
            object_name,
            reader=content,
            opts=CreateObjectOptions(content_type="image/png"),
        )
        await client.basic.wait_for_tx(hash=tx_hash)
        
        # Put Object
        await client.object.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            object_size=content.getbuffer().nbytes,
            reader=content.getvalue(),
            opts=PutObjectOptions(content_type="image/png")
        )

        await asyncio.sleep(5)

        breakpoint() # View the object in the explorer https://dcellar.io/

        # Delete Object
        tx_hash = await client.object.delete_object(
            bucket_name=bucket_name,
            object_name=object_name,
        )
        await client.basic.wait_for_tx(hash=tx_hash)

        # Delete Bucket
        tx_hash = await client.bucket.delete_bucket(
            bucket_name=bucket_name
        )
        await client.basic.wait_for_tx(hash=tx_hash)


if __name__ == "__main__":
    asyncio.run(main())

```


## Use Cases for the Greenfield Python SDK

The Greenfield Python SDK can solve a wide range of problems related to decentralized storage and data management. For instance, developers can use it to create decentralized applications (dApps) that interact with the Greenfield platform. These applications can provide user-friendly interfaces for managing data on Greenfield, or they can provide services that leverage Greenfield's capabilities.

Examples of potential applications include:

- Personal cloud storage services
- Content delivery networks
- Decentralized databases
- Blockchain-based data marketplaces

The Greenfield Python SDK provides a powerful and flexible way to interact with the BNB Greenfield platform. By combining the power of blockchain with the flexibility of Python, developers can create a wide range of innovative applications that leverage decentralized storage.
