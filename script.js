// DOM Elements
const reviewInput = document.getElementById('reviewText'); // Fixed: HTML uses 'reviewText' not 'reviewInput'
const predictBtn = document.getElementById('predictBtn');
const resultSection = document.getElementById('resultSection');
const sentimentResult = document.getElementById('sentimentResult');
const confidenceResult = document.getElementById('confidenceResult');
const errorMessage = document.getElementById('errorMessage');
const sampleButtons = document.querySelectorAll('.sample-btn');

// Additional DOM elements for displayResults function
const sentimentValue = document.getElementById('sentimentValue');
const confidenceValue = document.getElementById('confidenceValue');
const sentimentIcon = document.getElementById('sentimentIcon');
const confidenceFill = document.getElementById('confidenceFill');
const resultsSection = document.getElementById('resultsSection');

// History elements
const historyTableBody = document.getElementById('historyTableBody');
const refreshHistoryBtn = document.getElementById('refreshHistory');
const totalPredictionsSpan = document.getElementById('totalPredictions');
const historyLoading = document.getElementById('historyLoading');
const historyError = document.getElementById('historyError');

// Sentiment analysis simulation
class SentimentAnalyzer {
    constructor() {
        // Keywords for sentiment analysis
        this.positiveWords = [
            'amazing', 'excellent', 'fantastic', 'great', 'wonderful', 'awesome', 'perfect',
            'outstanding', 'brilliant', 'superb', 'incredible', 'magnificent', 'exceptional',
            'love', 'best', 'recommend', 'satisfied', 'happy', 'pleased', 'impressed',
            'quality', 'fast', 'quick', 'efficient', 'helpful', 'good', 'nice', 'beautiful',
            'comfortable', 'durable', 'reliable', 'worth', 'value', 'bargain'
        ];
        
        this.negativeWords = [
            'terrible', 'awful', 'horrible', 'bad', 'worst', 'hate', 'disappointed',
            'useless', 'broken', 'defective', 'poor', 'cheap', 'waste', 'money',
            'slow', 'delayed', 'damaged', 'wrong', 'missing', 'fake', 'scam',
            'uncomfortable', 'difficult', 'complicated', 'confusing', 'annoying',
            'frustrating', 'regret', 'return', 'refund', 'avoid', 'never', 'don\'t'
        ];
        
        this.neutralWords = [
            'okay', 'average', 'normal', 'standard', 'typical', 'regular', 'fine',
            'acceptable', 'decent', 'moderate', 'fair', 'reasonable', 'adequate'
        ];
    }
    
    analyzeSentiment(text) {
        if (!text || text.trim().length === 0) {
            return { sentiment: 'Neutral', confidence: 0.5 };
        }
        
        const words = text.toLowerCase().split(/\s+/);
        let positiveScore = 0;
        let negativeScore = 0;
        let neutralScore = 0;
        
        // Count sentiment words
        words.forEach(word => {
            // Remove punctuation
            const cleanWord = word.replace(/[^\w]/g, '');
            
            if (this.positiveWords.includes(cleanWord)) {
                positiveScore++;
            } else if (this.negativeWords.includes(cleanWord)) {
                negativeScore++;
            } else if (this.neutralWords.includes(cleanWord)) {
                neutralScore++;
            }
        });
        
        // Calculate sentiment based on scores
        const totalSentimentWords = positiveScore + negativeScore + neutralScore;
        
        if (totalSentimentWords === 0) {
            // No sentiment words found, analyze based on text characteristics
            return this.analyzeByCharacteristics(text);
        }
        
        let sentiment;
        let confidence;
        
        if (positiveScore > negativeScore && positiveScore > neutralScore) {
            sentiment = 'Positive';
            confidence = Math.min(0.95, 0.6 + (positiveScore / words.length) * 2);
        } else if (negativeScore > positiveScore && negativeScore > neutralScore) {
            sentiment = 'Negative';
            confidence = Math.min(0.95, 0.6 + (negativeScore / words.length) * 2);
        } else {
            sentiment = 'Neutral';
            confidence = Math.min(0.85, 0.5 + (neutralScore / words.length) * 1.5);
        }
        
        // Add some randomness to make it more realistic
        confidence += (Math.random() - 0.5) * 0.1;
        confidence = Math.max(0.3, Math.min(0.98, confidence));
        
        return { sentiment, confidence: Math.round(confidence * 100) / 100 };
    }
    
