from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from config import APP_NAME, APP_VERSION, FRONTEND_URL

from routes import pdf
from routes import image
from routes import jpg_to_pdf
from routes import word
from routes import excel
from routes import ppt
from routes import pdf_to_ppt
from routes import pdf_to_word
from routes import pdf_to_excel
from routes import pdf_text
from routes import gif_to_jpg
from routes import jpg_to_gif
from routes import webp_to_jpg
from routes import png_to_jpg
from routes import jpg_to_webp
from routes import image_compressor
from routes import pdf_compressor

from utils.cleanup import cleanup_old_files
from utils.file_handler import UPLOAD_DIR, OUTPUT_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Delete old temporary files when the server starts
    cleanup_old_files(UPLOAD_DIR, OUTPUT_DIR)

    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)


# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- ROUTES ----------------

app.include_router(pdf.router)
app.include_router(image.router)
app.include_router(jpg_to_pdf.router)
app.include_router(word.router)
app.include_router(excel.router)
app.include_router(ppt.router)
app.include_router(pdf_to_ppt.router)
app.include_router(pdf_to_word.router)
app.include_router(pdf_to_excel.router)
app.include_router(pdf_text.router)
app.include_router(gif_to_jpg.router)
app.include_router(jpg_to_gif.router)
app.include_router(webp_to_jpg.router)
app.include_router(png_to_jpg.router)
app.include_router(jpg_to_webp.router)
app.include_router(image_compressor.router)
app.include_router(pdf_compressor.router)


# ---------------- HOME ----------------

@app.get("/")
def home():
    return {
        "message": "File Converter API is running",
        "version": APP_VERSION,
    }


# ---------------- HEALTH CHECK ----------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "message": "Backend is healthy",
    }


# ---------------- SWAGGER FILE UPLOAD FIX ----------------

def custom_openapi():
    """
    Make Swagger UI recognize uploaded files correctly.
    """

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=APP_NAME,
        version=APP_VERSION,
        description="File Converter API",
        routes=app.routes,
    )

    def fix_schema(schema):
        if isinstance(schema, dict):

            # Fix a single uploaded file
            if (
                schema.get("type") == "string"
                and schema.get("contentMediaType")
            ):
                schema["format"] = "binary"
                schema.pop("contentMediaType", None)
                schema.pop("contentSchema", None)

            # Fix arrays of uploaded files
            for key, value in list(schema.items()):

                if isinstance(value, dict):
                    fix_schema(value)

                elif isinstance(value, list):

                    for item in value:
                        fix_schema(item)

    fix_schema(openapi_schema)

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi