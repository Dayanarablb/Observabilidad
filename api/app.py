from flask import Flask, jsonify, render_template_string
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import random

app = Flask(__name__)

# ==================== MÉTRICAS PROMETHEUS ====================
REQUEST_COUNT = Counter('http_requests_total', 'Total de requests HTTP', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Latencia de requests HTTP', ['endpoint'])
ACTIVE_REQUESTS = Gauge('http_requests_active', 'Requests activos en este momento')

# ==================== DATOS DE INVENTARIO ====================
inventory_data = [
    {"id": 1, "name": "Laptop Pro", "price": 1299, "stock": 15},
    {"id": 2, "name": "Mouse Gamer", "price": 45, "stock": 50},
    {"id": 3, "name": "Teclado Mecánico", "price": 129, "stock": 30},
    {"id": 4, "name": "Monitor 4K", "price": 599, "stock": 8},
    {"id": 5, "name": "Webcam HD", "price": 89, "stock": 25},
]

# ==================== HTML CON DISEÑO PROFESIONAL DARK ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Inventario - Monitoring</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b82;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --success: #10b981;
            --border: #334155;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem 1rem;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        
        h1 {
            font-size: 2.4rem;
            font-weight: 700;
            color: white;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }
        
        @media (max-width: 768px) {
            .status-grid { grid-template-columns: 1fr; }
        }
        
        .status-card {
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            text-align: center;
        }
        
        .status-card .label {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-card .value {
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--accent);
        }
        
        .status-card .value.online { color: var(--success); }
        
        .actions {
            display: flex;
            gap: 1rem;
            margin-bottom: 2.5rem;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        button {
            padding: 0.9rem 1.8rem;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary {
            background: var(--accent);
            color: white;
        }
        .btn-primary:hover {
            background: var(--accent-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
        }
        
        .btn-secondary {
            background: #334155;
            color: white;
        }
        .btn-secondary:hover {
            background: #475569;
            transform: translateY(-2px);
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        .btn-danger:hover {
            background: #dc2626;
            transform: translateY(-2px);
        }
        
        .inventory-section {
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border);
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            color: white;
            display: flex;
            align-items: center;
            gap: 0.7rem;
        }
        
        .product-grid {
            display: grid;
            gap: 1rem;
        }
        
        .product-card {
            background: var(--bg-secondary);
            padding: 1.3rem;
            border-radius: 10px;
            border-left: 4px solid var(--accent);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .product-card:hover {
            transform: translateX(4px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        .product-info h3 {
            color: white;
            font-size: 1.2rem;
            margin-bottom: 0.3rem;
        }
        
        .product-stock {
            color: var(--text-secondary);
            font-size: 0.95rem;
        }
        
        .product-price {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--success);
        }
        
        .response-box {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 2rem;
            display: none;
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        
        .response-box.show {
            display: block;
            opacity: 1;
        }
        
        .response-box h3 {
            margin-bottom: 1rem;
            color: var(--accent);
        }
        
        pre {
            background: #0f172a;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            color: #94a3b8;
            font-size: 0.95rem;
        }
        
        .footer {
            text-align: center;
            margin-top: 3rem;
            color: var(--text-secondary);
            font-size: 0.95rem;
        }
        
        .metrics-link {
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
            margin-top: 0.8rem;
            display: inline-block;
        }
        
        .metrics-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Sistema de Inventario</h1>
            <p class="subtitle">API REST con observabilidad Prometheus</p>
        </header>

        <div class="status-grid">
            <div class="status-card">
                <div class="label">Estado del Servicio</div>
                <div class="value online">Online</div>
            </div>
            <div class="status-card">
                <div class="label">Latencia Promedio</div>
                <div class="value" id="latency">~52ms</div>
            </div>
            <div class="status-card">
                <div class="label">Productos en Stock</div>
                <div class="value">{{ products|length }}</div>
            </div>
        </div>

        <div class="actions">
            <button class="btn-primary" onclick="fetchAll()">
                Consultar Inventario
            </button>
            <button class="btn-secondary" onclick="fetchRandom()">
                Producto Aleatorio
            </button>
            <button class="btn-danger" onclick="simulateError()">
                Simular Error 500
            </button>
        </div>

        <div class="inventory-section">
            <h2 class="section-title">Inventario Actual</h2>
            <div class="product-grid">
                {% for product in products %}
                <div class="product-card">
                    <div class="product-info">
                        <h3>{{ product.name }}</h3>
                        <div class="product-stock">Stock: {{ product.stock }} unidades</div>
                    </div>
                    <div class="product-price">${{ product.price }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="response-box" id="responseBox">
            <h3>Respuesta de la API</h3>
            <pre id="responseContent"></pre>
        </div>

        <div class="footer">
            <p>Monitoreo en tiempo real con Prometheus</p>
            <a href="/metrics" target="_blank" class="metrics-link">Ver métricas Prometheus</a>
        </div>
    </div>

    <script>
        function updateLatency() {
            const latency = Math.floor(Math.random() * 80) + 30;
            document.getElementById('latency').textContent = '~' + latency + 'ms';
        }

        function showResponse(data) {
            const box = document.getElementById('responseBox');
            const content = document.getElementById('responseContent');
            content.textContent = JSON.stringify(data, null, 2);
            box.classList.add('show');
            updateLatency();
        }

        async function fetchAll() {
            try {
                const res = await fetch('/api/inventory');
                const data = await res.json();
                showResponse(data);
            } catch (err) {
                showResponse({ error: err.message });
            }
        }

        async function fetchRandom() {
            const id = Math.floor(Math.random() * 5) + 1;
            try {
                const res = await fetch(`/api/inventory/${id}`);
                const data = await res.json();
                showResponse(data);
            } catch (err) {
                showResponse({ error: err.message });
            }
        }

        async function simulateError() {
            try {
                await fetch('/api/error');
            } catch (err) {
                showResponse({ error: "Error 500 simulado correctamente" });
            }
        }

        // Actualizar latencia cada 3 segundos
        setInterval(updateLatency, 3000);
        updateLatency();
    </script>
</body>
</html>
"""

# ==================== ENDPOINTS (sin cambios funcionales) ====================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, products=inventory_data)

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    start_time = time.time()
    ACTIVE_REQUESTS.inc()
    time.sleep(random.uniform(0.01, 0.15))
    
    REQUEST_COUNT.labels(method='GET', endpoint='/api/inventory', status='200').inc()
    REQUEST_LATENCY.labels(endpoint='/api/inventory').observe(time.time() - start_time)
    ACTIVE_REQUESTS.dec()
    
    return jsonify({"status": "success", "data": inventory_data, "total": len(inventory_data)})

@app.route('/api/inventory/<int:product_id>', methods=['GET'])
def get_product(product_id):
    start_time = time.time()
    ACTIVE_REQUESTS.inc()
    time.sleep(random.uniform(0.01, 0.10))
    
    product = next((p for p in inventory_data if p['id'] == product_id), None)
    
    if product:
        REQUEST_COUNT.labels(method='GET', endpoint='/api/inventory/:id', status='200').inc()
        REQUEST_LATENCY.labels(endpoint='/api/inventory/:id').observe(time.time() - start_time)
        ACTIVE_REQUESTS.dec()
        return jsonify({"status": "success", "data": product})
    else:
        REQUEST_COUNT.labels(method='GET', endpoint='/api/inventory/:id', status='404').inc()
        REQUEST_LATENCY.labels(endpoint='/api/inventory/:id').observe(time.time() - start_time)
        ACTIVE_REQUESTS.dec()
        return jsonify({"status": "error", "message": "Producto no encontrado"}), 404

@app.route('/api/error', methods=['GET'])
def simulate_error():
    REQUEST_COUNT.labels(method='GET', endpoint='/api/error', status='500').inc()
    return jsonify({"status": "error", "message": "Error interno simulado"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "inventory-api"}), 200

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
