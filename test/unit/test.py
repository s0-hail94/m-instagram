from test.unit.webapp import client


def test_home_content(client):
    '''Test if important phrases are present in HTML'''
    landing = client.get("/")
    html = landing.data.decode()
    assert " <a href=\"/register/\">login</a>" in html
    assert landing.status_code == 200


def test_landing_aliases(client):
    '''Test if data loads currectley in different home alias'''
    landing = client.get("/")
    assert client.get("/index/").data == landing.data

def test_login(client):
    '''Test if login works fine'''
    pass