# ============================================================
# FILE CONVERTER API - MAIN SERVER
# ============================================================
#
# This file:
# 1. Creates the FastAPI application
# 2. Loads all converter routes
# 3. Enables CORS so WordPress can call the API
# 4. Cleans old temporary files when the server starts
# 5. Provides / and /api/health
# 6. Fixes the Swagger/OpenAPI file-upload display
#
# IMPORTANT:
# Keep this file inside:
#
# file-converter-website/backend/main.py
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Your application configuration
from config import (
    APP_NAME,
    APP_VERSION,
    FRONTEND_URL,
)


# ============================================================
# 2. ROUTE IMPORTS
# ============================================================
#
# Every converter has its own route file.
# Do not remove a route unless you also remove its converter
# from the website.
# ============================================================

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


# ============================================================
# 3. CLEANUP IMPORTS
# ============================================================

from utils.cleanup import cleanup_old_files
from utils.file_handler import (
    UPLOAD_DIR,
    OUTPUT_DIR,
)


# ============================================================
# 4. STARTUP / LIFESPAN
# ============================================================
#
# When FastAPI starts, old temporary files are removed.
#
# Your converters use temporary upload/output folders.
# This prevents old files from staying around forever.
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:

        cleanup_old_files(
            UPLOAD_DIR,
            OUTPUT_DIR,
        )

    except Exception as error:

        # Do not prevent the API from starting just because
        # an old temporary file could not be cleaned.
        print(
            "Startup cleanup warning:",
            error
        )

    yield


# ============================================================
# 5. CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(

    title=APP_NAME,

    version=APP_VERSION,

    description=(
        "Online file converter and compressor API. "
        "Supports images, PDFs, Word, Excel and PowerPoint."
    ),

    lifespan=lifespan,

)


# ============================================================
# 6. CORS
# ============================================================
#
# THIS IS THE IMPORTANT FIX.
#
# Your frontend may be running from:
#
#   http://127.0.0.1:3002
#   http://127.0.0.1:3000
#   http://localhost
#   http://pdf.local
#
# and eventually from your real WordPress domain.
#
# Since the frontend and Render API are different origins,
# the browser requires CORS permission.
#
# We are not using cookies/session authentication for these
# converter requests, so allow_credentials=False is correct.
#
# Using "*" means your frontend does not have to be added
# manually every time you test from another local port.
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=False,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],

)


# ============================================================
# 7. INCLUDE ALL ROUTES
# ============================================================
#
# These lines connect each route file to the main API.
#
# Example:
#
# routes/jpg_to_pdf.py
#       ↓
# /api/image/to-pdf
# ============================================================


# ------------------------------------------------------------
# PDF routes
# ------------------------------------------------------------

app.include_router(
    pdf.router
)


# ------------------------------------------------------------
# Image routes
# ------------------------------------------------------------

app.include_router(
    image.router
)


# ------------------------------------------------------------
# JPG → PDF
# ------------------------------------------------------------

app.include_router(
    jpg_to_pdf.router
)


# ------------------------------------------------------------
# Word → PDF
# ------------------------------------------------------------

app.include_router(
    word.router
)


# ------------------------------------------------------------
# Excel → PDF
# ------------------------------------------------------------

app.include_router(
    excel.router
)


# ------------------------------------------------------------
# PowerPoint → PDF
# ------------------------------------------------------------

app.include_router(
    ppt.router
)


# ------------------------------------------------------------
# PDF → PowerPoint
# ------------------------------------------------------------

app.include_router(
    pdf_to_ppt.router
)


# ------------------------------------------------------------
# PDF → Word
# ------------------------------------------------------------

app.include_router(
    pdf_to_word.router
)


# ------------------------------------------------------------
# PDF → Excel
# ------------------------------------------------------------

app.include_router(
    pdf_to_excel.router
)


# ------------------------------------------------------------
# PDF → Text
# ------------------------------------------------------------

app.include_router(
    pdf_text.router
)


# ------------------------------------------------------------
# GIF → JPG
# ------------------------------------------------------------

app.include_router(
    gif_to_jpg.router
)


# ------------------------------------------------------------
# JPG → GIF
# ------------------------------------------------------------

app.include_router(
    jpg_to_gif.router
)


# ------------------------------------------------------------
# WEBP → JPG
# ------------------------------------------------------------

app.include_router(
    webp_to_jpg.router
)


# ------------------------------------------------------------
# PNG → JPG
# ------------------------------------------------------------

app.include_router(
    png_to_jpg.router
)


# ------------------------------------------------------------
# JPG → WEBP
# ------------------------------------------------------------

app.include_router(
    jpg_to_webp.router
)


# ------------------------------------------------------------
# IMAGE COMPRESSOR
# ------------------------------------------------------------

app.include_router(
    image_compressor.router
)


# ------------------------------------------------------------
# PDF COMPRESSOR
# ------------------------------------------------------------

app.include_router(
    pdf_compressor.router
)


# ============================================================
# 8. HOME ROUTE
# ============================================================
#
# Opening:
#
# https://your-render-domain.onrender.com/
#
# will show a simple status message.
# ============================================================

@app.get("/")
def home():

    return {

        "message":
            "File Converter API is running",

        "version":
            APP_VERSION,

        "status":
            "online",

    }


# ============================================================
# 9. HEALTH CHECK
# ============================================================
#
# Used for testing:
#
# /api/health
#
# Expected response:
#
# {
#   "status": "ok",
#   "message": "Backend is healthy"
# }
# ============================================================

@app.get("/api/health")
def health():

    return {

        "status":
            "ok",

        "message":
            "Backend is healthy",

        "version":
            APP_VERSION,

    }


# ============================================================
# 10. CUSTOM OPENAPI
# ============================================================
#
# FastAPI's newer OpenAPI schema can sometimes describe
# uploaded files using contentMediaType instead of the
# classic binary format.
#
# This function changes those schemas to:
#
#     format: binary
#
# so the Swagger UI file picker behaves correctly.
# ============================================================

def custom_openapi():

    # Return cached schema if it already exists.
    if app.openapi_schema:

        return app.openapi_schema


    # Generate normal OpenAPI schema first.
    openapi_schema = get_openapi(

        title=APP_NAME,

        version=APP_VERSION,

        description=(
            "File Converter API"
        ),

        routes=app.routes,

    )


    # --------------------------------------------------------
    # Recursive schema fixer
    # --------------------------------------------------------

    def fix_schema(schema):

        if not isinstance(
            schema,
            dict
        ):

            return


        # ----------------------------------------------------
        # Fix FastAPI upload schema
        # ----------------------------------------------------

        if (

            schema.get(
                "type"
            ) == "string"

            and schema.get(
                "contentMediaType"
            )

        ):

            schema[
                "format"
            ] = "binary"


            schema.pop(
                "contentMediaType",
                None
            )


            schema.pop(
                "contentSchema",
                None
            )


        # ----------------------------------------------------
        # Search every nested value
        # ----------------------------------------------------

        for value in list(
            schema.values()
        ):

            # Nested dictionary
            if isinstance(
                value,
                dict
            ):

                fix_schema(
                    value
                )


            # Nested list
            elif isinstance(
                value,
                list
            ):

                for item in value:

                    if isinstance(
                        item,
                        dict
                    ):

                        fix_schema(
                            item
                        )


    # Fix the entire OpenAPI document.
    fix_schema(
        openapi_schema
    )


    # Cache it.
    app.openapi_schema = (
        openapi_schema
    )


    return openapi_schema


# ============================================================
# 11. TELL FASTAPI TO USE OUR CUSTOM OPENAPI
# ============================================================

app.openapi = custom_openapi
