import os
import uuid
import zipfile
from pathlib import Path
from typing import Any, Generator

from bs4 import BeautifulSoup

from tos.chunk import Chunk
from tos.utils import BASE_PATH

ZIP_PATH = BASE_PATH / "sampledata/docs.zip"


class HTMLDumpProcessor:
    """
    HTMLDumpProcessor is responsible for extracting and processing a ZIP archive containing HTML files.

    The processor performs the following tasks:
    1. Extracts a ZIP file into a structured directory.
    2. Scans for valid `.html` files (ignoring macOS metadata files).
    3. Parses each HTML file and converts its contents to plain text.
    4. Yields each HTML page as a single chunk along with metadata.

    Attributes:
        `zip_path` str: The path to the ZIP file containing HTML documents.

    Methods:
        `start()` -> Generator[dict[str, Any], Any, None]:
            Starts the pipeline. Extracts the ZIP archive and yields parsed HTML chunks as dictionaries.

    Chunk Format:
        ```python
        {
            "id": "<unique UUID string>",
            "text": "<extracted plain text>",
            "meta": {
                "source": "<original file path as Path object>"
            }
        }
        ```

    Usage Example:
        ```python
        from pathlib import Path

        processor = HTMLDumpProcessor("sampledata/docs.zip")

        for chunk in processor.start():
            print(chunk["id"], chunk["meta"]["source"])
        ```
    """

    def __init__(self, zip_path: str) -> None:
        self.__zip_path = Path(zip_path)
        self.__extract_dir = BASE_PATH / "extracted_html_dump"

    def __extract_dump(self) -> None:
        os.makedirs(self.__extract_dir, exist_ok=True)
        with zipfile.ZipFile(self.__zip_path, "r") as z_ref:
            z_ref.extractall(self.__extract_dir)
        print("👋🏻 - Extracted HTML dump")

    def __html_to_text(self, file_path: Path) -> str | None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Failed to decode {file_path}: {e}")
            return None

        soup = BeautifulSoup(content, "html.parser")

        return soup.get_text(separator=" ").strip()

    def __extract_chunk(self) -> Generator[Chunk, Any, None]:
        def is_valid_file(file: str) -> bool:
            ext = os.path.splitext(file)[-1].lower()
            return ext == ".html" and not file.startswith("._")

        for root, _, files in os.walk(self.__extract_dir):
            for file in files:
                if is_valid_file(file):
                    file_path = Path(root) / file
                    # extract one page at a time so no need for chunk overlap
                    extracted_text = self.__html_to_text(file_path)
                    if extracted_text:
                        yield Chunk(
                            id=str(uuid.uuid4()),
                            text=extracted_text,
                            meta={"source": str(file_path)},
                        )

        print("✅ - Finished processing HTML dump")

    def start(self) -> Generator[Chunk, Any, None]:
        print("🤖 - Starting to process html dump")
        self.__extract_dump()
        return self.__extract_chunk()
