"""Validated image and document storage for the FARM BRAIN prototype."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image, UnidentifiedImageError
import io

IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp"}
DOCUMENT_MIMES = {"application/pdf"}
MAX_IMAGE_BYTES = 6 * 1024 * 1024
MAX_DOCUMENT_BYTES = 8 * 1024 * 1024


class UploadError(ValueError):
    pass


def _safe_original_name(name: str) -> str:
    base = secure_filename(name or "attachment")[:150]
    return base or "attachment"


def save_image(file_storage, area: str = "community") -> tuple[str, str, int, str]:
    if not file_storage or not file_storage.filename:
        raise UploadError("Choose an image to upload.")
    raw = file_storage.stream.read(MAX_IMAGE_BYTES + 1)
    if not raw or len(raw) > MAX_IMAGE_BYTES:
        raise UploadError("Images must be smaller than 6 MB.")
    try:
        with Image.open(io.BytesIO(raw)) as image:
            if image.format not in {"JPEG", "PNG", "WEBP"}:
                raise UploadError("Use a JPG, PNG or WEBP image.")
            image.verify()
        with Image.open(io.BytesIO(raw)) as image:
            image = image.convert("RGB")
            image.thumbnail((2400, 2400))
            out = io.BytesIO()
            image.save(out, format="JPEG", quality=86, optimize=True)
            cleaned = out.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise UploadError("That image could not be processed. Please choose another image.")

    cloud_values = [current_app.config.get("CLOUDINARY_CLOUD_NAME"),
                    current_app.config.get("CLOUDINARY_API_KEY"),
                    current_app.config.get("CLOUDINARY_API_SECRET")]
    if all(cloud_values):
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=cloud_values[0], api_key=cloud_values[1],
                api_secret=cloud_values[2], secure=True,
            )
            result = cloudinary.uploader.upload(
                io.BytesIO(cleaned), folder=f"farmbrain/{area}",
                resource_type="image", unique_filename=True, overwrite=False,
            )
            return result["secure_url"], _safe_original_name(file_storage.filename), len(cleaned), "image/jpeg"
        except Exception as exc:
            current_app.logger.exception("Cloudinary public image upload failed")
            raise UploadError("Image storage is temporarily unavailable. Please try again.") from exc

    filename = f"{uuid4().hex}.jpg"
    relative = f"public/{area}/{filename}"
    destination = Path(current_app.config["UPLOAD_FOLDER"]) / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(cleaned)
    return relative, _safe_original_name(file_storage.filename), len(cleaned), "image/jpeg"


def save_private_attachment(file_storage) -> tuple[str, str, int, str]:
    """Store a private PDF or image for a message; only participants can fetch it."""
    if not file_storage or not file_storage.filename:
        raise UploadError("Choose a file to attach.")
    original = _safe_original_name(file_storage.filename)
    suffix = Path(original).suffix.lower()
    raw = file_storage.stream.read(MAX_DOCUMENT_BYTES + 1)
    if not raw or len(raw) > MAX_DOCUMENT_BYTES:
        raise UploadError("Attachments must be smaller than 8 MB.")
    if suffix == ".pdf" and raw.startswith(b"%PDF-"):
        filename = f"{uuid4().hex}.pdf"
        relative = f"private/{filename}"
        mime = "application/pdf"
        cleaned = raw
    elif suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        try:
            with Image.open(io.BytesIO(raw)) as image:
                if image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise UploadError("Use a JPG, PNG, WEBP image or PDF document.")
                image.verify()
            with Image.open(io.BytesIO(raw)) as image:
                image = image.convert("RGB")
                image.thumbnail((2400, 2400))
                out = io.BytesIO()
                image.save(out, format="JPEG", quality=86, optimize=True)
                cleaned = out.getvalue()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
            raise UploadError("That image could not be processed.")
        filename = f"{uuid4().hex}.jpg"
        relative = f"private/{filename}"
        mime = "image/jpeg"
    else:
        raise UploadError("Attach a PDF or JPG, PNG or WEBP image.")

    destination = Path(current_app.config["UPLOAD_FOLDER"]) / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(cleaned)
    return relative, original, len(cleaned), mime
