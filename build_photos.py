import base64, glob, os, struct

os.makedirs('photos', exist_ok=True)
keys = sorted({os.path.basename(p).split('.')[0] for p in glob.glob('chunks/*')})
for key in keys:
    parts = sorted(glob.glob(f'chunks/{key}.*'))
    b64 = ''.join(open(p).read().strip() for p in parts)
    try:
        data = base64.b64decode(b64, validate=True)
    except Exception as e:
        print(f'{key}: BAD BASE64 ({e})'); continue
    if not data.startswith(b'\xff\xd8') or not data.endswith(b'\xff\xd9'):
        print(f'{key}: not a complete JPEG, skipping'); continue
    w = h = 0; i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF: break
        m = data[i+1]; L = struct.unpack('>H', data[i+2:i+4])[0]
        if m in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack('>HH', data[i+5:i+9]); break
        i += 2 + L
    open(f'photos/{key}.jpg', 'wb').write(data)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"><image width="{w}" height="{h}" '
           f'xlink:href="data:image/jpeg;base64,{b64}"/></svg>')
    open(f'photos/{key}.svg', 'w').write(svg)
    print(f'{key}: {w}x{h}, {len(data)} bytes, {len(parts)} chunks')
