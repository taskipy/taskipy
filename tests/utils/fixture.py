import tempfile
import shutil

class FixtureTempDir:
    def __init__(self, fixture_original_dir: str):
        self._tmpdir: str = tempfile.mktemp()
        shutil.copytree(fixture_original_dir, self._tmpdir)

    @property
    def path(self):
        return self._tmpdir

    def clean(self):
        shutil.rmtree(self._tmpdir, ignore_errors=True)
    