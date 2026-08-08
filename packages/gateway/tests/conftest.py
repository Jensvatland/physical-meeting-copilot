import os

# Must be set before meeting_gateway.app is imported by test modules.
os.environ["MEETING_CORE_DB"] = ":memory:"
