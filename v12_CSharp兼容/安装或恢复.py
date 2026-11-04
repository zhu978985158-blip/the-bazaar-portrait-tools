from pathlib import Path
import sys, json, hashlib, subprocess, tempfile, os, shutil, datetime

root = Path(__file__).resolve().parent
report = json.loads((root / '离线验证结果.json').read_text())
previous = root.parent / 'v10_自然待机/游戏替换测试包'
manifest = json.loads((previous / '验证记录.json').read_text())
target = Path(manifest['target'])
restore = '--restore' in sys.argv
dry = '--dry-run' in sys.argv
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

try:
    original_hash = manifest['source_sha256']
    replacement_hash = report['sha256']
    source = root / ('原版备份' if restore else '') / target.name
    if restore and not source.exists():
        source = previous / '原版备份' / target.name
    expected = original_hash if restore else replacement_hash
    if digest(source) != expected:
        raise RuntimeError('包内文件校验失败，未修改游戏。')
    current = digest(target)
    if current not in (original_hash, replacement_hash, report['previous_sha256']):
        raise RuntimeError('游戏文件版本不匹配，未修改游戏。')
    if dry:
        print('版本及文件检查通过；未修改游戏。')
        sys.exit(0)
    probe = subprocess.run(['/usr/bin/pgrep', '-f', 'Contents/MacOS/(TheBazaar|The Bazaar)'], capture_output=True)
    if probe.returncode != 1:
        raise RuntimeError('游戏仍在运行或无法确认退出，请完全退出后重试。')
    backup = root / '原版备份' / target.name
    backup.parent.mkdir(exist_ok=True)
    if not backup.exists():
        original = target if current == original_hash else previous / '原版备份' / target.name
        if digest(original) != original_hash:
            raise RuntimeError('原版备份校验失败。')
        shutil.copy2(original, backup)
    if digest(backup) != original_hash:
        raise RuntimeError('已有备份校验失败，未覆盖。')
    if current != expected:
        fd, temporary = tempfile.mkstemp(prefix='.bazaar-v11-', dir=target.parent)
        os.close(fd)
        try:
            shutil.copy2(source, temporary)
            if digest(Path(temporary)) != expected:
                raise RuntimeError('复制校验失败。')
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    assert digest(target) == expected
    state = {'installed': not restore, 'restored': restore, 'target': str(target), 'sha256': digest(target), 'backup': str(backup), 'backup_sha256': digest(backup), 'verified_at': datetime.datetime.now().astimezone().isoformat(), 'in_game_test': 'NOT PERFORMED'}
    (root / '本机安装结果.json').write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print('已恢复原版，文件校验通过。' if restore else 'V12 已安装，安装文件及原版备份校验通过。')
except Exception as error:
    print('未完成：' + str(error))
    sys.exit(1)
