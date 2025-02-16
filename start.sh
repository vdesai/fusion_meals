#!/bin/bash
# Run FastAPI in the background
uvicorn app:app --host 0.0.0.0 --port 8000 &

# Run Streamlit
streamlit run ui.py --server.port=$PORT --server.address=0.0.0.0
