# The Bazaar 动态立绘与对局头像制作工具

Historical build, validation and rollback scripts for custom Pygmalien portraits in **The Bazaar** on macOS Steam.

本项目作用于《大巴扎／The Bazaar》的皮格马利翁（Pygmalien）资源，保留从动态人物尝试到对局头像的分阶段制作代码。主要研究 Unity AssetBundle 的对象保持、Spine 骨骼兼容、解压载荷 CRC 和安装恢复，不改变对战数值或账号数据。

**这是特定资源版本的工具快照，不是通用 Mod SDK，也不是可直接安装的头像包。** 私人图片、Spine 骨骼/帧数据、游戏 bundle、原版备份及本机安装记录都未公开。

## 版本范围

| 阶段 | 代码用途与边界 |
| --- | --- |
| v10 | 旧自然待机包出现 CRC 失败并停用；本仓库不发布该失败包，仅保留后续步骤需要的输入目录约定 |
| v11 | 对已有候选载荷追加四字节未引用尾部，使解压载荷 CRC 与指定原版一致；逐对象与贴图数据保持检查 |
| v12 | 更换兼容的 Spine JSON，重新构建并检查其余对象保持；附使用自备游戏 Spine C# DLL 的检查工程 |
| v13 | 更新对局头像 Texture2D/Sprite，设置矩形网格和 UV，进行像素回读与安装/恢复校验 |

CRC 匹配只针对已知包的兼容问题，不证明资源可被所有游戏版本加载，也不等于安全或游戏内效果验证。脚本包含固定对象 ID、`skin_pyg_10_assets_all.bundle`、Spine 4.2.43 和预期 CRC `7228edc6`；其他版本必须重新适配，不能直接取消断言。

## 环境与依赖

- Python 3，UnityPy、Pillow。
- 脚本设置的 Unity 回退版本为 `6000.3.11f1`，这是原流程的解析提示，不是自动检测到的新游戏版本。
- C# 验证工程另外需要 .NET 8 SDK，以及自行取得、与游戏相匹配的 `spine-csharp.dll`。不附第三方 DLL 或运行库源码。
- 原项目面向 macOS Steam；其他平台和当前线上版本未在本次验证。

可先使用独立 Python 环境安装公开依赖：

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install UnityPy Pillow
```

## 先做只读资源分析

```sh
python3 inspect_bundle.py "/path/to/your/skin_pyg_10_assets_all.bundle" --output analysis
```

该工具读取用户指定 bundle，并把对象列表、选定类型树与 TextAsset 内容导出到 `analysis/`。不会写回源 bundle；分析输出可能包含原游戏数据，因此已忽略，不应直接提交到公开仓库。

## 自备输入与逐阶段构建

这些脚本以现有阶段目录为输入，不能从空仓库直接生成原项目成品。

1. 自行在 `v10_自然待机/游戏替换测试包/` 准备匹配版本的候选 bundle、`原版备份/` 中的原版，以及由自己的游戏路径和 SHA 填写的 `验证记录.json`。格式见同目录 `验证记录.example.json`。
2. v11 的输出将成为 v12 输入。v12 另外需要自己准备的兼容 `Skin_PYG_10a.json`。
3. v13 的输入是自己生成的 v12 bundle 和 1024×1024 透明 `对局头像.png`。私人绘图、骨骼和纹理没有替代样本，必须自行准备。

```sh
python3 v11_CRC兼容检查/构建校验兼容副本.py
python3 v12_CSharp兼容/构建.py
python3 v13_对局头像/构建.py
```

`v13_对局头像/准备.py` 是可选的历史裁切/生成步骤，需要 `BAZAAR_PORTRAIT_PNG` 指向自己的图片；它还会重新生成 v13 构建与安装脚本。仅复现原流程时使用，先保留代码副本，不要把它当成通用图片处理器。若已自行提供正确尺寸头像，直接运行 v13 构建即可。

```sh
export BAZAAR_PORTRAIT_PNG="/path/to/your/portrait.png"
python3 v13_对局头像/准备.py
```

C# 检查器还需要 v10 的 atlas、骨骼 JSON、预期运行帧数据等自备输入。构建时指定 DLL：

```sh
dotnet build v12_CSharp兼容/CSharpCheck/CSharpCheck.csproj   -p:SpineDll="/path/to/your/spine-csharp.dll"
dotnet run --no-build --project v12_CSharp兼容/CSharpCheck/CSharpCheck.csproj --   "$PWD/v12_CSharp兼容"
```

## 安装与恢复

仅对自己已构建并通过离线检查的 v13 包操作。先完全退出游戏；`验证记录.json` 的目标路径应指向自己的匹配原版 bundle。

```sh
python3 v13_对局头像/安装或恢复.py --dry-run
python3 v13_对局头像/安装或恢复.py
python3 v13_对局头像/安装或恢复.py --restore
```

安装器检查候选、当前文件和原版备份 SHA，确认游戏进程已退出，写同目录临时文件后原子替换。备份丢失、游戏更新或哈希不匹配时会停止，不能强行覆盖。恢复依赖本机备份，应随工作目录保留。默认无参数执行安装，因此请先运行 `--dry-run` 并核对目标。

## 本次验证与边界

本次只对整理后的 Python/XML 语法、CRC 核心算法与临时合成文件的安装/恢复及未知版本拒绝进行检查。没有解析或重建真实游戏资源，也没有运行 C# 游戏 DLL 验证、安装包或进入游戏。

历史阶段的 CRC、对象保持与帧数据检查只证明对应历史输入；v11–v13 不应据此标成当前游戏的稳定可用成品。

```sh
python3 -m unittest discover -s tests -v
```

工具代码公开不包含或授权分发原游戏、Unity/Spine 运行库及私人美术。所需依赖请按各自许可自行取得。
