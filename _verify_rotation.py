import urllib.request, json, os

key = None
with open(r'C:\Users\FANNNDI\Documents\farewell-helper\.env') as f:
    for line in f:
        if line.startswith('NINEROUTER_API_KEY'):
            key = line.split('=', 1)[1].strip()
            break

def test_model(name, expected_prefix):
    body = json.dumps({
        'model': name,
        'messages': [{'role': 'user', 'content': 'Reply with just the word: MODEL'}],
        'stream': False,
        'max_tokens': 10
    }).encode()
    req = urllib.request.Request('http://localhost:20128/v1/chat/completions', data=body)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {key}')
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
        actual = resp.get('model', 'UNKNOWN')
        match = 'MATCH' if actual.startswith(expected_prefix) else 'MISMATCH'
        print(f'{name:8s} -> expected: {expected_prefix:30s} | actual: {actual:35s} | {match}')
    except Exception as e:
        print(f'{name:8s} -> ERROR: {e}')

print('=== QUALITY PROFILE VERIFICATION ===')
print('(Pro/Flash/Free should all be ocg/deepseek-v4-pro)')
test_model('Pro', 'ocg/deepseek-v4-pro')
test_model('Flash', 'ocg/deepseek-v4-pro')
test_model('Free', 'ocg/deepseek-v4-pro')
print()

# Now rotate back to default and test again
print('=== RESTORING DEFAULT ===')

# Login and rotate via API
token = None
# Login
cj = __import__('http.cookiejar').CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
login_data = json.dumps({'password': '123456'}).encode()
login_req = urllib.request.Request('http://localhost:20128/api/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
opener.open(login_req, timeout=5)
for c in cj:
    if c.name == 'auth_token':
        token = c.value

if token:
    # Get combo IDs and restore default models
    req = urllib.request.Request('http://localhost:20128/api/combos', headers={'Cookie': f'auth_token={token}'})
    combos = json.loads(urllib.request.urlopen(req, timeout=5).read()).get('combos', [])
    default_map = {'Pro': 'ocg/deepseek-v4-pro', 'Flash': 'ocg/deepseek-v4-flash', 'Free': 'oc/deepseek-v4-flash-free'}
    for c in combos:
        if c['name'] in default_map:
            body = json.dumps({'models': [default_map[c['name']]]}).encode()
            put_req = urllib.request.Request(f'http://localhost:20128/api/combos/{c["id"]}', data=body, 
                headers={'Content-Type': 'application/json', 'Cookie': f'auth_token={token}'}, method='PUT')
            urllib.request.urlopen(put_req, timeout=5)
            print(f'  Restored {c["name"]} -> {default_map[c["name"]]}')

print()
print('=== DEFAULT PROFILE VERIFICATION ===')
test_model('Pro', 'ocg/deepseek-v4-pro')
test_model('Flash', 'ocg/deepseek-v4-flash')
test_model('Free', 'oc/deepseek-v4-flash-free')
print()
print('ALL ROTATION TESTS COMPLETE')
