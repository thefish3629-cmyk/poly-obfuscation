from web3 import Web3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..utils.config import get_settings
from ..utils.logging import setup_logging

logger = setup_logging("onchain_client")

MIXER_CONTRACTS = {
    "tornado_cash_ethereum": [
        "0x91031bCf8b7a6282b7a8403f46B4a7c9B6B0555D",
        "0xA160cdAB225685dA1d56d34277e6kD5DB7d16b3C",
        "0x4736dA21b373EFD54a3a3a62A655A6B2B0b198Ab",
    ],
    "tornado_cash_polygon": [],
    "aztec": [
        "0xFF741c2Ea3Eb1bD6D5D9a1aF9D7d7C5A5E9C8D3B",
    ],
    "railgun": [
        "0x19G7cF2D8b4E3f6A2c5D8A1b6F9E3D5C7A2B4E6D",
        "0xFA7093CDD9EE6932B4ef2c99Fc0E5eA930f67b0c",
    ],
}

BRIDGE_CONTRACTS = {
    "multichain_anywap": [
        "0xC564EE9f21c8C733732019Ca51bb6FA18EdA78A5",
        "0x6b7a878994dd6463132849b07333fe887fddb2b5",
    ],
    "stargate": [
        "0xdf0770dF86a8034b3EFEf0A1Bb3c889B8332FF56",
        "0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f4E",
    ],
    "layerzero": [
        "0xb6319cC6E9650A86F0cD1c817AbC76C91F9c5d4E",
        "0x9740FF51F32a7eA0b1fD4De08F5f783960e80F46",
        "0x9d1A46d6D1e16aE4eA9f4E7B4C8D8d8B3F9D7E6C",
    ],
    "wormhole": [
        "0x3ee18B2214AFF97000D974cf647E7C347E8fa585",
        "0x5a58505a96D1dbf8dA10A3d7d8B9e8D7C6B5A4E3F",
    ],
    "hop": [
        "0x8658Ce5E6fA48d7a6F0Ea1C4fB1b20936D3f9e3E",
        "0x22cc71a97174CE3C6fC1A456B3B4f2C9a5D7E6F8",
    ],
    "polygon_bridge": [
        "0x401F6c983eA43474dEF76a7926e5aC383aD3b939",
        "0xA8CE8aEabD93a98F52C351e7D3F1D89f15D4f34A",
    ],
    "quick_swap": [
        "0xa5E0829CaCEd8fFD4F384916Ce3e47Ffb4E6C8F3",
        "0x6bdE1c8e0F27E90C2E3d6C6B3e1A5F8D4C9E7B6A",
    ],
    "apy_bridge": [
        "0x2DA9f8E95C8d2a81fB75dE44eB4aEB6B2A3C9D8E",
    ],
}

USDC_CONTRACTS = {
    "polygon": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "optimism": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
    "avalanche": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
}


