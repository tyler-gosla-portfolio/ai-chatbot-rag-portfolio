from pathlib import Path
from io import BytesIO
from pypdf import PdfReader


def extract_text(filename: str, raw: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        reader = PdfReader(BytesIO(raw))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return raw.decode("utf-8", errors="ignore")


def ensure_upload_path(base_dir: str, filename: str) -> Path:
    path = Path(base_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path / filename
