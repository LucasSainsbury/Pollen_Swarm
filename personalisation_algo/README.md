# Product Recommendation Algorithm

A hybrid product recommendation system that combines historical purchase patterns with real-time browsing behavior to deliver personalized product recommendations for digital advertising.

## Features

✅ **Hybrid Scoring**: Combines 5 different signals (category affinity, repurchase likelihood, clickstream intent, popularity, exploration)

✅ **Explainable**: Provides detailed score breakdowns for every recommendation

✅ **Grocery-Optimized**: Detects repurchase cycles for frequently bought items

✅ **Real-Time Context**: Incorporates recent browsing behavior

✅ **Variety Mechanism**: Ensures different products on multiple runs

✅ **Configurable**: All parameters adjustable via YAML without code changes

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/waqas-saeed/personalisation-algo.git
cd personalisation-algo

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.main import RecommendationEngine

# Initialize the engine
engine = RecommendationEngine('config/config.yaml')

# Load your data
products, transactions, clickstream = engine.load_data(
    products_path='data/products.csv',
    transactions_path='data/transactions.csv',
    clickstream_path='data/clickstream.csv'
)

# Get recommendation for a customer
recommendation = engine.recommend_product(
    customer_id='C001',
    products=products,
    transactions=transactions,
    clickstream=clickstream
)

print(recommendation)
```

### Command Line Usage

```bash
python -m src.main data/products.csv data/transactions.csv data/clickstream.csv C001
```

## Data Requirements

### Products Catalog (CSV)

```csv
product_id,product_name,product_category,is_discounted,in_stock,price
P001,Organic Milk 1L,dairy,false,true,3.99
P002,Whole Wheat Bread,bakery,false,true,2.49
```

**Required columns**: `product_id`, `product_name`, `product_category`, `is_discounted`, `in_stock`

### Transaction History (CSV)

```csv
customer_id,product_id,date_of_transaction,quantity,product_category,total_amount,store_id
C001,P001,2024-11-01,2,dairy,7.98,S001
C001,P002,2024-11-03,1,bakery,2.49,S001
```

**Required columns**: `customer_id`, `product_id`, `date_of_transaction`, `quantity`, `product_category`

### Clickstream Data (CSV)

```csv
customer_id,session_id,event_id,event_timestamp,event_type,page_category,device_type,product_id
C001,S001,E001,2024-11-20T10:30:00,view,dairy,mobile,P001
C001,S001,E002,2024-11-20T10:31:15,add_to_cart,dairy,mobile,P001
```

**Required columns**: `customer_id`, `session_id`, `event_id`, `event_timestamp`, `event_type`

**Event types**: `view`, `click`, `add_to_cart`

## Output Format

```json
{
  "customer_id": "C001",
  "recommended_product_id": "P001",
  "product_name": "Organic Milk 1L",
  "product_category": "dairy",
  "final_score": 0.847,
  "score_components": {
    "category_affinity": 0.71,
    "repurchase_likelihood": 0.90,
    "clickstream_intent": 1.00,
    "product_popularity": 0.85,
    "exploration": 0.42
  },
  "rank": 3,
  "total_candidates": 157,
  "timestamp": "2025-11-20T14:22:47Z"
}
```

## Configuration

Edit `config/config.yaml` to customize the algorithm behavior:

```yaml
# Scoring component weights (must sum to 1.0)
scoring_weights:
  category_affinity: 0.30      # Historical preferences
  repurchase_likelihood: 0.25  # Buying cycles
  clickstream_intent: 0.25     # Recent browsing
  product_popularity: 0.10     # Global popularity
  exploration: 0.10            # Randomness for variety

# Adjust individual component parameters
category_affinity:
  decay_days: 90  # Time decay for preferences

repurchase_likelihood:
  expected_cycle_days: 14  # Default repurchase cycle
  cycle_std_days: 7
  min_purchases: 2

clickstream_intent:
  recency_weight: 0.7
  decay_hours: 24
  event_weights:
    view: 0.3
    click: 0.5
    add_to_cart: 1.0

# Business constraints
constraints:
  exclude_recent_purchases_days: 14
  exclude_discounted: true
  exclude_out_of_stock: true

# Selection parameters
selection:
  top_k: 20        # Number of top candidates
  decay_hours: 24  # Shown product tracking window
