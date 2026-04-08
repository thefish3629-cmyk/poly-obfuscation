"""
Batch processing for analyzing multiple wallets.
"""

import concurrent.futures
from typing import List, Dict, Callable, Any, Optional
from datetime import datetime
from ..models.schemas import Wallet, DetectionFlag
from ..utils.logging import setup_logging

logger = setup_logging("batch_processor")


class BatchProcessor:
    """
    Process multiple wallets in batches with parallel execution.
    
    Usage:
        processor = BatchProcessor(max_workers=5, batch_size=10)
        
        results = processor.process_wallets(
            wallet_addresses,
            detect_for_wallet,
            progress_callback=print
        )
    """
    
    def __init__(
        self, 
        max_workers: int = 5,
        batch_size: int = 10,
        timeout_seconds: int = 300
    ):
        """
        Initialize batch processor.
        
        Args:
            max_workers: Max parallel API calls
            batch_size: Wallets per batch
            timeout_seconds: Timeout for each wallet processing
        """
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
    
    def process_in_batches(
        self,
        items: List[Any],
        processor_func: Callable,
        batch_size: int = None,
        progress_callback: Callable[[int, int], None] = None
    ) -> List[Any]:
        """
        Process items in batches with optional progress callback.
        
        Args:
            items: List of items to process
            processor_func: Function to apply to each item
            batch_size: Items per batch (uses default if None)
            progress_callback: Called with (completed, total)
        
        Returns:
            List of results
        """
        if batch_size is None:
            batch_size = self.batch_size
        
        results = []
        total = len(items)
        
        for i in range(0, total, batch_size):
            batch = items[i:i + batch_size]
            
            # Process batch
            for item in batch:
                try:
                    result = processor_func(item)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to process {item}: {e}")
                    results.append(None)
            
            # Progress callback
            if progress_callback:
                progress_callback(len(results), total)
        
        return results
    
    def process_parallel(
        self,
        items: List[Any],
        processor_func: Callable,
        max_workers: int = None,
        progress_callback: Callable[[int, int], None] = None
    ) -> List[Any]:
        """
        Process items in parallel using ThreadPoolExecutor.
        
        Args:
            items: List of items to process
            processor_func: Function to apply to each item
            max_workers: Max parallel threads
            progress_callback: Called with (completed, total)
        
        Returns:
            List of results
        """
        if max_workers is None:
            max_workers = self.max_workers
        
        results = [None] * len(items)
        completed = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(processor_func, item): i 
                for i, item in enumerate(items)
            }
            
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result(timeout=self.timeout_seconds)
                except Exception as e:
                    logger.error(f"Failed to process item {index}: {e}")
                    results[index] = None
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(items))
        
        return results
    
    def process_wallets(
        self,
        wallet_addresses: List[str],
        detection_func: Callable[[str], List[DetectionFlag]],
        mode: str = "batch",
        progress_callback: Callable[[int, int, str], None] = None
    ) -> Dict[str, List[DetectionFlag]]:
        """
        Process multiple wallets for detection.
        
        Args:
            wallet_addresses: List of wallet addresses
            detection_func: Function that takes address and returns flags
            mode: "batch" or "parallel"
            progress_callback: Called with (completed, total, status)
        
        Returns:
            Dict mapping wallet -> list of detection flags
        """
        results = {}
        total = len(wallet_addresses)
        
        if mode == "parallel":
            # Process in parallel
            flag_results = self.process_parallel(
                wallet_addresses,
                detection_func,
                progress_callback=lambda c, t: (
                    progress_callback(c, t, "parallel") if progress_callback else None
                )
            )
            
            for wallet, flags in zip(wallet_addresses, flag_results):
                if flags:
                    results[wallet] = flags if isinstance(flags, list) else [flags]
        
        else:
            # Process in batches
            for i, wallet in enumerate(wallet_addresses):
                try:
                    flags = detection_func(wallet)
                    results[wallet] = flags
                except Exception as e:
                    logger.error(f"Detection failed for {wallet}: {e}")
                    results[wallet] = []
                
                if progress_callback:
                    progress_callback(i + 1, total, f"batch {i+1}/{total}")
        
        return results


