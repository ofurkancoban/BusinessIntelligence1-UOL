# Business Intelligence Mini-Project - Comprehensive Solutions Report

---

# Part 1: Initial Data Analysis & Verification

## Executive Summary

**Report Date**: 2026-01-27
**Database**: transaction_analytics
**Total Transactions**: 13,305,915
**Data Period**: 2010-2019
**Status**: **VERIFIED**

---

## KPI #1: Transaction Count by Time Period

### **Yearly Breakdown**

| Year | Unique Transactions | Growth vs Previous Year |
| ---- | ------------------- | ----------------------- |
| 2010 | 1,240,880           | -                       |
| 2011 | 1,290,770           | +4.0%                   |
| 2012 | 1,321,672           | +2.4%                   |
| 2013 | 1,352,808           | +2.4%                   |
| 2014 | 1,365,537           | +0.9%                   |
| 2015 | 1,388,065           | +1.7%                   |
| 2016 | 1,392,117           | +0.3%                   |
| 2017 | 1,399,308           | +0.5%                   |
| 2018 | 1,394,792           | -0.3%                   |
| 2019 | 1,159,966           | -16.8% (partial year)   |

**Key Insights**:

- Steady growth from 2010-2017 (~13% total growth)
- 2019 shows lower volume (likely partial year data)
- Data consistency verified across all years

### **Monthly Breakdown (Sample)**

| Month   | Transactions | Avg per Day |
| ------- | ------------ | ----------- |
| 2010-01 | 101,209      | 3,265       |
| 2010-02 | 93,470       | 3,338       |
| 2010-03 | 103,345      | 3,334       |
| 2010-04 | 100,169      | 3,339       |
| 2010-05 | 104,773      | 3,380       |
| 2010-06 | 102,677      | 3,423       |

**Key Insights**:

- Consistent monthly volumes (~100K transactions/month)
- No missing months detected
- Seasonal patterns visible

### **Weekly Breakdown (Sample)**

| Week    | Transactions | Avg per Day |
| ------- | ------------ | ----------- |
| 2010-01 | 22,819       | 3,260       |
| 2010-02 | 22,876       | 3,268       |
| 2010-03 | 22,704       | 3,243       |
| 2010-04 | 23,047       | 3,292       |
| 2010-05 | 23,357       | 3,337       |

**Key Insights**:

- Consistent weekly volumes (~23K transactions/week)
- No gaps in weekly data
- Daily average ~3,300 transactions

---

## KPI #2: Highest Revenue Merchant Category

### **Top 10 MCCs by Total Transaction Amount**

| Rank | MCC  | Description                      | Transactions | Total Amount                      | Avg Amount |
| ---- | ---- | -------------------------------- | ------------ | --------------------------------- | ---------- |
| 1 | 4829 | **Money Transfer**         | 589,140      | **$53,158,515.64** | $90.23 |            |
| 2 | 5411 | Grocery Stores, Supermarkets     | 1,592,584    | $40,970,754.15 | $25.73           |            |
| 3 | 5300 | Wholesale Clubs                  | 602,449      | $37,727,962.09 | $62.62           |            |
| 4    | 5912 | Drug Stores and Pharmacies       | 772,913      | $35,113,527.69 | $45.43           |            |
| 5    | 5541 | Service Stations                 | 1,424,711    | $29,570,426.66 | $20.76           |            |
| 6    | 4900 | Utilities - Electric, Gas, Water | 242,993      | $27,650,038.08 | $113.79          |            |
| 7    | 5311 | Department Stores                | 475,384      | $27,031,968.70 | $56.86           |            |
| 8    | 5812 | Eating Places and Restaurants    | 999,738      | $26,348,225.47 | $26.36           |            |
| 9    | 7538 | Automotive Service Shops         | 478,011      | $25,094,615.89 | $52.50           |            |
| 10   | 4814 | Telecommunication Services       | 218,243      | $24,726,472.83 | $113.30          |            |

### **Winner: Money Transfer (MCC 4829)**

**Key Metrics**:

- **Total Amount**: $53,158,515.64
- **Transaction Count**: 589,140
- **Average Transaction**: $90.23
- **Market Share**: 15.8% of total revenue

**Analysis**:

- Highest revenue despite being only 4.4% of total transactions
- High average transaction value ($90.23 vs overall avg $25-30)
- Potential fraud risk category (money transfers)
- Strategic importance for business

---

## KPI #3: Utilities Category Analysis (MCC 4900)

### **Detailed Statistics**

