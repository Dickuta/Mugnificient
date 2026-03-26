# Free & Easy AI Model Integration

## Overview
This document outlines FREE external AI/ML model services that can be easily integrated with the Mugnificent platform. These free alternatives help universities leverage advanced AI capabilities without budget constraints while maintaining high functionality.

## Free AI Model Services Integration

### 1. Hugging Face Inference API

**Cost**: Free tier available with generous limits
**Ease of Integration**: Very easy - simple REST API
**Use Case**: Demand forecasting and seasonal pattern recognition

#### Setup
1. Create free Hugging Face account at [huggingface.co](https://huggingface.co)
2. Get API token from Settings → Access Tokens
3. Create a forecasting model or use existing time-series models

#### Environment Configuration
```
# Add to your .env file  
HF_API_TOKEN=your_hugging_face_api_token
HF_FORECASTING_MODEL_ID=your-org/forecasting-model
```

#### Integration Code
```python
# backend/app/core/ml_free/huggingface_integration.py
import requests
import json
from typing import Dict, List, Any
from datetime import datetime

class HuggingFaceForecasting:
    def __init__(self):
        self.api_token = os.getenv('HF_API_TOKEN')
        self.model_id = os.getenv('HF_FORECASTING_MODEL_ID', 'huggingface-projects/demand-forecasting')
        self.url = f"https://api-inference.huggingface.co/models/{self.model_id}"
    
    def forecast_demand(
        self, 
        historical_data: List[Dict[str, Any]], 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Use Hugging Face inference API for demand forecasting
        """
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        payload = {
            "inputs": {
                "historical_data": historical_data,
                "days_ahead": days_ahead,
                "academic_calendar_integration": True
            }
        }
        
        try:
            response = requests.post(
                self.url, 
                headers=headers, 
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'predictions': result.get('predictions', []),
                    'confidence_intervals': result.get('confidence_intervals', {}),
                    'model_source': 'huggingface',
                    'processed_at': datetime.utcnow().isoformat()
                }
            else:
                # Fall back to local model
                from app.core.ml_local.forecasting import LocalForecasting
                local_forecaster = LocalForecasting()
                return local_forecaster.forecast_demand(historical_data, days_ahead)
                
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            # Fall back to local model
            from app.core.ml_local.forecasting import LocalForecasting
            local_forecaster = LocalForecasting()
            return local_forecaster.forecast_demand(historical_data, days_ahead)
```

### 2. Google Colab with Custom Models

**Cost**: Completely free
**Ease of Integration**: Easy - use Google Colab as external model server  
**Use Case**: Advanced ML models for seasonal adjustment and demand prediction

#### Setup Process
1. Create forecasting model in Google Colab notebook
2. Use ngrok to expose the Colab model as HTTP API
3. Integrate with your application via REST API

#### Colab Model Example
```python
# Google Colab notebook code (save as forecasting_model_colab.ipynb)
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    
    # Load model or use pre-trained model
    historical_data = data['historical_data']
    days_ahead = data.get('days_ahead', 30)
    
    # Preprocess data
    df = pd.DataFrame(historical_data)
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    
    # Your forecasting logic here
    # This is where you'd implement your ML model
    
    # Return predictions
    predictions = [{'date': str(date), 'predicted_quantity': qty} 
                  for date, qty in zip(range(days_ahead), [1]*days_ahead)]
    
    return jsonify({
        'predictions': predictions,
        'confidence_intervals': {'low': [0.5]*days_ahead, 'high': [1.5]*days_ahead}
    })

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000)
```

Then expose via ngrok in Colab:
```python
# In Google Colab cell
!pip install flask flask-ngrok
!pip install ngrok

from pyngrok import ngrok
public_url = ngrok.connect(5000)
print(f"Colab model API available at: {public_url}")
```

### 3. OpenAI API (Free Credits Available)

**Cost**: Free credits initially ($18 in free credits for new users)
**Ease of Integration**: Easy with OpenAI Python client
**Use Case**: Natural language processing for seasonal event predictions

#### Setup
1. Create OpenAI account with free trial
2. Get API key from OpenAI dashboard
3. Define custom function for forecasting

#### Environment Configuration
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_FORECASTING_MODEL=gpt-3.5-turbo
```

#### Integration Code
```python
# backend/app/core/ml_free/openai_integration.py
import openai
import os
from typing import Dict, List, Any
from datetime import datetime

class OpenAIForecasting:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_FORECASTING_MODEL', 'gpt-3.5-turbo')
    
    def forecast_demand(
        self, 
        historical_data: List[Dict[str, Any]], 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Use OpenAI for forecasting based on historical data
        """
        try:
            # Prepare prompt for the model
            historical_text = "\n".join([
                f"Date: {item['date']}, Quantity: {item['quantity']}" 
                for item in historical_data[-30:]  # Last 30 days
            ])
            
            prompt = f"""
            You are an inventory management expert at a university. 
            Analyze the following sales data and predict demand for the next {days_ahead} days.
            Consider university seasonal patterns like student intake (September), 
            exam periods (December/January, May/June), and holidays.
            
            Historical data:
            {historical_text}
            
            Provide the following in JSON format:
            {{
                "predictions": [
                    {{"date": "YYYY-MM-DD", "predicted_quantity": number}},
                    ...
                ],
                "confidence_intervals": {{
                    "low": [numbers...],
                    "high": [numbers...]
                }},
                "seasonal_notes": "string"
            }}
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a university inventory and forecasting expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            parsed_result = json.loads(result)
            
            return {
                'predictions': parsed_result.get('predictions', []),
                'confidence_intervals': parsed_result.get('confidence_intervals', {}),
                'seasonal_notes': parsed_result.get('seasonal_notes', ''),
                'model_source': 'openai',
                'processed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fall back to local model
            from app.core.ml_local.forecasting import LocalForecasting
            local_forecaster = LocalForecasting()
            return local_forecaster.forecast_demand(historical_data, days_ahead)
```

### 4. Google Cloud Platform (Free Tier)

**Cost**: $300 free credits + always-free tier
**Ease of Integration**: Moderate - requires GCP account setup
**Use Case**: Advanced forecasting with Google Cloud AI Platform

#### Setup
1. Create Google Cloud account with free tier
2. Enable AI Platform API
3. Deploy your forecasting model
4. Set up authentication

#### Environment Configuration
```
GOOGLE_APPLICATION_CREDENTIALS_PATH=./gcp-service-account.json
GOOGLE_PROJECT_ID=your-gcp-project-id
GCLOUD_FORECASTING_MODEL_NAME=demand-forecasting
```

#### Integration Code
```python
# backend/app/core/ml_free/gcloud_free.py
from google.cloud import aiplatform
import os
from typing import Dict, List, Any

class GoogleCloudFreeForecasting:
    def __init__(self):
        # Initialize with free tier credentials
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_PATH')
        if credentials_path and os.path.exists(credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
        project_id = os.getenv('GOOGLE_PROJECT_ID')
        if project_id:
            aiplatform.init(project=project_id, location='us-central1')
    
    def forecast_demand(
        self, 
        historical_data: List[Dict[str, Any]], 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Use Google Cloud AI Platform (free tier eligible)
        """
        try:
            # Use vertex AI for prediction within free tier limits
            # Implementation would use vertex AI prediction service
            pass
        except Exception:
            # Fall back to local model
            from app.core.ml_local.forecasting import LocalForecasting
            local_forecaster = LocalForecasting()
            return local_forecaster.forecast_demand(historical_data, days_ahead)
```

### 5. Azure Cognitive Services (Free Tier Available)

**Cost**: Limited free tier available
**Ease of Integration**: Easy with Azure SDK
**Use Case**: Anomaly detection and forecasting

#### Setup
1. Create Azure account (free credit available)
2. Create Anomaly Detector resource
3. Get resource key and endpoint

#### Integration Code
```python
# backend/app/core/ml_free/azure_free.py
import requests
import json
import os
from typing import Dict, List, Any

class AzureFreeForecasting:
    def __init__(self):
        self.subscription_key = os.getenv('AZURE_ANOMALY_KEY')
        self.endpoint = os.getenv('AZURE_ANOMALY_ENDPOINT')
    
    def forecast_demand(
        self, 
        historical_data: List[Dict[str, Any]], 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Use Azure Anomaly Detection (free tier eligible)
        """
        if not self.subscription_key:
            # Fall back to local model
            from app.core.ml_local.forecasting import LocalForecasting
            local_forecaster = LocalForecasting()
            return local_forecaster.forecast_demand(historical_data, days_ahead)
        
        try:
            # Use Azure's anomaly detection service
            headers = {
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Content-Type': 'application/json'
            }
            
            # Prepare time series data
            time_series = [
                {"timestamp": item['date'], "value": item['quantity']}
                for item in historical_data
            ]
            
            request_data = {
                "series": time_series,
                "granularity": "daily",
                "fillingMethod": "previous"
            }
            
            response = requests.post(
                f"{self.endpoint}/anomalydetector/v1.0/timeseries/forecast/last",
                headers=headers,
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'predictions': result.get('periods', []),
                    'confidence_intervals': result.get('expectedValues', {}),
                    'model_source': 'azure',
                    'processed_at': datetime.utcnow().isoformat()
                }
            else:
                # Fall back to local model
                from app.core.ml_local.forecasting import LocalForecasting
                local_forecaster = LocalForecasting()
                return local_forecaster.forecast_demand(historical_data, days_ahead)
                
        except Exception as e:
            print(f"Azure API error: {e}")
            # Fall back to local model
            from app.core.ml_local.forecasting import LocalForecasting
            local_forecaster = LocalForecasting()
            return local_forecaster.forecast_demand(historical_data, days_ahead)
```

## Integration Strategy

### Model Orchestrator with Free Providers
Update the model orchestrator to prioritize free services:

```python
# backend/app/core/ml_free/orchestrator.py
from .huggingface_integration import HuggingFaceForecasting
from .openai_integration import OpenAIForecasting
from app.core.ml_local.forecasting import LocalForecasting

class FreeModelOrchestrator:
    def __init__(self):
        self.models = {}
        
        # Initialize free models if configured
        if os.getenv('HF_API_TOKEN'):
            try:
                self.models['huggingface'] = HuggingFaceForecasting()
            except:
                pass
        
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.models['openai'] = OpenAIForecasting()
            except:
                pass
        
        # Always have local model as fallback
        self.models['local'] = LocalForecasting()
    
    def forecast_demand(
        self, 
        historical_data: List[Dict[str, Any]], 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Try free models in order of preference
        """
        preferred_order = ['huggingface', 'openai', 'local']
        
        for provider in preferred_order:
            if provider in self.models:
                try:
                    result = self.models[provider].forecast_demand(
                        historical_data, days_ahead
                    )
                    result['selected_provider'] = provider
                    return result
                except Exception as e:
                    print(f"Failed to use {provider} model: {e}")
                    continue
        
        # If all free models fail, use local model
        result = self.models['local'].forecast_demand(historical_data, days_ahead)
        result['selected_provider'] = 'local'
        return result
```

### Update Main Forecasting Service
```python
# backend/app/core/forecasting.py
from .ml_free.orchestrator import FreeModelOrchestrator

class ForecastingService:
    def __init__(self):
        self.model_orchestrator = FreeModelOrchestrator()
        # ... other initialization
```

## Free Integration Benefits

### Cost Effective
- **Zero Infrastructure Costs**: No need for GPU servers or ML infrastructure
- **Free Tier Utilization**: Leverage generous free quotas
- **Pay-as-you-grow**: Easy to upgrade when budget allows

### University Friendly
- **No Contract Requirements**: Easy trial and implementation
- **Flexible Integration**: Add/remove services as needed
- **Educational Discounts**: Many services offer educational discounts

### Easy Implementation
- **Quick Setup**: Many services have API-first approach
- **Simple Integration**: Usually just REST API calls
- **Fallback Support**: Local models always available as backup

## Configuration Example

### For Free Hugging Face Integration
```yaml
# deployment/docker/docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - HF_API_TOKEN=your_huggingface_token
      - HF_FORECASTING_MODEL_ID=huggingface-projects/university-demand-forecasting
      - PREFERRED_FORECASTING_PROVIDER=huggingface  # Use free service
      # ... other vars
```

### For OpenAI Integration
```env
# .env file
OPENAI_API_KEY=your_openai_key
PREFERRED_FORECASTING_PROVIDER=openai
OPENAI_FORECASTING_MODEL=gpt-3.5-turbo
```

## Migration Strategy

### Phase 1: Add Free Provider
1. Choose a free provider that meets your needs
2. Add API credentials to environment
3. Update orchestrator to try free provider first
4. Test integration thoroughly

### Phase 2: Monitor Usage
1. Track API usage vs. free tier limits
2. Monitor accuracy between free vs. local models
3. Adjust model usage based on performance

### Phase 3: Optimize
1. Implement result caching to reduce API calls
2. Use batch requests where possible  
3. Consider hybrid approach (seasonal patterns local, complex forecasting external)

This approach provides universities with the ability to leverage powerful external AI/ML services at no initial cost while maintaining the reliability of local models as a fallback.