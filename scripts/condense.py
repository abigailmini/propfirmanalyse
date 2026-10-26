import sys,re
seen=[]
for line in open(sys.argv[1]):
    s=line.strip()
    if 'InlineTextBox' in s: continue
    m=re.match(r'- (heading|link|button|columnheader|StaticText|cell|combobox|checkbox|tab|option|textbox|row)\s+"(.*?)"(.*)',s)
    if not m: continue
    kind,txt,rest=m.groups()
    url=re.search(r'\[url=(.*?)\]',rest)
    out=(kind[0:4]+': '+txt[:160]+(' -> '+url.group(1) if url else ''))
    if seen and seen[-1].endswith(txt[:160]): continue
    seen.append(out)
print('\n'.join(seen))
