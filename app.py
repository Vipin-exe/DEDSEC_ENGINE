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
                linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.3)), 
                url('/static/bg.jpg'); 
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
            color: #e2e8f0; display: flex; justify-content: center; align-items: center;
            min-height: 100vh; overflow: hidden; padding: 20px;
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
            padding: 45px 40px;
            border-radius: 0px; 
            border: 1px solid rgba(255, 0, 85, 0.2); 
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
            width: 100%; 
            max-width: 550px;
            text-align: center;
            animation: fadeIn 0.6s ease-out forwards;
        }
        h2 { 
            color: #ff0055; 
            font-size: clamp(24px, 5vw, 28px); 
            margin-bottom: 6px; 
            letter-spacing: 2px;
            text-transform: uppercase;
            text-shadow: 0 0 10px rgba(255, 0, 85, 0.4);
        }
        p.subtitle { 
            color: #94a3b8; 
            font-size: clamp(13px, 3vw, 14px); 
            margin-bottom: 30px; 
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .upload-area {
            border: 2px dashed #ff0055; 
            padding: 35px 20px;
            background: rgba(0, 0, 0, 0.6);
            margin-bottom: 25px;
            transition: all 0.3s ease;
            position: relative;
        }
        .upload-area:hover, .upload-area.dragover {
            border-color: #ffffff;
            background: rgba(255, 0, 85, 0.1);
        }
        input[type="file"] { display: none; }
        .upload-label {
            background: rgba(0, 0, 0, 0.5);
            color: #ff0055;
            border: 1px solid #ff0055;
            padding: 14px 28px;
            cursor: pointer;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            width: 100%; max-width: 250px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .upload-label:hover {
            background: #ff0055;
            color: white;
            box-shadow: 0 0 15px rgba(255, 0, 85, 0.5);
            transform: translateY(-2px);
        }
        .filename-display { 
            margin-top: 15px; 
            font-size: 14px; 
            color: #cbd5e1; 
            font-family: monospace;
            min-height: 20px;
            word-wrap: break-word;
            padding: 0 10px;
        }
        button[type="submit"] {
            background: linear-gradient(135deg, #ff0055, #b3003b); 
            color: white;
            border: none;
            padding: 16px 30px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 0, 85, 0.3);
        }
        button[type="submit"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 0, 85, 0.5);
            animation: pulseGlow 1.5s infinite;
        }
        button[type="submit"]:disabled {
            background: #333333;
            color: #666666;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
            animation: none;
        }
        .stats {
            margin-top: 30px;
            background: rgba(0, 0, 0, 0.8);
            padding: 25px;
            border-left: 4px solid #ff0055; 
            text-align: left;
            animation: fadeIn 0.5s ease-out forwards;
        }
        .stats strong {
            display: block;
            color: #fff;
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 1px solid rgba(255, 0, 85, 0.3);
            padding-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-size: 15px;
        }
        .stat-label { color: #94a3b8; }
        .stat-value { font-family: monospace; color: #e2e8f0; font-size: 16px;}
        .highlight { 
            color: #ff0055; 
            font-weight: bold; 
            font-size: clamp(20px, 4vw, 24px);
            text-shadow: 0 0 15px rgba(255, 0, 85, 0.5);
        }
        .download-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 25px;
            background: transparent;
            color: #ff0055;
            text-decoration: none;
            padding: 15px;
            font-weight: 600;
            border: 1px solid #ff0055;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .download-btn:hover {
            background: #ff0055;
            color: #fff;
            box-shadow: 0 0 15px rgba(255, 0, 85, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Huffman Engine</h2>
        <p class="subtitle">Lossless C-Core Text Compression</p>
        
        <form action="/" method="POST" enctype="multipart/form-data">
            <div class="upload-area" id="drop-zone">
                <label for="file-upload" class="upload-label">
                    Select Target File
                </label>
                <input id="file-upload" type="file" name="file" accept=".txt" required onchange="showFileName(this)">
                <div class="filename-display" id="filename">Awaiting file input...</div>
            </div>
            <button type="submit" id="compress-btn">Execute Compression</button>
        </form>

        {% if error %}
        <div style="margin-top: 20px; color: #ff3333; font-family: monospace; background: rgba(255,0,0,0.1); padding: 10px; border: 1px solid #ff3333; text-align: left; font-size: 13px;">
            <strong>C-CORE ERROR:</strong><br>{{ error }}
        </div>
        {% endif %}

        {% if stats %}
        <div class="stats">
            <strong>Diagnostic Results</strong>
            <div class="stat-row">
                <span class="stat-label">Original Payload:</span>
                <span class="stat-value">{{ stats.original }} bytes</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Compressed Package:</span>
                <span class="stat-value">{{ stats.compressed }} bytes</span>
            </div>
            <div class="stat-row highlight-row" style="margin-top: 20px;">
                <span class="stat-label" style="color: #fff; font-weight: bold;">Space Reclaimed:</span>
                <span class="stat-value highlight">{{ stats.ratio }}%</span>
            </div>
            
            <a href="/download" class="download-btn">
                Download .bin Package
            </a>
        </div>
        {% endif %}
    </div>

    <script>
        function showFileName(input) {
            const display = document.getElementById('filename');
            const btn = document.getElementById('compress-btn');
            if (input.files[0]) {
                display.style.color = '#ff0055';
                display.innerText = "> " + input.files[0].name + " loaded.";
                btn.style.opacity = '1';
                btn.disabled = false;
            } else {
                display.style.color = '#cbd5e1';
                display.innerText = "Awaiting file input...";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    stats = None
    error = None
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(HTML_TEMPLATE, stats=None, error="No file part provided.")
        file = request.files['file']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, stats=None, error="No selected file.")
        
        input_path = "temp_input.txt"
        output_path = "output.bin"
        
        try:
            # Save uploaded file temporarily
            file.save(input_path)
            
            # Select backend binary based on server environment
            if platform.system() == "Windows":
                backend_executable = "./huffman_backend.exe"
            else:
                backend_executable = "./huffman_backend"
                # Ensure execution permission on Linux/Render
                os.system(f"chmod +x {backend_executable}")

            # Execute the C-Core binary via subprocess
            result = subprocess.run(
                [backend_executable, "compress", input_path, output_path],
                capture_output=True,
                text=True,
                check=True
            )

            # Measure true physical files on disk
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)

            # Calculate accurate space reclaimed ratio
            if original_size > 0:
                ratio = round(((original_size - compressed_size) / original_size) * 100, 2)
            else:
                ratio = 0.0

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
            # Clean up the temporary input text file
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except:
                    pass

    return render_template_string(HTML_TEMPLATE, stats=stats, error=error)

@app.route('/download')
def download():
    output_path = "output.bin"
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True, download_name="compressed_package.bin")
    return "No compressed package found.", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)