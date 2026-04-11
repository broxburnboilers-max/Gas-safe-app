import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = r'C:\Users\Andrew\Documents\gas-safety-multiuser\src\App.jsx'
with open(path, encoding='utf-8') as f:
    src = f.read()

replacements = [
    # Admin email — keep as is, it's the actual admin contact, not branding
    # Demo data — engineer details (generic demo engineer)
    ('"West Lothian Gas Services"',          '"Demo Gas Services"'),
    ('"info@westlothiangas.co.uk"',          '"info@yourgascompany.co.uk"'),
    # Demo data — client address (West Lothian as place name is fine in addresses — leave those)
    # UI branding strings
    ('West Lothian Gas Ltd · Gas Safe Register', 'Gas Safe App · Gas Safe Register'),
    ('>West Lothian Gas Ltd<',                   '>Gas Safe App<'),
    # HomeScreen subtitle
    ('"West Lothian Gas Ltd"',                   '"Gas Safe App"'),
    # Paywall direct debit text
    ('West Lothian Gas Ltd to collect',          'us to collect'),
    # Account name placeholder (already changed but catch any remaining)
    ('e.g. West Lothian Gas Ltd',                'e.g. Your Company Name'),
    # Alt text
    ('alt="West Lothian Gas"',                   'alt="Company Logo"'),
    # Support strip plain text (not in JSX tags)
    ("West Lothian Gas Ltd · Gas Safe Register", "Gas Safe App · Gas Safe Register"),
]

count = 0
for old, new in replacements:
    n = src.count(old)
    if n > 0:
        src = src.replace(old, new)
        print(f'  {n}x  "{old[:60]}" -> "{new[:60]}"')
        count += n
    else:
        print(f'  --  NOT FOUND: "{old[:60]}"')

print(f'\nTotal replacements: {count}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print('File saved.')
