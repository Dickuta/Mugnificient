# External Model Service Integration

## Overview
The Mugnificent platform is designed with extensibility in mind, allowing for integration with external AI/ML model services. This document outlines various external model services that can be integrated and how to implement them.

## Potential External Model Services

### 1. Cloud AI Services

#### Google Cloud AI Platform
- **Service**: Vertex AI for advanced forecasting models
- **Integration**: API-based with Google Cloud SDK
- **Benefits**: 
  - More sophisticated ML models
  - AutoML capabilities
  - Advanced hyperparameter tuning
  - Managed model deployment

#### AWS SageMaker
- **Service**: Amazon SageMaker for managed ML service
- **Integration**: SageMaker Python SDK and boto3
- **Benefits**:
  - Distributed training
  - Built-in algorithms
  - Model versioning
  - A/B testing capabilities

#### Microsoft Azure ML
- **Service**: Azure Machine Learning for cloud-based ML
- **Integration**: Azure ML SDK
- **Benefits**:
  - AutoML features
  - MLOps capabilities
  - Integration with Office 365 (if university uses it)
  - Enterprise security features

### 2. Specialized Forecasting Services

#### Prophet (Facebook) via Cloud
- **Service**: Facebook Prophet models hosted on cloud platforms
- **Integration**: REST API calls to Prophet endpoints
- **Benefits**:
  - Excellent for seasonal data
  - Handles holidays and events well
  - Robust to missing data
  - Uncertainty intervals

#### Azure Cognitive Services - Anomaly Detector
- **Service**: Anomaly detection for unusual demand patterns
- **Integration**: REST API with authentication
- **Benefits**:
  - Detect unusual demand spikes
  - Automatic anomaly detection
  - Built-for-purpose service
  - Easy integration

### 3. Open Source Model APIs

#### Hugging Face Inference API
- **Service**: Various pre-trained models available
- **Integration**: Simple HTTP requests with API key
- **Benefits**:
  - Pre-trained models available
  - Easy to use
  - Good for experimentation
  - Cost-effective for prototyping

#### TensorFlow Serving (Self-hosted)
- **Service**: Self-hosted TensorFlow model serving
- **Integration**: GRPC or REST API calls
- **Benefits**:
  - High performance
  - Model versioning
  - A/B testing
  - Flexible deployment

## Integration Approach

### Architecture for External Model Integration

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Application  │    │  Model Request   │    │ External Model   │    │    Response     │
│    (FastAPI)    │───▶│    Handler      │───▶│   Service        │───▶│    Processor    │
│                 │    │ • Validation    │    │ • Forecasting    │    │ • Validation    │
│ • Business Logic│    │ • Preprocessing │    │ • Seasonal Adj.  │    │ • Post-processing│
│ • Data Layer    │    │ • API Format    │    │ • Trend Analysis │    │ • Result Cache  │
│ • User Interface│    │ • Security      │    │ • ML Processing  │    │ • Dashboard     │
└─────────────────┘    │ • Error Handling│    │ • Model Serving  │    │   Update        │
         │             │ • Retry Logic   │    │ • Monitoring     │    │ • Alert         │
         │             └─────────────────┘    └──────────────────┘    │   Generation    │
         │                       │                        │           └─────────────────┘
         │                       │                        │                   │
         └───────────────────────┼───────────────────────────────────────────────┘
                                 ▼
                        ┌─────────────────┐
                        │  LOCAL ML      │
                        │  FALLBACK      │
                        │  (sklearn)     │
                        │  • Backup      │
                        │  • Fallback    │
                        │  • Consistency │
                        └─────────────────┘
```

## Implementation Examples

### 1. Google Cloud AI Platform Integration

First, create environment variables for Google Cloud:
```
GOOGLE_APPLICATION_CREDENTIALS_PATH=./path/to/service-account.json
GOOGLE_PROJECT_ID=your-university-project-id
GOOGLE_FORECASTING_MODEL_NAME=demand-forecasting-model
```

Create the Google Cloud forecasting integration:

```python
# backend/app/core/ml_external/google_cloud.py
from google.cloud import aiplatform
from google.oauth2 import service_account
import json
import os
from typing import Dict, List, Any
import numpy as np
from datetime import datetime, timedelta

