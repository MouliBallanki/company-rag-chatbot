from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
 
app = FastAPI(title="RAG Pipeline API")
 
# Allow your Streamlit frontend to make API calls

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],  # In production, specify your exact UI URL

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)
 
# Include the routes you created

app.include_router(router)
 
if __name__ == "__main__":

    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
 