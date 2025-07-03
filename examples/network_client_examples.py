# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Network Client Usage Examples

This file demonstrates various usage patterns for the NetworkClient,
which provides HTTP/HTTPS communication for web APIs and REST services.
"""

import time
import json
from vta.api.factory import APIFactory
from vta.api.base import ClientConfig


def basic_http_operations():
    """Basic HTTP operations example."""
    print("=== Basic HTTP Operations ===")
    
    # Create network client for REST API
    api_client = APIFactory.create_network_client(
        base_url="https://httpbin.org"  # Public testing API
    )
    
    try:
        # Connect to service
        print("Connecting to HTTP service...")
        api_client.connect()
        
        if api_client.is_connected():
            print("✓ HTTP service connected successfully")
        
        # GET request
        print("\n--- GET Request ---")
        response = api_client.get("/get", params={"param1": "value1", "param2": "value2"})
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Query Args: {data.get('args', {})}")
            print(f"Headers: {data.get('headers', {})}")
        
        # POST request
        print("\n--- POST Request ---")
        payload = {
            "name": "VTA Test",
            "version": "1.0",
            "timestamp": time.time()
        }
        
        response = api_client.post("/post", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Posted Data: {data.get('json', {})}")
        
        # PUT request
        print("\n--- PUT Request ---")
        update_data = {"status": "updated", "timestamp": time.time()}
        response = api_client.put("/put", json=update_data)
        print(f"PUT Status Code: {response.status_code}")
        
        # DELETE request
        print("\n--- DELETE Request ---")
        response = api_client.delete("/delete")
        print(f"DELETE Status Code: {response.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        api_client.disconnect()


def rest_api_example():
    """REST API interaction example."""
    print("\n=== REST API Example ===")
    
    # Create client for JSONPlaceholder API (public testing API)
    rest_client = APIFactory.create_network_client(
        base_url="https://jsonplaceholder.typicode.com"
    )
    
    try:
        rest_client.connect()
        
        # Get all posts
        print("--- Getting Posts ---")
        response = rest_client.get("/posts")
        
        if response.status_code == 200:
            posts = response.json()
            print(f"Retrieved {len(posts)} posts")
            
            # Show first 3 posts
            for post in posts[:3]:
                print(f"  Post {post['id']}: {post['title'][:50]}...")
        
        # Get specific post
        print("\n--- Getting Specific Post ---")
        post_id = 1
        response = rest_client.get(f"/posts/{post_id}")
        
        if response.status_code == 200:
            post = response.json()
            print(f"Post {post['id']}: {post['title']}")
            print(f"Body: {post['body'][:100]}...")
        
        # Create new post
        print("\n--- Creating New Post ---")
        new_post = {
            "title": "VTA Test Post",
            "body": "This is a test post created by VTA Network Client",
            "userId": 1
        }
        
        response = rest_client.post("/posts", json=new_post)
        
        if response.status_code == 201:
            created_post = response.json()
            print(f"Created post with ID: {created_post['id']}")
            print(f"Title: {created_post['title']}")
        
        # Update post
        print("\n--- Updating Post ---")
        updated_post = {
            "id": 1,
            "title": "Updated VTA Test Post",
            "body": "This post has been updated",
            "userId": 1
        }
        
        response = rest_client.put("/posts/1", json=updated_post)
        
        if response.status_code == 200:
            updated = response.json()
            print(f"Updated post: {updated['title']}")
        
        # Delete post
        print("\n--- Deleting Post ---")
        response = rest_client.delete("/posts/1")
        print(f"Delete status: {response.status_code}")
        
        # Get users
        print("\n--- Getting Users ---")
        response = rest_client.get("/users")
        
        if response.status_code == 200:
            users = response.json()
            print(f"Retrieved {len(users)} users")
            for user in users[:3]:
                print(f"  User {user['id']}: {user['name']} ({user['email']})")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        rest_client.disconnect()


def file_upload_download_example():
    """File upload and download example."""
    print("\n=== File Upload/Download Example ===")
    
    # Create client for file operations
    file_client = APIFactory.create_network_client(
        base_url="https://httpbin.org"
    )
    
    try:
        file_client.connect()
        
        # Create test file
        test_file = "test_upload.txt"
        test_content = "This is a test file for VTA Network Client upload."
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Upload file
        print("--- File Upload ---")
        with open(test_file, 'rb') as f:
            files = {'file': ('test_upload.txt', f, 'text/plain')}
            response = file_client.post("/post", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ File uploaded successfully")
            print(f"Files: {data.get('files', {})}")
        
        # Download file (simulate with GET request)
        print("\n--- File Download ---")
        response = file_client.get("/bytes/1024")  # Download 1KB of random data
        
        if response.status_code == 200:
            downloaded_file = "downloaded_data.bin"
            with open(downloaded_file, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded {len(response.content)} bytes to {downloaded_file}")
        
        # Cleanup
        import os
        try:
            os.remove(test_file)
            os.remove(downloaded_file)
        except Exception:
            pass
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        file_client.disconnect()


def authentication_example():
    """Authentication and headers example."""
    print("\n=== Authentication Example ===")
    
    # Create client with authentication
    config = ClientConfig(
        timeout=30.0,
        extra_config={
            "base_url": "https://httpbin.org",
            "default_headers": {
                "Authorization": "Bearer your-token-here",
                "User-Agent": "VTA-Network-Client/1.0",
                "Content-Type": "application/json"
            }
        }
    )
    
    auth_client = APIFactory.create_client(APIFactory.ClientType.NETWORK_CLIENT, config)
    
    try:
        auth_client.connect()
        
        # Request with authentication
        print("--- Authenticated Request ---")
        response = auth_client.get("/bearer", 
                                  headers={"Authorization": "Bearer test-token"})
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Authentication successful")
            print(f"Token: {data.get('token')}")
            print(f"Authenticated: {data.get('authenticated')}")
        
        # Basic authentication
        print("\n--- Basic Authentication ---")
        response = auth_client.get("/basic-auth/user/passwd", 
                                  auth=("user", "passwd"))
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Basic auth successful")
            print(f"User: {data.get('user')}")
            print(f"Authenticated: {data.get('authenticated')}")
        
        # Custom headers
        print("\n--- Custom Headers ---")
        custom_headers = {
            "X-Custom-Header": "VTA-Test-Value",
            "X-Request-ID": "12345",
            "X-Timestamp": str(int(time.time()))
        }
        
        response = auth_client.get("/headers", headers=custom_headers)
        
        if response.status_code == 200:
            data = response.json()
            received_headers = data.get('headers', {})
            print("✓ Custom headers sent")
            for header, value in custom_headers.items():
                if header in received_headers:
                    print(f"  {header}: {received_headers[header]}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        auth_client.disconnect()


def streaming_example():
    """Streaming and chunked data example."""
    print("\n=== Streaming Example ===")
    
    stream_client = APIFactory.create_network_client(
        base_url="https://httpbin.org"
    )
    
    try:
        stream_client.connect()
        
        # Stream large response
        print("--- Streaming Response ---")
        response = stream_client.get("/stream/10", stream=True)  # Stream 10 lines
        
        if response.status_code == 200:
            print("✓ Streaming response:")
            line_count = 0
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    print(f"  Line {line_count + 1}: {data.get('url')}")
                    line_count += 1
                    if line_count >= 5:  # Limit output
                        break
        
        # Chunked encoding
        print("\n--- Chunked Encoding ---")
        response = stream_client.get("/drip", 
                                   params={"numbytes": 100, "duration": 2})
        
        if response.status_code == 200:
            print(f"✓ Received chunked data: {len(response.content)} bytes")
        
        # Large file simulation
        print("\n--- Large File Download ---")
        response = stream_client.get("/bytes/10240", stream=True)  # 10KB
        
        if response.status_code == 200:
            total_size = 0
            chunk_count = 0
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    total_size += len(chunk)
                    chunk_count += 1
                    if chunk_count <= 3:  # Show first 3 chunks
                        print(f"  Chunk {chunk_count}: {len(chunk)} bytes")
            
            print(f"✓ Downloaded {total_size} bytes in {chunk_count} chunks")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        stream_client.disconnect()


def advanced_networking_example():
    """Advanced networking features example."""
    print("\n=== Advanced Networking Example ===")
    
    # Create client with advanced configuration
    config = ClientConfig(
        timeout=60.0,
        retry_count=3,
        retry_delay=2.0,
        connection_pool_size=10,
        extra_config={
            "base_url": "https://httpbin.org",
            "verify_ssl": True,
            "allow_redirects": True,
            "max_redirects": 5,
            "default_headers": {
                "User-Agent": "VTA-Advanced-Client/1.0"
            }
        }
    )
    
    advanced_client = APIFactory.create_client(APIFactory.ClientType.NETWORK_CLIENT, config)
    
    try:
        advanced_client.connect()
        
        # Test redirects
        print("--- Redirect Handling ---")
        response = advanced_client.get("/redirect/3")  # 3 redirects
        print(f"Final URL: {response.url}")
        print(f"Status Code: {response.status_code}")
        print(f"Redirect History: {len(response.history)} redirects")
        
        # Test cookies
        print("\n--- Cookie Handling ---")
        response = advanced_client.get("/cookies/set/test-cookie/test-value")
        
        response = advanced_client.get("/cookies")
        if response.status_code == 200:
            data = response.json()
            print(f"Cookies: {data.get('cookies', {})}")
        
        # Test compression
        print("\n--- Compression ---")
        response = advanced_client.get("/gzip")
        if response.status_code == 200:
            data = response.json()
            print("✓ Gzip decompression successful")
            print(f"Gzipped: {data.get('gzipped', False)}")
        
        # Test different content types
        print("\n--- Content Types ---")
        
        # JSON response
        response = advanced_client.get("/json")
        if response.status_code == 200:
            print("✓ JSON content type handled")
        
        # HTML response
        response = advanced_client.get("/html")
        if response.status_code == 200:
            print("✓ HTML content type handled")
        
        # XML response
        response = advanced_client.get("/xml")
        if response.status_code == 200:
            print("✓ XML content type handled")
        
        # Test status codes
        print("\n--- Status Code Handling ---")
        status_codes = [200, 201, 400, 404, 500]
        
        for status in status_codes:
            try:
                response = advanced_client.get(f"/status/{status}")
                print(f"  Status {status}: {response.status_code}")
            except Exception as e:
                print(f"  Status {status}: Error - {e}")
        
        # Performance test
        print("\n--- Performance Test ---")
        start_time = time.time()
        
        # Make multiple concurrent-like requests
        for i in range(5):
            response = advanced_client.get("/delay/1")  # 1 second delay
            print(f"  Request {i+1}: {response.status_code} "
                  f"({time.time() - start_time:.1f}s)")
        
        total_time = time.time() - start_time
        print(f"✓ Total time for 5 requests: {total_time:.1f}s")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        advanced_client.disconnect()


def webhook_simulation_example():
    """Webhook and callback simulation example."""
    print("\n=== Webhook Simulation Example ===")
    
    webhook_client = APIFactory.create_network_client(
        base_url="https://webhook.site"  # Webhook testing service
    )
    
    try:
        webhook_client.connect()
        
        # Simulate webhook data
        webhook_data = {
            "event": "test_event",
            "timestamp": time.time(),
            "source": "VTA_Network_Client",
            "data": {
                "device_id": "test_device_001",
                "status": "active",
                "measurements": {
                    "temperature": 23.5,
                    "humidity": 45.2,
                    "voltage": 12.1
                }
            }
        }
        
        # Note: You would need to get a unique webhook URL from webhook.site
        # For this example, we'll use a placeholder
        # webhook_url = "/your-unique-webhook-id"
        
        print("--- Sending Webhook Data ---")
        print("(Note: Replace webhook URL with actual webhook.site URL)")
        print(f"Webhook payload: {json.dumps(webhook_data, indent=2)}")
        
        # In a real scenario:
        # response = webhook_client.post(webhook_url, json=webhook_data)
        # print(f"Webhook sent: {response.status_code}")
        
        # Simulate callback verification
        print("\n--- Callback Verification ---")
        verification_data = {
            "challenge": "verification_string_12345",
            "timestamp": time.time()
        }
        
        print(f"Verification data: {json.dumps(verification_data, indent=2)}")
        
        print("✓ Webhook simulation completed")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        webhook_client.disconnect()


if __name__ == "__main__":
    print("VTA Network Client Examples")
    print("===========================")
    
    # Run all examples
    try:
        basic_http_operations()
        rest_api_example()
        file_upload_download_example()
        authentication_example()
        streaming_example()
        advanced_networking_example()
        webhook_simulation_example()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    print("\nAll network examples completed!")
