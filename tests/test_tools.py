import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zlib

REPO = Path(__file__).resolve().parents[1]
sha = lambda value: hashlib.sha256(value).hexdigest()


class ToolChecks(unittest.TestCase):
    def test_real_crc_solver_with_synthetic_payloads(self):
        source = (REPO / "v12_CSharp兼容/构建.py").read_text()
        core = source[source.index("base=b''.join"):source.index("for i,(k,b,flags)")]
        for payload in (b"", b"fixture", bytes(range(256))):
            values = {"parts": [("fixture.resS", payload, 0)], "zlib": zlib}
            exec(compile(core, "crc-core", "exec"), values)
            suffix = values["suffix"]
            self.assertEqual(len(suffix), 4)
            self.assertEqual(zlib.crc32(payload + suffix), 0x7228EDC6)
            self.assertEqual(values["base"], payload)

    def run_installer(self, script, args):
        with patch.object(sys, "argv", [str(script)] + args), patch("subprocess.run", return_value=SimpleNamespace(returncode=1)), contextlib.redirect_stdout(io.StringIO()):
            try:
                runpy.run_path(str(script), run_name="__main__")
                return 0
            except SystemExit as error:
                return error.code

    def test_dry_run_install_restore_and_unknown_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            current, previous = root / "v13_对局头像", root / "v10_自然待机/游戏替换测试包"
            current.mkdir()
            (previous / "原版备份").mkdir(parents=True)
            game = root / "game"; game.mkdir()
            target = game / "skin_pyg_10_assets_all.bundle"
            original, replacement = b"original bundle fixture", b"replacement bundle fixture"
            target.write_bytes(original)
            (previous / "原版备份" / target.name).write_bytes(original)
            (current / target.name).write_bytes(replacement)
            (previous / "验证记录.json").write_text(json.dumps(dict(target=str(target), source_sha256=sha(original))))
            (current / "离线验证结果.json").write_text(json.dumps(dict(sha256=sha(replacement), previous_sha256=sha(original))))
            script = current / "安装或恢复.py"
            shutil.copy2(REPO / "v13_对局头像/安装或恢复.py", script)
            self.assertEqual(self.run_installer(script, ["--dry-run"]), 0)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(self.run_installer(script, []), 0)
            self.assertEqual(target.read_bytes(), replacement)
            self.assertEqual(self.run_installer(script, ["--restore"]), 0)
            self.assertEqual(target.read_bytes(), original)
            target.write_bytes(b"unknown bundle version")
            self.assertEqual(self.run_installer(script, []), 1)
            self.assertEqual(target.read_bytes(), b"unknown bundle version")


if __name__ == "__main__":
    unittest.main()
