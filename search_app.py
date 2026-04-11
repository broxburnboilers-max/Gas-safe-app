import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
lines = open('C:/Users/Andrew/Documents/gas-safety-multiuser/src/App.jsx', encoding='utf-8').readlines()
for i, l in enumerate(lines, 1):
    if 'wlgContactsPulse' in l:
        print(f'{i}: {l.rstrip()[:120]}')
    if 'wlg-contacts-pulse-style' in l:
        print(f'{i}: {l.rstrip()[:120]}')
