from pathlib import Path
import UnityPy,zlib,json,hashlib
from UnityPy.streams import EndianBinaryReader
UnityPy.config.FALLBACK_UNITY_VERSION='6000.3.11f1'
out=Path(__file__).parent;src=out.parent/'v10_自然待机/游戏替换测试包';name='skin_pyg_10_assets_all.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
def rawfiles(env):return [(k,v.reader.bytes if hasattr(v,'reader') else v.bytes,v.flags) for k,v in env.file.files.items()]
orig=UnityPy.load(str(src/'原版备份'/name));target_crc=zlib.crc32(b''.join(b for _,b,_ in rawfiles(orig)))
assert target_crc==0x7228edc6
modified=UnityPy.load(str(src/name));parts=rawfiles(modified);base=b''.join(b for _,b,_ in parts);before=zlib.crc32(base);zero=zlib.crc32(bytes(4),before)
# Solve the 32-bit linear CRC contribution of a four-byte unused resource tail.
basis={}
for i in range(32):
 delta=zlib.crc32((1<<i).to_bytes(4,'little'),before)^zero;comb=1<<i
 while delta:
  pivot=delta.bit_length()-1
  if pivot in basis:delta^=basis[pivot][0];comb^=basis[pivot][1]
  else:basis[pivot]=(delta,comb);break
wanted=target_crc^zero;bits=0
while wanted:
 pivot=wanted.bit_length()-1;delta,comb=basis[pivot];wanted^=delta;bits^=comb
suffix=bits.to_bytes(4,'little');assert zlib.crc32(base+suffix)==target_crc
# Preserve exact original payload bytes, avoid reserializing assets or editing catalog.
for index,(key,blob,flags) in enumerate(parts):
 if index==len(parts)-1:
  assert key.endswith('.resS');blob+=suffix
 reader=EndianBinaryReader(blob);reader.flags=flags;modified.file.files[key]=reader
result=out/name;result.write_bytes(modified.file.save(packer='lz4'))
check=UnityPy.load(str(result));after=rawfiles(check)
assert [k for k,_,_ in parts]==[k for k,_,_ in after]
assert after[0][1]==parts[0][1];assert after[-1][1][:-4]==parts[-1][1]
assert zlib.crc32(b''.join(b for _,b,_ in after))==target_crc
beforeenv=UnityPy.load(str(src/name));a={o.path_id:sha(o.get_raw_data()) for o in beforeenv.objects};b={o.path_id:sha(o.get_raw_data()) for o in check.objects};assert a==b
textures=0
for o in check.objects:
 if o.type.name=='Texture2D':
  d=o.read();old=next(x for x in beforeenv.objects if x.path_id==o.path_id).read();assert d.image.tobytes()==old.image.tobytes();textures+=1
 if o.path_id==-8549261268203946734:
  data=json.loads(o.read().m_Script);assert data['skeleton']['spine']=='4.2.43';assert 'idle' in data['animations'];(out/'回读骨骼.json').write_text(o.read().m_Script)
manifest=json.loads((src/'验证记录.json').read_text());actual=Path(manifest['target']);assert sha(actual.read_bytes())==manifest['source_sha256']
report={'expected_crc':f'{target_crc:08x}','previous_crc':f'{before:08x}','rebuilt_crc':f'{zlib.crc32(b"".join(b for _,b,_ in after)):08x}','added_unused_bytes':4,'suffix_hex':suffix.hex(),'all_asset_objects_unchanged_from_v10':len(a),'all_textures_pixel_identical_to_v10':textures,'sha256':sha(result.read_bytes()),'game_original_unchanged':True,'installed':False,'in_game_test':'NOT PERFORMED','source_reference':'https://docs.unity3d.com/ScriptReference/AssetBundle.LoadFromFile.html'}
(out/'离线验证结果.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
