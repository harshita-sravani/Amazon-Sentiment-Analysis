import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional

class PredictionDatabase:
    """Database handler for storing and retrieving sentiment predictions."""
    
    def __init__(self, db_path: str = 'predictions.db'):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Create the predictions table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        review_text TEXT NOT NULL,
                        predicted_sentiment TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise
    
    def save_prediction(self, review_text: str, sentiment: str, confidence: float) -> bool:
        """
        Save a prediction to the database.
        
        Args:
            review_text: The original review text
            sentiment: Predicted sentiment (Positive, Negative, Neutral)
            confidence: Confidence score (0-1)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO predictions (review_text, predicted_sentiment, confidence_score)
                    VALUES (?, ?, ?)
                ''', (review_text, sentiment, confidence))
                conn.commit()
                logging.info(f"Prediction saved: {sentiment} ({confidence:.3f})")
                return True
        except Exception as e:
            logging.error(f"Error saving prediction: {e}")
            return False
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve the most recent predictions from the database.
        
        Args:
            limit: Number of predictions to retrieve (default: 10)
            
        Returns:
            List of dictionaries containing prediction data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, review_text, predicted_sentiment, confidence_score, timestamp
                    FROM predictions
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                predictions = []
                
                for row in rows:
                    predictions.append({
                        'id': row[0],
                        'review_text': row[1],
                        'predicted_sentiment': row[2],
                        'confidence_score': row[3],
                        'timestamp': row[4]
                    })
                
                logging.info(f"Retrieved {len(predictions)} recent predictions")
                return predictions
                
        except Exception as e:
            logging.error(f"Error retrieving predictions: {e}")
            return []
    
    def get_prediction_count(self) -> int:
        """Get the total number of predictions in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM predictions')
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            logging.error(f"Error getting prediction count: {e}")
            return 0
    
    def get_sentiment_stats(self) -> Dict[str, int]:
        """Get statistics about sentiment distribution."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT predicted_sentiment, COUNT(*) as count
                    FROM predictions
                    GROUP BY predicted_sentiment
                ''')
                
                stats = {}
                for row in cursor.fetchall():
                    stats[row[0]] = row[1]
                
                return stats
        except Exception as e:
            logging.error(f"Error getting sentiment stats: {e}")
            return {}
    
    def clear_all_predictions(self) -> bool:
        """Clear all predictions from the database (for testing purposes)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM predictions')
                conn.commit()
                logging.info("All predictions cleared from database")
                return True
        except Exception as e:
            logging.error(f"Error clearing predictions: {e}")
            return False

# Test the database functionality
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Test database operations
    db = PredictionDatabase('test_predictions.db')
    
    # Test saving predictions
    test_reviews = [
        ("This product is amazing! I love it.", "Positive", 0.95),
        ("Terrible quality, waste of money.", "Negative", 0.88),
        ("It's okay, nothing special.", "Neutral", 0.72),
        ("Best purchase ever! Highly recommend.", "Positive", 0.92),
        ("Poor customer service experience.", "Negative", 0.85)
    ]
    
    print("Testing database operations...")
    
    for review, sentiment, confidence in test_reviews:
        success = db.save_prediction(review, sentiment, confidence)
        print(f"Saved: {success}")
    
    # Test retrieving predictions
    recent = db.get_recent_predictions(3)
    print(f"\nRecent predictions (last 3):")
    for pred in recent:
        print(f"- {pred['predicted_sentiment']} ({pred['confidence_score']:.3f}): {pred['review_text'][:50]}...")
    
    # Test statistics
    count = db.get_prediction_count()
    stats = db.get_sentiment_stats()
    print(f"\nTotal predictions: {count}")
    print(f"Sentiment distribution: {stats}")