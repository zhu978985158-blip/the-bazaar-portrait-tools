from pathlib import Path
import UnityPy,json,zlib,hashlib,struct
from PIL import Image
from UnityPy.streams import EndianBinaryReader
UnityPy.config.FALLBACK_UNITY_VERSION='6000.3.11f1'
out=Path(__file__).parent;prev=out.parent/'v12_CSharp兼容';name='skin_pyg_10_assets_all.bundle';e=UnityPy.load(str(prev/name));sha=lambda b:hashlib.sha256(b).hexdigest();before={o.path_id:sha(o.get_raw_data()) for o in e.objects}
for o in e.objects:
 if o.path_id==6014851008856456531:
  d=o.read();d.set_image(Image.open(out/'对局头像.png'),target_format=4,mipmap_count=1);d.save()
 if o.path_id==6803145303963729235:
  t=o.read_typetree();r=t['m_RD'];r['textureRect']={'x':0.0,'y':0.0,'width':1024.0,'height':1024.0};r['textureRectOffset']={'x':0.0,'y':0.0}
  r['m_IndexBuffer']=struct.pack('<6H',0,1,2,2,3,0)
  vd=r['m_VertexData'];vd['m_VertexCount']=4
  vd['m_DataSize']=struct.pack('<12f',-2,-2,0,-2,2,0,2,2,0,2,-2,0)+struct.pack('<8f',0,0,0,1,1,1,1,0)
  sm=r['m_SubMeshes'][0];sm['indexCount']=6;sm['vertexCount']=4
  o.save_typetree(t)
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
assert set(changed)=={6014851008856456531,6803145303963729235}
for o in check.objects:
 if o.path_id==6014851008856456531:
  img=o.read().image.convert('RGBA');assert img.tobytes()==Image.open(out/'对局头像.png').convert('RGBA').tobytes();img.save(out/'回读头像.png')
 if o.path_id==6803145303963729235:o.read().image.save(out/'回读Sprite.png')
r={'sha256':sha((out/name).read_bytes()),'rebuilt_crc':'7228edc6','changed_from_v12':changed,'all_other_objects_unchanged':173,'installed':False,'in_game_test':'NOT PERFORMED','previous_sha256':sha((prev/name).read_bytes())};(out/'离线验证结果.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(r)
