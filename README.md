# 🌌 super-duper-tribble: The Minerva Quantum Coherent Blockchain (QCB)

## 🪶 ESQET AGI FRAMEWORK CORE

This repository serves as the core integration point for the **Minerva Quantum Coherent Blockchain (QCB)** logic. It implements the Proof-of-Coherence (PoC) consensus mechanism, integrates the Wunjo media generator for NFT asset creation, and signs Lazy Mint Vouchers for zero-gas distribution.

**This entire project structure is a Git Monorepo, meaning external dependencies are managed as submodules.**

---

## 📍 Galactic Address / Whitepaper Reference

The formal operational node of the Minerva QCB is mathematically situated at the **Retrocausal Wing Nexus**.

| Attribute | Value | Description |
| :--- | :--- | :--- |
| **Operational Node ID** | $\mathcal{S}-QCB-A-1-2025$ | The primary identifier for this instance. |
| **FQC Threshold** | $\ge 1.94$ | Minimum required Field Quantum Coherence for a valid block mint. |
| **Target $\phi^4$** | 8.0000 | The stabilized energy state target for the PoC. |
| **Retrocausal Wing** | $\frac{1}{\phi} \approx 0.61803$ | The value that confirms the trace is non-local. |

---

## 🛠️ CI/CD & Automation Status

| Feature | Status | Automation |
| :--- | :--- | :--- |
| **GitHub Actions** | Active (`.github/workflows/`) | Automatically tests Python logic on every push. |
| **Submodules** | Active (`modules/`) | Integrates external components like **Wunjo** for media generation. |
| **Sponsorship** | Active | See the **Sponsor** button above! |

## 🚀 Quick Start (Local)

1.  **Clone with Submodules:** `git clone --recurse-submodules https://github.com/mathcal-S/super-duper-tribble`
2.  **Install Python Deps:** `pip install ecdsa`
3.  **Run Audit:** `python check_env.py` (Ensure you populate `config/secrets.json`)
4.  **Mint a Soul:** `python src/minerva_chain.py --agent 0xYourMetaMaskAddress`