    analyzeByCharacteristics(text) {
        const exclamationCount = (text.match(/!/g) || []).length;
        const questionCount = (text.match(/\?/g) || []).length;
        const capsCount = (text.match(/[A-Z]/g) || []).length;
        const textLength = text.length;
        
        let sentiment = 'Neutral';
        let confidence = 0.5;
        
        // High exclamation marks might indicate strong sentiment
        if (exclamationCount > 2) {
            sentiment = Math.random() > 0.5 ? 'Positive' : 'Negative';
            confidence = 0.6 + Math.random() * 0.2;
        }
        
        // Very short reviews might be negative
        if (textLength < 20) {
            sentiment = 'Negative';
            confidence = 0.4 + Math.random() * 0.2;
        }
        
        // Very long reviews might be more detailed and positive
        if (textLength > 200) {
            sentiment = 'Positive';
            confidence = 0.6 + Math.random() * 0.2;
        }
        
        return { sentiment, confidence: Math.round(confidence * 100) / 100 };
    }
}

// Initialize sentiment analyzer
const analyzer = new SentimentAnalyzer();

// History management functions
async function loadPredictionHistory() {
    try {
        // Check if required elements exist
        if (!historyLoading || !historyError || !historyTableBody || !totalPredictionsSpan) {
            console.error('Required DOM elements not found');
            return;
        }
        
        historyLoading.style.display = 'block';
        historyError.style.display = 'none';
        
        const response = await fetch('/history');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('History data received:', data); // Debug log
        
        // Ensure data is an array
        const predictions = Array.isArray(data) ? data : [];
        
        // Update total predictions count
        totalPredictionsSpan.textContent = `Total: ${predictions.length}`;
        
        // Clear existing table rows
        historyTableBody.innerHTML = '';
        
        // Populate table with predictions
        if (predictions.length > 0) {
            predictions.forEach(prediction => {
                const row = createHistoryRow(prediction);
                historyTableBody.appendChild(row);
            });
        } else {
            // Show empty state
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `
                <td colspan="4" style="text-align: center; color: #666; font-style: italic;">
                    No predictions yet. Submit a review to see history!
                </td>
            `;
            historyTableBody.appendChild(emptyRow);
        }
        
    } catch (error) {
        console.error('Error loading history:', error);
        if (historyError) {
            historyError.style.display = 'block';
            historyError.textContent = 'Failed to load prediction history';
        }
    } finally {
        if (historyLoading) {
            historyLoading.style.display = 'none';
        }
    }
}

function createHistoryRow(prediction) {
    const row = document.createElement('tr');
    
    // Safely access prediction properties with fallbacks
    const reviewText = prediction.review_text || prediction.review || 'No review text';
    const sentiment = prediction.predicted_sentiment || prediction.sentiment || 'unknown';
    const confidence = prediction.confidence_score || prediction.confidence || 0;
    const timestamp = prediction.timestamp || new Date().toISOString();
    
    // Format timestamp
    const timeString = new Date(timestamp).toLocaleString();
    
    // Truncate review text if too long
    const displayText = reviewText.length > 50 
        ? reviewText.substring(0, 50) + '...' 
        : reviewText;
    
    // Format confidence as decimal value
    const confidenceDecimal = Number(confidence).toFixed(2);
    
    // Create sentiment badge class
    const sentimentClass = `sentiment-${sentiment.toLowerCase()}`;
    
    row.innerHTML = `
        <td title="${reviewText}">${displayText}</td>
        <td><span class="sentiment-badge ${sentimentClass}">${sentiment}</span></td>
        <td><span class="confidence-score">${confidenceDecimal}</span></td>
        <td><span class="timestamp">${timeString}</span></td>
    `;
    
    return row;
}

