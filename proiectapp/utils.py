import datetime
from urllib.parse import urlparse, parse_qs

class Accesare:
    id_counter = 1
    
    def __init__(self, ip_client=None, url=None, data=None):
        self.id = Accesare.id_counter
        Accesare.id_counter += 1
        
        self.ip_client = ip_client
        self.url_complet = url
        self.data_acces = data or datetime.datetime.now()
        
    def lista_parametri(self):
        return [
            ("id", self.id),
            ("ip_client", self.ip_client if self.ip_client else None),
            ("url", self.url_complet if self.url_complet else None),
            ("data", self.data_acces if self.data_acces else None)
        ]

    def url(self):
        return self.url_complet

    def data(self, fmt=None):
        if fmt:
            return self.data_acces.strftime(fmt)
        return self.data_acces

    def pagina(self):
        if not self.url_complet:
            return None
        parsed = urlparse(self.url_complet)
        return parsed.path