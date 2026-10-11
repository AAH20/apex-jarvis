import unittest
from audio_ingress.mock_mic_stream import MockMicStream
from audio_ingress.vad_detector import VADDetector


class TestVADDetector(unittest.TestCase):
    def test_silence_detection(self):
        mic = MockMicStream()
        vad = VADDetector(energy_threshold=350.0)

        silence = mic.generate_silence_chunk()
        is_voice, energy, lat_us = vad.process_frame(silence)
        self.assertFalse(is_voice)
        self.assertLess(energy, 100.0)
        self.assertLess(lat_us, 500.0)  # Sub-500μs

    def test_speech_detection(self):
        mic = MockMicStream()
        vad = VADDetector(energy_threshold=350.0)

        speech = mic.generate_speech_chunk(freq_hz=440.0)
        is_voice, energy, lat_us = vad.process_frame(speech)
        self.assertTrue(is_voice)
        self.assertGreater(energy, 1000.0)


if __name__ == "__main__":
    unittest.main()
