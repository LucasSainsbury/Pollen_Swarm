"""
Example: Batch recommendations for multiple customers
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import RecommendationEngine
import json

def main():
    # Initialize engine
    engine = RecommendationEngine('config/config.yaml')
    
    # Load data
    print("Loading data...")
    products, transactions, clickstream = engine.load_data(
        products_path='data/sample_products.csv',
        transactions_path='data/sample_transactions.csv',
        clickstream_path='data/sample_clickstream.csv'
    )
    
    # Get all customer IDs
    customer_ids = transactions['customer_id'].unique().tolist()
    print(f"\nGenerating recommendations for {len(customer_ids)} customers...")
    
    # Generate batch recommendations
    recommendations = engine.recommend_batch(
        customer_ids=customer_ids,
        products=products,
        transactions=transactions,
        clickstream=clickstream
    )
    
    # Display results
    print(f"\n{'='*70}")
    print(f"BATCH RECOMMENDATIONS - {len(recommendations)} customers")
    print(f"{'='*70}\n")
    
    for rec in recommendations:
        print(f"Customer: {rec['customer_id']}")
        print(f"  Product: {rec['product_name']} ({rec['recommended_product_id']})")
        print(f"  Category: {rec['product_category']}")
        print(f"  Score: {rec['final_score']:.3f}")
        print(f"  Rank: {rec['rank']} / {rec['total_candidates']}")
        print()
    
    # Save to file
    with open('recommendations_output.json', 'w') as f:
        json.dump(recommendations, f, indent=2)
    print(f"Saved recommendations to recommendations_output.json")

if __name__ == '__main__':
    main()