// Event listeners
refreshHistoryBtn?.addEventListener('click', loadPredictionHistory);

// Initialize history on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPredictionHistory();
});

// Event listeners
predictBtn?.addEventListener('click', handlePrediction);
reviewInput?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        handlePrediction();
    }
});

// Sample button event listeners
sampleButtons.forEach(button => {
    button?.addEventListener('click', () => {
        const sampleReview = button.getAttribute('data-review');
        if (reviewInput) {
            reviewInput.value = sampleReview;
            reviewInput.focus();
        }
    });
});

// Main prediction function
async function handlePrediction() {
    const reviewText = reviewInput.value.trim();
    
    if (!reviewText) {
        showError('Please enter a review to analyze.');
        return;
    }
    
    if (reviewText.length < 5) {
        showError('Please enter a longer review (at least 5 characters).');
        return;
    }
    
    setLoadingState(true);
    
    try {
        const response = await fetch('/api/predict', {   // ✅ FIXED
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                review: reviewText   // ✅ FIXED
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        displayResults({
            sentiment: result.sentiment,
            confidence: result.confidence
        });
        
        await loadPredictionHistory();
        
    } catch (error) {
        console.error('Prediction error:', error);
        showError('An error occurred while analyzing the sentiment. Please try again.');
    } finally {
        setLoadingState(false);
    }
}

// Display results function
function displayResults(result) {
    const { sentiment, confidence } = result;
    
    // Update sentiment display
    sentimentValue.textContent = sentiment;
    confidenceValue.textContent = confidence.toFixed(2);
    
    // Update sentiment icon and styling
    const sentimentResult = document.querySelector('.sentiment-result');
    sentimentResult.classList.remove('positive', 'negative', 'neutral');
    
    switch (sentiment.toLowerCase()) {
        case 'positive':
            sentimentResult.classList.add('positive');
            sentimentIcon.textContent = '😊';
            break;
        case 'negative':
            sentimentResult.classList.add('negative');
            sentimentIcon.textContent = '😞';
            break;
        case 'neutral':
            sentimentResult.classList.add('neutral');
            sentimentIcon.textContent = '😐';
            break;
    }
    
    // Animate confidence bar
    setTimeout(() => {
        confidenceFill.style.width = `${confidence * 100}%`;
    }, 300);
    
    // Show results section with animation
    resultsSection.classList.add('show');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Loading state management
function setLoadingState(isLoading) {
    if (isLoading) {
        predictBtn.classList.add('loading');
        predictBtn.disabled = true;
        predictBtn.querySelector('.button-text').textContent = 'Analyzing...';
    } else {
        predictBtn.classList.remove('loading');
        predictBtn.disabled = false;
        predictBtn.querySelector('.button-text').textContent = '🔍 Predict Sentiment';
    }
}

// Error handling
function showError(message) {
    // Create or update error message
    let errorDiv = document.querySelector('.error-message');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border: 1px solid #f5c6cb;
            font-weight: 500;
            text-align: center;
        `;
        predictBtn.parentNode.insertBefore(errorDiv, predictBtn.nextSibling);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Hide error after 5 seconds
    setTimeout(() => {
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }, 5000);
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    // Focus on input field
    if (reviewInput) {
        reviewInput.focus();
        
        // Add some interactive features
        reviewInput.addEventListener('input', () => {
            const charCount = reviewInput.value.length;
            if (predictBtn) {
                if (charCount > 0) {
                    predictBtn.style.opacity = '1';
                } else {
                    predictBtn.style.opacity = '0.7';
                }
            }
        });
        
        // Add keyboard shortcuts info
        const shortcutInfo = document.createElement('div');
        shortcutInfo.innerHTML = '<small style="color: #6c757d; font-style: italic;">💡 Tip: Press Ctrl+Enter to quickly analyze your review</small>';
        shortcutInfo.style.marginTop = '10px';
        reviewInput.parentNode.appendChild(shortcutInfo);
    }
    
    console.log('Amazon Review Sentiment Analyzer initialized successfully! 🚀');
});