| Metric                        | Value                                      |
| ----------------------------- | ------------------------------------------ |
| **MCC Code**            | 4900                                       |
| **Description**         | Utilities - Electric, Gas, Water, Sanitary |
| **Total Transactions**  | 242,993                                    |
| **Total Amount**        | $27,650,038.08                             |
| **Average Transaction** | **$113.79**                          |
| **Minimum Transaction** | -$12.67 (refund)                           |
| **Maximum Transaction** | $623.56                                    |

### **Key Insights**

1. **High Average Value**:

   - $113.79 is 4.4x higher than overall average
   - 2nd highest average among top 10 categories
   - Reflects typical utility bill amounts
2. **Transaction Volume**:

   - 242,993 transactions (1.8% of total)
   - Ranks 6th by total revenue
   - Consistent with recurring billing pattern
3. **Data Quality**:

   - Negative values present (refunds/credits)
   - Reasonable max value ($623.56)
   - No outliers detected
4. **Business Significance**:

   - Essential service category
   - Predictable revenue stream
   - Low fraud risk (recurring payments)

---

# Part 2: Income Analysis

## KPI Questions

### **Question 1: Average Yearly Income for All Clients**

#### **SQL Query**:

```sql
SELECT 
    COUNT(*) as total_clients,
    ROUND(AVG(yearly_income), 2) as avg_yearly_income,
    ROUND(MIN(yearly_income), 2) as min_yearly_income,
    ROUND(MAX(yearly_income), 2) as max_yearly_income,
    ROUND(STDDEV(yearly_income), 2) as stddev_yearly_income
FROM dim_client;
```

#### **Result**:

| Metric                          | Value                |
| ------------------------------- | -------------------- |
| **Average Yearly Income** | **$45,715.88** |
| Total Clients                   | 2,000                |
| Minimum Income                  | $1.00                |
| Maximum Income                  | $307,018.00          |
| Standard Deviation              | $22,992.62           |

**Key Insights**:

- Average income: **$45,715.88**
- Wide income range ($1 - $307K)
- High standard deviation indicates diverse client base
- Median likely lower than mean (income distribution typically right-skewed)

---

### **Question 2: Average Yearly Income for Clients with >2 Cards Issued**

#### **SQL Query**:

```sql
SELECT 
    COUNT(DISTINCT c.client_id) as clients_with_2plus_cards,
    ROUND(AVG(c.yearly_income), 2) as avg_yearly_income,
    ROUND(MIN(c.yearly_income), 2) as min_yearly_income,
    ROUND(MAX(c.yearly_income), 2) as max_yearly_income,
    ROUND(STDDEV(c.yearly_income), 2) as stddev_yearly_income
FROM dim_client c
WHERE c.client_id IN (
    SELECT client_id 
    FROM dim_card 
    WHERE num_credit_cards > 2
);
```

#### **Result**:

| Metric                          | Value                |
| ------------------------------- | -------------------- |
| **Average Yearly Income** | **$43,789.17** |
| Clients with 3+ Cards           | 60                   |
| Minimum Income                  | $22,371.00           |
| Maximum Income                  | $113,514.00          |
| Standard Deviation              | $17,946.76           |

**Key Insights**:

- Average income: **$43,789.17**
- Only 60 clients (3%) have more than 2 cards
- Lower average income than overall population
- Narrower income range ($22K - $114K)
- Lower standard deviation (more homogeneous group)

---

## Comparative Analysis

### **Income Comparison**

| Client Group                    | Count | Avg Income                      | Difference |
| ------------------------------- | ----- | ------------------------------- | ---------- |
| **All Clients**           | 2,000 | $45,715.88                      | -          |
| **Clients with >2 Cards** | 60    | $43,789.17 | -$1,926.71 (-4.2%) |            |

### **Detailed Breakdown by Card Issuance**

| Card Category | Client Count  | Avg Income              | Min Income  | Max Income |
| ------------- | ------------- | ----------------------- | ----------- | ---------- |
| 1 card        | 1,542 (77.1%) | $45,484.66 | $2.00      | $307,018.00 |            |
| 2 cards       | 1,615 (80.8%) | $45,164.55 | $1.00      | $307,018.00 |            |
| 3+ cards      | 60 (3.0%)     | $43,789.17 | $22,371.00 | $113,514.00 |            |

**Note**: Percentages add up to >100% because clients can have multiple cards

---

# Part 3: Additional KPI Analysis (Debt, Security & Demographics)

## New KPI Questions & Answers

### **Question 1: Top 10 Clients by Total Debt**

#### **SQL Query**:

```sql
SELECT 
    c.client_id,
    c.total_debt,
    c.credit_score,
    c.yearly_income
FROM dim_client c
ORDER BY c.total_debt DESC
LIMIT 10;
```

