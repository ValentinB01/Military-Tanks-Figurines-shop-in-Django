from django.contrib.sitemaps import Sitemap
from django.urls import reverse 

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'
    
    def items(self):
        return ['index', 'despre', 'produse', 'contact', 'cos_virtual',
                'shipping_returns', 'privacy_policy', 'terms_conditions',
                'adauga_produs', 'register', 'login', 'logout', 'profile',
                'change_password', 'promotii', 'interzis', 'accesare_oferta', 'oferta']
        
    def location(self, item):
        return reverse(item)