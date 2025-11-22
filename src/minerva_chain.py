#!/usr/bin/env python3
"""
Minerva Chain — One-node, zero-gas, quantum-coherent blockchain
Runs in pure Python. Includes Wunjo Media Generation and Lazy Mint Voucher Signing.
"""

import hashlib
import json
import time
import os
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum
import subprocess
import base64
import argparse 

# --- Rich Import & Fallback ---
try:
    from ecdsa import SigningKey, SECP256k1
except ImportError:
    # This is handled by GitHub Actions or the local user
    print("FATAL: Required dependency 'ecdsa' missing. Run: pip install ecdsa")
    sys.exit(1)


# ──────── ESQET CONSTANTS ────────
PHI = (1 + 5**0.5) / 2
PHI_INV = 1 / PHI
PHI4_TARGET = 8.0000
FQC_THRESHOLD = 1.94
SACRED_SAMPLES = 198

# ──────── DATA STRUCTURES ────────
class MobiusSide(Enum):
    Forward = "Forward"
    Return = "Return"

@dataclass
class SoulTrace:
    timestamp: int
    phi4: float
    entropy: float
    quantum_counts: int

@dataclass
class SoulDNA:
    incarnation: int
    trace_3_3h: List[SoulTrace]
    retrocausal_wing: float
    final_phi4: float
    f_qc: float
    mobius_side: MobiusSide
    minerva_resonance: bool
    agent: str

@dataclass
class EternalSoul:
    dna: SoulDNA
    signature: str = ""
    ipfs_hash: str = ""

@dataclass
class Block:
    index: int
    timestamp: int
    soul: EternalSoul
    previous_hash: str
    hash: str
    nonce: int = 0
    voucher: Optional[dict] = None

# ──────── CONFIG LOAD ────────
def load_secrets():
    try:
        with open(os.path.join(os.getcwd(), "config/secrets.json")) as f:
            return json.load(f)
    except FileNotFoundError:
        print("WARNING: config/secrets.json not found. Using dummy keys.")
        return {
            "MINER_PRIVATE_KEY": "0000000000000000000000000000000000000000000000000000000000000001",
            "WUNJO_CLI_COMMAND": "echo Wunjo: Output saved to ",
            "MEDIA_PROMPT_TEMPLATE": "A highly coherent quantum field (FQC: <FQC>). Retrocausal event detected.",
            "OUTPUT_MEDIA_DIR": os.path.join(os.getcwd(), "media/wunjo_nfts")
        }

SECRETS = load_secrets()

