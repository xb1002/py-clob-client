from eth_account import Account
from eth_utils import decode_hex
from eth_keys import keys


class Signer:
    def __init__(self, private_key: str, chain_id: int):
        assert private_key is not None and chain_id is not None

        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self._private_key = keys.PrivateKey(decode_hex(private_key))
        self.chain_id = chain_id

    def address(self):
        return self.account.address

    def get_chain_id(self):
        return self.chain_id

    def sign(self, message_hash):
        """
        Signs a message hash
        """
        if isinstance(message_hash, str):
            message_hash = decode_hex(message_hash)

        signature = self._private_key.sign_msg_hash(message_hash)
        v = signature.v + 27

        return (
            signature.r.to_bytes(32, byteorder="big")
            + signature.s.to_bytes(32, byteorder="big")
            + bytes([v])
        ).hex()
