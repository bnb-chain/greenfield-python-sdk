import binascii
import hashlib
import os
from typing import Optional

import ecdsa
import hdwallets
from Crypto.PublicKey import ECC
from eth_utils import keccak, to_checksum_address
from mnemonic import Mnemonic
from py_ecc.bls import G2ProofOfPossession as bls_pop


def seed_to_private_key(seed, derivation_path, passphrase: str = ""):
    seed_bytes = Mnemonic.to_seed(seed, passphrase=passphrase)
    hd_wallet = hdwallets.BIP32.from_seed(seed_bytes)
    derived_privkey = hd_wallet.get_privkey_from_path(derivation_path)

    return derived_privkey


def privkey_to_pubkey(privkey: bytes, raw: bool = False) -> bytes:
    privkey_obj = ecdsa.SigningKey.from_string(privkey, curve=ecdsa.SECP256k1)
    pubkey_obj = privkey_obj.get_verifying_key()
    return pubkey_obj.to_string("raw") if raw else pubkey_obj.to_string("compressed")


def pubkey_to_eth_address(pubkey: bytes) -> str:
    k = keccak(pubkey)[-20:].hex()
    return to_checksum_address("0x" + k)


def privkey_to_eth_address(privkey: bytes) -> str:
    pubkey = privkey_to_pubkey(privkey, raw=True)
    return pubkey_to_eth_address(pubkey)


class AccountED25519:
    def __init__(
        self,
        private_key: str = None,
    ):
        if not private_key:
            self._key = ECC.generate(curve="Ed25519")
        else:
            self._key = ECC.import_key(bytes.fromhex(private_key))

    @property
    def private_key(self) -> bytes:
        return binascii.hexlify(self._key.export_key(format="DER"))

    @property
    def public_key(self) -> bytes:
        return binascii.hexlify(self._key.public_key().export_key(format="raw"))


class Account:
    address: str
    """the address of the account derived by using the slip44 param and the address_index"""

    _RAW_DERIVATION_PATH = "m/44'/60'/0'/0/{address_index}"

    def __init__(
        self,
        seed_phrase: str = None,
        private_key: str = None,
        next_sequence: int = None,
        account_number: int = None,
        address_index: int = 0,
    ):
        self._address_index = address_index
        self._next_sequence = next_sequence
        self._account_number = account_number

        if not seed_phrase and not private_key:
            self._seed_phrase = Mnemonic(language="english").generate(strength=256)
            self._private_key = seed_to_private_key(self._seed_phrase, self._derivation_path())

        elif seed_phrase and not private_key:
            self._seed_phrase = seed_phrase
            self._private_key = seed_to_private_key(seed_phrase, self._derivation_path())

        elif private_key and not seed_phrase:
            self._seed_phrase = None
            self._private_key = bytes.fromhex(private_key)

        else:
            raise AttributeError("Please set only a private key or a seed phrase. Not both!")

    def _derivation_path(self, address_index: int = None):
        adr_id = self._address_index if not address_index else address_index
        params = {"address_index": adr_id}
        return self._RAW_DERIVATION_PATH.format(**params)

    @property
    def address(self) -> str:
        """
        Current address which depends on the private key.

        Returns:
            Address
        """
        if not self._seed_phrase:
            address = privkey_to_eth_address(self._private_key)

        else:
            sub_private_key = seed_to_private_key(
                self._seed_phrase,
                self._derivation_path(address_index=self._address_index),
            )
            address = privkey_to_eth_address(sub_private_key)

        return address

    @property
    def seed_phrase(self) -> str:
        """
        Current Seed Phrase

        Returns:
            Seed Phrase
        """
        return self._seed_phrase

    @property
    def private_key(self) -> bytes:
        """
        Current private key which depends on the slip 44 param and the address index if the account is instantiated through a seed.

        Returns:
            Private Key
        """
        if self._seed_phrase:
            private_key = seed_to_private_key(
                self._seed_phrase,
                self._derivation_path(address_index=self._address_index),
            )
            return private_key
        else:
            return self._private_key

    @property
    def public_key(self) -> str:
        """
        Current public key which depends on the slip 44 param and the address index if the account is instantiated through a seed.

        Returns:
            Public Key
        """
        pubkey_bytes = privkey_to_pubkey(self.private_key)

        pubkey = ecdsa.VerifyingKey.from_string(pubkey_bytes, curve=ecdsa.SECP256k1).to_string(encoding="compressed")
        return pubkey

    @property
    def account_number(self) -> int:
        """
        On-chain account number which will be assigned when the address receives coins for the first time.

        Args:
            account_number (int): Account Number
        Returns:
            Account number
        """
        return self._account_number

    @account_number.setter
    def account_number(self, account_number: int):
        self._account_number = account_number

    @property
    def next_sequence(self) -> int:
        """
        Sequence which will be used for transactions signed with this Account.

        Args:
            next_sequence (int): Next sequence (only when used as setter)

        Returns:
            Next Sequence
        """
        return self._next_sequence

    @next_sequence.setter
    def next_sequence(self, next_sequence):
        self._next_sequence = next_sequence

    def increase_sequence(self, change: int = 1) -> None:
        """
        Increase the sequence by ``change``

        Args:
            change (int): Value to increase the sequence
        """
        self._next_sequence += change

    @property
    def address_index(self):
        """
        Change the address index to use a sub account. This works only if a seed has been used to instantiate the Account.

        Args:
            address_index (int): New address index

        Returns:
            Address Index
        """
        return self._address_index

    @address_index.setter
    def address_index(self, address_index: int) -> None:
        if self._seed_phrase:
            self._DEFAULT_ADDRESS_INDEX = address_index
        else:
            raise ValueError("Can't the change the address index without provided seed")


