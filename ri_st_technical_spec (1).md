**Technical Specification for Reputation‑Splitting Tokens (RiSTs)**

*Modular Credential Infrastructure for Web3 Identity, DAO Access, and Professional Verification*

---

### 1. Overview

Reputation‑Splitting Tokens (RiSTs) are non‑transferable, modular, and cryptographically‑verifiable credentials designed to record on‑chain reputation **by domain** without leaking private data or allowing any single authority to control everyone’s score.

> **Toxic over‑centralisation** happens when one issuer (e.g., a LinkedIn‑style monopoly or a dominant grant‑platform) can *unilaterally revoke* or manipulate millions of credentials, breaking user agency and enabling sybil exploits in DAOs.† RiSTs prevent this by letting many issuers operate side‑by‑side while keeping credentials domain‑scoped.
>
> **Ephemeral Rights Tokens (ERTs)** enable *time‑limited* or *view‑count‑limited* access to a résumé generated from RiSTs — handy for job searches (e.g., burnable one‑time recruiter links) where you don’t want your entire history visible forever.

† *Sybil attacks = creating many fake identities to game voting or reward systems.*

---

### 2. Token Standard and Architecture

#### 2.1 Base protocol

- **Token type** · ERC‑721 **inheriting from draft EIP‑5114** (Soulbound) for built‑in non‑transferability, with light extensions for domain metadata.  ↳ *Use a battle‑tested OpenZeppelin‑style 5114 implementation to avoid draft‑spec pitfalls.*
- **Interfaces** · `IERC721Metadata`  `IERC5114`  *optional* `IZKRiSTVerifier` (zero‑knowledge module)

#### 2.2 Core struct

```solidity
struct RiST {
    string  domain;       // e.g. "ux_design", "solidity_dev"
    string  issuer;       // org name or DID string
    string  level;        // "L3", "Gold", etc.
    uint256 issuedAt;     // block timestamp
    uint256 validUntil;   // 0 = perpetual
    bool    revoked;      // hard revocation flag
    string  metadataURI;  // IPFS / HTTPS / Arweave pointer
    bytes32 contentHash;  // keccak256 of full off‑chain JSON
}
```

- `transferFrom()` / `safeTransferFrom()` permanently **revert** ⇢ soulbound.
- Minting restricted to **whitelisted issuers** (on‑chain registry). If `tokenId` not supplied, contract auto‑increments via Counters.

---

### 3. Metadata Schema

#### 3.1 On‑chain fields

`tokenId` · `owner` · `issuer` · `domain` · `level` · `validUntil` · `revoked` · `metadataURI`

#### 3.2 Off‑chain JSON (IPFS / Arweave)

```json
{
  "name": "UX Design Contributor – Gitcoin Q3 2024",
  "description": "Issued to a verified contributor in Gitcoin’s UX audit round (Q3 2024).",
  "image": "ipfs://…",
  "vc_jwt": "eyJ…",                     // OPTIONAL: W3C VC JWT (per DID/VC specs)
  "attributes": [
    { "trait_type": "Domain",     "value": "ux_design" },
    { "trait_type": "Level",      "value": "L3" },
    { "trait_type": "Issuer",     "value": "GitcoinDAO" },
    { "trait_type": "Issued At",  "value": "2024‑09‑15" },
    { "trait_type": "Expiration", "value": "2025‑09‑15" }
  ]
}
```

- **Hashing:** `contentHash = keccak256(abi.encode(jsonBlob))`
- **Pinning policy:** issuers must pin via ≥ 1 decentralised pin‑service or Filecoin deal.

---

### 4. Smart‑Contract Logic

#### 4.1 Roles

- **Admin** – manages issuer registry & upgrades (UUPS proxy with 7‑day timelock)
- **Issuer** – mints & (if needed) revokes RiSTs

#### 4.2 Core functions

```solidity
function mintRiST(address to, RiST calldata data) external onlyIssuer; // auto‑tokenId
function revokeRiST(uint256 tokenId)            external onlyIssuerOrAdmin;
function isValid(uint256 tokenId) public view returns (bool);
function getRiST(uint256 tokenId) public view returns (RiST memory);

// Optional holder‑approved metadata fix
function updateMetadata(uint256 tokenId, string newURI, bytes32 newHash, bytes sig) external onlyIssuer;
```