class GCPCloudForecasting:
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        
        # Initialize AI Platform
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_PATH")
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            aiplatform.init(
                project=project_id,
                location=location,
                credentials=credentials
            )
        
    def forecast_demand(
        self, 
        historical_data: List[Dict[str, Any]], 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Use Google Cloud AI Platform to forecast demand
        """
        try:
            # Prepare the input for Google Cloud model
            model_inputs = self._prepare_gcp_inputs(historical_data, days_ahead)
            
            # Use Vertex AI model for prediction
            endpoint = aiplatform.Endpoint(
                f"projects/{self.project_id}/locations/{self.location}/endpoints/{os.getenv('GOOGLE_FORECASTING_MODEL_NAME')}"
            )
            
            predictions = endpoint.predict(instances=model_inputs)
            
            # Process and return results
            return self._process_gcp_results(predictions)
            
        except Exception as e:
            # Fall back to local model if GCP service fails
            from app.core.ml_local.forecasting import LocalForecasting
            local_forecaster = LocalForecasting()
            return local_forecaster.forecast_demand(historical_data, days_ahead)
    
    def _prepare_gcp_inputs(self, historical_data, days_ahead):
        """Prepare input data for GCP model"""
        # Convert to GCP expected format
        return [[item['date'], item['quantity']] for item in historical_data]
    
    def _process_gcp_results(self, predictions):
        """Process GCP model results"""
        results = predictions.predictions[0]
        return {
            'predictions': results,
            'confidence_intervals': predictions.explanation[0] if hasattr(predictions, 'explanation') else None,
            'model_source': 'gcp_vertex_ai',
            'processed_at': datetime.utcnow().isoformat()
        }
```

### 2. AWS SageMaker Integration

Create configuration for AWS SageMaker:
```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=your-region
SAGEMAKER_FORECASTING_ENDPOINT_NAME=forecasting-endpoint
```

AWS SageMaker integration code:

```python
# backend/app/core/ml_external/aws_sagemaker.py
import boto3
import json
from typing import Dict, List, Any
from datetime import datetime
import os

class SageMakerForecasting:
    def __init__(self):
        self.sagemaker_runtime = boto3.client(
            'sagemaker-runtime',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.endpoint_name = os.getenv('SAGEMAKER_FORECASTING_ENDPOINT_NAME')
    
    def forecast_demand(
        self, 
        historical_data: List[Dict[str, Any]], 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Use AWS SageMaker to forecast demand
        """
        try:
            # Prepare input data
            payload = {
                'historical_data': historical_data,
                'days_ahead': days_ahead,
                'academic_calendar': True  # University-specific seasonal adjustment
            }
            
            # Call SageMaker endpoint
            response = self.sagemaker_runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )
            
            result = json.loads(response['Body'].read().decode())
            
            return {
                'predictions': result.get('predictions'),
                'confidence_intervals': result.get('confidence_intervals'),
                'model_source': 'aws_sagemaker',
                'processed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Fall back to local model
            from app.core.ml_local.forecasting import LocalForecasting
            local_forecaster = LocalForecasting()
            return local_forecaster.forecast_demand(historical_data, days_ahead)
```

### 3. Azure ML Integration

Create Azure ML integration:

```python
# backend/app/core/ml_external/azure_ml.py
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import json
from typing import Dict, List, Any
from datetime import datetime
import os

class AzureMLForecasting:
    def __init__(self):
        try:
            # Initialize Azure ML client
            self.ml_client = MLClient(
                credential=DefaultAzureCredential(),
                subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'),
                resource_group_name=os.getenv('AZURE_RESOURCE_GROUP'),
                workspace_name=os.getenv('AZURE_ML_WORKSPACE_NAME')
            )
            self.model_name = os.getenv('AZURE_FORECASTING_MODEL_NAME')
        except Exception:
            self.ml_client = None
    
    def forecast_demand(
        self, 
        historical_data: List[Dict[str, Any]], 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Use Azure ML to forecast demand
        """
        if not self.ml_client:
            # Fall back to local model
            from app.core.ml_local.forecasting import LocalForecasting
            local_forecaster = LocalForecasting()
            return local_forecaster.forecast_demand(historical_data, days_ahead)
        
        try:
            # Call Azure ML model
            result = self.ml_client.online_endpoints.invoke(
                endpoint_name=os.getenv('AZURE_ML_ENDPOINT_NAME'),
                deployment_name=os.getenv('AZURE_ML_DEPLOYMENT_NAME'),
                input_data={
                    'input_data': {
                        'historical_data': historical_data,
                        'days_ahead': days_ahead,
                        'seasonal_adjustments': True
                    }
                }
            )
            
            return {
                'predictions': result['predictions'],
                'confidence_intervals': result['confidence_intervals'],
                'model_source': 'azure_ml',
                'processed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Fall back to local model
            from app.core.ml_local.forecasting import LocalForecasting
            local_forecaster = LocalForecasting()
            return local_forecaster.forecast_demand(historical_data, days_ahead)
```

### 4. Model Selection Strategy

Create a model orchestrator that can select the best model based on:

```python
# backend/app/core/ml_external/orchestrator.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime
import logging

from .google_cloud import GCPCloudForecasting
from .aws_sagemaker import SageMakerForecasting
from .azure_ml import AzureMLForecasting
from app.core.ml_local.forecasting import LocalForecasting

logger = logging.getLogger(__name__)

class ModelProvider(ABC):
    @abstractmethod
    def forecast_demand(self, historical_data: List[Dict], days_ahead: int) -> Dict[str, Any]:
        pass

class ForecastingOrchestrator:
    def __init__(self):
        self.local_model = LocalForecasting()
        
        # Initialize external models if configured
        try:
            self.gcp_model = GCPCloudForecasting(os.getenv('GOOGLE_PROJECT_ID'))
        except:
            self.gcp_model = None
            
        try:
            self.aws_model = SageMakerForecasting()
        except:
            self.aws_model = None
            
        try:
            self.azure_model = AzureMLForecasting()
        except:
            self.azure_model = None
    
    def forecast_demand(
        self, 
        historical_data: List[Dict[str, Any]], 
        days_ahead: int = 30,
        preferred_provider: str = None
    ) -> Dict[str, Any]:
        """
        Get demand forecast using best available model
        """
        # Determine preferred model
        model_map = {
            'local': ('local', self.local_model),
            'gcp': ('gcp', self.gcp_model),
            'aws': ('aws', self.aws_model),
            'azure': ('azure', self.azure_model)
        }
        
        # If specific provider requested
        if preferred_provider and preferred_provider in model_map:
            provider_key, model = model_map[preferred_provider]
            if model:
                try:
                    result = model.forecast_demand(historical_data, days_ahead)
                    logger.info(f"Using {provider_key} model for forecasting")
                    return result
                except Exception as e:
                    logger.warning(f"{provider_key} model failed, falling back to local: {e}")
        
        # Strategy: Try providers in order of preference based on cost/performance
        providers_to_try = [
            # Try external models if configured
            ('gcp', self.gcp_model),
            ('azure', self.azure_model),
            ('aws', self.aws_model),
            # Fall back to local model
            ('local', self.local_model)
        ]
        
        for provider_name, model in providers_to_try:
            if model:
                try:
                    result = model.forecast_demand(historical_data, days_ahead)
                    result['selected_provider'] = provider_name
                    logger.info(f"Successfully used {provider_name} model")
                    return result
                except Exception as e:
                    logger.warning(f"{provider_name} model failed: {e}")
        
        # If all providers fail, raise exception
        raise Exception("All forecasting models failed, no fallback possible")
```

### 5. Update Main Forecasting Service

Update the main forecasting service to use the orchestrator:

```python
# backend/app/core/forecasting.py
from .ml_external.orchestrator import ForecastingOrchestrator
from typing import Dict, List, Any
from datetime import datetime

class ForecastingService:
    def __init__(self):
        self.orchestrator = ForecastingOrchestrator()
    
    def generate_forecast(
        self, 
        product_id: int, 
        days_ahead: int = 30,
        use_external_model: bool = True
    ) -> Dict[str, Any]:
        """
        Generate demand forecast for a product
        """
        # Get historical sales data
        historical_data = self._get_historical_data(product_id)
        
        # Apply seasonal adjustments based on academic calendar
        seasonal_adjusted_data = self._apply_seasonal_adjustments(
            historical_data, product_id
        )
        
        # Use orchestrator to get forecast
        forecast_result = self.orchestrator.forecast_demand(
            seasonal_adjusted_data, 
            days_ahead,
            preferred_provider=os.getenv('PREFERRED_FORECASTING_PROVIDER', 'local')
        )
        
        # Calculate additional metrics
        metrics = self._calculate_forecasting_metrics(forecast_result['predictions'])
        
        return {
            'product_id': product_id,
            'historical_data': historical_data,
            'predictions': forecast_result['predictions'],
            'confidence_intervals': forecast_result['confidence_intervals'],
            'seasonal_patterns': self._get_seasonal_patterns(product_id),
            'recommended_actions': self._generate_recommended_actions(
                product_id, forecast_result['predictions']
            ),
            'metrics': metrics,
            'model_source': forecast_result['selected_provider'],
            'generated_at': forecast_result.get('processed_at', datetime.utcnow().isoformat())
        }
```

### 6. Configuration for External Models

Update the configuration to support external model selection:

```python
# backend/app/core/config.py
import os
from typing import Optional

class Settings:
    # ... existing settings ...
    
    # External Model Settings
    USE_EXTERNAL_MODELS: bool = os.getenv('USE_EXTERNAL_MODELS', '').lower() == 'true'
    PREFERRED_FORECASTING_PROVIDER: Optional[str] = os.getenv(
        'PREFERRED_FORECASTING_PROVIDER', 'local'
    )
    
    # Google Cloud Settings
    GOOGLE_APPLICATION_CREDENTIALS_PATH: Optional[str] = os.getenv(
        'GOOGLE_APPLICATION_CREDENTIALS_PATH'
    )
    GOOGLE_PROJECT_ID: Optional[str] = os.getenv('GOOGLE_PROJECT_ID')
    GOOGLE_FORECASTING_MODEL_NAME: Optional[str] = os.getenv(
        'GOOGLE_FORECASTING_MODEL_NAME', 'demand-forecasting'
    )
    
    # AWS Settings
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION: Optional[str] = os.getenv('AWS_REGION', 'us-east-1')
    SAGEMAKER_FORECASTING_ENDPOINT_NAME: Optional[str] = os.getenv(
        'SAGEMAKER_FORECASTING_ENDPOINT_NAME'
    )
    
    # Azure Settings
    AZURE_SUBSCRIPTION_ID: Optional[str] = os.getenv('AZURE_SUBSCRIPTION_ID')
    AZURE_RESOURCE_GROUP: Optional[str] = os.getenv('AZURE_RESOURCE_GROUP')
    AZURE_ML_WORKSPACE_NAME: Optional[str] = os.getenv('AZURE_ML_WORKSPACE_NAME')
    AZURE_FORECASTING_MODEL_NAME: Optional[str] = os.getenv(
        'AZURE_FORECASTING_MODEL_NAME'
    )
    AZURE_ML_ENDPOINT_NAME: Optional[str] = os.getenv('AZURE_ML_ENDPOINT_NAME')
    AZURE_ML_DEPLOYMENT_NAME: Optional[str] = os.getenv('AZURE_ML_DEPLOYMENT_NAME')
```

### 7. Update Docker Configuration

Add external model environment variables to Docker configuration:

```yaml
# deployment/docker/.env.example
# ... existing variables ...
# Google Cloud AI Platform (Optional)
GOOGLE_APPLICATION_CREDENTIALS_PATH=
GOOGLE_PROJECT_ID=
GOOGLE_FORECASTING_MODEL_NAME=demand-forecasting-model

# AWS SageMaker (Optional)  
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
SAGEMAKER_FORECASTING_ENDPOINT_NAME=

# Azure ML (Optional)
AZURE_SUBSCRIPTION_ID=
AZURE_RESOURCE_GROUP=
AZURE_ML_WORKSPACE_NAME=
AZURE_FORECASTING_MODEL_NAME=
AZURE_ML_ENDPOINT_NAME=
AZURE_ML_DEPLOYMENT_NAME=

# External Model Preference
USE_EXTERNAL_MODELS=false
PREFERRED_FORECASTING_PROVIDER=local
```

### 8. Frontend Integration

Update the frontend to show which model provider was used:

```javascript
// frontend/src/pages/forecasting/ForecastingPage.vue
// Add to forecast display
computed: {
  forecastInfo() {
    if (!this.currentForecast) return {}
    return {
      ...this.currentForecast,
      providerInfo: `Forecast generated using ${this.currentForecast.model_source} model`,
      confidence: this.calculateConfidence(this.currentForecast.metrics)
    }
  }
}

// Update the display to show provider information
// In template, add:
/*
<div v-if="currentForecast.model_source" class="q-mb-md">
  <q-chip color="info" text-color="white" size="sm">
    Model: {{ currentForecast.model_source.toUpperCase() }}
  </q-chip>
</div>
*/
```

## Benefits of External Model Integration

### 1. Performance Benefits
- **Superior Models**: Cloud providers often have more advanced algorithms
- **Distributed Computing**: Better processing power for complex models
- **Auto-scaling**: Handle demand spikes automatically
- **Managed Infrastructure**: No need to maintain GPU clusters

### 2. University Benefits
- **Cost Optimization**: Pay only for what you use
- **Advanced Features**: AutoML, hyperparameter optimization, A/B testing
- **Reliability**: SLA-backed services with high availability
- **Expert Maintenance**: Cloud provider handles model maintenance

### 3. Operational Benefits
- **Reduced Hardware**: Offload computation to cloud
- **Security**: Isolated model environment
- **Monitoring**: Built-in metrics from cloud providers
- **Flexibility**: Easy to switch between providers

## Implementation Considerations

### 1. Data Privacy
- Ensure data anonymization before sending to external services
- Verify compliance with GDPR/student data regulations
- Use encryption for data in transit to external providers
- Implement data retention policies for external services

### 2. Cost Management
- Monitor usage to avoid unexpected charges
- Implement cost controls and budget alerts
- Compare costs between providers regularly
- Consider hybrid approach (local for routine, external for complex)

### 3. Reliability
- Always have local model as fallback
- Implement retry logic with exponential backoff
- Monitor external service health
- Handle degraded performance gracefully

### 4. Performance
- Consider network latency when calling external APIs
- Cache results where appropriate
- Batch requests when possible
- Implement async processing for long-running model calls

This external model integration architecture allows the Mugnificent platform to leverage advanced cloud AI/ML services while maintaining reliability through local fallbacks. The system can start with local models and progressively integrate external services based on university needs, budget constraints, and performance requirements.