from .auth import auth
from .home import home
from .users import users
from .messages import messages
from .mailbox import mailbox
from .calendar import calendar

blueprints = [home, auth, users, messages, mailbox, calendar]
