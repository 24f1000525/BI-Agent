"""
Utility script to generate sample CSV files for testing the GenAI application.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def generate_sales_data(num_records=100):
    """Generate sample sales data CSV."""
    np.random.seed(42)
    
    dates = pd.date_range(start='2023-01-01', periods=num_records, freq='D')
    regions = ['North', 'South', 'East', 'West', 'Central']
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    
    data = {
        'Date': dates,
        'Region': np.random.choice(regions, num_records),
        'Product': np.random.choice(products, num_records),
        'Quantity': np.random.randint(1, 100, num_records),
        'Unit_Price': np.random.uniform(10, 500, num_records),
        'Discount_%': np.random.uniform(0, 30, num_records),
        'Sales_Rep': [f'Rep_{i%10}' for i in range(num_records)]
    }
    
    df = pd.DataFrame(data)
    df['Total_Revenue'] = df['Quantity'] * df['Unit_Price'] * (1 - df['Discount_%']/100)
    
    return df


def generate_customer_data(num_records=100):
    """Generate sample customer data CSV."""
    np.random.seed(42)
    
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    
    data = {
        'Customer_ID': [f'CUST_{i:05d}' for i in range(1, num_records + 1)],
        'First_Name': np.random.choice(first_names, num_records),
        'Last_Name': np.random.choice(last_names, num_records),
        'Email': [f'customer{i}@example.com' for i in range(1, num_records + 1)],
        'Phone': [f'555-{np.random.randint(1000, 9999)}' for _ in range(num_records)],
        'City': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], num_records),
        'Age': np.random.randint(18, 80, num_records),
        'Tenure_Years': np.random.randint(0, 20, num_records),
        'Total_Purchases': np.random.randint(1, 50, num_records),
        'Average_Order_Value': np.random.uniform(50, 1000, num_records),
        'Last_Purchase_Days_Ago': np.random.randint(0, 365, num_records),
        'Customer_Segment': np.random.choice(['Premium', 'Standard', 'Basic'], num_records),
        'Churn_Risk': np.random.choice(['Low', 'Medium', 'High'], num_records)
    }
    
    return pd.DataFrame(data)


def generate_product_data(num_records=50):
    """Generate sample product inventory data CSV."""
    np.random.seed(42)
    
    categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Books']
    
    data = {
        'Product_ID': [f'PROD_{i:04d}' for i in range(1, num_records + 1)],
        'Product_Name': [f'Product_{i}' for i in range(1, num_records + 1)],
        'Category': np.random.choice(categories, num_records),
        'Cost_Price': np.random.uniform(10, 500, num_records),
        'Selling_Price': np.random.uniform(20, 1000, num_records),
        'Quantity_In_Stock': np.random.randint(0, 500, num_records),
        'Reorder_Level': np.random.randint(10, 100, num_records),
        'Last_Restocked': pd.date_range(start='2023-01-01', periods=num_records, freq='4D'),
        'Supplier_Name': [f'Supplier_{np.random.randint(1, 6)}' for _ in range(num_records)],
        'Lead_Time_Days': np.random.randint(1, 30, num_records),
        'Average_Monthly_Sales': np.random.randint(5, 200, num_records),
        'Rating': np.random.uniform(1, 5, num_records)
    }
    
    return pd.DataFrame(data)


def generate_student_performance_data(num_records=100):
    """Generate sample student performance data CSV."""
    np.random.seed(42)
    
    data = {
        'Student_ID': [f'STU_{i:05d}' for i in range(1, num_records + 1)],
        'Name': [f'Student_{i}' for i in range(1, num_records + 1)],
        'Grade': np.random.choice(['A', 'B', 'C', 'D', 'F'], num_records),
        'Math_Score': np.random.randint(40, 100, num_records),
        'Science_Score': np.random.randint(40, 100, num_records),
        'English_Score': np.random.randint(40, 100, num_records),
        'History_Score': np.random.randint(40, 100, num_records),
        'Attendance_%': np.random.uniform(50, 100, num_records),
        'Homework_Completed_%': np.random.uniform(0, 100, num_records),
        'Class_Participation_Score': np.random.randint(0, 10, num_records),
        'Exam_Date': pd.date_range(start='2023-01-01', periods=num_records, freq='H').date,
        'Teacher': [f'Teacher_{np.random.randint(1, 5)}' for _ in range(num_records)],
        'Previous_GPA': np.random.uniform(1.0, 4.0, num_records)
    }
    
    return pd.DataFrame(data)


def save_sample_csv(filename, df):
    """Save DataFrame to CSV file."""
    filepath = os.path.join(os.path.dirname(__file__), f'sample_{filename}.csv')
    df.to_csv(filepath, index=False)
    print(f"✅ Created: {filepath}")
    return filepath


def main():
    """Generate all sample CSV files."""
    print("🔄 Generating sample CSV files for testing...\n")
    
    # Generate and save each dataset
    save_sample_csv('sales_data', generate_sales_data(100))
    save_sample_csv('customer_data', generate_customer_data(100))
    save_sample_csv('product_inventory', generate_product_data(50))
    save_sample_csv('student_performance', generate_student_performance_data(100))
    
    print("\n✨ All sample CSV files generated successfully!")
    print("📁 Files created in project root directory")
    print("\n💡 You can now upload these files to test the GenAI application")


if __name__ == '__main__':
    main()
