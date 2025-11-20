"""
Product Scoring Engine

This module implements the hybrid scoring system that combines multiple signals
to score products for recommendation.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging


class ProductScoringEngine:
    """
    Main scoring engine that combines multiple scoring components to generate
    final product scores for recommendation.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the scoring engine with configuration.
        
        Args:
            config: Configuration dictionary with scoring parameters
        """
        self.config = config
        self.weights = config['scoring_weights']
        self.logger = logging.getLogger(__name__)
        
        # Validate weights sum to 1.0
        weight_sum = sum(self.weights.values())
        if not (0.99 <= weight_sum <= 1.01):  # Allow small floating point error
            self.logger.warning(f"Scoring weights sum to {weight_sum}, expected 1.0")
    
    def score_products(
        self,
        customer_id: str,
        products: pd.DataFrame,
        transactions: pd.DataFrame,
        clickstream: pd.DataFrame,
        current_time: datetime = None
    ) -> pd.DataFrame:
        """
        Score all products for a given customer using all components.
        
        Args:
            customer_id: Customer ID to score products for
            products: Product catalog DataFrame
            transactions: Transaction history DataFrame
            clickstream: Clickstream data DataFrame
            current_time: Current timestamp (defaults to now)
            
        Returns:
            DataFrame with products and their scores
        """
        if current_time is None:
            current_time = datetime.now()
            
        # Filter customer data
        customer_txns = transactions[transactions['customer_id'] == customer_id].copy()
        customer_clicks = clickstream[clickstream['customer_id'] == customer_id].copy()
        
        # Initialize scores DataFrame
        scored_products = products.copy()
        
        # Calculate each scoring component
        self.logger.debug(f"Scoring {len(scored_products)} products for customer {customer_id}")
        
        scored_products['category_affinity'] = self._score_category_affinity(
            scored_products, customer_txns, current_time
        )
        
        scored_products['repurchase_likelihood'] = self._score_repurchase_likelihood(
            scored_products, customer_txns, current_time
        )
        
        scored_products['clickstream_intent'] = self._score_clickstream_intent(
            scored_products, customer_clicks, current_time
        )
        
        scored_products['product_popularity'] = self._score_product_popularity(
            scored_products, transactions
        )
        
        scored_products['exploration'] = self._score_exploration(scored_products)
        
        # Calculate final weighted score
        scored_products['final_score'] = (
            self.weights['category_affinity'] * scored_products['category_affinity'] +
            self.weights['repurchase_likelihood'] * scored_products['repurchase_likelihood'] +
            self.weights['clickstream_intent'] * scored_products['clickstream_intent'] +
            self.weights['product_popularity'] * scored_products['product_popularity'] +
            self.weights['exploration'] * scored_products['exploration']
        )
        
        return scored_products
    
    def _score_category_affinity(
        self,
        products: pd.DataFrame,
        customer_txns: pd.DataFrame,
        current_time: datetime
    ) -> pd.Series:
        """
        Score products based on time-weighted historical category preferences.
        
        Uses exponential decay to give more weight to recent purchases.
        
        Args:
            products: Product catalog
            customer_txns: Customer transaction history
            current_time: Current timestamp
            
        Returns:
            Series of category affinity scores [0, 1]
        """
        if len(customer_txns) == 0:
            return pd.Series(0.0, index=products.index)
        
        decay_days = self.config['category_affinity']['decay_days']
        
        # Convert dates to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(customer_txns['date_of_transaction']):
            customer_txns = customer_txns.copy()
            customer_txns['date_of_transaction'] = pd.to_datetime(customer_txns['date_of_transaction'])
        
        # Calculate days since purchase
        customer_txns = customer_txns.copy()
        customer_txns['days_ago'] = (current_time - customer_txns['date_of_transaction']).dt.days
        
        # Apply exponential decay: weight = exp(-days_ago / decay_days)
        customer_txns['weight'] = np.exp(-customer_txns['days_ago'] / decay_days)
        
        # Calculate weighted category scores
        category_scores = customer_txns.groupby('product_category').agg({
            'weight': 'sum',
            'quantity': 'sum'
        })
        category_scores['score'] = category_scores['weight'] * np.log1p(category_scores['quantity'])
        
        # Normalize to [0, 1]
        if category_scores['score'].max() > 0:
            category_scores['score'] = category_scores['score'] / category_scores['score'].max()
        
        # Map to products
        category_score_dict = category_scores['score'].to_dict()
        scores = products['product_category'].map(category_score_dict).fillna(0.0)
        
        return scores
    
    def _score_repurchase_likelihood(
        self,
        products: pd.DataFrame,
        customer_txns: pd.DataFrame,
        current_time: datetime
    ) -> pd.Series:
        """
        Score products based on repurchase cycle patterns using Gaussian curves.
        
        For grocery items, customers tend to repurchase on regular cycles.
        This uses a Gaussian distribution around the expected next purchase time.
        
        Args:
            products: Product catalog
            customer_txns: Customer transaction history
            current_time: Current timestamp
            
        Returns:
            Series of repurchase likelihood scores [0, 1]
        """
        if len(customer_txns) == 0:
            return pd.Series(0.0, index=products.index)
        
        expected_cycle = self.config['repurchase_likelihood']['expected_cycle_days']
        cycle_std = self.config['repurchase_likelihood']['cycle_std_days']
        min_purchases = self.config['repurchase_likelihood']['min_purchases']
        
        # Convert dates to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(customer_txns['date_of_transaction']):
            customer_txns = customer_txns.copy()
            customer_txns['date_of_transaction'] = pd.to_datetime(customer_txns['date_of_transaction'])
        
        scores = []
        
        for idx, product in products.iterrows():
            product_txns = customer_txns[
                customer_txns['product_id'] == product['product_id']
            ].sort_values('date_of_transaction')
            
            if len(product_txns) < min_purchases:
                scores.append(0.0)
                continue
            
            # Get last purchase date and calculate days since
            last_purchase = product_txns['date_of_transaction'].iloc[-1]
            days_since = (current_time - last_purchase).days
            
            # Calculate average cycle for this product
            if len(product_txns) >= 2:
                purchase_dates = product_txns['date_of_transaction'].values
                cycles = np.diff(purchase_dates).astype('timedelta64[D]').astype(int)
                avg_cycle = np.mean(cycles)
            else:
                avg_cycle = expected_cycle
            
            # Use Gaussian centered at average cycle
            # Score is high when days_since is close to avg_cycle
            deviation = abs(days_since - avg_cycle)
            score = np.exp(-(deviation ** 2) / (2 * cycle_std ** 2))
            
            scores.append(score)
        
        return pd.Series(scores, index=products.index)
    
    def _score_clickstream_intent(
        self,
        products: pd.DataFrame,
        customer_clicks: pd.DataFrame,
        current_time: datetime
    ) -> pd.Series:
        """
        Score products based on real-time browsing behavior.
        
        Combines event recency with event type importance.
        
        Args:
            products: Product catalog
            customer_clicks: Customer clickstream data
            current_time: Current timestamp
            
        Returns:
            Series of clickstream intent scores [0, 1]
        """
        if len(customer_clicks) == 0:
            return pd.Series(0.0, index=products.index)
        
        recency_weight = self.config['clickstream_intent']['recency_weight']
        decay_hours = self.config['clickstream_intent']['decay_hours']
        event_weights = self.config['clickstream_intent']['event_weights']
        
        # Convert timestamps to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(customer_clicks['event_timestamp']):
            customer_clicks = customer_clicks.copy()
            customer_clicks['event_timestamp'] = pd.to_datetime(customer_clicks['event_timestamp'])
        
        customer_clicks = customer_clicks.copy()
        
        # Calculate hours since event
        customer_clicks['hours_ago'] = (
            current_time - customer_clicks['event_timestamp']
        ).dt.total_seconds() / 3600
        
        # Apply recency decay
        customer_clicks['recency_score'] = np.exp(-customer_clicks['hours_ago'] / decay_hours)
        
        # Map event types to weights
        customer_clicks['event_weight'] = customer_clicks['event_type'].map(
            event_weights
        ).fillna(0.3)  # Default weight for unknown events
        
        # Combined score: weighted average of recency and event type
        customer_clicks['combined_score'] = (
            recency_weight * customer_clicks['recency_score'] +
            (1 - recency_weight) * customer_clicks['event_weight']
        )
        
        # Aggregate by product - filter clicks with product_id
        product_clicks = customer_clicks[customer_clicks['product_id'].notna()]
        
        if len(product_clicks) == 0:
            return pd.Series(0.0, index=products.index)
        
        # Sum scores by product
        click_scores = product_clicks.groupby('product_id')['combined_score'].sum()
        
        # Normalize to [0, 1]
        if click_scores.max() > 0:
            click_scores = click_scores / click_scores.max()
        
        # Map to products
        scores = products['product_id'].map(click_scores).fillna(0.0)
        
        return scores
    
    def _score_product_popularity(
        self,
        products: pd.DataFrame,
        all_transactions: pd.DataFrame
    ) -> pd.Series:
        """
        Score products based on global popularity.
        
        Combines unique customers and purchase frequency.
        
        Args:
            products: Product catalog
            all_transactions: All transaction data
            
        Returns:
            Series of popularity scores [0, 1]
        """
        if len(all_transactions) == 0:
            return pd.Series(0.5, index=products.index)  # Neutral score
        
        customer_weight = self.config['product_popularity']['customer_weight']
        frequency_weight = self.config['product_popularity']['frequency_weight']
        
        # Calculate metrics by product
        popularity = all_transactions.groupby('product_id').agg({
            'customer_id': 'nunique',  # Unique customers
            'quantity': 'sum'           # Total quantity sold
        }).rename(columns={'customer_id': 'unique_customers', 'quantity': 'total_quantity'})
        
        # Normalize each metric to [0, 1]
        if popularity['unique_customers'].max() > 0:
            popularity['customer_score'] = (
                popularity['unique_customers'] / popularity['unique_customers'].max()
            )
        else:
            popularity['customer_score'] = 0.0
        
        if popularity['total_quantity'].max() > 0:
            popularity['frequency_score'] = (
                popularity['total_quantity'] / popularity['total_quantity'].max()
            )
        else:
            popularity['frequency_score'] = 0.0
        
        # Weighted combination
        popularity['score'] = (
            customer_weight * popularity['customer_score'] +
            frequency_weight * popularity['frequency_score']
        )
        
        # Map to products
        popularity_dict = popularity['score'].to_dict()
        scores = products['product_id'].map(popularity_dict).fillna(0.5)  # Default middle score
        
        return scores
    
    def _score_exploration(self, products: pd.DataFrame) -> pd.Series:
        """
        Generate random exploration scores for variety.
        
        Args:
            products: Product catalog
            
        Returns:
            Series of random scores [0, 1]
        """
        random_seed = self.config['selection'].get('random_seed')
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        scores = pd.Series(
            np.random.random(len(products)),
            index=products.index
        )
        
        return scores