# ──────── WUNJO INTEGRATION ────────
def generate_wunjo_media(dna: SoulDNA) -> str:
    """Generates media using Wunjo CLI and returns the local file path."""
    print("🌀 Initiating Wunjo Media Generation...")
    
    prompt = SECRETS["MEDIA_PROMPT_TEMPLATE"].replace("<FQC>", f"{dna.f_qc:.6f}")
    output_filename = f"soul_{dna.incarnation}_{int(time.time())}.mp4"
    output_path = os.path.join(SECRETS["OUTPUT_MEDIA_DIR"], output_filename)
    
    # Placeholder command: The submodule must be initialized for this to work locally.
    # In CI, this will be mocked as Wunjo requires a complex environment.
    wunjo_cmd = f'{SECRETS["WUNJO_CLI_COMMAND"]} --prompt "{prompt}" --output "{output_path}" --type "video"'
    
    try:
        # Use shell=True for this, but only in controlled environments like this.
        subprocess.run(wunjo_cmd, shell=True, check=True, capture_output=False)
        print(f"✅ Wunjo Output Saved to: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"🚨 Wunjo CLI Failed (Expected in CI). Error: {e}")
        return "ERROR_WUNJO_FAILED"

# ──────── NFT VOUCHER CREATION ────────
def create_lazy_mint_voucher(soul: EternalSoul, media_path: str, ipfs_cid: str = "placeholder_cid") -> dict:
    """Creates a signed, distributable Lazy Mint Voucher."""
    
    dna_str = json.dumps(asdict(soul.dna), sort_keys=True, default=str)
    token_id_int = int(hashlib.sha512(dna_str.encode()).hexdigest(), 16)
    token_id_hex = hex(token_id_int)[2:]
    
    voucher_data = {
        "tokenId": token_id_hex,
        "mediaUri": f"file://{media_path}", 
        "minter": soul.dna.agent,
        "fqc": soul.dna.f_qc,
        "minerva_resonance": soul.dna.minerva_resonance,
        "metadata": asdict(soul.dna)
    }
    voucher_str = json.dumps(voucher_data, sort_keys=True)

    try:
        private_key_hex = SECRETS["MINER_PRIVATE_KEY"].lstrip('0x').zfill(64)
             
        sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
        signature = sk.sign(hashlib.sha256(voucher_str.encode()).digest())
        voucher_data["signature"] = base64.b64encode(signature).decode('utf-8')
    except Exception as e:
        print(f"🚨 Signing failed. Check MINER_PRIVATE_KEY. Error: {e}")
        voucher_data["signature"] = "DUMMY_SIGNATURE_FAILED"

    return voucher_data

# ──────── BLOCKCHAIN CLASS ────────
class MinervaChain:
    def __init__(self, genesis_agent: str = "0xYourMetaMaskHere"):
        self.chain: List[Block] = []
        self.data_dir = os.path.join(os.getcwd(), "output/blocks")
        os.makedirs(self.data_dir, exist_ok=True)
        self.chain_file = os.path.join(self.data_dir, "chain.json")
        self.load_chain() or self.create_genesis(genesis_agent)
        
    def create_genesis(self, agent: str):
        genesis_soul = EternalSoul(
            dna=SoulDNA(
                incarnation=int(time.time()),
                trace_3_3h=[],
                retrocausal_wing=PHI_INV,
                final_phi4=PHI4_TARGET,
                f_qc=FQC_THRESHOLD,
                mobius_side=MobiusSide.Forward,
                minerva_resonance=True,
                agent=agent
            )
        )
        genesis = Block(0, int(time.time()), genesis_soul, "0" * 64, "")
        genesis.hash = self.hash_block(genesis)
        self.chain.append(genesis)
        self.save_chain()
        print("Genesis block created — Minerva Chain awakened")
        
    def hash_block(self, block: Block) -> str:
        temp_block = asdict(block)
        temp_block['hash'] = ''
        temp_block['voucher'] = None
        block_str = json.dumps(temp_block, sort_keys=True, default=str)
        return hashlib.sha3_512(block_str.encode()).hexdigest()

    def proof_of_coherence(self, last_block: Block) -> int:
        nonce = 0
        target_int = int("f" * 16, 16) * PHI_INV
        while True:
            test_block = Block(
                index=last_block.index + 1,
                timestamp=int(time.time()),
                soul=last_block.soul,
                previous_hash=last_block.hash,
                nonce=nonce
            )
            test_hash = self.hash_block(test_block)
            if int(test_hash[:16], 16) <= target_int:
                return nonce
            nonce += 1
            if nonce > 100000:
                return -1

    def validate_soul(self, soul: EternalSoul) -> bool:
        dna = soul.dna
        if len(dna.trace_3_3h) != SACRED_SAMPLES: return False
        if abs(dna.final_phi4 - PHI4_TARGET) > 1e-9: return False
        if dna.f_qc < FQC_THRESHOLD - 1e-6: return False
        if abs(dna.retrocausal_wing - PHI_INV) > 0.01: return False
        return True 

    def mint_soul(self, soul: EternalSoul, ipfs_hash: str = "") -> bool:
        if not self.validate_soul(soul):
            print("Soul validation failed — rejected by the Goddess")
            return False

        last_block = self.chain[-1]
        nonce = self.proof_of_coherence(last_block)
        if nonce == -1: return False

        media_path = generate_wunjo_media(soul.dna)
        voucher = create_lazy_mint_voucher(soul, media_path, ipfs_hash)

        new_block = Block(
            index=last_block.index + 1,
            timestamp=int(time.time()),
            soul=soul,
            previous_hash=last_block.hash,
            nonce=nonce,
            voucher=voucher
        )
        new_block.hash = self.hash_block(new_block)

        self.chain.append(new_block)
        self.save_chain()
        print(f"Block {new_block.index} minted | F_QC={soul.dna.f_qc:.6f} | Voucher Signed")
        
        voucher_file = os.path.join(os.getcwd(), "output/vouchers", f"voucher_{new_block.index}.json")
        os.makedirs(os.path.dirname(voucher_file), exist_ok=True)
        with open(voucher_file, "w") as f:
             json.dump(voucher, f, indent=2)
        print(f"✨ NFT Voucher saved for distribution: {voucher_file}")

        return True

    def save_chain(self):
        with open(self.chain_file, "w") as f:
            json.dump([asdict(b) for b in self.chain], f, indent=2, default=str)

    def load_chain(self):
        if not os.path.exists(self.chain_file): return False
        try:
            with open(self.chain_file) as f:
                data = json.load(f)
                self.chain = []
                for b in data:
                    if 'mobius_side' in b['soul']['dna']:
                        b['soul']['dna']['mobius_side'] = MobiusSide(b['soul']['dna']['mobius_side'])
                    self.chain.append(Block(**b))
            print(f"Chain loaded — {len(self.chain)} blocks")
            return True
        except Exception as e:
            print(f"Error loading chain: {e}")
            return False
            
    def show_stats(self):
        minerva = sum(1 for b in self.chain if b.soul.dna.minerva_resonance)
        print(f"Total souls: {len(self.chain)-1} | Minerva resonances: {minerva}")
        
# ──────── USAGE EXAMPLE ────────
def generate_example_soul(agent_address):
    # Generates a valid soul that passes the FQC threshold
    return EternalSoul(
        dna=SoulDNA(
            incarnation=int(time.time()),
            trace_3_3h=[SoulTrace(int(time.time()-i*60), 7.0 + i*0.005, 0.1, 1024) for i in range(SACRED_SAMPLES)][::-1],
            retrocausal_wing=PHI_INV,
            final_phi4=PHI4_TARGET,
            f_qc=2.05,
            mobius_side=MobiusSide.Forward,
            minerva_resonance=True,
            agent=agent_address
        )
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Minerva Chain QCB Minting Tool")
    parser.add_argument("--agent", type=str, default="0xYourMetaMaskAddress", help="The agent address to associate with the minted soul.")
    args = parser.parse_args()

    chain = MinervaChain(args.agent)

    soul = generate_example_soul(args.agent)

    chain.mint_soul(soul, "ipfs://QmVideoCIDPlaceholder")
    chain.show_stats()
    
