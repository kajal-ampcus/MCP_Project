from .mcp_server import mcp

from .tools import datetime
from .tools import calendar
from .tools import weather
from .tools import email
from .tools import notetaker
from .tools import meeting
from .tools import test_calendar

if __name__ == "__main__":
    
    mcp.run(transport="streamable-http")
