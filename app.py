import os
import subprocess
import platform
from flask import Flask, request, render_template_string, send_file

app = Flask(__name__)
app.secret_key = 'dedsec_secret_key'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Huffman Engine | DedSec Compression</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background-image: 
                linear-gradient(rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.4)), 
                url('/static/bg.jpg'); 
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
            color: #e2e8f0; display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 20px;
            position: relative;
            z-index: 1;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseGlow {
            0% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.4); }
            70% { box-shadow: 0 0 0 12px rgba(255, 0, 85, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0); }
        }
        .container {
            background: rgba(10, 10, 10, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 35px 30px;
            border-radius: 0px; 
            border: 1px solid rgba(255, 0, 85, 0.3); 
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
            width: 100%; 
            max-width: 600px;
            text-align: center;
            animation: fadeIn 0.6s ease-out forwards;
        }
        h2 { 
            color: #ff0055; 
            font-size: clamp(22px, 4vw, 26px); 
            margin-bottom: 4px; 
            letter-spacing: 2px;
            text-transform: uppercase;
            text-shadow: 0 0 10px rgba(255, 0, 85, 0.4);
        }
        p.subtitle { 
            color: #94a3b8; 
            font-size: clamp(12px, 3vw, 13px); 
            margin-bottom: 25px; 
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .engine-panel {
            background: rgba(0, 0, 0, 0.6);
            border: 1px dashed #ff0055;
            padding: 20px;
            margin-bottom: 20px;
            text-align: left;
        }
        .engine-panel h3 {
            color: #fff;
            font-size: 14px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid rgba(255, 0, 85, 0.2);
            padding-bottom: 6px;
        }
        input[type="file"] { 
            display: none; 
        }
        .upload-label {
            background: rgba(0, 0, 0, 0.5);
            color: #ff0055;
            border: 1px solid #ff0055;
            padding: 10px 15px;
            cursor: pointer;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 13px;
            margin-bottom: 10px;
        }
        .upload-label:hover {
            background: #ff0055;
            color: white;
            box-shadow: 0 0 15px rgba(255, 0, 85, 0.5);
        }
        .filename-display { 
            font-size: 13px; 
            color: #cbd5e1; 
            font-family: monospace;
            margin-bottom: 12px;
            word-break: break-all;
        }
        button[type="submit"] {
            background: linear-gradient(135deg, #ff0055, #b3003b); 
            color: white;
            border: none;
            padding: 12px 20px;
            font-size: 14px;
            cursor: pointer;
            width: 100%;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 0, 85, 0.3);
        }
        button[type="submit"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(255, 0, 85, 0.5);
        }
        .stats {
            margin-top: 15px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-left: 3px solid #ff0055; 
            text-align: left;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .stat-label { color: #94a3b8; }
        .stat-value { font-family: monospace; color: #e2e8f0; }
        .highlight { 
            color: #ff0055; 
            font-weight: bold; 
            font-size: 18px;
        }
        .success-box {
            margin-top: 15px;
            background: rgba(0, 255, 100, 0.1);
            border: 1px solid #00ff64;
            padding: 12px;
            color: #00ff64;
            font-family: monospace;
            font-size: 13px;
            text-align: left;
        }
        .download-btn {
            display: block;
            margin-top: 12px;
            background: transparent;
            color: #ff0055;
            text-decoration: none;
            padding: 10px;
            font-weight: 600;
            border: 1px solid #ff0055;
            text-align: center;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 13px;
        }
        .download-btn:hover {
            background: #ff0055;
            color: #fff;
            box-shadow: 0 0 12px rgba(255, 0, 85, 0.4);
        }
        .error-box {
            margin-top: 15px; 
            color: #ff3333; 
            font-family: monospace; 
            background: rgba(255,0,0,0.1); 
            padding: 10px; 
            border: 1px solid #ff3333; 
            text-align: left; 
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Huffman Engine</h2>
        <p class="subtitle">Lossless C-Core Text Compression & Decompression</p>
        
        <!-- COMPRESSION PANEL -->
        <div class="engine-panel">
            <h3>1. Compression Pipeline</h3>
            <form action="/compress" method="POST" enctype="multipart/form-data">
                <label for="file-upload-comp" class="upload-label">Select Text File (.txt)</label>
                <input id="file-upload-comp" type="file" name="file" accept=".txt" required onchange="showFileName(this, 'filename-comp', 'btn-comp')">
                <div class="filename-display" id="filename-comp">Awaiting file input...</div>
                <button type="submit" id="btn-comp">Execute Compression</button>
            </form>

            {% if comp_stats %}
            <div class="stats">
                <div class="stat-row"><span class="stat-label">Original Payload:</span><span class="stat-value">{{ comp_stats.original }} bytes</span></div>
                <div class="stat-row"><span class="stat-label">Compressed Package:</span><span class="stat-value">{{ comp_stats.compressed }} bytes</span></div>
                <div class="stat-row" style="margin-top: 10px;"><span class="stat-label" style="color: #fff; font-weight: bold;">Space Reclaimed:</span><span class="stat-value highlight">{{ comp_stats.ratio }}%</span></div>
                <a href="/download/output.bin" class="download-btn">Download .bin Package</a>
            </div>
            {% endif %}
        </div>

        <!-- DECOMPRESSION PANEL -->
        <div class="engine-panel">
            <h3>2. Decompression Pipeline</h3>
            <form action="/decompress" method="POST" enctype="multipart/form-data">
                <label for="file-upload-decomp" class="upload-label">Select Binary Package (.bin)</label>
                <input id="file-upload-decomp" type="file" name="file" accept=".bin" required onchange="showFileName(this, 'filename-decomp', 'btn-decomp')">
                <div class="filename-display" id="filename-decomp">Awaiting file input...</div>
                <button type="submit" id="btn-decomp">Execute Decompression</button>
            </form>

            {% if decomp_success %}
            <div class="success-box">
                Status: <strong>Successfully Restored!</strong><br>
                <a href="/download/restored_text.txt" class="download-btn" style="color: #00ff64; border-color: #00ff64;">Download Restored .txt File</a>
            </div>
            {% endif %}
        </div>

        {% if error %}
        <div class="error-box">
            <strong>C-CORE ERROR:</strong><br>{{ error }}
        </div>
        {% endif %}
    </div>

    <script>
        function showFileName(input, displayId, btnId) {
            const display = document.getElementById(displayId);
            if (input.files[0]) {
                display.style.color = '#ff0055';
                display.innerText = "> " + input.files[0].name + " loaded.";
            } else {
                display.style.color = '#cbd5e1';
                display.innerText = "Awaiting file input...";
            }
        }
    </script>
</body>
</html>
"""

def get_backend_executable():
    if platform.system() == "Windows":
        return "./huffman_backend.exe"
    else:
        backend = "./huffman_backend"
        os.system(f"chmod +x {backend}")
        return backend

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, comp_stats=None, decomp_success=False, error=None)

@app.route('/compress', methods=['POST'])
def compress():
    error = None
    stats = None
    input_path = "temp_input.txt"
    output_path = "output.bin"
    
    try:
        if 'file' not in request.files:
            return render_template_string(HTML_TEMPLATE, comp_stats=None, decomp_success=False, error="No file part provided.")
        file = request.files['file']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, comp_stats=None, decomp_success=False, error="No selected file.")
        
        file.save(input_path)
        backend = get_backend_executable()

        subprocess.run(
            [backend, "compress", input_path, output_path],
            capture_output=True,
            text=True,
            check=True
        )

        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)

        ratio = round(((original_size - compressed_size) / original_size) * 100, 2) if original_size > 0 else 0.0

        stats = {
            "original": original_size,
            "compressed": compressed_size,
            "ratio": ratio
        }

    except subprocess.CalledProcessError as e:
        error = f"Exit code {e.returncode}\nStdout: {e.stdout}\nStderr: {e.stderr}"
    except Exception as e:
        error = str(e)
    finally:
        if os.path.exists(input_path):
            try: os.remove(input_path)
            except: pass

    return render_template_string(HTML_TEMPLATE, comp_stats=stats, decomp_success=False, error=error)

@app.route('/decompress', methods=['POST'])
def decompress():
    error = None
    decomp_success = False
    input_path = "temp_compressed.bin"
    output_path = "restored_text.txt"
    
    try:
        if 'file' not in request.files:
            return render_template_string(HTML_TEMPLATE, comp_stats=None, decomp_success=False, error="No file part provided.")
        file = request.files['file']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, comp_stats=None, decomp_success=False, error="No selected file.")
        
        file.save(input_path)
        backend = get_backend_executable()

        subprocess.run(
            [backend, "decompress", input_path, output_path],
            capture_output=True,
            text=True,
            check=True
        )

        decomp_success = True

    except subprocess.CalledProcessError as e:
        error = f"Exit code {e.returncode}\nStdout: {e.stdout}\nStderr: {e.stderr}"
    except Exception as e:
        error = str(e)
    finally:
        if os.path.exists(input_path):
            try: os.remove(input_path)
            except: pass

    return render_template_string(HTML_TEMPLATE, comp_stats=None, decomp_success=decomp_success, error=error)

@app.route('/download/<filename>')
def download(filename):
    # Sanitize filename to prevent directory traversal
    safe_filename = os.path.basename(filename)
    if os.path.exists(safe_filename):
        return send_file(safe_filename, as_attachment=True)
    return "Requested package not found.", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)