```

## API Reference

### RecommendationEngine

Main class for generating recommendations.

#### `__init__(config_path: str)`

Initialize the recommendation engine.

**Parameters**:
- `config_path`: Path to YAML configuration file

#### `recommend_product(customer_id, products, transactions, clickstream, current_time=None)`

Generate a recommendation for a single customer.

**Parameters**:
- `customer_id` (str): Customer ID to recommend for
- `products` (DataFrame): Product catalog
- `transactions` (DataFrame): Transaction history
- `clickstream` (DataFrame): Clickstream data
- `current_time` (datetime, optional): Current timestamp

**Returns**: Dictionary with recommendation and metadata, or `None` if no valid products

#### `recommend_batch(customer_ids, products, transactions, clickstream, current_time=None)`

Generate recommendations for multiple customers.

**Parameters**:
- `customer_ids` (List[str]): List of customer IDs
- `products` (DataFrame): Product catalog
- `transactions` (DataFrame): Transaction history
- `clickstream` (DataFrame): Clickstream data
- `current_time` (datetime, optional): Current timestamp

**Returns**: List of recommendation dictionaries

#### `load_data(products_path, transactions_path, clickstream_path)`

Load data from CSV files.

**Parameters**:
- `products_path` (str): Path to products CSV
- `transactions_path` (str): Path to transactions CSV
- `clickstream_path` (str): Path to clickstream CSV

**Returns**: Tuple of (products, transactions, clickstream) DataFrames

## Examples

### Example 1: Single Customer Recommendation

```python
from src.main import RecommendationEngine
import pandas as pd

engine = RecommendationEngine()

# Load data
products = pd.read_csv('data/products.csv')
transactions = pd.read_csv('data/transactions.csv')
clickstream = pd.read_csv('data/clickstream.csv')

# Get recommendation
result = engine.recommend_product(
    customer_id='C001',
    products=products,
    transactions=transactions,
    clickstream=clickstream
)

print(f"Recommended: {result['product_name']}")
print(f"Score: {result['final_score']:.3f}")
```

### Example 2: Batch Recommendations

```python
from src.main import RecommendationEngine

engine = RecommendationEngine()
products, transactions, clickstream = engine.load_data(
    'data/products.csv',
    'data/transactions.csv',
    'data/clickstream.csv'
)

# Get all customer IDs
customer_ids = transactions['customer_id'].unique().tolist()

# Generate recommendations for all customers
recommendations = engine.recommend_batch(
    customer_ids=customer_ids,
    products=products,
    transactions=transactions,
    clickstream=clickstream
)

print(f"Generated {len(recommendations)} recommendations")

# Save to file
import json
with open('recommendations.json', 'w') as f:
    json.dump(recommendations, f, indent=2)
```

### Example 3: Custom Configuration

```python
from src.main import RecommendationEngine

# Use custom config file
engine = RecommendationEngine('config/custom_config.yaml')

# ... generate recommendations
```

### Example 4: Verbose Logging

```python
from src.main import RecommendationEngine
import logging

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

engine = RecommendationEngine()
# ... will now show detailed debug information
```

## Algorithm Components

### 1. Category Affinity (30% weight)
Scores products based on time-weighted historical category preferences. Recent purchases in a category boost products from that category.

### 2. Repurchase Likelihood (25% weight)
Identifies products due for repurchase based on customer's buying cycles. Uses Gaussian distribution around expected next purchase date.

### 3. Clickstream Intent (25% weight)
Captures real-time customer interest from browsing behavior. Combines event recency with event type importance.

### 4. Product Popularity (10% weight)
Promotes globally popular products based on unique customers and purchase frequency.

### 5. Exploration (10% weight)
Introduces randomness for variety and serendipity, preventing overly deterministic recommendations.

## Constraints

The algorithm enforces the following hard constraints:

1. **Recent Purchases**: Excludes products purchased in last 14 days (configurable)
2. **Discounted Products**: Excludes products currently on discount
3. **Out of Stock**: Excludes unavailable products

## Variety Mechanism

To ensure variety across multiple runs:

1. Top-K candidates are selected (default: 20)
2. Recently shown products are filtered (24-hour window)
3. Weighted random selection from remaining candidates
4. Shown products tracked in `data/shown_products.json`

## Performance

- **Execution Time**: < 5 seconds per customer
- **Data Volume**: Designed for 50 customers, ~200 transactions each, 6 months history
- **Memory Usage**: < 500 MB

## Troubleshooting

### No recommendation generated

**Cause**: All products filtered out by constraints

**Solution**: 
- Check constraint settings in config
- Verify product catalog has valid products (in stock, not discounted)
- Check if customer has recent purchases excluding all products

### Always recommends same product

**Cause**: Exploration weight too low or random_seed set

**Solution**:
- Increase exploration weight in config
- Remove or change random_seed setting
- Verify shown_products.json is being updated

### Poor recommendations

**Cause**: Weights not tuned for your data

**Solution**:
- Analyze score components in output
- Adjust weights based on which signals are most predictive
- Consider your use case (e.g., increase clickstream for real-time targeting)

## Documentation

For detailed algorithm documentation, see [DESIGN_DOCUMENT.md](DESIGN_DOCUMENT.md)

## Requirements

- Python 3.8+
- pandas >= 2.0.0
- numpy >= 1.24.0
- pyyaml >= 6.0

## License

This project is provided as-is for evaluation purposes.

## Contributing

This is a demonstration project. For questions or issues, please contact the repository owner.

## Acknowledgments

Built as an MVP recommendation system for grocery/retail personalization.
