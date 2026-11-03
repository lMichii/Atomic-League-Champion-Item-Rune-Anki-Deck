import shutil
import unittest
from helpers import sandbox_project
from lol_anki.media import gif, gif_info, V4_FILTER
from lol_anki.project import Project


class GifTests(unittest.TestCase):
    def test_twenty_supplied_gifs_are_animated_and_loop_forever(self):
        paths = list((Project().legacy/'media/gifs').glob('*.gif'))
        self.assertEqual(len(paths),20)
        for p in paths:
            info = gif_info(p.read_bytes())
            self.assertGreater(info['frames'],1,p.name)
            self.assertEqual(info['loop'],0,p.name)
        with self.assertRaises(ValueError):
            gif_info(b'GIF89a')

    @unittest.skipUnless(shutil.which('ffmpeg'),'Optional FFmpeg required for conversion integration test')
    def test_real_ffmpeg_conversion_and_content_based_resume(self):
        with sandbox_project() as project:
            source = Project().legacy/'media/videos/ezreal_e.mp4'
            target = project.root/'ezreal_e.gif'
            first = gif(source,target)
            before = target.stat().st_mtime_ns
            self.assertEqual(first['status'],'converted')
            self.assertEqual(first['recipe']['filter'],V4_FILTER)
            self.assertEqual(gif_info(target.read_bytes())['loop'],0)
            second = gif(source,target)
            self.assertEqual(second['status'],'cached')
            self.assertEqual(first['sha256'],second['sha256'])
            self.assertEqual(before,target.stat().st_mtime_ns)
