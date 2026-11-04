from pathlib import Path
import UnityPy,json,zlib,hashlib
from UnityPy.streams import EndianBinaryReader
UnityPy.config.FALLBACK_UNITY_VERSION='6000.3.11f1'
out=Path(__file__).parent;prev=out.parent/'v11_CRC兼容检查';name='skin_pyg_10_assets_all.bundle';e=UnityPy.load(str(prev/name));sha=lambda b:hashlib.sha256(b).hexdigest();before={o.path_id:sha(o.get_raw_data()) for o in e.objects}
for o in e.objects:
 if o.path_id==-8549261268203946734:
  d=o.read();d.m_Script=(out/'Skin_PYG_10a.json').read_text();d.save()
parts=[]
for k,v in e.file.files.items():
 b=v.save() if hasattr(v,'save') else v.bytes
 if k.endswith('.resS'):b=b[:-4]
 parts.append((k,b,v.flags))
base=b''.join(b for _,b,_ in parts);crc=zlib.crc32(base);zero=zlib.crc32(bytes(4),crc);basis={}
for i in range(32):
 v=zlib.crc32((1<<i).to_bytes(4,'little'),crc)^zero;bits=1<<i
 while v:
  j=v.bit_length()-1
  if j in basis:v^=basis[j][0];bits^=basis[j][1]
  else:basis[j]=(v,bits);break
v=0x7228edc6^zero;bits=0
while v:
 a,b=basis[v.bit_length()-1];v^=a;bits^=b
suffix=bits.to_bytes(4,'little');assert zlib.crc32(base+suffix)==0x7228edc6
for i,(k,b,flags) in enumerate(parts):
 if i==len(parts)-1:b+=suffix
 r=EndianBinaryReader(b);r.flags=flags;e.file.files[k]=r
(out/name).write_bytes(e.file.save(packer='lz4'));check=UnityPy.load(str(out/name));raw=b''.join(v.reader.bytes if hasattr(v,'reader') else v.bytes for v in check.file.files.values());assert zlib.crc32(raw)==0x7228edc6
changed=[]
for o in check.objects:
 if before[o.path_id]!=sha(o.get_raw_data()):changed.append(o.path_id)
 if o.path_id==-8549261268203946734:(out/'回读骨骼.json').write_text(o.read().m_Script)
assert changed==[-8549261268203946734]
r={'sha256':sha((out/name).read_bytes()),'rebuilt_crc':'7228edc6','changed_from_v11':changed,'all_other_objects_unchanged':174,'installed':False,'in_game_test':'NOT PERFORMED','previous_sha256':sha((prev/name).read_bytes())};(out/'离线验证结果.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(r)
