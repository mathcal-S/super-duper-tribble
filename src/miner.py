import hashlib
import time
import json

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index                # block height
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data                  # e.g. transactions, eternal souls
        self.hash = hash

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @classmethod
    def create_block(cls, index, previous_hash, data):
        timestamp = int(time.time())
        temp_block = cls(index, previous_hash, timestamp, data, hash=None)
        block_hash = temp_block.compute_hash()
        return cls(index, previous_hash, timestamp, data, block_hash)


class MinervaChain:
    def __init__(self):
        self.blocks = []

    def get_last_block(self):
        if self.blocks:
            return self.blocks[-1]
        else:
            # Genesis block placeholder
            return None

    def proof_of_coherence(self, last_block):
        # Example: create a new test block with incremented height and previous hash
        index = (last_block.index + 1) if last_block else 0
        previous_hash = last_block.hash if last_block else "0" * 64
        data = "Sample coherence data for block {}".format(index)
        test_block = Block.create_block(index, previous_hash, data)
        # Implement your actual coherence proof logic here

        return test_block  # your mining function would validate this

    def mint_soul(self, soul_data, ipfs_uri):
        last_block = self.get_last_block()
        new_block = self.proof_of_coherence(last_block)
        # Add soul data and uri as block data or in a transaction list
        new_block.data = {
            "soul": soul_data,
            "ipfs": ipfs_uri
        }
        # Recompute hash since data changed
        new_block.hash = new_block.compute_hash()

        self.blocks.append(new_block)
        print("Block mined & soul minted with hash:", new_block.hash)


# Example usage:

if __name__ == "__main__":
    chain = MinervaChain()
    # Create and add the genesis block if empty
    if not chain.blocks:
        genesis_block = Block.create_block(0, "0" * 64, "Genesis Block")
        chain.blocks.append(genesis_block)
        print("Genesis block created — Minerva Chain awakened")

    soul = {"name": "Eternal Soul #1", "attributes": {"coherence": 0.999}}
    chain.mint_soul(soul, "ipfs://QmVideoCIDPlaceholder")
