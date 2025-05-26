from tos.db import DB
from tos.html_dump_processor import HTMLDumpProcessor
from tos.utils import BASE_PATH

db = DB()

processor = HTMLDumpProcessor(str(BASE_PATH / "sampledata/APR_Guide.zip"))
count = 0

for chunk in processor.start():
    db.add_document(chunk)
    count += 1

print(f"Total Count: {count}")
