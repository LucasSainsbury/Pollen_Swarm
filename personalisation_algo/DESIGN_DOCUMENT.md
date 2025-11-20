# Product Recommendation Algorithm - Design Document

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Algorithm Components](#algorithm-components)
4. [Data Models](#data-models)
5. [Configuration Guide](#configuration-guide)
6. [Mathematical Formulations](#mathematical-formulations)
7. [Examples and Use Cases](#examples-and-use-cases)

## Overview

This system implements a hybrid product recommendation algorithm designed for personalized digital advertising in the grocery/retail sector. The algorithm combines historical purchase patterns with real-time browsing behavior to select one product per customer.

### Key Features
- **Hybrid Scoring**: Combines 5 different signals with configurable weights
- **Explainable**: Provides detailed score breakdowns
- **Grocery-Optimized**: Detects repurchase cycles for frequently bought items
- **Real-Time Context**: Incorporates recent clickstream behavior
- **Variety Mechanism**: Ensures different products on multiple runs
- **Configurable**: All parameters adjustable via YAML without code changes

### Design Philosophy
- **Heuristic-Based**: No ML training required, fast to deploy
- **Transparent**: All scoring logic is explicit and explainable
- **Scalable**: Designed for 50 customers with 6 months of data
- **Modular**: Each component can be tuned independently

## System Architecture

### High-Level Pipeline

```
┌─────────────┐
│   Input     │
│   Data      │
└──────┬──────┘
       │
       ├─ Products Catalog
       ├─ Transaction History
       └─ Clickstream Data
       │
       ▼
┌──────────────────┐
│  Scoring Engine  │
│                  │
│  ┌────────────┐  │
│  │ Category   │  │  30%
│  │ Affinity   │──┤
│  └────────────┘  │
│  ┌────────────┐  │
│  │ Repurchase │  │  25%
│  │ Likelihood │──┤
│  └────────────┘  │
│  ┌────────────┐  │
│  │Clickstream │  │  25%
│  │  Intent    │──┤
│  └────────────┘  │
│  ┌────────────┐  │
│  │  Product   │  │  10%
│  │ Popularity │──┤
│  └────────────┘  │
│  ┌────────────┐  │
│  │Exploration │  │  10%
│  └────────────┘  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Constraint       │
│ Filter           │
│                  │
│ • Recent         │
│   Purchases      │
│ • Discounted     │
│ • Out of Stock   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Product          │
│ Selector         │
│                  │
│ • Top-K Filter   │
│ • Shown History  │
│ • Weighted       │
│   Random         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Recommendation   │
│ Output           │
└──────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Output |
|-----------|---------------|--------|
| **Scoring Engine** | Calculate scores for all products using 5 components | Scored products DataFrame |
| **Constraint Filter** | Apply hard business rules to exclude invalid products | Filtered products DataFrame |
| **Product Selector** | Select final product with variety mechanism | Single product recommendation |
| **Recommendation Engine** | Orchestrate pipeline and manage configuration | Final recommendation JSON |

## Algorithm Components

### 1. Category Affinity (30% weight)

**Purpose**: Capture customer's historical category preferences with time decay.

**Logic**:
- Calculate time-weighted scores for each category based on purchase history
- Recent purchases have higher influence (exponential decay)
- Products in preferred categories score higher

**Parameters**:
- `decay_days`: Half-life for exponential decay (default: 90 days)

**Normalization**: Scores normalized to [0, 1] range

### 2. Repurchase Likelihood (25% weight)

**Purpose**: Identify products due for repurchase based on customer's buying cycles.

**Logic**:
- For each product previously purchased, calculate average repurchase cycle
- Use Gaussian distribution centered at expected next purchase date
- Score peaks when current time matches expected repurchase time

**Parameters**:
- `expected_cycle_days`: Default cycle for grocery items (default: 14 days)
- `cycle_std_days`: Standard deviation for Gaussian curve (default: 7 days)
- `min_purchases`: Minimum purchases to calculate cycle (default: 2)

**Normalization**: Gaussian output naturally in [0, 1] range

### 3. Clickstream Intent (25% weight)

**Purpose**: Capture real-time customer interest from browsing behavior.

**Logic**:
- Score products based on recent interactions (views, clicks, cart adds)
- Combine event recency with event type importance
- More recent events and higher-intent actions score higher

**Parameters**:
- `recency_weight`: Balance between recency vs event type (default: 0.7)
- `decay_hours`: Recency decay window (default: 24 hours)
- `event_weights`: Scores for view (0.3), click (0.5), add_to_cart (1.0)

**Normalization**: Combined scores normalized to [0, 1]

### 4. Product Popularity (10% weight)

**Purpose**: Promote globally popular products as safe recommendations.

**Logic**:
- Combine number of unique customers with purchase frequency
- More widely purchased products score higher
- Serves as a baseline recommendation

**Parameters**:
- `customer_weight`: Weight for unique customers (default: 0.6)
- `frequency_weight`: Weight for purchase frequency (default: 0.4)

**Normalization**: Both metrics normalized to [0, 1] and combined

### 5. Exploration (10% weight)

**Purpose**: Introduce randomness for variety and serendipity.

**Logic**:
- Generate random scores for all products
- Ensures different products can be selected on multiple runs
- Prevents algorithm from being too deterministic

**Parameters**:
- `random_seed`: Optional seed for reproducibility

**Normalization**: Random values in [0, 1]

### Final Score Calculation

```
final_score = 0.30 × category_affinity +
              0.25 × repurchase_likelihood +
              0.25 × clickstream_intent +
              0.10 × product_popularity +
              0.10 × exploration
```

## Data Models

### Products Catalog

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| product_id | string | Unique product identifier | Yes |
| product_name | string | Display name | Yes |
| product_category | string | Product category | Yes |
| is_discounted | boolean | Currently on discount | Yes |
| in_stock | boolean | Availability status | Yes |
| price | float | Product price | No |

**Example**:
```csv
product_id,product_name,product_category,is_discounted,in_stock,price
P001,Organic Milk 1L,dairy,false,true,3.99
P002,Whole Wheat Bread,bakery,true,true,2.49
```

### Transaction History

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| customer_id | string | Customer identifier | Yes |
| product_id | string | Product purchased | Yes |
| date_of_transaction | date | Purchase date (YYYY-MM-DD) | Yes |
| quantity | integer | Units purchased | Yes |
| product_category | string | Product category | Yes |
| total_amount | float | Transaction amount | No |
| store_id | string | Store location | No |

**Example**:
```csv
customer_id,product_id,date_of_transaction,quantity,product_category,total_amount,store_id
C001,P001,2024-11-01,2,dairy,7.98,S001
C001,P002,2024-11-03,1,bakery,2.49,S001
```

### Clickstream Data

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| customer_id | string | Customer identifier | Yes |
| session_id | string | Session identifier | Yes |
| event_id | string | Unique event ID | Yes |
| event_timestamp | datetime | Event time (ISO format) | Yes |
| event_type | string | view/click/add_to_cart | Yes |
| page_category | string | Page category | No |
| device_type | string | Device used | No |
| product_id | string | Product interacted with | No* |

*Required for product-specific events

**Example**:
```csv
customer_id,session_id,event_id,event_timestamp,event_type,page_category,device_type,product_id
C001,S001,E001,2024-11-20T10:30:00,view,dairy,mobile,P001
C001,S001,E002,2024-11-20T10:31:15,add_to_cart,dairy,mobile,P001
```

### Recommendation Output

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

## Configuration Guide

### config.yaml Structure

```yaml
scoring_weights:         # Must sum to 1.0
  category_affinity: 0.30
  repurchase_likelihood: 0.25
  clickstream_intent: 0.25
  product_popularity: 0.10
  exploration: 0.10

category_affinity:
  decay_days: 90        # Time decay for preferences

repurchase_likelihood:
  expected_cycle_days: 14
  cycle_std_days: 7
  min_purchases: 2

clickstream_intent:
  recency_weight: 0.7
  decay_hours: 24
  event_weights:
    view: 0.3
    click: 0.5
    add_to_cart: 1.0

product_popularity:
  customer_weight: 0.6
  frequency_weight: 0.4

constraints:
  exclude_recent_purchases_days: 14
  exclude_discounted: true
  exclude_out_of_stock: true

selection:
  top_k: 20
  decay_hours: 24
  random_seed: null

logging:
  level: INFO
  verbose: false
```

### Tuning Guide

**To prioritize recent purchases**:
- Increase `category_affinity` weight
- Decrease `decay_days`

**To emphasize repurchase patterns**:
- Increase `repurchase_likelihood` weight
- Adjust `expected_cycle_days` for your product mix

**To focus on real-time behavior**:
- Increase `clickstream_intent` weight
- Decrease `decay_hours` for shorter memory

**To increase variety**:
- Increase `exploration` weight
- Decrease `top_k` for more randomness

**To promote popular items**:
- Increase `product_popularity` weight

## Mathematical Formulations

### Category Affinity Score

For product *p* with category *c*:

```
weight(t) = exp(-days_ago(t) / decay_days)

category_score(c) = Σ weight(t) × log(1 + quantity(t))
                    t ∈ purchases(c)

score(p) = category_score(category(p)) / max(category_scores)
```

### Repurchase Likelihood Score

For product *p* previously purchased:

```
avg_cycle = mean(diff(purchase_dates))

days_since_last = current_time - last_purchase_date

deviation = |days_since_last - avg_cycle|

score(p) = exp(-(deviation² / (2 × cycle_std²)))
```

If product never purchased: `score(p) = 0`

### Clickstream Intent Score

For product *p*:

```
recency_score(e) = exp(-hours_ago(e) / decay_hours)

event_weight(e) = weight_map[event_type(e)]

combined_score(e) = recency_weight × recency_score(e) +
                    (1 - recency_weight) × event_weight(e)

score(p) = Σ combined_score(e) / max(all_scores)
           e ∈ events(p)
```

### Product Popularity Score

```
customer_score(p) = unique_customers(p) / max(unique_customers)

frequency_score(p) = total_quantity(p) / max(total_quantity)

score(p) = customer_weight × customer_score(p) +
           frequency_weight × frequency_score(p)
```

### Weighted Random Selection

Given candidate products with scores *s₁, s₂, ..., sₙ*:

```
probability(pᵢ) = sᵢ / Σsⱼ

selected_product ~ Multinomial(probabilities)
```

Higher scores have proportionally higher selection probability.

## Examples and Use Cases

### Use Case 1: Regular Grocery Shopper

**Profile**: Customer buys milk every 14 days

**Scenario**: Last milk purchase was 13 days ago, recently viewed dairy section

**Expected Behavior**:
- High `repurchase_likelihood` (near expected cycle)
- High `category_affinity` (dairy preference)
- High `clickstream_intent` (recent dairy views)
- Milk products recommended

### Use Case 2: New Customer

**Profile**: First-time customer, minimal history

**Scenario**: Browsed electronics, no purchases yet

**Expected Behavior**:
- Low `category_affinity` (no history)
- Zero `repurchase_likelihood` (no purchases)
- Medium `clickstream_intent` (browsing data)
- High `product_popularity` (compensates for no history)
- Popular electronics recommended

### Use Case 3: Variety Seeker

**Profile**: Customer buys diverse products

**Scenario**: Run algorithm multiple times

**Expected Behavior**:
- `exploration` component provides variety
- Recently shown products filtered
- Different products selected each run
- Still relevant to customer preferences

### Use Case 4: High-Intent Shopper

**Profile**: Customer added items to cart

**Scenario**: Multiple add_to_cart events for specific products

**Expected Behavior**:
- Very high `clickstream_intent` (cart adds = 1.0)
- Products with cart adds prioritized
- Strong signal overrides other factors

### Performance Characteristics

| Metric | Expected Value |
|--------|---------------|
| Execution Time | < 5 seconds per customer |
| Products Processed | ~200 products |
| Transaction History | 6 months |
| Clickstream Events | Last 24-48 hours |
| Memory Usage | < 500 MB |

### Error Handling

| Scenario | Behavior |
|----------|----------|
| No valid products after filtering | Return `None` |
| Customer has no history | Use popularity + exploration |
| No clickstream data | Score = 0 for that component |
| All products recently shown | Fall back to all products |
| Missing data columns | Log warning, skip that filter |

### Limitations

1. **Cold Start**: New customers rely heavily on popularity
2. **No Feedback Loop**: Doesn't learn from recommendation success
3. **Static Weights**: Requires manual tuning per use case
4. **Single Product**: Only one product recommended at a time
5. **Heuristic-Based**: Not ML-optimized for conversions

### Future Enhancements

- **Multi-Product Recommendations**: Return ranked lists
- **A/B Testing Framework**: Test different weight configurations
- **Feedback Loop**: Learn from click-through and conversion rates
- **Contextual Factors**: Time of day, weather, promotions
- **Collaborative Filtering**: Similar customer preferences
- **Deep Learning**: Neural network-based scoring
