
from flask import Flask, request, jsonify, render_template_string
from galicia_bot import calificar_urls, get_status
import os

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Bot Galicia N4</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root {
            --naranja-galicia: #f7931e;
            --gris-fondo: #f5f5f5;
            --texto: #333;
        }
        body {
            margin: 0;
            font-family: 'Segoe UI', sans-serif;
            background-color: white;
            color: var(--texto);
        }
        header {
            background-color: var(--naranja-galicia);
            color: white;
            padding: 12px 20px;
            display: flex;
            align-items: center;
        }
        header img {
            height: 36px;
            margin-right: 12px;
        }
        main {
            max-width: 800px;
            margin: 20px auto;
            padding: 0 20px;
        }
        h2 {
            font-size: 1.4rem;
            margin-bottom: 20px;
        }
        .form-section {
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }
        input[type=number], button {
            padding: 10px;
            font-size: 16px;
        }
        button {
            background-color: var(--naranja-galicia);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 20px;
            cursor: pointer;
        }
        button:hover {
            background-color: #e47d12;
        }
        .progress-container {
            background: #eee;
            height: 25px;
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        .progress-bar {
            background-color: var(--naranja-galicia);
            height: 100%;
            width: 0%;
            color: white;
            text-align: center;
            line-height: 25px;
            transition: width 0.5s;
        }
        .resultado {
            background: #fdfdfd;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 5px solid var(--naranja-galicia);
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .ok { border-left-color: green; }
        .error { border-left-color: darkorange; }
        @media (max-width: 600px) {
            .form-section {
                flex-direction: column;
                align-items: flex-start;
            }
            input[type=number], button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <header>
        <strong>Bot Galicia N4 - Calificador Automático</strong>
    </header>

    <main>
        <h2>🛠️ Herramienta de calificación de artículos N4</h2>

        <div class="form-section">
            <label>¿Cuántas URLs querés calificar?</label>
            <input type="number" id="cantidad" value="1" min="1" max="20">
            <button onclick="activar()">Activar</button>
        </div>

        <div class="progress-container">
            <div id="progress-bar" class="progress-bar">0%</div>
        </div>

        <div id="resultados"></div>
    </main>

    <script>
        async function activar() {
            const cantidad = parseInt(document.getElementById("cantidad").value);
            const progressBar = document.getElementById("progress-bar");
            const resultadosDiv = document.getElementById("resultados");

            progressBar.style.width = "0%";
            progressBar.innerText = "0%";
            resultadosDiv.innerHTML = "<p>⏳ Calificando " + cantidad + " URLs...</p>";

            let progreso = 0;
            const avanceSimulado = 100 / cantidad;

            const intervalo = setInterval(() => {
                progreso += avanceSimulado;
                progressBar.style.width = Math.min(progreso, 100) + "%";
                progressBar.innerText = Math.round(Math.min(progreso, 100)) + "%";
            }, 500);

            try {
                const response = await fetch(`/activar_json?cantidad=${cantidad}`);
                const data = await response.json();
                clearInterval(intervalo);
                progressBar.style.width = "100%";
                progressBar.innerText = "100%";

                const resultados = data.calificadas || [];
                if (resultados.length === 0) {
                    resultadosDiv.innerHTML = "<p>✅ No hay URLs nuevas para calificar</p>";
                    return;
                }

                let html = "<h3>📋 Resultados:</h3>";
                resultados.forEach(r => {
                    html += `<div class="resultado ${r.resultado.includes('✅') ? 'ok' : 'error'}">
                        <div><strong>URL:</strong> <a href="${r.url}" target="_blank">${r.url}</a></div>
                        <div>${r.resultado} ⏱ ${r.tiempo}s</div>
                    </div>`;
                });
                resultadosDiv.innerHTML = html;
            } catch (err) {
                clearInterval(intervalo);
                progressBar.style.width = "100%";
                progressBar.innerText = "100%";
                resultadosDiv.innerHTML = "<p style='color: red;'>❌ Error al calificar: " + err + "</p>";
            }
        }
    </script>
</body>
</html>"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/activar_json")
def activar_json():
    cantidad = int(request.args.get("cantidad", 1))
    resultado = calificar_urls(cantidad)
    return jsonify(resultado)

@app.route("/status")
def status():
    return get_status()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