class OnchainClient:
    def __init__(self, rpc_url: str = None):
        settings = get_settings()
        self.rpc_url = rpc_url or settings.polygon_rpc_url
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.is_connected():
            logger.warning("Could not connect to Polygon RPC")
        
        self.usdc_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(USDC_CONTRACTS["polygon"]),
            abi=self._get_usdc_abi()
        )
    
    def _get_usdc_abi(self) -> List:
        return [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "from", "type": "address"},
                    {"indexed": True, "name": "to", "type": "address"},
                    {"indexed": False, "name": "value", "type": "uint256"},
                ],
                "name": "Transfer",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "owner", "type": "address"},
                    {"indexed": True, "name": "spender", "type": "address"},
                    {"indexed": False, "name": "value", "type": "uint256"},
                ],
                "name": "Approval",
                "type": "event"
            }
        ]
    
    def get_usdc_transfers(self, address: str, from_block: int = 0, 
                           to_block: str = "latest") -> List[Dict]:
        address = self.w3.to_checksum_address(address)
        
        Transfer = self.usdc_contract.events.Transfer
        try:
            approval_filter = Transfer.create_filter(
                from_block=from_block,
                to_block=to_block,
                argument_filters={"to": address}
            )
        except Exception:
            return {"incoming": [], "outgoing": []}
        
        incoming = []
        for event in approval_filter.get_all_entries():
            incoming.append({
                "from": event.args["from"],
                "to": event.args["to"],
                "value": event.args["value"] / 1e6,
                "block_number": event.blockNumber,
                "tx_hash": event.transactionHash.hex(),
            })
        
        try:
            send_filter = Transfer.create_filter(
                from_block=from_block,
                to_block=to_block,
                argument_filters={"from": address}
            )
        except Exception:
            send_filter = []
        
        outgoing = []
        for event in send_filter.get_all_entries():
            outgoing.append({
                "from": event.args["from"],
                "to": event.args["to"],
                "value": event.args["value"] / 1e6,
                "block_number": event.blockNumber,
                "tx_hash": event.transactionHash.hex(),
            })
        
        return {"incoming": incoming, "outgoing": outgoing}
    
    def trace_fund_origin(self, address: str, max_hops: int = 5) -> List[Dict]:
        """Trace USDC funding sources for an address."""
        all_hops = []
        visited = set()
        queue = [(address.lower(), 0, None, "wallet")]
        
        while queue and len(all_hops) < 100:
            current_addr, hop, prev_addr, contract_type = queue.pop(0)
            
            if current_addr in visited or hop >= max_hops:
                continue
            visited.add(current_addr)
            
            transfers = self.get_usdc_transfers(current_addr)
            
            for transfer in transfers["incoming"]:
                to_addr = transfer["to"].lower()
                from_addr = transfer["from"].lower()
                
                hop_data = {
                    "trace_id": f"{address.lower()}_origin_{hop}",
                    "from_address": from_addr,
                    "to_address": to_addr,
                    "token": "USDC",
                    "amount": str(transfer["value"]),
                    "contract_type": self._classify_address(from_addr),
                    "hop_number": hop + 1,
                    "timestamp": datetime.now(),
                    "tx_hash": transfer["tx_hash"]
                }
                all_hops.append(hop_data)
                
                if hop + 1 < max_hops:
                    queue.append((from_addr, hop + 1, to_addr, hop_data["contract_type"]))
        
        return all_hops
    
    def _classify_address(self, address: str) -> str:
        """Classify what type of contract/address this is."""
        address_lower = address.lower()
        
        for mixer_type, addresses in MIXER_CONTRACTS.items():
            if address_lower in [a.lower() for a in addresses]:
                return f"mixer:{mixer_type}"
        
        for bridge_type, addresses in BRIDGE_CONTRACTS.items():
            if address_lower in [a.lower() for a in addresses]:
                return f"bridge:{bridge_type}"
        
        if address_lower in [a.lower() for a in USDC_CONTRACTS.values()]:
            return "usdc_contract"
        
        return "wallet"
    
    def get_transaction_trace(self, tx_hash: str) -> Dict:
        """Get detailed trace of a transaction."""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "hash": tx_hash,
                "from": tx["from"],
                "to": tx["to"],
                "value": tx["value"],
                "gas_used": receipt["gasUsed"],
                "status": receipt["status"],
                "logs": [
                    {
                        "address": log["address"],
                        "topics": [t.hex() for t in log["topics"]],
                        "data": log["data"]
                    }
                    for log in receipt["logs"]
                ]
            }
        except Exception as e:
            logger.error(f"Failed to trace tx {tx_hash}: {e}")
            return {}
    
    def is_contract(self, address: str) -> bool:
        address = self.w3.to_checksum_address(address)
        code = self.w3.eth.get_code(address)
        return len(code) > 2
    
    def get_contract_type(self, address: str) -> str:
        """Determine if an address is a contract and what type."""
        if not self.is_contract(address):
            return "EOA"
        
        address_lower = address.lower()
        
        for mixer_type, addresses in MIXER_CONTRACTS.items():
            if address_lower in [a.lower() for a in addresses]:
                return f"mixer:{mixer_type}"
        
        for bridge_type, addresses in BRIDGE_CONTRACTS.items():
            if address_lower in [a.lower() for a in addresses]:
                return f"bridge:{bridge_type}"
        
        return "unknown_contract"