View‑only decay logic:

```solidity
return !rist.revoked && (rist.validUntil == 0 || block.timestamp <= rist.validUntil);
```

#### 4.3 Events

```solidity
event RiSTIssued(uint256 indexed tokenId, address indexed to, string domain);
event RiSTRevoked(uint256 indexed tokenId, address indexed revoker);
event IssuerWhitelisted(address indexed issuer);
event MetadataUpdated(uint256 indexed tokenId, string newURI);
```

---

### 5. QR Résumé Infrastructure

#### 5.1 Master profile URL

`https://qr.reputation.xyz/@{ENS|wallet}` → client fetches **valid** RiSTs; UI filters by domain/issuer/date.

#### 5.2 Decentralised ERTs (Access Chips)

- **ERC‑1155 chips** (`RésuméAccessChip`) minted by the holder.
- Chip metadata encodes `expiry`, `maxViews`, optional `riSTId` scope.
- Chips **transferable** (holder can share) but résumé DApp burns **one** per view via `burnAndVerifyAccess()`; on‑chain events = audit trail.

---

### 6. Issuer Dashboard

- Enum’d domain list (custom via DAO vote)
- Batch issuance: CSV or GitHub/Discord webhook (OAuth read PRs/roles)
- **Preview JSON** button before mint to catch errors

---

### 7. Holder Dashboard

- Wallet connect → filters & table
- Generate résumé QR (optionally chip‑gated)
- Water‑marked PDF export (expiry watermark)
- Rarity stats via The Graph indexer cache
- Future: social‑recovery via ERC‑6551 token‑bound accounts

---

### 8. Security & Privacy

- No PII on‑chain
- Identity proofs = `keccak256(email || salt)`
- **zk‑RiST baseline:** Groth16 circuit proving “domain == ux\_design ∧ level ≥ L2” without issuer leak (SnarkJS setup)
- Anti‑scrape: chip burn + Cloudflare Turnstile
- **Audit target:** full contract review by Q4 2025 (Quantstamp/Trail of Bits)

---

### 9. Roadmap & KPIs

| Phase | Quarter     | Milestones                                                  | KPI                                    | Risk / Mitigation                                           |
| ----- | ----------- | ----------------------------------------------------------- | -------------------------------------- | ----------------------------------------------------------- |
| MVP   | **Q3 2025** | Testnet contracts ▸ manual issuer dashboard ▸ résumé viewer | **1 000 RiSTs** / ≥ 3 issuers          | L2 gas volatility → deploy on Base testnet                  |
| 2     | Q4 2025     | On‑chain chips ▸ vanity QR ▸ résumé templates               | ≥ 5 paying issuers                     | Issuer UX friction → guided CSV wizard                      |
| 3     | Q1 2026     | zk‑RiST proofs ▸ DAO vote‑weight adapter ▸ public API       | ≥ 10 000 RiSTs • first DAO integration | ZK setup ceremony delay → fallback to Semaphore-lite proofs |

---

### 10. Tooling & Dependencies

Solidity • Foundry + Hardhat • OZ 5114 impl • React + Wagmi / viem • Tailwind • Node / Next.js • `qr‑code‑styling` • SnarkJS / Semaphore / Noir • Lit Protocol

Static‑analysis via **Slither**; fuzz via **Foundry**.

---

### 11. Integration Targets

Gitcoin Passport • Lens • Snapshot adapter • EAS auto‑attest mirror • LayerZero bridge (multi‑chain roadmap)

---

### 12. License & Governance

- Code: MIT (core) + BSL (premium UI)
- UUPS proxy with 7‑day timelock → **RiST DAO** (Phase 3)
- **Issuer Council multisig** = “issuer‑of‑last‑resort” for revocations when an issuer disappears
- DAO weight formula (Phase 3): Σ(levelPoints × issuerReputation) across domains

---

### 13. Closing Summary

RiSTs deliver **domain‑scoped, privacy‑respecting, verifiably‑earned** credentials. With QR résumés, on‑chain ERT chips, and zk modules, RiSTs aim to become one of the most powerful decentralised résumé & access layers in the Web3 stack.

