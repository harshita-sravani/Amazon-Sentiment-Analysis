"""
Enhanced ML Model Wrapper
Provides backward compatibility while supporting both traditional and transformer models
"""

import os
import pickle
import logging
from datetime import datetime
import numpy as np

# Try to import lightweight transformer model, fall back to traditional if not available
try:
    from lightweight_transformer import LightweightTransformerSentiment
    TRANSFORMER_AVAILABLE = True
except ImportError:
    TRANSFORMER_AVAILABLE = False
    logging.warning("Lightweight transformer model not available, falling back to traditional model")

# Import traditional model as fallback
from ml_model import SentimentAnalyzer as TraditionalSentimentAnalyzer

logger = logging.getLogger(__name__)

class EnhancedMLModel:
    """
    Enhanced ML Model that can use either transformer or traditional models
    """
    
    def __init__(self, use_transformer=False):
        """
        Initialize the enhanced model
        
        Args:
            use_transformer: Whether to use lightweight transformer model (if available) - Default False for traditional model
        """
        self.use_transformer = use_transformer and TRANSFORMER_AVAILABLE
        self.model = None
        self.model_type = None
        self.model_loaded = False
        
        # Initialize the appropriate model
        if self.use_transformer:
            logger.info("Initializing lightweight transformer-based model...")
            self.model = LightweightTransformerSentiment()
            self.model_type = "transformer"
        else:
            logger.info("Initializing traditional model...")
            self.model = TraditionalSentimentAnalyzer()
            self.model_type = "traditional"
    
    def load_model(self):
        """
        Load the appropriate model (transformer or traditional)
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            if self.model_type == "transformer":
                # Load lightweight transformer model
                logger.info("Loading lightweight transformer model...")
                result = self.model.load_model()
                if result:
                    self.model_loaded = True
                    logger.info("Lightweight transformer model loaded successfully!")
                return result
            else:
                # Load traditional model
                result = self.model.load_model()
                if result:
                    self.model_loaded = True
                return result
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def train_model(self):
        """
        Train the model (only for traditional model in this context)
        
        Returns:
            float: Training accuracy
        """
        if self.model_type == "transformer":
            logger.warning("Transformer model training should be done separately")
            return 0.0
        else:
            return self.model.train_model()
    
    def save_model(self):
        """
        Save the model (only for traditional model in this context)
        
        Returns:
            bool: True if saved successfully
        """
        if self.model_type == "transformer":
            logger.info("Transformer model saving is handled during training")
            return True
        else:
            return self.model.save_model()
    
    def predict_sentiment(self, text):
        """
        Predict sentiment for given text
        
        Args:
            text: Input text string
            
        Returns:
            dict: Prediction result with sentiment, confidence, and timestamp
        """
        if not self.model_loaded:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        try:
            if self.model_type == "transformer":
                # Use lightweight transformer model
                result = self.model.predict_sentiment(text)
                
                # Add model type to result
                result['model_type'] = 'lightweight_transformer'
                return result
            else:
                # Use traditional model
                result = self.model.predict_sentiment(text)
                result['model_type'] = 'traditional'
                return result
                
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            raise
    
    def get_model_info(self):
        """
        Get information about the current model
        
        Returns:
            dict: Model information
        """
        return {
            'model_type': self.model_type,
            'transformer_available': TRANSFORMER_AVAILABLE,
            'model_loaded': self.model_loaded,
            'supports_sarcasm': self.model_type == "transformer"
        }

class SentimentAnalyzer:
    """
    Backward-compatible wrapper for the enhanced model
    Maintains the same interface as the original SentimentAnalyzer
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer with enhanced capabilities"""
        # Use traditional model by default for backward compatibility
        self.enhanced_model = EnhancedMLModel(use_transformer=False)
        
    def enable_transformer_mode(self):
        """Enable transformer mode for better sarcasm detection"""
        if TRANSFORMER_AVAILABLE:
            self.enhanced_model = EnhancedMLModel(use_transformer=True)
            return self.enhanced_model.load_model()
        return False
        
    def load_model(self):
        """Load the model"""
        return self.enhanced_model.load_model()
    
    def train_model(self):
        """Train the model"""
        return self.enhanced_model.train_model()
    
    def save_model(self):
        """Save the model"""
        return self.enhanced_model.save_model()
    
    def predict_sentiment(self, text):
        """Predict sentiment for given text"""
        return self.enhanced_model.predict_sentiment(text)
    
    def get_model_info(self):
        """Get model information"""
        return self.enhanced_model.get_model_info()

# For backward compatibility, export the main class
__all__ = ['SentimentAnalyzer', 'EnhancedMLModel']