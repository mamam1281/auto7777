# Import individual router modules to make them accessible
from . import auth
from . import games
from . import segments
from . import chat
from . import feedback
from . import ai
from . import analyze
from . import recommend

# Optional: define __all__ list for controlled imports
__all__ = ["auth", "games", "segments", "chat", "feedback", "ai", "analyze", "recommend"]
