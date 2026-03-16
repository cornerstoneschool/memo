# Open auth.js and force change memo2526 to memo
with open('js/auth.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace('"memo2526"', '"memo"')

with open('js/auth.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("✅ Force-changed repo name to 'memo' in auth.js!")