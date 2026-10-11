import unittest
from audio_egress.viseme_streamer import VisemeStreamer
from core.types import VisemeID


class TestVisemeStreamer(unittest.TestCase):
    def test_viseme_generation(self):
        streamer = VisemeStreamer()
        visemes = streamer.generate_visemes_for_text("Hello", speech_duration_ms=500.0)

        self.assertTrue(len(visemes) > 0)
        self.assertAlmostEqual(visemes[0].timestamp_ms, 0.0)
        self.assertEqual(visemes[-1].viseme, VisemeID.OH)  # 'o' maps to OH

    def test_silence_handling(self):
        streamer = VisemeStreamer()
        visemes = streamer.generate_visemes_for_text("", speech_duration_ms=300.0)
        self.assertEqual(len(visemes), 1)
        self.assertEqual(visemes[0].viseme, VisemeID.SILENCE)


if __name__ == "__main__":
    unittest.main()
