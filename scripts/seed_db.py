from tos.db import DB
from tos.html_dump_processor import HTMLDumpProcessor

db = DB()

processor = HTMLDumpProcessor("sampledata/docs.zip")

for chunk in processor.start():
    db.add_document(chunk)
