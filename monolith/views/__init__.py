from .auth import auth
from .home import home
from .users import users
from .messages import messages
from .mailbox import mailbox

blueprints = [home, auth, users, messages, mailbox]
