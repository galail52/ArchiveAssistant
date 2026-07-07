from pathlib import Path

from PIL import Image
from PIL import ImageOps
from PIL import UnidentifiedImageError

from core.similarity.image_fingerprint import ImageFingerprint


class FingerprintEngine:
    algorithm = "dhash8_mean"
    hash_size = 8

    def fingerprint(self, image_path):
        image_path = Path(image_path)

        try:
            with Image.open(image_path) as image:
                grayscale = ImageOps.grayscale(image)
                resized = grayscale.resize(
                    (self.hash_size + 1, self.hash_size),
                    Image.Resampling.LANCZOS,
                )
                pixels = list(resized.tobytes())
        except (OSError, UnidentifiedImageError):
            return None

        bits = []

        for row in range(self.hash_size):
            offset = row * (self.hash_size + 1)

            for column in range(self.hash_size):
                left = pixels[offset + column]
                right = pixels[offset + column + 1]
                bits.append("1" if left > right else "0")

        bit_string = "".join(bits)
        hash_value = f"{int(bit_string, 2):016x}"
        mean_value = round(sum(pixels) / len(pixels))
        fingerprint_value = f"{hash_value}:{mean_value:02x}"

        return ImageFingerprint.create(
            image_id=str(image_path),
            fingerprint_algorithm=self.algorithm,
            fingerprint_value=fingerprint_value,
        )

    def compare(self, source, target):
        source_hash, source_mean = self.parse_value(
            source.fingerprint_value
        )
        target_hash, target_mean = self.parse_value(
            target.fingerprint_value
        )

        if (
            source.fingerprint_algorithm == target.fingerprint_algorithm
            and source.fingerprint_value == target.fingerprint_value
        ):
            return 1.0

        hamming_distance = self.hamming_distance(source_hash, target_hash)
        hash_similarity = 1 - (hamming_distance / 64)
        mean_similarity = 1 - (abs(source_mean - target_mean) / 255)
        score = (hash_similarity * 0.85) + (mean_similarity * 0.15)
        return max(0.0, min(1.0, score))

    def parse_value(self, fingerprint_value):
        hash_value, mean_value = fingerprint_value.split(":", 1)
        return int(hash_value, 16), int(mean_value, 16)

    def hamming_distance(self, source_hash, target_hash):
        return (source_hash ^ target_hash).bit_count()
