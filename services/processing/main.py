from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI()

@app.post("/process/")
async def process_data(data: dict):
    try:
        df = pd.DataFrame(data["data"])
        # Estandarización y procesamiento de datos aquí
        # Por ejemplo, asegurarse de que los datos estén en el mismo formato
        processed_data = df.to_dict()
        return {"status": "success", "data": processed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
