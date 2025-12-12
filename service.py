import httpx # if using requests instead, the bot would handle one request at a time only

# disguise the request to the API
# this tells the server: "I am Chrome on Windows, trust me."
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BASE_URL = "https://api.guerrillamail.com/ajax.php"

# _function means it is internal.
# DO NOT CALL IT OUTSIDE THIS SCRIPT
async def _make_request(params: str):
    # internal helper to handle the HTTP connection logic
    url = f'{BASE_URL}?{params}'
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, headers=HEADERS) as client:
            response = await client.get(url)
            # raises for error 404, 500, etc.
            response.raise_for_status()
            data = response.json()
            # check the raw data if needed:
            print("🔍 RAW DATA:", data)
            return data
    except Exception as e:
        # if any response exists, print the raw text to see if it's an HTML error page
        if 'response' in locals():
            print(f"🔴 Server Response: {response.text}\n\n")
        print(f'🔴 Service Error: {e} | URL: {url}')
        return None

async def create_email_identity():
    # connects to API and generates a new email
    # returns a dict: {'email': str, 'sid_token': str}
    # returns None if failed
    data = await _make_request('f=get_email_address')

    if data:
        return {
                'email': data.get('email_addr'),
                'sid_token': data.get('sid_token')
            }
    return None


async def fetch_inbox(sid_token: str):
    # fetches the list of emails for a given session token
    # returns a list of messages or None if failed
    data = await _make_request(f'f=get_email_list&offset=0&sid_token={sid_token}')

    if data:
        return data.get('list', [])
    # if a function fetches a list,
    # return an empty list on failure
    return []
    # this is safer than return None (for lists)


async def fetch_email_content(msg_id: str, sid_token: str):
    
    data = await _make_request(f'f=fetch_email&email_id={msg_id}&sid_token={sid_token}')

    return data


async def destroy_identity(sid_token: str, email: str):
        # tells API to forget this session
        data = await _make_request(f'f=forget_me&email_addr={email}&sid_token={sid_token}')
        # if data is not None, the request reached the server
        return data is not None
