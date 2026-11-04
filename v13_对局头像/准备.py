from pathlib import Path
import os
from PIL import Image
p=Path(__file__).parent
im=Image.open(Path(os.environ['BAZAAR_PORTRAIT_PNG'])).convert('RGBA')
# Preserve complete hair, card and arms; crop at waist for small in-game readability.
im=im.crop((180,0,780,600)).resize((920,920),Image.Resampling.LANCZOS)
canvas=Image.new('RGBA',(1024,1024));canvas.alpha_composite(im,(52,52));canvas.save(p/'对局头像.png')
bg=Image.new('RGBA',canvas.size,'#57432a');bg.alpha_composite(canvas);bg.resize((512,512)).convert('RGB').save(p/'头像预览.jpg')
s=(p.parent/'v12_CSharp兼容/构建.py').read_text().replace("import UnityPy,json,zlib,hashlib","import UnityPy,json,zlib,hashlib,struct\nfrom PIL import Image").replace("prev=out.parent/'v11_CRC兼容检查'","prev=out.parent/'v12_CSharp兼容'")
a=s.index('for o in e.objects:');b=s.index('parts=[]',a)
s=s[:a]+'''for o in e.objects:
 if o.path_id==6014851008856456531:
  d=o.read();d.set_image(Image.open(out/'对局头像.png'),target_format=4,mipmap_count=1);d.save()
 if o.path_id==6803145303963729235:
  t=o.read_typetree();r=t['m_RD'];r['textureRect']={'x':0.0,'y':0.0,'width':1024.0,'height':1024.0};r['textureRectOffset']={'x':0.0,'y':0.0}
  r['m_IndexBuffer']=struct.pack('<6H',0,1,2,2,3,0)
  vd=r['m_VertexData'];vd['m_VertexCount']=4
  vd['m_DataSize']=struct.pack('<12f',-2,-2,0,-2,2,0,2,2,0,2,-2,0)+struct.pack('<8f',0,0,0,1,1,1,1,0)
  sm=r['m_SubMeshes'][0];sm['indexCount']=6;sm['vertexCount']=4
  o.save_typetree(t)
''' +s[b:]
s=s.replace("assert changed==[-8549261268203946734]","assert set(changed)=={6014851008856456531,6803145303963729235}\nfor o in check.objects:\n if o.path_id==6014851008856456531:\n  img=o.read().image.convert('RGBA');assert img.tobytes()==Image.open(out/'对局头像.png').convert('RGBA').tobytes();img.save(out/'回读头像.png')\n if o.path_id==6803145303963729235:o.read().image.save(out/'回读Sprite.png')")
s=s.replace('changed_from_v11','changed_from_v12').replace("'all_other_objects_unchanged':174","'all_other_objects_unchanged':173")
(p/'构建.py').write_text(s)
i=(p.parent/'v12_CSharp兼容/安装或恢复.py').read_text().replace('V12 已安装','V13 已安装').replace('.bazaar-v11-','.bazaar-v13-');(p/'安装或恢复.py').write_text(i)
