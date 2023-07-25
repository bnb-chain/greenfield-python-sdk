from enum import IntEnum


class BroadcastMode(IntEnum):
    "zero-value for mode ordering"
    BROADCAST_MODE_UNSPECIFIED = 0
    """
      DEPRECATED: use BROADCAST_MODE_SYNC instead,
	  BROADCAST_MODE_BLOCK is not supported by the SDK from v0.47.x onwards.
      Deprecated: Do not use.
    """
    BROADCAST_MODE_BLOCK = 1
    """
      BROADCAST_MODE_SYNC defines a tx broadcasting mode where the client waits
	  for a CheckTx execution response only.
    """
    BROADCAST_MODE_SYNC = 2
    """
      BROADCAST_MODE_ASYNC defines a tx broadcasting mode where the client
	  returns immediately.
    """
    BROADCAST_MODE_ASYNC = 3
