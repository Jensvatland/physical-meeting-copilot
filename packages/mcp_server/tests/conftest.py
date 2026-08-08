import os

# Avoid writing test sessions into the developer's real meetings DB.
os.environ["MEETING_CORE_DB"] = ":memory:"
