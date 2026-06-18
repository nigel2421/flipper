#!/usr/bin/env python
"""Minimal Cloud Run WSGI app that bypasses Django settings issues"""
import os
import sys

# Set minimal Django configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
os.environ['PORT'] = os.environ.get('PORT', '8080')

def simple_app(environ, start_response):
    """Ultra-simple WSGI app for health checks"""
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b'OK']

if __name__ == '__main__':
    from gunicorn.app.base import BaseApplication
    
    class SimpleApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.application = app
            self.options = options or {}
            super().__init__()
            
        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key.lower(), value)
                
        def load(self):
            return self.application
    
    options = {
        'bind': f'0.0.0.0:{os.environ.get("PORT", 8080)}',
        'workers': 1,
        'timeout': 90,
        'accesslog': '-',
        'errorlog': '-',
        'loglevel': 'debug',
    }
    
    print(f"Starting simple health check app on port {os.environ.get('PORT', 8080)}")
    app = SimpleApplication(simple_app, options)
    app.run()
