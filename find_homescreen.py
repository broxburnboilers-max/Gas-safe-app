import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
lines = open(r'C:\Users\Andrew\Documents\gas-safety-multiuser\src\App.jsx', encoding='utf-8').readlines()
checks = ['onDemo', 'Demo Certificates', 'DemoCertificatesScreen', 'seedDemoData', 'isDemo', 'id.*demo', 'folder.*demo']
import re
for i, l in enumerate(lines, 1):
    for c in checks:
        if re.search(c, l):
            print(f'{i}: {l.rstrip()[:130]}')
            break
