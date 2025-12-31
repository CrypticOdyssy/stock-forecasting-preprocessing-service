"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PreprocessRequest(BaseModel):
    """Request schema for preprocessing endpoint"""
    series_id: str = Field(..., description="Unique identifier for the time series")
    interpolation_method: str = Field(default="linear", description="Method for handling missing values")
    outlier_method: str = Field(default="zscore", description="Method for detecting outliers")
    outlier_threshold: float = Field(default=3.0, gt=0, description="Threshold for outlier detection")
    resample_frequency: Optional[str] = Field(None, description="Frequency for resampling (e.g., 'D', 'H')")
    aggregation_method: str = Field(default="mean", description="Aggregation method for resampling")
    
    class Config:
        json_schema_extra = {
            "example": {
                "series_id": "sensor_123",
                "interpolation_method": "linear",
                "outlier_method": "zscore",
                "outlier_threshold": 3.0,
                "resample_frequency": "D",
                "aggregation_method": "mean"
            }
        }


class FeatureRequest(BaseModel):
    """Request schema for feature engineering endpoint"""
    series_id: str = Field(..., description="Unique identifier for the time series")
    lag_features: Optional[List[int]] = Field(None, description="List of lag values")
    rolling_window_sizes: Optional[List[int]] = Field(None, description="List of rolling window sizes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "series_id": "sensor_123",
                "lag_features": [1, 7, 30],
                "rolling_window_sizes": [7, 14, 30]
                }
        }
        

class PreprocessResponse(BaseModel):
    """Response schema for preprocessing endpoint"""
    status: str
    series_id: str
    data_points: int
    metadata: Dict[str, Any]


class FeatureResponse(BaseModel):
    """Response schema for feature engineering endpoint"""
    status: str
    series_id: str
    features: List[str]
    rows: int


class OHLCVStats(BaseModel):
    missing_count: int
    missing_percentage: float
    mean: float
    std: float
    min: float
    max: float

class DataQualityChecks(BaseModel):
    high_ge_low: int
    high_ge_open: int
    high_ge_close: int
    low_le_open: int
    low_le_close: int
    volume_positive: int

class ValidationResponse(BaseModel):
    """Response schema for validation endpoint"""
    total_points: int
    date_range: Dict[str, str]
    ohlcv_stats: Dict[str, OHLCVStats]
    data_quality_checks: DataQualityChecks


