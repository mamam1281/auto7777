
# This file makes models a package and imports from the main models.py file
# We're using models.py as the single source of truth for all models
pass
from app.models.adult_content import AdultContent
from app.models.vip_access_log import VIPAccessLog
from app.database import Base