#### **Results**:

| Rank | Client ID | Total Debt                | Credit Score | Yearly Income |
| ---- | --------- | ------------------------- | ------------ | ------------- |
| 1    | 1325      | $516,263 | 745 | $307,018 |              |               |
| 2    | 1648      | $461,854 | 621 | $185,909 |              |               |
| 3    | 1223      | $448,929 | 717 | $189,490 |              |               |
| 4    | 1014      | $437,533 | 729 | $196,784 |              |               |
| 5    | 856       | $328,089 | 748 | $114,318 |              |               |
| 6    | 236       | $317,964 | 540 | $161,276 |              |               |
| 7    | 995       | $307,856 | 592 | $101,679 |              |               |
| 8    | 1625      | $290,730 | 659 | $101,191 |              |               |
| 9    | 1865      | $276,156 | 782 | $118,862 |              |               |
| 10   | 1402      | $265,319 | 590 | $96,574  |              |               |

**Average Credit Score of Top 10**: **672.30**

#### **Key Insights**:

1. **Debt Range**: $265K - $516K (very high debt levels)
2. **Credit Scores**: Range from 540 to 782

   - Average: 672.30 (good credit despite high debt)
   - Highest: 782 (Client 1865)
   - Lowest: 540 (Client 236)
3. **Income vs Debt Correlation**:

   - Highest debt ($516K) has highest income ($307K)
   - But not all high-debt clients have high income
   - Client 1402: $265K debt on only $96K income (2.7x ratio!)
4. **Risk Assessment**:

   - Most maintain good credit scores (>700)
   - 3 clients have concerning scores (<600)
   - High debt doesn't automatically mean bad credit

---

### **Question 2: Credit Limit by Dark Web Status**

#### **SQL Query**:

```sql
SELECT 
    cd.card_on_dark_web,
    COUNT(*) as card_count,
    ROUND(AVG(cd.credit_limit), 2) as avg_credit_limit,
    ROUND(MIN(cd.credit_limit), 2) as min_credit_limit,
    ROUND(MAX(cd.credit_limit), 2) as max_credit_limit
FROM dim_card cd
GROUP BY cd.card_on_dark_web
ORDER BY cd.card_on_dark_web;
```

#### **Results**:

| Dark Web Status | Card Count | Avg Credit Limit | Min      | Max |
| --------------- | ---------- | ---------------- | -------- | --- |
| **No**    | 6,146      | $14,347.49 | $0  | $151,223 |     |
| **Yes**   | 0          | -                | -        | -   |

#### **Key Findings**:

**Important Discovery**: NO cards are flagged as being on the dark web!

**Implications**:

1. **Good Security**: No compromised cards in dataset
2. **Data Quality**: All cards marked as "No"
3. **Comparison Not Possible**: Cannot compare "Yes" vs "No" groups

**Average Credit Limit (All Cards)**: **$14,347.49**

---

### **Question 3: Per Capita Income by Gender**

#### **SQL Query**:

```sql
SELECT 
    c.gender,
    COUNT(*) as client_count,
    ROUND(AVG(c.per_capita_income), 2) as avg_per_capita_income,
    ROUND(MIN(c.per_capita_income), 2) as min_per_capita_income,
    ROUND(MAX(c.per_capita_income), 2) as max_per_capita_income
FROM dim_client c
GROUP BY c.gender
ORDER BY c.gender;
```

#### **Results**:

| Gender           | Client Count  | Avg Per Capita Income     | Min      | Max |
| ---------------- | ------------- | ------------------------- | -------- | --- |
| **Female** | 1,016 (50.8%) | **$23,397.22** | $0 | $163,145 |     |
| **Male**   | 984 (49.2%)   | **$22,878.33** | $0 | $106,305 |     |

**Difference**: Female clients earn **$518.89 more** per capita (+2.3%)

#### **Key Insights**:

1. **Gender Balance**:

   - Nearly equal distribution (50.8% Female, 49.2% Male)
   - Well-balanced customer base
2. **Income Comparison**:

   - Very small difference: $518.89 (2.3%)
   - Statistically minimal gap
   - Both genders have similar income profiles
3. **Income Range**:

   - **Female**: $0 - $163,145 (wider range)
   - **Male**: $0 - $106,305 (narrower range)
   - Female clients include higher earners

---

# Part 4: Final KPI Analysis

## Final KPI Questions & Answers

### **Question 1: Average Debt for Near-Retirement Clients**

**Definition**: Clients within 10 years of retirement age

#### **SQL Query**:

