import logging
import json
import io

logger = logging.getLogger(__name__)

BUCKET_NAME = "caredesk-files"


def upload_file(app, file_content, file_name, folder="general"):
    """Upload a file to Catalyst Stratus (Cloud Scale / File Store)."""
    try:
        file_store = app.filestore()
        folder_obj = file_store.folder(BUCKET_NAME)
        uploaded = folder_obj.upload_file(file_name, io.BytesIO(file_content))
        file_id = uploaded.get("id", "")
        logger.info(f"File uploaded to Stratus: {file_name} (ID: {file_id})")
        return file_id
    except Exception as e:
        logger.error(f"Stratus upload failed: {e}")
        return None


def get_file_download_url(app, file_id):
    """Get a download URL for a file stored in Stratus."""
    try:
        file_store = app.filestore()
        folder_obj = file_store.folder(BUCKET_NAME)
        file_obj = folder_obj.file(file_id)
        return file_obj.get_download_url()
    except Exception as e:
        logger.error(f"Stratus get URL failed: {e}")
        return None


def upload_clinic_logo(app, file_content, clinic_id, file_name):
    """Upload clinic logo to Stratus."""
    logo_name = f"logo_{clinic_id}_{file_name}"
    return upload_file(app, file_content, logo_name, folder="logos")


def upload_prescription_pdf(app, pdf_content, prescription_id):
    """Upload a prescription PDF to Stratus."""
    pdf_name = f"prescription_{prescription_id}.pdf"
    return upload_file(app, pdf_content, pdf_name, folder="prescriptions")
