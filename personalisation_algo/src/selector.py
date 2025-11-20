"""
Product Selector

This module implements the final product selection logic with variety mechanisms.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path
import logging


class ProductSelector:
    """
    Select final product from scored and filtered candidates.
    Tracks shown products to ensure variety across multiple runs.
    """
    
    def __init__(self, config: Dict, shown_products_path: str = 'data/shown_products.json'):
        """
        Initialize the product selector.
        
        Args:
            config: Configuration dictionary
            shown_products_path: Path to JSON file tracking shown products
        """
        self.config = config
        self.selection_config = config['selection']
        self.shown_products_path = Path(shown_products_path)
        self.logger = logging.getLogger(__name__)
        
        # Load shown products history
        self._load_shown_products()
    
    def select_product(
        self,
        customer_id: str,
        scored_products: pd.DataFrame,
        current_time: datetime = None
    ) -> Optional[Dict]:
        """
        Select a single product for recommendation.
        
        Args:
            customer_id: Customer ID
            scored_products: DataFrame with scored and filtered products
            current_time: Current timestamp (defaults to now)
            
        Returns:
            Dictionary with selected product and metadata, or None if no valid products
        """
        if current_time is None:
            current_time = datetime.now()
        
        if len(scored_products) == 0:
            self.logger.warning(f"No valid products to recommend for customer {customer_id}")
            return None
        
        # Get top-K candidates
        top_k = self.selection_config['top_k']
        candidates = scored_products.nlargest(top_k, 'final_score').copy()
        
        self.logger.debug(
            f"Selected top {min(top_k, len(candidates))} candidates from "
            f"{len(scored_products)} products"
        )
        
        # Filter recently shown products
        candidates = self._filter_recently_shown(customer_id, candidates, current_time)
        
        if len(candidates) == 0:
            self.logger.warning(
                f"All top candidates were recently shown to customer {customer_id}, "
                f"expanding to all products"
            )
            # Fall back to all scored products if top-K all recently shown
            candidates = scored_products.copy()
            candidates = self._filter_recently_shown(customer_id, candidates, current_time)
            
            if len(candidates) == 0:
                self.logger.error(
                    f"No products available for customer {customer_id} after filtering"
                )
                return None
        
        # Weighted random selection
        selected_product = self._weighted_random_selection(candidates)
        
        # Get product rank in original scored list
        rank = (scored_products['final_score'] > selected_product['final_score']).sum() + 1
        
        # Build result dictionary
        result = {
            'customer_id': customer_id,
            'recommended_product_id': selected_product['product_id'],
            'product_name': selected_product.get('product_name', 'Unknown'),
            'product_category': selected_product.get('product_category', 'Unknown'),
            'final_score': float(selected_product['final_score']),
            'score_components': {
                'category_affinity': float(selected_product['category_affinity']),
                'repurchase_likelihood': float(selected_product['repurchase_likelihood']),
                'clickstream_intent': float(selected_product['clickstream_intent']),
                'product_popularity': float(selected_product['product_popularity']),
                'exploration': float(selected_product['exploration'])
            },
            'rank': int(rank),
            'total_candidates': len(scored_products),
            'timestamp': current_time.isoformat()
        }
        
        # Track shown product
        self._record_shown_product(customer_id, selected_product['product_id'], current_time)
        
        self.logger.info(
            f"Selected product {selected_product['product_id']} (rank {rank}) "
            f"for customer {customer_id} with score {selected_product['final_score']:.3f}"
        )
        
        return result
    
    def _filter_recently_shown(
        self,
        customer_id: str,
        products: pd.DataFrame,
        current_time: datetime
    ) -> pd.DataFrame:
        """
        Filter out products recently shown to this customer.
        
        Args:
            customer_id: Customer ID
            products: Products to filter
            current_time: Current timestamp
            
        Returns:
            Filtered products
        """
        decay_hours = self.selection_config['decay_hours']
        cutoff_time = current_time - timedelta(hours=decay_hours)
        
        # Get customer's shown products
        if customer_id not in self.shown_products:
            return products
        
        # Filter by time window
        recent_shown = set()
        for product_id, timestamp_str in self.shown_products[customer_id].items():
            shown_time = datetime.fromisoformat(timestamp_str)
            if shown_time >= cutoff_time:
                recent_shown.add(product_id)
        
        if len(recent_shown) > 0:
            self.logger.debug(
                f"Filtering {len(recent_shown)} recently shown products "
                f"(within {decay_hours} hours)"
            )
            filtered = products[~products['product_id'].isin(recent_shown)]
            return filtered
        
        return products
    
    def _weighted_random_selection(self, candidates: pd.DataFrame) -> pd.Series:
        """
        Perform weighted random selection based on final scores.
        
        Higher scores have higher probability of selection.
        
        Args:
            candidates: Candidate products with scores
            
        Returns:
            Selected product as Series
        """
        random_seed = self.selection_config.get('random_seed')
        
        # Ensure scores are non-negative
        scores = candidates['final_score'].values
        scores = np.maximum(scores, 0)
        
        # Add small epsilon to avoid zero probabilities
        scores = scores + 1e-10
        
        # Normalize to probabilities
        probabilities = scores / scores.sum()
        
        # Random selection
        if random_seed is not None:
            np.random.seed(random_seed)
        
        selected_idx = np.random.choice(
            candidates.index,
            p=probabilities
        )
        
        return candidates.loc[selected_idx]
    
    def _load_shown_products(self):
        """Load shown products history from JSON file."""
        try:
            if self.shown_products_path.exists():
                with open(self.shown_products_path, 'r') as f:
                    self.shown_products = json.load(f)
                self.logger.debug(f"Loaded shown products from {self.shown_products_path}")
            else:
                self.shown_products = {}
                self.logger.debug("No shown products file found, starting fresh")
        except Exception as e:
            self.logger.error(f"Error loading shown products: {e}")
            self.shown_products = {}
    
    def _record_shown_product(
        self,
        customer_id: str,
        product_id: str,
        current_time: datetime
    ):
        """
        Record that a product was shown to a customer.
        
        Args:
            customer_id: Customer ID
            product_id: Product ID
            current_time: Timestamp when shown
        """
        if customer_id not in self.shown_products:
            self.shown_products[customer_id] = {}
        
        self.shown_products[customer_id][product_id] = current_time.isoformat()
        
        # Save to file
        try:
            self.shown_products_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.shown_products_path, 'w') as f:
                json.dump(self.shown_products, f, indent=2)
            self.logger.debug(f"Recorded shown product {product_id} for customer {customer_id}")
        except Exception as e:
            self.logger.error(f"Error saving shown products: {e}")
    
    def clear_shown_products(self, customer_id: Optional[str] = None):
        """
        Clear shown products history.
        
        Args:
            customer_id: If provided, clear only for this customer. 
                        Otherwise clear all.
        """
        if customer_id:
            if customer_id in self.shown_products:
                del self.shown_products[customer_id]
                self.logger.info(f"Cleared shown products for customer {customer_id}")
        else:
            self.shown_products = {}
            self.logger.info("Cleared all shown products")
        
        # Save to file
        try:
            with open(self.shown_products_path, 'w') as f:
                json.dump(self.shown_products, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving shown products: {e}")
