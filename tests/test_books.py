import tempfile
import unittest
from pathlib import Path
from aevonyr.book_library import Library
from aevonyr.book_translation import chunks, api

class BookTests(unittest.TestCase):
    def test_reimport_preserves_progress_and_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'story.txt';path.write_text('original')
            lib=Library(directory);lib.add(path);lib.save(str(path),42,'my notes');lib.add(path)
            self.assertEqual(lib.all()[0][2:],(42,'my notes'))
            lib.db.close();lib=Library(directory)
            self.assertEqual(lib.all()[0][2:],(42,'my notes'))
            self.assertEqual(path.read_text(),'original');lib.db.close()
    def test_invalid_progress_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'story.txt';path.touch();lib=Library(directory);lib.add(path)
            with self.assertRaises(ValueError):lib.save(str(path),101,'bad')
            self.assertEqual(lib.all()[0][2],0);lib.db.close()
    def test_chunks_preserve_whitespace_and_unicode(self):
        text=('Příběh\n\n猫 '*1000)+'konec'
        parts=list(chunks(text));self.assertEqual(''.join(parts),text)
        self.assertTrue(all(len(p)<=2000 for p in parts))
    def test_reject_insecure_translation_endpoint(self):
        with self.assertRaises(ValueError):api('http://example.com','languages')

class AndroidStateTests(unittest.TestCase):
    def test_partial_and_complete_download(self):
        from aevonyr.android_state import ready
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.assertFalse(ready(root))
            (root/'waydroid.cfg').write_text('[waydroid]\n')
            images=root/'images';images.mkdir();(images/'system.img').write_bytes(b'system')
            self.assertFalse(ready(root));(images/'vendor.img').write_bytes(b'vendor')
            self.assertTrue(ready(root))
    def test_custom_image_path(self):
        from aevonyr.android_state import ready
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);images=root/'custom';images.mkdir()
            (root/'waydroid.cfg').write_text('[waydroid]\nimages_path='+str(images)+'\n')
            for name in ('system.img','vendor.img'):(images/name).write_bytes(b'image')
            self.assertTrue(ready(root))
