using Spine;
using System.Text.Json;
class NoTexture : TextureLoader {
 public void Load(AtlasPage page, string path) {}
 public void Unload(object texture) {}
}
class Program {
 static void Main(string[] args) {
  string root = args[0];
  var atlas = new Atlas(new StringReader(File.ReadAllText(Path.Combine(root,"../v10_自然待机/Skin_PYG_10a.atlas"))), "", new NoTexture());
  var parser = new SkeletonJson(atlas);
  if(args.Length<2) {
   try { parser.ReadSkeletonData(new StringReader(File.ReadAllText(Path.Combine(root,"../v10_自然待机/Skin_PYG_10a.json")))); throw new Exception("Expected original hash error was not reproduced"); }
   catch(KeyNotFoundException e) {Console.WriteLine("Original failure reproduced: "+e.Message);}
  }
  var data = parser.ReadSkeletonData(new StringReader(File.ReadAllText(Path.Combine(root,args.Length>1?args[1]:"Skin_PYG_10a.json"))));
  var sk = new Skeleton(data); sk.SetSkin("default"); sk.SetToSetupPose();
  var state = new AnimationState(new AnimationStateData(data));state.SetAnimation(0,"idle",true);
  var expected=JsonSerializer.Deserialize<float[][]>(File.ReadAllText(Path.Combine(root,"../v10_自然待机/运行库帧数据.json")));
  float maxDiff=0, last=0;float[][] output=new float[121][];
  for(int i=0;i<=120;i++) {
   float t=i*8f/120f;state.Update(t-last);last=t;state.Apply(sk);var update=typeof(Skeleton).GetMethods().Single(m=>m.Name=="UpdateWorldTransform" && m.GetParameters().Length==1);update.Invoke(sk,new object[]{Enum.Parse(update.GetParameters()[0].ParameterType,"Update")});
   var mesh=(MeshAttachment)sk.Slots.Items[0].Attachment;float[] v=new float[mesh.WorldVerticesLength];mesh.ComputeWorldVertices(sk.Slots.Items[0],0,v.Length,v,0,2);
   for(int j=0;j<v.Length;j++){if(!float.IsFinite(v[j]))throw new Exception("Nonfinite vertex"); maxDiff=Math.Max(maxDiff,Math.Abs(v[j]-expected[i][j]));}
   output[i]=v;
  }
  if(maxDiff>.2)throw new Exception("Runtime mismatch "+maxDiff);
  File.WriteAllText(Path.Combine(root,"CSharp验证结果.json"),JsonSerializer.Serialize(new {assembly=typeof(Skeleton).Assembly.FullName,version=data.Version,bones=data.Bones.Count,frames=121,max_difference=maxDiff,passed=true}));
  Console.WriteLine("PASS CSharp actual game DLL; bones="+data.Bones.Count+" frames=121 maxDifference="+maxDiff);
 }
}
