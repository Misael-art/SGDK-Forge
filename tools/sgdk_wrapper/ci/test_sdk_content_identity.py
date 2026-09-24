import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("identity", Path(__file__).resolve().parents[1] / "sdk_content_identity.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class IdentityTests(unittest.TestCase):
    def test_content_mutations_and_parameters(self):
        with tempfile.TemporaryDirectory(prefix="sdk with spaces ") as directory:
            root = Path(directory)
            bridge = root / "bridge.sh"
            bridge.write_text("bridge v1")
            sdk = root / "sdk"
            sdk.mkdir()
            for name in ("makefile.gen", "inc/test.h", "src/test.c", "bin/gcc.exe", "lib/libmd.a"):
                path = sdk / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(name)
            previous = module.inventory(sdk, bridge)["sha256"]
            self.assertEqual(previous, module.inventory(sdk, bridge)["sha256"])
            for name in ("inc/test.h", "src/test.c", "bin/gcc.exe", "lib/libmd.a"):
                path = sdk / name
                path.write_text(path.read_text() + "changed")
                current = module.inventory(sdk, bridge)["sha256"]
                self.assertNotEqual(previous, current, name)
                previous = current
            bridge.write_text("bridge v2")
            self.assertNotEqual(previous, module.inventory(sdk, bridge)["sha256"])
            previous = module.inventory(sdk, bridge)["sha256"]
            (sdk / "inc/test.h").unlink()
            self.assertNotEqual(previous, module.inventory(sdk, bridge)["sha256"])

    def test_missing_sdk_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                module.inventory(Path(directory), Path(__file__))

if __name__ == "__main__":
    unittest.main()
