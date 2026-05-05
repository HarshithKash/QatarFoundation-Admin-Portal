import requests

BASE = 'http://127.0.0.1:5000'
s = requests.Session()

# 1. Signup
r = s.post(f'{BASE}/api/signup', json={
    'full_name': 'Test Admin',
    'email': 'admin@test.com',
    'password': 'password123'
})
print(f'SIGNUP: {r.status_code} {r.json()}')

# 2. Login
r = s.post(f'{BASE}/api/login', json={
    'email': 'admin@test.com',
    'password': 'password123'
})
print(f'LOGIN: {r.status_code} {r.json()}')

# 3. Create opportunity
r = s.post(f'{BASE}/api/opportunities', json={
    'name': 'Test Opportunity',
    'duration': '3 Months',
    'start_date': '2026-06-01',
    'description': 'This is a test',
    'skills': 'Python, Flask, SQL',
    'category': 'technology',
    'future_opportunities': 'Software Developer roles'
})
print(f'CREATE OPP: {r.status_code} {r.json()}')

# 4. Get opportunities
r = s.get(f'{BASE}/api/opportunities')
print(f'GET OPPS: {r.status_code} {r.json()}')
