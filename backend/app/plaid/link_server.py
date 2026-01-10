"""Simple HTTP server for Plaid Link integration"""

import http.server
import socketserver
import urllib.parse
import json
import threading
from typing import Optional, Callable


class PlaidLinkHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for Plaid Link"""
    
    def __init__(self, *args, link_token: str, on_success: Callable, **kwargs):
        self.link_token = link_token
        self.on_success = on_success
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve the Plaid Link HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self._get_plaid_link_html()
            self.wfile.write(html.encode())
        
        elif parsed_path.path == '/success':
            # Handle successful connection
            query_params = urllib.parse.parse_qs(parsed_path.query)
            public_token = query_params.get('public_token', [None])[0]
            
            if public_token:
                try:
                    access_token, item_id = self.on_success(public_token)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    success_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Connection Successful</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                max-width: 600px;
                                margin: 50px auto;
                                padding: 20px;
                                background: #f5f5f5;
                            }}
                            .success {{
                                background: white;
                                padding: 30px;
                                border-radius: 8px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            }}
                            h1 {{
                                color: #4CAF50;
                                margin-top: 0;
                            }}
                            .token {{
                                background: #f9f9f9;
                                padding: 15px;
                                border-radius: 4px;
                                font-family: monospace;
                                word-break: break-all;
                                margin: 10px 0;
                            }}
                            .info {{
                                color: #666;
                                font-size: 14px;
                                margin-top: 20px;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="success">
                            <h1>✓ Bank Account Connected Successfully!</h1>
                            <p>Your access token has been saved. You can close this window.</p>
                            <div class="info">
                                <strong>Access Token:</strong>
                                <div class="token">{access_token}</div>
                                <strong>Item ID:</strong>
                                <div class="token">{item_id}</div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(success_html.encode())
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    error_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>Error</title></head>
                    <body>
                        <h1>Error</h1>
                        <p>Failed to exchange token: {str(e)}</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(error_html.encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Missing public_token')
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def _get_plaid_link_html(self) -> str:
        """Generate HTML page with Plaid Link"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Connect Bank Account</title>
    <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin-top: 0;
            color: #333;
        }}
        #plaid-link-button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 20px;
        }}
        #plaid-link-button:hover {{
            background: #45a049;
        }}
        .info {{
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Connect Your Bank Account</h1>
        <p>Click the button below to securely connect your bank account using Plaid.</p>
        <button id="plaid-link-button">Connect Bank Account</button>
        <div class="info">
            <p>This will open Plaid's secure connection interface. Your credentials are never shared with us.</p>
        </div>
    </div>

    <script>
        const linkToken = '{self.link_token}';
        
        const handler = Plaid.create({{
            token: linkToken,
            onSuccess: function(public_token, metadata) {{
                console.log('Success! Public token:', public_token);
                // Redirect to success page with public token
                window.location.href = '/success?public_token=' + public_token;
            }},
            onExit: function(err, metadata) {{
                if (err) {{
                    console.error('Error:', err);
                    alert('Connection failed: ' + err.error_message);
                }} else {{
                    console.log('User exited without connecting');
                }}
            }},
            onEvent: function(eventName, metadata) {{
                console.log('Event:', eventName, metadata);
            }}
        }});

        document.getElementById('plaid-link-button').addEventListener('click', function(e) {{
            e.preventDefault();
            handler.open();
        }});
    </script>
</body>
</html>
        """


def start_link_server(link_token: str, on_success: Callable, port: int = 8080) -> tuple[socketserver.TCPServer, threading.Thread]:
    """
    Start a local HTTP server for Plaid Link
    
    Args:
        link_token: Plaid link token
        on_success: Callback function that takes public_token and returns (access_token, item_id)
        port: Port to run server on
        
    Returns:
        Tuple of (server, thread)
    """
    # Create a handler class with the link_token and callback bound
    class Handler(PlaidLinkHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, link_token=link_token, on_success=on_success, **kwargs)
    
    server = socketserver.TCPServer(("", port), Handler)
    server.allow_reuse_address = True
    
    def run_server():
        server.serve_forever()
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    
    return server, thread
