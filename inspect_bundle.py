from pathlib import Path
import argparse
import UnityPy,json,collections
UnityPy.config.FALLBACK_UNITY_VERSION='6000.3.11f1'
parser=argparse.ArgumentParser(description='Inspect The Bazaar Unity bundle metadata without changing the source.')
parser.add_argument('bundle', type=Path)
parser.add_argument('--output', type=Path, default=Path('analysis'))
args=parser.parse_args()
p=args.bundle
e=UnityPy.load(str(p)); out=args.output; out.mkdir(parents=True,exist_ok=True); rows=[]
for o in e.objects:
 try:
  t=o.read_typetree(); n=t.get('m_Name',''); rows.append({'id':o.path_id,'type':o.type.name,'name':n})
  if o.type.name in ['TextAsset','MonoBehaviour','MonoScript','AnimationClip','Animator','SkinnedMeshRenderer','Mesh','Material']:
   (out/(str(o.path_id)+'_'+o.type.name+'.json')).write_text(json.dumps(t,ensure_ascii=False,indent=2,default=str))
  if o.type.name=='TextAsset':
   d=o.read(); b=d.m_Script; b=b.encode('utf8','surrogateescape') if isinstance(b,str) else b;(out/(n.replace('/','_')+'.bytes')).write_bytes(b)
 except Exception as ex: rows.append({'id':o.path_id,'type':o.type.name,'error':str(ex)})
(out/'objects.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(collections.Counter(x['type'] for x in rows));print(json.dumps([r for r in rows if r['type'] in ['TextAsset','MonoScript','AnimationClip']],ensure_ascii=False,indent=2))
