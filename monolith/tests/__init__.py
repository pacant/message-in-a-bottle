from monolith.app import app as tested_app

sender = 'prova_003@example.it'
recipient = 'prove_004@example.it'

def register(client, email, firstname, lastname, password, dateofbirth):
    return client.post("/create_user",
                       data=dict(
                           email=email,
                           firstname=firstname,
                           lastname=lastname,
                           password=password,
                           dateofbirth=dateofbirth
                       ),
                       follow_redirects=True)


def login(client, email, password):
    return client.post("/login",
                       data=dict(
                           email=email,
                           password=password
                       ),
                       follow_redirects=True)

tested_app.config['WTF_CSRF_ENABLED'] = False
app = tested_app.test_client()

register(app, sender, "Prova", "Example", "1234", "01/01/2001")
register(app, recipient, "Prova", "Example", "1234", "01/01/2001")
login(app, sender, "1234")