class WalletBatchAnalyzer:
    """
    High-level analyzer for processing batches of wallets.
    
    Usage:
        analyzer = WalletBatchAnalyzer()
        
        # Analyze top traders
        results = analyzer.analyze_by_volume(
            market_id="0x123...",
            top_n=100
        )
        
        # Analyze suspicious wallets
        results = analyzer.analyze_suspicious(
            threshold_volume=10000,
            max_wallets=50
        )
    """
    
    def __init__(self):
        self.processor = BatchProcessor(max_workers=5, batch_size=10)
    
    def analyze_by_volume(
        self,
        trades: List[Dict],
        detection_func: Callable,
        top_n: int = 100
    ) -> Dict[str, Dict]:
        """
        Analyze top N wallets by volume.
        
        Args:
            trades: List of trade dicts
            detection_func: Function to detect flags
            top_n: Number of top wallets
        
        Returns:
            Dict with wallet analysis
        """
        from collections import Counter
        
        # Get top wallets by volume
        volumes = Counter(t.get("amount_usd", 0) for t in trades)
        top_wallets = [w for w, v in volumes.most_common(top_n)]
        
        logger.info(f"Analyzing top {top_n} wallets by volume")
        
        # Process wallets
        results = self.processor.process_wallets(
            top_wallets,
            detection_func,
            mode="parallel",
            progress_callback=lambda c, t, s: logger.info(f"Progress: {c}/{t}")
        )
        
        return results
    
    def analyze_all(
        self,
        trades: List[Dict],
        detection_func: Callable,
        min_volume: float = 100,
        max_wallets: int = None
    ) -> Dict[str, Dict]:
        """
        Analyze all wallets above volume threshold.
        
        Args:
            trades: List of trade dicts
            detection_func: Detection function
            min_volume: Minimum volume to analyze
            max_wallets: Max wallets to process
        
        Returns:
            Dict with wallet analysis
        """
        from collections import Counter
        
        # Filter by volume
        volumes = Counter(t.get("amount_usd", 0) for t in trades if t.get("amount_usd", 0) >= min_volume)
        
        if max_wallets:
            wallets = [w for w, v in volumes.most_common(max_wallets)]
        else:
            wallets = list(volumes.keys())
        
        logger.info(f"Analyzing {len(wallets)} wallets (min_volume=${min_volume})")
        
        results = self.processor.process_wallets(
            wallets,
            detection_func,
            mode="parallel",
            progress_callback=lambda c, t, s: logger.info(f"Progress: {c}/{t}")
        )
        
        return results
    
    def analyze_network(
        self,
        wallet_addresses: List[str],
        funding_func: Callable,
        detection_func: Callable,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze wallet network with funding tracing.
        
        Args:
            wallet_addresses: Starting wallets
            funding_func: Function to trace funding
            detection_func: Detection function
            max_depth: Max tracing depth
        
        Returns:
            Network analysis results
        """
        network = {}
        visited = set()
        
        def trace_and_analyze(wallet, depth=0):
            if wallet in visited or depth > max_depth:
                return
            
            visited.add(wallet)
            
            # Trace funding
            try:
                funding = funding_func(wallet)
                network[wallet] = {"funding": funding, "depth": depth}
            except:
                network[wallet] = {"funding": [], "depth": depth}
            
            # Analyze this wallet
            try:
                flags = detection_func(wallet)
                network[wallet]["flags"] = flags
            except:
                network[wallet]["flags"] = []
            
            # Continue tracing through funding sources
            for hop in network[wallet].get("funding", []):
                source = hop.get("from_address")
                if source and source not in visited:
                    trace_and_analyze(source, depth + 1)
        
        # Process all wallets
        for wallet in wallet_addresses:
            trace_and_analyze(wallet)
        
        return network