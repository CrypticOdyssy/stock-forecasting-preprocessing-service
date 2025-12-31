# /app/src/send_ingestion_event.py
from kafka import KafkaProducer
import json
from sqlalchemy import create_engine, text
import os

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://tsuser:ts_password@localhost:5432/timeseries")
engine = create_engine(DATABASE_URL)

# Kafka producer - connect to localhost:9094 from host machine
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None
)

def send_ingestion_complete(series_id: str, topic: str = 'data.ingestion.completed'):
    """
    Send ingestion completion event to trigger preprocessing.
    
    Args:
        series_id: The series identifier (e.g., 'AAPL', 'GOOGL')
        topic: Kafka topic name for ingestion events
    """
    
    # Query to verify data exists
    query = text("""
        SELECT COUNT(*) as count
        FROM time_series_raw
        WHERE series_id = :sid
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"sid": series_id}).fetchone()
        data_count = result[0] if result else 0
        
        if data_count == 0:
            print(f"⚠ No data found for series {series_id}")
            return
        
        # Build ingestion complete message matching your handler's expectations
        message = {
            "series_id": series_id,
            "job_id": f"ingestion_job_{series_id}_{data_count}",
            "preprocessing_config": {
                "interpolation_method": "linear",
                "outlier_method": "iqr",
                "outlier_threshold": 3.0,
                "resample_frequency": None,  # Optional: "1D", "1H", etc.
                "aggregation_method": "mean",
                "lag_features": [1, 7, 30],
                "rolling_window_sizes": [7, 30]
            },
            "metadata": {
                "data_points": data_count,
                "timestamp": "2025-12-31T21:04:00Z"
            }
        }
        
        # Send to Kafka with series_id as key
        future = producer.send(topic, key=series_id, value=message)
        producer.flush()
        
        # Wait for confirmation
        record_metadata = future.get(timeout=10)
        
        print(f"✓ Sent ingestion event for {series_id}")
        print(f"  Topic: {record_metadata.topic}")
        print(f"  Partition: {record_metadata.partition}")
        print(f"  Offset: {record_metadata.offset}")
        print(f"  Data points: {data_count}")


# Send ingestion events for all series
if __name__ == "__main__":
    series_list = ["AAPL", "GOOGL", "MSFT", "DUMMY"]
    
    print("Sending ingestion completion events...\n")
    
    for series_id in series_list:
        send_ingestion_complete(series_id)
        print()
        break
    
    producer.close()
    print("✓ All ingestion events sent successfully")
