# Run Commands

## Local Development

**Backend**
```
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Agent**
```
cd agent
venv\Scripts\activate
uvicorn main:app --reload --port 8001
```

**Frontend**
```
cd frontend
venv\Scripts\activate
streamlit run app.py
```

---

## Production

**Backend**
```
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Agent**
```
cd agent
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

**Frontend**
```
cd frontend
venv\Scripts\activate
streamlit run app.py --server.address 0.0.0.0
```