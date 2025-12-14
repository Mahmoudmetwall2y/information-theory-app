# Enhanced Flask Application for Information Theory Project
# Integrates with modern web interface and provides API endpoints

from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
from pathlib import Path
from datetime import datetime
import json
import os

from codec import run_full_pipeline

app = Flask(__name__)
CORS(app)  # Enable CORS for modern frontend integration

RUNS_DIR = Path("runs")
UPLOAD_DIR = Path("uploads")

# Ensure directories exist
RUNS_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    """Serve the main landing page"""
    return send_from_directory('.', 'index.html')

@app.route('/project')
def project():
    """Serve the project execution interface"""
    return send_from_directory('.', 'project.html')

@app.route('/documentation')
def documentation():
    """Serve the documentation page"""
    return send_from_directory('.', 'documentation.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return file information"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.txt'):
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upload_{timestamp}.txt"
        filepath = UPLOAD_DIR / filename
        file.save(filepath)
        
        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'filename': file.filename,
            'size': len(content),
            'content': content[:1000] + '...' if len(content) > 1000 else content,
            'upload_path': str(filepath)
        })
    
    return jsonify({'error': 'Invalid file format. Please upload a .txt file'}), 400

@app.route('/api/process', methods=['POST'])
def process_text():
    """Process text through the complete pipeline"""
    try:
        data = request.get_json()
        
        # Extract parameters
        text = data.get('text', '')
        error_interval = int(data.get('error_interval', 50))
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Run the complete pipeline
        results = run_full_pipeline(text, error_interval=error_interval)
        
        # Create run directory and save outputs
        run_dir = make_run_dir()
        save_part_outputs(run_dir, text, error_interval, results)
        
        # Prepare response data
        response_data = {
            'success': True,
            'run_directory': str(run_dir),
            'summary': {
                'original_length': results['text_length'],
                'encoded_length': len(results['encoded_bits']),
                'hamming_length': len(results['hamming_bits']),
                'pad_bits': results['pad_bits'],
                'compression_ratio': f"{results['text_length'] / len(results['encoded_bits']):.2f}:1"
            },
            'quality_metrics': {
                'huffman_ok': results['huffman_ok'],
                'hamming_ok': results['hamming_ok'],
                'corrupted_decode_ok': results['corrupted_decode_ok'],
                'recovered_text_ok': results['recovered_text_ok']
            },
            'top_probabilities': sorted(results['probabilities'].items(), key=lambda x: -x[1])[:10],
            'encoded_bits_preview': results['encoded_bits'][:200],
            'hamming_bits_preview': results['hamming_bits'][:200],
            'corrupted_bits_preview': results['corrupted_bits'][:200],
            'recovered_bits_preview': results['recovered_bits'][:200],
            'original_text_preview': text[:300],
            'decoded_text_preview': results['decoded_text'][:300],
            'corrupted_decoded_preview': results['corrupted_decoded_text'][:300],
            'recovered_decoded_preview': results['recovered_decoded_text'][:300]
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/sample-text', methods=['GET'])
def get_sample_text():
    """Return sample text content for demonstration"""
    sample_type = request.args.get('type', 'simple')
    
    samples = {
        'simple': 'Hello World! This is a sample text for Huffman encoding demonstration.',
        'info_theory': 'Information theory is a mathematical study of information storage and communication. It was originally proposed by Claude Shannon in 1948 to find fundamental limits on signal processing and communication operations.',
        'lorem': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
        'mixed': 'The quick brown fox jumps over the lazy dog. 1234567890!@#$%^&*()_+{}[]|\\:;\"<>?,./\''
    }
    
    return jsonify({
        'content': samples.get(sample_type, samples['simple']),
        'type': sample_type
    })

@app.route('/api/runs', methods=['GET'])
def list_runs():
    """List all processing runs"""
    runs = []
    if RUNS_DIR.exists():
        for run_dir in RUNS_DIR.iterdir():
            if run_dir.is_dir():
                summary_file = run_dir / "summary.json"
                if summary_file.exists():
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                    runs.append({
                        'directory': run_dir.name,
                        'timestamp': run_dir.name,
                        'summary': summary
                    })
    
    return jsonify({'runs': sorted(runs, key=lambda x: x['timestamp'], reverse=True)})

@app.route('/api/runs/<run_id>', methods=['GET'])
def get_run(run_id):
    """Get detailed information about a specific run"""
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        return jsonify({'error': 'Run not found'}), 404
    
    try:
        # Load summary
        with open(run_dir / "summary.json", 'r') as f:
            summary = json.load(f)
        
        # Load other relevant files
        result = {'summary': summary}
        
        # Add file contents if they exist
        files_to_load = {
            'text': 'Text.txt',
            'huffman_codes': 'huffman_codes.txt',
            'encoded_bits': 'part2_bits.txt',
            'decoded_text': 'part3_decoded.txt',
            'hamming_bits': 'part4_hamming_bits.txt',
            'corrupted_bits': 'part5_corrupted_bits.txt',
            'recovered_bits': 'part6_recovered_bits.txt'
        }
        
        for key, filename in files_to_load.items():
            file_path = run_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    result[key] = content[:1000] + '...' if len(content) > 1000 else content
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to load run data: {str(e)}'}), 500

# Original helper functions (unchanged)
def make_run_dir() -> Path:
    RUNS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = RUNS_DIR / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")

def save_part_outputs(run_dir: Path, original_text: str, interval: int, results: dict) -> None:
    write_file(run_dir / "Text.txt", original_text)
    
    probs = results["probabilities"]
    part1_lines = ["# symbol\tprobability"]
    for sym, p in sorted(probs.items(), key=lambda kv: kv[0]):
        part1_lines.append(f"{repr(sym)}\t{p:.10f}")
    write_file(run_dir / "part1_symbols.txt", "\n".join(part1_lines))
    
    codes = results["codes"]
    codes_lines = ["# symbol\tcode"]
    for sym, code in sorted(codes.items(), key=lambda kv: kv[0]):
        codes_lines.append(f"{repr(sym)}\t{code}")
    write_file(run_dir / "huffman_codes.txt", "\n".join(codes_lines))
    
    write_file(run_dir / "part2_bits.txt", results["encoded_bits"])
    write_file(run_dir / "part3_decoded.txt", results["decoded_text"])
    write_file(run_dir / "part4_hamming_bits.txt", results["hamming_bits"])
    write_file(run_dir / "part4_pad.txt", str(results["pad_bits"]))
    write_file(run_dir / "part5_corrupted_bits.txt", results["corrupted_bits"])
    
    # Corrupted decode artifacts (no correction)
    write_file(run_dir / "part5b_corrupted_data_bits.txt", results["corrupted_data_bits"])
    write_file(run_dir / "part5c_corrupted_decoded_text.txt", results["corrupted_decoded_text"])
    write_file(run_dir / "part5c_corrupted_decode_ok.txt", str(results["corrupted_decode_ok"]))
    
    write_file(run_dir / "part6_recovered_bits.txt", results["recovered_bits"])
    write_file(run_dir / "part6_recovered_decoded_text.txt", results["recovered_decoded_text"])
    write_file(run_dir / "part6_recovered_text_ok.txt", str(results["recovered_text_ok"]))
    
    summary = {
        "error_interval": interval,
        "text_length_symbols": results["text_length"],
        "encoded_length_bits": len(results["encoded_bits"]),
        "hamming_length_bits": len(results["hamming_bits"]),
        "pad_bits": results["pad_bits"],
        "huffman_ok": results["huffman_ok"],
        "hamming_ok": results["hamming_ok"],
        "corrupted_decode_ok": results["corrupted_decode_ok"],
        "recovered_text_ok": results["recovered_text_ok"],
    }
    write_file(run_dir / "summary.json", json.dumps(summary, indent=2))

# Serve static files
@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, images, etc.)"""
    return send_from_directory('.', filename)

if __name__ == "__main__":
    print("Starting Information Theory Project Server...")
    print("Available endpoints:")
    print("  - GET  /                    : Main landing page")
    print("  - GET  /project             : Project execution interface")
    print("  - GET  /documentation       : Documentation page")
    print("  - POST /api/upload          : Upload text file")
    print("  - POST /api/process         : Process text through pipeline")
    print("  - GET  /api/sample-text     : Get sample text content")
    print("  - GET  /api/runs            : List all processing runs")
    print("  - GET  /api/runs/<run_id>   : Get specific run details")
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)