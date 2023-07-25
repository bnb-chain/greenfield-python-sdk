from greenfield_python_sdk.__version__ import __version__

PACKAGE = "greenfield-python-sdk"

USER_AGENT = "Greenfield " + PACKAGE + "/" + __version__
ETH_ADDRESS_LENGTH = 20

CREATE_OBJECT_ACTION = "CreateObject"
CREATE_BUCKET_ACTION = "CreateBucket"
SIGN_ALGORITHM = "ECDSA-secp256k1"
AUTH_V1 = "authTypeV1"
SUPPORT_HEADERS = [
    "Content-MD5",
    "Content-Type",
    "Range",
    "X-Gnfd-Content-Sha256",
    "X-Gnfd-Date",
    "X-Gnfd-Object-ID",
    "X-Gnfd-Piece-Index",
    "X-Gnfd-Redundancy-Index",
    "X-Gnfd-Txn-Hash",
    "X-Gnfd-Unsigned-Msg",
    "X-Gnfd-User-Address",
]
