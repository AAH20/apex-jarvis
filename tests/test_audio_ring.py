import unittest
from core.audio_ring_buffer import AudioRingBuffer


class TestAudioRingBuffer(unittest.TestCase):
    def test_write_and_read_chunks(self):
        buf = AudioRingBuffer(capacity_chunks=16, chunk_size_bytes=320)
        self.assertEqual(buf.available(), 0)

        chunk = b"\x01\x02" * 160  # 320 bytes
        success = buf.write_chunk(chunk)
        self.assertTrue(success)
        self.assertEqual(buf.available(), 1)

        read_data = buf.read_chunk()
        self.assertEqual(read_data, chunk)
        self.assertEqual(buf.available(), 0)

    def test_buffer_overflow_safety(self):
        buf = AudioRingBuffer(capacity_chunks=4, chunk_size_bytes=10)
        for i in range(4):
            self.assertTrue(buf.write_chunk(b"0123456789"))

        # 5th write should be rejected to protect audio jitter
        self.assertFalse(buf.write_chunk(b"0123456789"))


if __name__ == "__main__":
    unittest.main()
