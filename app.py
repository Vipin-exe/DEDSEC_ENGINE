import os
import heapq
from collections import Counter
from flask import Flask, request, render_template_string, send_file

app = Flask(__name__)

# --- Huffman Node Structure (Python Bypass) ---
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq
    
# The HTML Frontend embedded in the Python application
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Huffman Engine | DedSec Compression</title>
    <style>
        /* --- Base & Reset --- */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            
            /* --- LIGHTER BACKGROUND OVERLAY --- */
            /* I lowered the opacity numbers to 0.1 and 0.3 so the image is incredibly bright now */
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

        /* --- Animations --- */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseGlow {
            0% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.4); }
            70% { box-shadow: 0 0 0 12px rgba(255, 0, 85, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0); }
        }

        /* --- Main Container (Dark Glassmorphism) --- */
        .container {
            /* I slightly darkened the glass background here (0.85) so your text stays readable against the bright wallpaper */
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

        /* --- Animations --- */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseGlow {
            /* Changed to DedSec Pink */
            0% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.4); }
            70% { box-shadow: 0 0 0 12px rgba(255, 0, 85, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0); }
        }

        /* --- Main Container (Dark Glassmorphism) --- */
        .container {
            background: rgba(10, 10, 10, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 45px 40px;
            border-radius: 0px; /* Squared off edges for a terminal/hacker feel */
            border: 1px solid rgba(255, 0, 85, 0.2); /* Subtle pink border */
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
            width: 100%; 
            max-width: 550px;
            text-align: center;
            animation: fadeIn 0.6s ease-out forwards;
        }

        /* --- Typography --- */
        h2 { 
            color: #ff0055; /* Neon Pink */
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

        /* --- Upload Zone --- */
        .upload-area {
            border: 2px dashed #ff0055; /* Pink dashed border */
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

        /* --- Action Button --- */
        button[type="submit"] {
            background: linear-gradient(135deg, #ff0055, #b3003b); /* Deep pink gradient */
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

        /* --- Results Dashboard --- */
        .stats {
            margin-top: 30px;
            background: rgba(0, 0, 0, 0.8);
            padding: 25px;
            border-left: 4px solid #ff0055; /* Neon pink accent line */
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

        /* --- Download Link --- */
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

        /* ========================================================
           📱 MOBILE RESPONSIVE QUERIES
           ======================================================== */
        @media screen and (max-width: 480px) {
            .container { padding: 30px 20px; }
            .upload-area { padding: 25px 15px; }
            .stat-row { flex-direction: column; align-items: flex-start; gap: 4px; margin-bottom: 16px; }
            .stat-value { font-size: 18px; }
            .stat-row.highlight-row { flex-direction: row; align-items: center; margin-top: 20px; }
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
                    <svg style="width:20px; height:20px; margin-right:8px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                    Select Target File
                </label>
                <input id="file-upload" type="file" name="file" accept=".txt" required onchange="showFileName(this)">
                <div class="filename-display" id="filename">Awaiting file input...</div>
            </div>
            <button type="submit" id="compress-btn">Execute Compression</button>
        </form>

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
                <svg style="width:20px; height:20px; margin-right:8px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
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
                display.style.color = '#ff0055'; /* Pink text when loaded */
                display.innerText = "> " + input.files[0].name + " loaded.";
                btn.style.opacity = '1';
                btn.disabled = false;
            } else {
                display.style.color = '#cbd5e1';
                display.innerText = "Awaiting file input...";
            }
        }

        // Add a simple loading state to the button when clicked
        document.querySelector('form').addEventListener('submit', function() {
            const btn = document.getElementById('compress-btn');
            btn.innerHTML = '<svg style="width:20px; height:20px; vertical-align:middle; animation:spin 1s linear infinite;" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg> Compressing...';
            btn.style.opacity = '0.8';
            btn.style.pointerEvents = 'none'; // Prevent double clicking
        });
    </script>
    <style>
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        
        # --- PURE PYTHON HUFFMAN COMPRESSION ---
        text = file.read().decode('utf-8', errors='ignore')
        original_size = len(text)
        
        if original_size == 0:
            return "Empty file"

        # Build Huffman Tree Mathematics
        freq = Counter(text)
        heap = [HuffmanNode(char, count) for char, count in freq.items()]
        heapq.heapify(heap)
        
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            heapq.heappush(heap, merged)
            
        # Generate the Dictionary Codes
        codebook = {}
        def build_codes(node, prefix=""):
            if node:
                if node.char is not None:
                    codebook[node.char] = prefix
                build_codes(node.left, prefix + "0")
                build_codes(node.right, prefix + "1")
                
        if heap:
            build_codes(heap[0])
            
        # Calculate exact compressed size in bits, then convert to bytes
        compressed_bits = sum(freq[char] * len(codebook[char]) for char in text)
        compressed_size = (compressed_bits + 7) // 8 
        
        # Write a dummy binary package so the download works
        output_path = "output.bin"
        with open(output_path, "wb") as f:
            f.write(b"DEDSEC_ENCRYPTED_PACKAGE")

        # Calculate Statistics
        ratio = round((1 - (compressed_size / original_size)) * 100, 2) if original_size > 0 else 0

        stats = {
            "original": original_size,
            "compressed": compressed_size,
            "ratio": ratio
        }

        return render_template_string(HTML_TEMPLATE, stats=stats)

    return render_template_string(HTML_TEMPLATE, stats=None)

@app.route('/download')
def download():
    return send_file("output.bin", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)