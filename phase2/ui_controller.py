"""Flask REST API for Play Store Review Analyzer."""
import os
import sys
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import Config
from common.models import AnalysisRequest, PipelineStatus
from phase2.pipeline_orchestrator import PipelineOrchestrator


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Enable CORS for Next.js frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


# Global pipeline orchestrator
orchestrator = PipelineOrchestrator()


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get configuration limits."""
    return jsonify({
        'min_weeks': Config.MIN_WEEKS,
        'max_weeks': Config.MAX_WEEKS,
        'max_themes': Config.MAX_THEMES,
        'word_limit': Config.REPORT_WORD_LIMIT,
        'groq_model': Config.GROQ_MODEL
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Handle analysis request and start pipeline (REST API)."""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        weeks_back = data.get('weeks_back')
        recipient_email = data.get('recipient_email')
        
        # Validation
        if not weeks_back or not isinstance(weeks_back, int):
            return jsonify({'error': 'weeks_back must be an integer'}), 400
        
        if weeks_back < Config.MIN_WEEKS or weeks_back > Config.MAX_WEEKS:
            return jsonify({
                'error': f'weeks_back must be between {Config.MIN_WEEKS} and {Config.MAX_WEEKS}'
            }), 400
        
        if not recipient_email or '@' not in recipient_email:
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Create analysis request
        timestamp = datetime.now()
        request_id = f"req_{timestamp.strftime('%Y%m%d_%H%M%S')}_{timestamp.microsecond}"
        
        analysis_request = AnalysisRequest(
            weeks_back=weeks_back,
            recipient_email=recipient_email,
            request_timestamp=timestamp,
            request_id=request_id
        )
        
        # Start pipeline in background thread
        import threading
        thread = threading.Thread(
            target=orchestrator.run_pipeline,
            args=(analysis_request,)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'request_id': request_id,
            'status': 'pending',
            'message': 'Analysis started'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<request_id>', methods=['GET'])
def status(request_id):
    """Get pipeline status for a request (REST API)."""
    pipeline_status = orchestrator.get_status(request_id)
    
    if pipeline_status:
        return jsonify({
            'request_id': pipeline_status.request_id,
            'status': pipeline_status.status,
            'current_step': pipeline_status.current_step,
            'progress_percent': pipeline_status.progress_percent,
            'error_message': pipeline_status.error_message,
            'started_at': pipeline_status.started_at.isoformat() if pipeline_status.started_at else None,
            'completed_at': pipeline_status.completed_at.isoformat() if pipeline_status.completed_at else None
        })
    else:
        return jsonify({'error': 'Request not found'}), 404


@app.route('/api/report/<request_id>', methods=['GET'])
def report(request_id):
    """Get the generated report (REST API)."""
    result = orchestrator.get_result(request_id)
    
    if result and result['status'] == 'complete':
        return jsonify({
            'request_id': request_id,
            'status': 'complete',
            'report': result['report'],
            'email_draft': result['email_draft'],
            'metadata': result['metadata']
        })
    elif result and result['status'] == 'error':
        return jsonify({
            'request_id': request_id,
            'status': 'error',
            'error': result.get('error', 'Unknown error')
        }), 500
    else:
        return jsonify({'error': 'Report not found'}), 404


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint (REST API)."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'groq_model': Config.GROQ_MODEL,
            'max_reviews': Config.SCRAPER_MAX_REVIEWS,
            'max_themes': Config.MAX_THEMES,
            'min_weeks': Config.MIN_WEEKS,
            'max_weeks': Config.MAX_WEEKS
        }
    })


def main():
    """Run the Flask REST API server."""
    print("=" * 80)
    print("PLAY STORE REVIEW ANALYZER - REST API")
    print("=" * 80)
    print()
    print(f"Starting Flask API server...")
    print(f"Configuration:")
    print(f"  - Groq Model: {Config.GROQ_MODEL}")
    print(f"  - Max Reviews: {Config.SCRAPER_MAX_REVIEWS}")
    print(f"  - Max Themes: {Config.MAX_THEMES}")
    print(f"  - Report Word Limit: {Config.REPORT_WORD_LIMIT}")
    print()
    print("API Endpoints:")
    print("  - POST   /api/analyze        - Start analysis")
    print("  - GET    /api/status/<id>    - Get status")
    print("  - GET    /api/report/<id>    - Get report")
    print("  - GET    /api/config         - Get config")
    print("  - GET    /api/health         - Health check")
    print()
    print("API Server: http://localhost:5000")
    print("CORS enabled for: http://localhost:3000")
    print("=" * 80)
    print()
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
