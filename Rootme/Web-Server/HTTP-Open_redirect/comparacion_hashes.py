import hashlib

# Sin secreto, solo la URL
hash_fb = hashlib.md5(b'https://facebook.com').hexdigest()
print(f"Facebook: {hash_fb}")
print(f"Esperado:  a023cfbf5f1c39bdf8407f28b60cd134")
print(f"✅ {hash_fb == 'a023cfbf5f1c39bdf8407f28b60cd134'}\n")

hash_tw = hashlib.md5(b'https://twitter.com').hexdigest()
print(f"Twitter:  {hash_tw}")
print(f"Esperado: be8b09f7f1f66235a9c91986952483f0")
print(f"✅ {hash_tw == 'be8b09f7f1f66235a9c91986952483f0'}\n")

hash_sl = hashlib.md5(b'https://slack.com').hexdigest()
print(f"Slack:    {hash_sl}")
print(f"Esperado: e52dc719664ead63be3d5066c135b6da")
print(f"✅ {hash_sl == 'e52dc719664ead63be3d5066c135b6da'}")
