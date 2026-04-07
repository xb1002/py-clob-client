from functools import lru_cache

from eth_utils import keccak, to_canonical_address
from py_order_utils.utils import prepend_zx

from ..signer import Signer

CLOB_DOMAIN_NAME = "ClobAuthDomain"
CLOB_VERSION = "1"
MSG_TO_SIGN = "This message attests that I control the given wallet"

_EIP712_DOMAIN_TYPE = "EIP712Domain(string name,string version,uint256 chainId)"
_CLOB_AUTH_TYPE = "ClobAuth(address address,string timestamp,uint256 nonce,string message)"

_DOMAIN_TYPEHASH = keccak(text=_EIP712_DOMAIN_TYPE)
_CLOB_AUTH_TYPEHASH = keccak(text=_CLOB_AUTH_TYPE)
_NAME_HASH = keccak(text=CLOB_DOMAIN_NAME)
_VERSION_HASH = keccak(text=CLOB_VERSION)
_MESSAGE_HASH = keccak(text=MSG_TO_SIGN)


def _encode_uint256(value: int) -> bytes:
    return int(value).to_bytes(32, byteorder="big")


def _encode_address(value: str) -> bytes:
    return b"\x00" * 12 + to_canonical_address(value)


@lru_cache(maxsize=8)
def _clob_auth_domain_separator(chain_id: int) -> bytes:
    return keccak(
        _DOMAIN_TYPEHASH
        + _NAME_HASH
        + _VERSION_HASH
        + _encode_uint256(chain_id)
    )


def sign_clob_auth_message(signer: Signer, timestamp: int, nonce: int) -> str:
    timestamp_hash = keccak(text=str(timestamp))

    auth_struct_hash = keccak(
        _CLOB_AUTH_TYPEHASH
        + _encode_address(signer.address())
        + timestamp_hash
        + _encode_uint256(nonce)
        + _MESSAGE_HASH
    )

    digest = keccak(
        b"\x19\x01"
        + _clob_auth_domain_separator(signer.get_chain_id())
        + auth_struct_hash
    )

    return prepend_zx(signer.sign(digest))