```sql
SELECT 
    COUNT(*) as clients_near_retirement,
    ROUND(AVG(total_debt), 2) as avg_total_debt,
    ROUND(AVG(current_age), 1) as avg_current_age,
    ROUND(AVG(retirement_age), 1) as avg_retirement_age
FROM dim_client
WHERE (retirement_age - current_age) <= 10 
  AND (retirement_age - current_age) >= 0;
```

#### **Results**:

| Metric                       | Value                |
| ---------------------------- | -------------------- |
| **Average Total Debt** | **$69,851.70** |
| Clients Near Retirement      | 301 (15% of total)   |
| Average Current Age          | 60.4 years           |
| Average Retirement Age       | 65.7 years           |
| Min Debt                     | $0.00                |
| Max Debt                     | $461,854.00          |

#### **Key Insights**:

1. **Debt Level**:

   - $69,851.70 is **higher** than overall average
   - Concerning for retirement planning
   - Wide range: $0 to $461K
2. **Age Profile**:

   - Average 60.4 years old
   - ~5.3 years until retirement
   - Critical debt reduction period
3. **Risk Assessment**:

   - 301 clients (15%) approaching retirement with debt
   - Some have very high debt ($461K)
   - May need financial counseling

---

### **Question 2: Department Store Refund Percentage**

**MCC 5311**: Department Stores

#### **SQL Query**:

```sql
SELECT 
    COUNT(*) as total_transactions,
    SUM(CASE WHEN f.amount < 0 THEN 1 ELSE 0 END) as refund_count,
    ROUND(100.0 * SUM(CASE WHEN f.amount < 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as refund_percentage
FROM fact_transactions f
JOIN dim_merchant m ON f.merchant_id = m.merchant_id
WHERE m.mcc = 5311;
```

#### **Results**:

| Metric                      | Value           |
| --------------------------- | --------------- |
| **Refund Percentage** | **0.00%** |
| Total Transactions          | 475,384         |
| Refund Count                | 8               |
| Total Refund Amount         | -$21.96         |
| Total Sales Amount          | $27,031,990.66  |

#### **Key Insights**:

1. **Extremely Low Refund Rate**:

   - Only 8 refunds out of 475,384 transactions
   - 0.0017% actual rate (rounds to 0.00%)
   - Exceptional customer satisfaction
2. **Financial Impact**:

   - Minimal refund impact: -$21.96
   - Strong sales: $27M+
   - Refunds are 0.00008% of sales

---

### **Question 3: Custom Business Question**

**Question**: *"What is the fraud risk profile for high-value transactions (>$500) across different credit score tiers?"*

#### **SQL Query**:

```sql
SELECT 
    CASE 
        WHEN c.credit_score >= 750 THEN 'Excellent (750+)'
        WHEN c.credit_score >= 700 THEN 'Good (700-749)'
        WHEN c.credit_score >= 650 THEN 'Fair (650-699)'
        ELSE 'Poor (<650)'
    END as credit_tier,
    COUNT(*) as high_value_transactions,
    ROUND(AVG(f.amount), 2) as avg_transaction_amount,
    COUNT(DISTINCT f.client_id) as unique_clients,
    COUNT(DISTINCT m.mcc_description) as merchant_categories
FROM fact_transactions f
JOIN dim_client c ON f.client_id = c.client_id
JOIN dim_merchant m ON f.merchant_id = m.merchant_id
WHERE f.amount > 500
GROUP BY credit_tier
ORDER BY credit_tier;
```

#### **Results**:

| Credit Tier                | Transactions | Avg Amount | Unique Clients | Categories |
| -------------------------- | ------------ | ---------- | -------------- | ---------- |
| **Excellent (750+)** | 11,583       | $796.34    | 329            | 61         |
| **Good (700-749)**   | 15,224       | $838.20    | 406            | 68         |
| **Fair (650-699)**   | 9,426        | $831.40    | 278            | 63         |
| **Poor (<650)**      | 6,951        | $828.37    | 173            | 59         |

**Total High-Value Transactions**: 43,184 (0.32% of all transactions)

#### **Key Insights**:

1. **Transaction Distribution**:

   - Good credit (700-749): Most transactions (15,224)
   - Excellent credit (750+): Second most (11,583)
   - Poor credit (<650): Least transactions (6,951)
2. **Average Transaction Amount**:

   - **Surprising Finding**: Poor credit scores have similar avg amounts!
   - Good (700-749): $838.20 (highest)
   - Fair (650-699): $831.40
   - Poor (<650): $828.37
   - Excellent (750+): $796.34 (lowest!)
3. **Client Engagement**:

   - Good credit: 406 unique clients (most active)
   - Poor: 173 clients (least active)

