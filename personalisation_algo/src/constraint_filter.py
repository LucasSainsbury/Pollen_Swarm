"""
Constraint Filter

This module implements business rule constraints that filter out products
that should not be recommended.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
import logging


class ConstraintFilter:
    """
    Filter products based on hard business rules and constraints.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the constraint filter with configuration.
        
        Args:
            config: Configuration dictionary with constraint parameters
        """
        self.config = config
        self.constraints = config['constraints']
        self.logger = logging.getLogger(__name__)
    
    def filter_products(
        self,
        customer_id: str,
        scored_products: pd.DataFrame,
        transactions: pd.DataFrame,
        current_time: datetime = None
    ) -> pd.DataFrame:
        """
        Apply all constraint filters to scored products.
        
        Args:
            customer_id: Customer ID
            scored_products: DataFrame with scored products
            transactions: Transaction history
            current_time: Current timestamp (defaults to now)
            
        Returns:
            Filtered DataFrame with valid products only
        """
        if current_time is None:
            current_time = datetime.now()
        
        filtered = scored_products.copy()
        initial_count = len(filtered)
        
        # Filter recently purchased products
        if self.constraints.get('exclude_recent_purchases_days', 0) > 0:
            filtered = self._filter_recent_purchases(
                customer_id, filtered, transactions, current_time
            )
            self.logger.debug(
                f"After recent purchase filter: {len(filtered)}/{initial_count} products"
            )
        
        # Filter discounted products
        if self.constraints.get('exclude_discounted', False):
            filtered = self._filter_discounted(filtered)
            self.logger.debug(
                f"After discount filter: {len(filtered)}/{initial_count} products"
            )
        
        # Filter out-of-stock products
        if self.constraints.get('exclude_out_of_stock', False):
            filtered = self._filter_out_of_stock(filtered)
            self.logger.debug(
                f"After stock filter: {len(filtered)}/{initial_count} products"
            )
        
        self.logger.info(
            f"Filtered {initial_count - len(filtered)} products, "
            f"{len(filtered)} candidates remaining for customer {customer_id}"
        )
        
        return filtered
    
    def _filter_recent_purchases(
        self,
        customer_id: str,
        products: pd.DataFrame,
        transactions: pd.DataFrame,
        current_time: datetime
    ) -> pd.DataFrame:
        """
        Exclude products purchased by customer in the last N days.
        
        Args:
            customer_id: Customer ID
            products: Scored products DataFrame
            transactions: Transaction history
            current_time: Current timestamp
            
        Returns:
            Filtered products
        """
        days = self.constraints['exclude_recent_purchases_days']
        cutoff_date = current_time - timedelta(days=days)
        
        # Get customer transactions
        customer_txns = transactions[transactions['customer_id'] == customer_id].copy()
        
        if len(customer_txns) == 0:
            return products
        
        # Convert dates to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(customer_txns['date_of_transaction']):
            customer_txns['date_of_transaction'] = pd.to_datetime(
                customer_txns['date_of_transaction']
            )
        
        # Find recently purchased products
        recent_txns = customer_txns[customer_txns['date_of_transaction'] >= cutoff_date]
        recent_products = set(recent_txns['product_id'].unique())
        
        if len(recent_products) > 0:
            self.logger.debug(
                f"Excluding {len(recent_products)} recently purchased products "
                f"(within {days} days)"
            )
        
        # Filter out recent products
        filtered = products[~products['product_id'].isin(recent_products)]
        
        return filtered
    
    def _filter_discounted(self, products: pd.DataFrame) -> pd.DataFrame:
        """
        Exclude products currently on discount.
        
        Args:
            products: Scored products DataFrame
            
        Returns:
            Filtered products
        """
        if 'is_discounted' not in products.columns:
            self.logger.warning("is_discounted column not found, skipping discount filter")
            return products
        
        # Keep only non-discounted products
        filtered = products[products['is_discounted'] == False]
        
        excluded_count = len(products) - len(filtered)
        if excluded_count > 0:
            self.logger.debug(f"Excluding {excluded_count} discounted products")
        
        return filtered
    
    def _filter_out_of_stock(self, products: pd.DataFrame) -> pd.DataFrame:
        """
        Exclude out-of-stock products.
        
        Args:
            products: Scored products DataFrame
            
        Returns:
            Filtered products
        """
        if 'in_stock' not in products.columns:
            self.logger.warning("in_stock column not found, skipping stock filter")
            return products
        
        # Keep only in-stock products
        filtered = products[products['in_stock'] == True]
        
        excluded_count = len(products) - len(filtered)
        if excluded_count > 0:
            self.logger.debug(f"Excluding {excluded_count} out-of-stock products")
        
        return filtered
