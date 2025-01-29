import os
import sys
import time
import socket
import psycopg2

def resolve_hostname(hostname):
    """Resolve hostname to IP address."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        print(f"Could not resolve hostname: {hostname}")
        return None

def is_port_open(host, port):
    """Check if a port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error checking port: {e}")
        return False

def test_postgres_connection():
    """Attempt to connect to PostgreSQL using psycopg2."""
    try:
        conn_params = {
            'dbname': os.environ.get('PGDATABASE', 'aibf_db'),
            'user': os.environ.get('PGUSER', 'root'),
            'password': os.environ.get('PGPASSWORD', 'pass'),
            'host': os.environ.get('PGHOST', 'db'),
            'port': os.environ.get('PGPORT', '5434')
        }
        
        print("Connection parameters:")
        for key, value in conn_params.items():
            print(f"{key}: {value}")
        
        conn = psycopg2.connect(**conn_params)
        conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL connection error: {e}")
        return False

def wait_for_postgres(max_attempts=30, delay=2):
    """Wait for PostgreSQL to be ready."""
    host = os.environ.get('PGHOST', 'db')
    port = os.environ.get('PGPORT', '5434')
    
    print(f"Attempting to connect to PostgreSQL at {host}:{port}")
    
    # First, try to resolve the hostname
    resolved_host = resolve_hostname(host)
    if not resolved_host:
        print(f"Failed to resolve hostname: {host}")
        sys.exit(1)
    
    # Then check port connectivity and PostgreSQL connection
    attempts = 0
    while attempts < max_attempts:
        if is_port_open(resolved_host, port):
            print(f"Port {port} is open on {resolved_host}")
            
            # Try to establish a PostgreSQL connection
            if test_postgres_connection():
                print(f"PostgreSQL is ready on {resolved_host}:{port}!")
                return
        
        print(f"Waiting for PostgreSQL... (Attempt {attempts + 1}/{max_attempts})")
        time.sleep(delay)
        attempts += 1
    
    print(f"PostgreSQL is not ready after maximum attempts. Host: {resolved_host}, Port: {port}")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_postgres()
