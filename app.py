from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import os
from enhanced_ml_model import SentimentAnalyzer
from database import PredictionDatabase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the sentiment analyzer and database
analyzer = SentimentAnalyzer()
db = PredictionDatabase()

# Global variable to track model status
model_loaded = False

def initialize_model():
    """Initialize or load the ML model and database"""
    global model_loaded, analyzer, db
    try:
        # Initialize database
        logger.info("Initializing database...")
        db = PredictionDatabase()
        
        # Try to load existing model
        if analyzer.load_model():
            logger.info("Existing model loaded successfully!")
            model_loaded = True
        else:
            logger.info("No existing model found. Training new model...")
            accuracy = analyzer.train_model()
            analyzer.save_model()
            logger.info(f"New model trained with accuracy: {accuracy:.3f}")
            model_loaded = True
        return True
    except Exception as e:
        logger.error(f"Error initializing model or database: {str(e)}")
        return False

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory('.', filename)

@app.route('/api/predict', methods=['POST'])
def predict_sentiment():
    """Predict sentiment for a given review text."""
    global analyzer, db
    
    if not model_loaded:
        return jsonify({
            'error': 'Model not loaded',
            'message': 'The ML model is not available. Please try again later.'
        }), 503
    
    try:
        # Get review text from request
        data = request.get_json()
        if not data or 'review' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Please provide review text in the request body.'
            }), 400
        
        review_text = data['review'].strip()
        if not review_text:
            return jsonify({
                'error': 'Empty review',
                'message': 'Review text cannot be empty.'
            }), 400
        
        if len(review_text) < 5:
            return jsonify({
                'error': 'Review too short',
                'message': 'Please provide a longer review (at least 5 characters).'
            }), 400
        
        # Predict sentiment using ML model
        result = analyzer.predict_sentiment(review_text)
        sentiment = result['sentiment']
        confidence = result['confidence']
        
        # Save prediction to database
        db_success = db.save_prediction(review_text, sentiment, confidence)
        if not db_success:
            logger.warning("Failed to save prediction to database")
        
        logger.info(f"Prediction: {sentiment} ({confidence:.3f}) for review: {review_text[:50]}...")
        
        return jsonify({
            'sentiment': sentiment,
            'confidence': confidence,
            'review': review_text,
            'timestamp': result.get('timestamp', None)
        })
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        return jsonify({
            'error': 'Prediction failed',
            'message': 'An error occurred while analyzing the sentiment. Please try again.'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_prediction_history():
    """Get the last 10 predictions from the database."""
    global db
    
    try:
        # Get limit from query parameter (default: 10)
        limit = request.args.get('limit', 10, type=int)
        if limit > 50:  # Prevent excessive data retrieval
            limit = 50
        
        # Retrieve predictions from database
        predictions = db.get_recent_predictions(limit)
        
        # Format predictions for frontend
        formatted_predictions = []
        for pred in predictions:
            formatted_predictions.append({
                'id': pred['id'],
                'review': pred['review_text'],
                'sentiment': pred['predicted_sentiment'],
                'confidence': round(pred['confidence_score'], 3),
                'timestamp': pred['timestamp']
            })
        
        logger.info(f"Retrieved {len(formatted_predictions)} predictions from history")
        
        return jsonify({
            'predictions': formatted_predictions,
            'count': len(formatted_predictions),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error retrieving prediction history: {str(e)}")
        return jsonify({
            'error': 'History retrieval failed',
            'message': 'Unable to retrieve prediction history. Please try again.'
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_prediction_stats():
    """Get statistics about predictions in the database."""
    global db
    
    try:
        total_count = db.get_prediction_count()
        sentiment_stats = db.get_sentiment_stats()
        
        return jsonify({
            'total_predictions': total_count,
            'sentiment_distribution': sentiment_stats,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error retrieving prediction stats: {str(e)}")
        return jsonify({
            'error': 'Stats retrieval failed',
            'message': 'Unable to retrieve prediction statistics.'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'message': 'Sentiment Analysis API is running'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Amazon Review Sentiment Analyzer API...")
    
    # Initialize the model on startup
    logger.info("Initializing ML model...")
    if initialize_model():
        logger.info("Model initialization successful!")
    else:
        logger.warning("Model initialization failed. Will retry on first request.")
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting server on port {port}")
    logger.info("API Endpoints:")
    logger.info("  GET  /                 - Serve web interface")
    logger.info("  POST /api/predict      - Predict sentiment")
    logger.info("  GET  /api/history      - Get prediction history")
    logger.info("  GET  /api/stats        - Get prediction statistics")
    logger.info("  GET  /api/model-info   - Get model information")
    logger.info("  GET  /api/health       - Health check")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )