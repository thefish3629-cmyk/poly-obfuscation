from py2neo import Graph, Node, Relationship
from typing import List, Optional
from datetime import datetime
from ..utils.config import get_settings


class GraphStore:
    def __init__(self):
        settings = get_settings()
        self.graph = Graph(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    
    def clear_all(self):
        self.graph.delete_all()
    
    def create_wallet_node(self, address: str, **props):
        node = Node("Wallet", address=address.lower(), **props)
        self.graph.create(node)
        return node
    
    def get_wallet_node(self, address: str):
        return self.graph.nodes.match("Wallet", address=address.lower()).first()
    
    def create_market_node(self, condition_id: str, **props):
        node = Node("Market", condition_id=condition_id, **props)
        self.graph.create(node)
        return node
    
    def create_trade_relationship(self, wallet_address: str, market_id: str, volume: float):
        wallet = self.get_wallet_node(wallet_address)
        if not wallet:
            wallet = self.create_wallet_node(wallet_address)
        
        market = self.graph.nodes.match("Market", condition_id=market_id).first()
        if not market:
            market = self.create_market_node(market_id)
        
        rel = Relationship(wallet, "TRADED_ON", market, volume=volume, timestamp=datetime.now())
        self.graph.create(rel)
        return rel
    
    def create_funded_from_relationship(self, from_addr: str, to_addr: str, 
                                         contract_type: str, amount: float = 0):
        from_node = self.get_wallet_node(from_addr)
        if not from_node:
            from_node = self.create_wallet_node(from_addr)
        
        to_node = self.get_wallet_node(to_addr)
        if not to_node:
            to_node = self.create_wallet_node(to_addr)
        
        if contract_type == "mixer":
            rel = Relationship(from_node, "VIA_MIXER", to_node, amount=amount)
        elif contract_type == "bridge":
            rel = Relationship(from_node, "VIA_BRIDGE", to_node, amount=amount)
        else:
            rel = Relationship(from_node, "FUNDED_FROM", to_node, amount=amount)
        
        self.graph.create(rel)
        return rel
    
    def create_cluster_relationship(self, wallet1: str, wallet2: str, 
                                    cluster_type: str, confidence: float):
        node1 = self.get_wallet_node(wallet1)
        if not node1:
            node1 = self.create_wallet_node(wallet1)
        
        node2 = self.get_wallet_node(wallet2)
        if not node2:
            node2 = self.create_wallet_node(wallet2)
        
        rel = Relationship(node1, "CLUSTERED_WITH", node2, 
                           cluster_type=cluster_type, confidence=confidence)
        self.graph.create(rel)
        return rel
    
    def get_wallet_clusters(self):
        query = """
        MATCH (w1:Wallet)-[r:CLUSTERED_WITH]-(w2:Wallet)
        RETURN w1.address as wallet1, w2.address as wallet2, 
               r.cluster_type as cluster_type, r.confidence as confidence
        """
        return list(self.graph.run(query))
    
    def get_fund_flow_path(self, from_addr: str, to_addr: str, max_hops: int = 5):
        query = f"""
        MATCH path = (start:Wallet {{address: '{from_addr.lower()}'}})-[*1..{max_hops}]-(end:Wallet {{address: '{to_addr.lower()}'}})
        RETURN path
        """
        return list(self.graph.run(query))
    
    def get_wallet_connected_entities(self, address: str):
        query = f"""
        MATCH (w:Wallet {{address: '{address.lower()}'}})-[r]-(other)
        RETURN type(r) as relationship, other.address as entity, r
        """
        return list(self.graph.run(query))
    
    def get_suspicious_wallets(self, min_score: float = 50):
        query = f"""
        MATCH (w:Wallet)
        WHERE w.risk_score >= {min_score}
        RETURN w.address as address, w.risk_score as score
        ORDER BY score DESC
        """
        return list(self.graph.run(query))
    
    def create_mixer_node(self, address: str, mixer_type: str):
        node = Node("Mixer", address=address.lower(), mixer_type=mixer_type)
        self.graph.create(node)
        return node
    
    def create_bridge_node(self, address: str, bridge_name: str):
        node = Node("Bridge", address=address.lower(), bridge_name=bridge_name)
        self.graph.create(node)
        return node