class KeyManager:
    def __init__(self, private_key: Optional[str] = None, mnemonic: Optional[str] = None):
        self.private_key = private_key
        self.mnemonic = mnemonic
        self.address = None
        self._account = None

        if self.private_key and self.mnemonic:
            raise AttributeError("Only use private_key OR mnemonic")

        if self.private_key:
            self._init_from_private_key()

        elif self.mnemonic:
            self._init_from_mnemonic()

        else:
            self._init_from_nothing()

    def _init_from_private_key(self):
        self.private_key_instance = ecdsa.SigningKey.from_string(bytes.fromhex(self.private_key), curve=ecdsa.SECP256k1)

        self.eth_private_key = self.private_key_instance.to_string().hex()
        self.account = Account(private_key=self.eth_private_key)

        self.address = self.account.address

    def _init_from_mnemonic(self):
        raise NotImplementedError

    def _init_from_nothing(self):
        self.private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1).to_string().hex()
        self._init_from_private_key()

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, account: Account):
        self._account = account
        self.private_key = account.private_key
        self.address = account.address


def tmhash(data):
    """Compute a hash using the same algorithm as Tendermint."""
    return hashlib.sha256(data).digest()


class BLSAccount:
    def __init__(self, private_key: str = None):
        # Convert the hex private key to an integer
        self._key = int(private_key, 16)

    @property
    def private_key(self) -> str:
        return self._key.hex()

    @property
    def public_key(self) -> str:
        pub_key = bls_pop.SkToPk(self._key)
        return pub_key.hex()

    def bls_proof(self):
        # Sign the hash of the public key and get the signature in hex
        proof = bls_pop.Sign(SK=self._key, message=tmhash(bytes.fromhex(self.public_key)))
        return proof.hex()


class BLSKeyManager:
    def __init__(self, private_key: Optional[str] = None):
        self.private_key = private_key
        self.account = None
        if self.private_key:
            self._init_from_private_key()
        else:
            self._init_from_nothing()

    def _init_from_private_key(self):
        self.account = BLSAccount(private_key=self.private_key)

    def _init_from_nothing(self):
        # Generate a new private key
        while True:
            potential_privkey = int.from_bytes(os.urandom(32), "big")
            if bls_pop._is_valid_privkey(potential_privkey):  # Check if it's a valid BLS private key
                self.private_key = hex(potential_privkey)[2:]
                break
        self._init_from_private_key()
