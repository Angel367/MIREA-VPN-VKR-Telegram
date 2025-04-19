import logging
import requests
import json
from config import API_URL, API_USERNAME, API_PASSWORD

logger = logging.getLogger(__name__)

# Session for API requests
session = requests.Session()
# session.auth = (API_USERNAME, API_PASSWORD)


async def register_user(telegram_id, username=None, first_name=None):
    """Register or update user in the backend"""
    try:
        # Check if user already exists
        response = session.get(f"{API_URL}/users/?telegram_id={telegram_id}")
        users = response.json().get('results', [])

        user_data = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "is_active": True
        }

        if users:
            # Update existing user
            user_id = users[0]['id']
            response = session.patch(f"{API_URL}/users/{user_id}/", json=user_data)
            return response.json()
        else:
            # Create new user
            response = session.post(f"{API_URL}/users/", json=user_data)
            return response.json()

    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return None


async def get_user_keys(telegram_id):
    """Get VPN keys for a user"""
    try:
        # First get user ID from telegram_id
        response = session.get(f"{API_URL}/users/?telegram_id={telegram_id}")
        users = response.json().get('results', [])

        if not users:
            return []

        user_id = users[0]['id']

        # Get keys for this user
        response = session.get(f"{API_URL}/users/{user_id}/keys/")
        return response.json()

    except Exception as e:
        logger.error(f"Error getting user keys: {e}")
        return []


async def get_available_servers():
    """Get list of available servers"""
    try:
        response = session.get(f"{API_URL}/servers/")
        servers = response.json().get('results', [])

        # Filter only active servers
        return [server for server in servers if server['active']]

    except Exception as e:
        logger.error(f"Error getting servers: {e}")
        return []


async def create_vpn_key(user_id, server_id, name, traffic_limit_gb=0, expiration_days=30):
    """Create a new VPN key"""
    try:
        # Convert GB to bytes for traffic limit
        traffic_limit_bytes = int(traffic_limit_gb * (1024 ** 3)) if traffic_limit_gb > 0 else 0

        # First get user's telegram_id
        response = session.get(f"{API_URL}/users/?telegram_id={user_id}")
        users = response.json().get('results', [])

        if not users:
            raise ValueError(f"User with telegram_id {user_id} not found")

        backend_user_id = users[0]['id']

        # Create key
        data = {
            "user_id": backend_user_id,
            "server_id": server_id,
            "name": name,
            "traffic_limit": traffic_limit_bytes,
            "expiration_days": expiration_days
        }

        response = session.post(f"{API_URL}/keys/create_key/", json=data)

        if response.status_code != 201:
            raise ValueError(f"Failed to create key: {response.text}")

        return response.json()

    except Exception as e:
        logger.error(f"Error creating VPN key: {e}")
        raise


async def revoke_key(key_id):
    """Revoke a VPN key"""
    try:
        response = session.post(f"{API_URL}/keys/{key_id}/revoke/")
        return response.status_code == 200

    except Exception as e:
        logger.error(f"Error revoking key: {e}")
        return False


async def get_all_users():
    """Get all users (admin function)"""
    try:
        response = session.get(f"{API_URL}/users/")
        return response.json().get('results', [])

    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []


async def get_all_servers():
    """Get all servers (admin function)"""
    try:
        response = session.get(f"{API_URL}/servers/")
        return response.json().get('results', [])

    except Exception as e:
        logger.error(f"Error getting all servers: {e}")
        return []


async def get_all_keys():
    """Get all keys (admin function)"""
    try:
        response = session.get(f"{API_URL}/keys/")
        return response.json().get('results', [])

    except Exception as e:
        logger.error(f"Error getting all keys: {e}")
        return []