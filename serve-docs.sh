#!/bin/bash
# Serve API documentation locally

PORT=${1:-8080}

echo "🚀 Starting documentation server on port $PORT..."
echo ""
echo "📖 Available documentation:"
echo "   Swagger UI: http://localhost:$PORT/docs/"
echo "   ReDoc:      http://localhost:$PORT/docs/redoc.html"
echo "   API Spec:   http://localhost:$PORT/openapi.yaml"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m http.server $PORT
else
    echo "❌ Python not found. Please install Python 3 to serve documentation."
    echo ""
    echo "Alternative: Install Node.js and run:"
    echo "   npx http-server -p $PORT"
    exit 1
fi
