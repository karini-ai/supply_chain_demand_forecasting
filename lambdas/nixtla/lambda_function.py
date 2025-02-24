import json
import os
import pandas as pd
from nixtla import NixtlaClient
import boto3
from io import StringIO

def get_nixtla_client():
    """Initialize Nixtla client"""
    api_key = os.environ.get('NIXTLA_API_KEY')
    if not api_key:
        raise ValueError("NIXTLA_API_KEY is not set in environment variables.")
    print("Nixtla API Key loaded successfully.")
    return NixtlaClient(api_key=api_key)

def validate_timestamps(df):
    """Ensure timestamps are unique, properly formatted, and match expected frequency"""
    print("Validating timestamps...")

    df['ds'] = pd.to_datetime(df['ds'], errors='coerce')  # Convert to datetime
    df = df.dropna(subset=['ds'])  # Drop rows where conversion failed

    duplicate_count = df.duplicated(subset=['ds']).sum()
    if duplicate_count > 0:
        print(f"Found {duplicate_count} duplicate timestamps. Dropping duplicates...")
        df = df.drop_duplicates(subset=['ds'])

    df = df.set_index('ds').asfreq('MS')  # Force monthly frequency
    missing_count = df.isnull().sum().sum()
    if missing_count > 0:
        print(f"Found {missing_count} missing values. Filling missing timestamps...")
        df = df.fillna(method='ffill')  # Forward fill missing values

    df = df.reset_index()  # Reset index after fixing timestamps
    print(f"Timestamps validated successfully! Final shape: {df.shape}")
    return df

def generate_forecast(df_train, forecast_horizon=3, model_type='default'):
    """Generate forecast using Nixtla"""
    print(f"Generating forecast with horizon: {forecast_horizon}, model: {model_type}")
    
    nixtla_client = get_nixtla_client()

    model = 'timegpt-1-long-horizon' if model_type == 'long_horizon' else 'timegpt-1'

    forecast = nixtla_client.forecast(
        df=df_train,
        h=forecast_horizon,
        freq='MS',
        time_col='ds',
        target_col='y',
        model=model
    )

    print("Forecast generated successfully!")
    return forecast

def lambda_handler(event, context):
    try:
        # Extract event parameters
        bucket_name = event.get('bucket_name')
        file_key = event.get('file_key')
        forecast_horizon = event.get('forecast_horizon', 3)
        model_type = event.get('model_type', 'default')
        product_category = event.get('product_category')  # Accept product category as input
        
        if not bucket_name or not file_key or not product_category:
            raise ValueError("Missing 'bucket_name', 'file_key', or 'product_category' in event payload.")
        
        print(f"Processing file from S3: {bucket_name}/{file_key} for product category: {product_category}")
        
        # Initialize S3 client
        s3 = boto3.client('s3')

        # Read CSV file from S3
        print(f"Reading data from S3...")
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(file_content))

        print(f"Data successfully loaded! Shape: {df.shape}")

        # Filter data for the specified product category
        print(f"Filtering data for product category: {product_category}")
        df_filtered = df[df['product_category'] == product_category]
        print(f"Filtered data shape: {df_filtered.shape}")

        # Validate timestamps for the filtered data
        df_filtered = validate_timestamps(df_filtered)

        # Prepare training data (ensure data is after 2021-01-01)
        df_train = df_filtered.query("ds > '2021-01-01'")
        print(f"Training data prepared. Shape: {df_train.shape}")

        # Generate forecast
        forecast_df = generate_forecast(
            df_train,
            forecast_horizon=forecast_horizon,
            model_type=model_type
        )

        # Convert forecast to JSON
        forecast_json = forecast_df.to_json(
            orient='records',
            date_format='iso',
            double_precision=3  # Limit decimal places for smaller payload
        )

        # Create output file path in S3
        output_key = f"forecasts/{file_key.split('/')[-1].replace('.csv', f'_{product_category}_forecast.json')}"
        print(f"Saving forecast to: s3://{bucket_name}/{output_key}")

        # Upload forecast back to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=output_key,
            Body=forecast_json,
            ContentType='application/json'
        )

        print(f"Forecast successfully saved to S3! Location: s3://{bucket_name}/{output_key}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Forecast generated successfully',
                'forecast_location': f"s3://{bucket_name}/{output_key}",
                'record_count': len(forecast_df),
                'forecast_output' : forecast_json
            })
        }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