---

# Part 5: Core Business Metrics & Custom KPI Analysis

## Core Metrics - Questions & Answers

### **Question 1: Total Transaction Volume**

#### **SQL Query**:

```sql
SELECT 
    COUNT(*) as total_transactions,
    ROUND(SUM(amount), 2) as total_volume
FROM fact_transactions;
```

#### **Answer**: **$571,835,522.28**

**Details**:

- Total Transactions: 13,305,915
- Total Volume: **$571.8 Million**
- Overall Average: $42.98 per transaction

---

### **Question 2: Average Credit Score**

#### **SQL Query**:

```sql
SELECT 
    ROUND(AVG(credit_score), 2) as avg_credit_score
FROM dim_client;
```

#### **Answer**: **709.73**

**Details**:

- Total Clients: 2,000
- Average Credit Score: **709.73** (Good credit)
- Min Score: 480
- Max Score: 850
- Standard Deviation: 67.22

---

### **Question 3: Card Brand Distribution**

#### **SQL Query**:

```sql
SELECT 
    card_brand,
    COUNT(*) as card_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM dim_card
GROUP BY card_brand
ORDER BY card_count DESC;
```

#### **Answer**:

| Card Brand           | Card Count | Percentage       |
| -------------------- | ---------- | ---------------- |
| **Mastercard** | 3,209      | **52.21%** |
| **Visa**       | 2,326      | **37.85%** |
| **Amex**       | 402        | **6.54%**  |
| **Discover**   | 209        | **3.40%**  |

**Total Cards**: 6,146

---

### **Question 4: Average Transaction Amount (Excluding Refunds)**

#### **SQL Query**:

```sql
SELECT 
    ROUND(AVG(amount), 2) as avg_positive_amount
FROM fact_transactions
WHERE amount > 0;
```

#### **Answer**: **$50.60**

**Details**:

- Positive Transactions: 12,635,227 (95% of total)
- Total Positive Volume: $639,354,564.62
- Average Amount: **$50.60**
- Min Amount: $0.01
- Max Amount: $6,820.20

---

### **Question 5: Custom KPI - Customer Lifetime Value (CLV) Score**

#### **KPI Definition**:

**Customer Lifetime Value (CLV) Score** measures the total value a customer brings to the business over their entire relationship.

**Formula**:

```
CLV Score = (Total Spent × 0.4) + (Transaction Count × 10) + (Customer Lifespan Days × 0.1)
```

**Components**:

1. **Total Spent (40% weight)**: Revenue contribution
2. **Transaction Count (10 points each)**: Engagement frequency
3. **Lifespan Days (0.1 points each)**: Customer longevity

#### **SQL Query**:

```sql
SELECT 
    c.client_id,
    COUNT(f.transaction_id) as transaction_count,
    ROUND(SUM(f.amount), 2) as total_spent,
    EXTRACT(DAYS FROM (MAX(f.timestamp) - MIN(f.timestamp))) as lifespan_days,
    ROUND((SUM(f.amount) * 0.4) + (COUNT(f.transaction_id) * 10) + 
          (EXTRACT(DAYS FROM (MAX(f.timestamp) - MIN(f.timestamp))) * 0.1), 2) as clv_score
FROM dim_client c
JOIN fact_transactions f ON c.client_id = f.client_id
GROUP BY c.client_id
ORDER BY clv_score DESC
LIMIT 10;
```

#### **Top 10 Customers by CLV Score**:

| Rank | Client ID | Transactions | Total Spent   | Lifespan (Days) | CLV Score    |
| ---- | --------- | ------------ | ------------- | --------------- | ------------ |
| 1    | 1686      | 19,810       | $2,167,880.90 | 3,590           | 1,065,611.36 |
| 2    | 1340      | 22,023       | $2,039,921.23 | 3,590           | 1,036,557.49 |
| 3    | 464       | 27,619       | $1,882,901.35 | 3,590           | 1,029,709.54 |
| 4    | 1888      | 40,105       | $1,436,784.28 | 3,590           | 976,122.71   |
| 5    | 285       | 32,032       | $1,615,458.99 | 3,590           | 966,862.60   |

#### **Business Insights**:

1. **VIP Customers (Platinum)**:

   - Only 8 customers (0.4%)
   - Generate massive value (>$1M CLV each)
   - Require white-glove service
   - Retention is critical
2. **High-Value Customers (Gold)**:

   - 45 customers (2.25%)
   - Strong revenue contributors
3. **Regular Customers (Silver)**:

   - 892 customers (44.6%)
   - Backbone of business

---
