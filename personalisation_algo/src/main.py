"""
Main Recommendation Engine

This module orchestrates the entire recommendation pipeline.
"""

import pandas as pd
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from src.scoring_engine import ProductScoringEngine
from src.constraint_filter import ConstraintFilter
from src.selector import ProductSelector

# FastAPI imports for API
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


class RecommendationEngine:
    """
    Main orchestrator for the product recommendation system.
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize the recommendation engine.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._setup_logging()
        
        # Initialize components
        self.scoring_engine = ProductScoringEngine(self.config)
        self.constraint_filter = ConstraintFilter(self.config)
        self.selector = ProductSelector(self.config)
        
        self.logger.info("Recommendation engine initialized")
    
    def recommend_product(
        self,
        customer_id: str,
        products: pd.DataFrame,
        transactions: pd.DataFrame,
        clickstream: pd.DataFrame,
        current_time: datetime = None
    ) -> Optional[Dict]:
        """
        Recommend a single product for a customer.
        
        Args:
            customer_id: Customer ID to recommend for
            products: Product catalog DataFrame
            transactions: Transaction history DataFrame
            clickstream: Clickstream data DataFrame
            current_time: Current timestamp (defaults to now)
            
        Returns:
            Dictionary with recommendation and metadata, or None if no valid products
        """
        if current_time is None:
            current_time = datetime.now()
        
        self.logger.info(f"Generating recommendation for customer {customer_id}")
        
        try:
            # Step 1: Score all products
            scored_products = self.scoring_engine.score_products(
                customer_id=customer_id,
                products=products,
                transactions=transactions,
                clickstream=clickstream,
                current_time=current_time
            )
            
            if self.config['logging']['verbose']:
                self._log_top_scores(scored_products, customer_id)
            
            # Step 2: Apply constraints
            filtered_products = self.constraint_filter.filter_products(
                customer_id=customer_id,
                scored_products=scored_products,
                transactions=transactions,
                current_time=current_time
            )
            
            # Step 3: Select final product
            recommendation = self.selector.select_product(
                customer_id=customer_id,
                scored_products=filtered_products,
                current_time=current_time
            )
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error generating recommendation for {customer_id}: {e}", exc_info=True)
            return None
    
    def recommend_batch(
        self,
        customer_ids: List[str],
        products: pd.DataFrame,
        transactions: pd.DataFrame,
        clickstream: pd.DataFrame,
        current_time: datetime = None
    ) -> List[Dict]:
        """
        Generate recommendations for multiple customers.
        
        Args:
            customer_ids: List of customer IDs
            products: Product catalog DataFrame
            transactions: Transaction history DataFrame
            clickstream: Clickstream data DataFrame
            current_time: Current timestamp (defaults to now)
            
        Returns:
            List of recommendation dictionaries
        """
        if current_time is None:
            current_time = datetime.now()
        
        self.logger.info(f"Generating recommendations for {len(customer_ids)} customers")
        
        recommendations = []
        
        for customer_id in customer_ids:
            recommendation = self.recommend_product(
                customer_id=customer_id,
                products=products,
                transactions=transactions,
                clickstream=clickstream,
                current_time=current_time
            )
            
            if recommendation:
                recommendations.append(recommendation)
            else:
                self.logger.warning(f"No recommendation generated for customer {customer_id}")
        
        self.logger.info(
            f"Generated {len(recommendations)} recommendations out of {len(customer_ids)} customers"
        )
        
        return recommendations
    
    def load_data(
        self,
        products_path: str,
        transactions_path: str,
        clickstream_path: str
    ) -> tuple:
        """
        Load data from CSV files.
        
        Args:
            products_path: Path to products CSV
            transactions_path: Path to transactions CSV
            clickstream_path: Path to clickstream CSV
            
        Returns:
            Tuple of (products, transactions, clickstream) DataFrames
        """
        self.logger.info("Loading data files...")
        
        try:
            products = pd.read_csv(products_path)
            self.logger.info(f"Loaded {len(products)} products from {products_path}")
            
            transactions = pd.read_csv(transactions_path)
            transactions['date_of_transaction'] = pd.to_datetime(transactions['date_of_transaction'])
            self.logger.info(f"Loaded {len(transactions)} transactions from {transactions_path}")
            
            clickstream = pd.read_csv(clickstream_path)
            clickstream['event_timestamp'] = pd.to_datetime(clickstream['event_timestamp'])
            self.logger.info(f"Loaded {len(clickstream)} clickstream events from {clickstream_path}")
            
            return products, transactions, clickstream
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}", exc_info=True)
            raise
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            raise ValueError(f"Error loading config from {self.config_path}: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config['logging']['level']
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _log_top_scores(self, scored_products: pd.DataFrame, customer_id: str, top_n: int = 10):
        """Log top scoring products for debugging."""
        top_products = scored_products.nlargest(top_n, 'final_score')
        
        self.logger.debug(f"\nTop {top_n} scored products for customer {customer_id}:")
        for idx, product in top_products.iterrows():
            self.logger.debug(
                f"  {product['product_id']} ({product.get('product_name', 'Unknown')}): "
                f"score={product['final_score']:.3f} "
                f"[CA={product['category_affinity']:.2f}, "
                f"RP={product['repurchase_likelihood']:.2f}, "
                f"CI={product['clickstream_intent']:.2f}, "
                f"PP={product['product_popularity']:.2f}, "
                f"EX={product['exploration']:.2f}]"
            )


def cli_main(engine: RecommendationEngine):
    """CLI helper for manual runs."""
    import sys
    # Check if data paths provided
    if len(sys.argv) < 4:
        print("Usage: python -m src.main <products.csv> <transactions.csv> <clickstream.csv> [customer_id]")
        print("\nExample:")
        print("  python -m src.main data/products.csv data/transactions.csv data/clickstream.csv C001")
        return
    
    # Load data
    products, transactions, clickstream = engine.load_data(
        products_path=sys.argv[1],
        transactions_path=sys.argv[2],
        clickstream_path=sys.argv[3]
    )
    
    # Get customer ID
    if len(sys.argv) >= 5:
        customer_id = sys.argv[4]
    else:
        customer_id = transactions['customer_id'].iloc[0]
    
    # Generate recommendation
    recommendation = engine.recommend_product(
        customer_id=customer_id,
        products=products,
        transactions=transactions,
        clickstream=clickstream
    )
    
    if recommendation:
        print("\n" + "="*60)
        print("RECOMMENDATION")
        print("="*60)
        print(f"Customer ID: {recommendation['customer_id']}")
        print(f"Recommended Product: {recommendation['product_name']} ({recommendation['recommended_product_id']})")
        print(f"Category: {recommendation['product_category']}")
        print(f"Final Score: {recommendation['final_score']:.3f}")
        print(f"Rank: {recommendation['rank']} / {recommendation['total_candidates']}")
        print("\nScore Components:")
        for component, score in recommendation['score_components'].items():
            print(f"  {component}: {score:.3f}")
        print(f"\nTimestamp: {recommendation['timestamp']}")
        print("="*60)
    else:
        print(f"No recommendation could be generated for customer {customer_id}")


# ----- FastAPI wiring -----

class RecommendRequest(BaseModel):
    customer_id: str
    products_path: str
    transactions_path: str
    clickstream_path: str


def create_app() -> FastAPI:
    app = FastAPI(title="Recommendation Engine API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    engine = RecommendationEngine('config/config.yaml')
    
    @app.post("/recommend")
    def recommend(payload: RecommendRequest):
        try:
            products, transactions, clickstream = engine.load_data(
                products_path=payload.products_path,
                transactions_path=payload.transactions_path,
                clickstream_path=payload.clickstream_path
            )
            rec = engine.recommend_product(
                customer_id=payload.customer_id,
                products=products,
                transactions=transactions,
                clickstream=clickstream
            )
            if not rec:
                raise HTTPException(status_code=404, detail="No recommendation available")
            return rec
        except FileNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        cli_main(RecommendationEngine('config/config.yaml'))
    else:
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
