"""Service for generating pattern embeddings for similarity search."""

import hashlib
import json
from typing import Any

import numpy as np
from sklearn.preprocessing import StandardScaler

from app.core.config import settings


class EmbeddingService:
    """Generate embeddings from pattern parameters for similarity search."""

    def __init__(self, dimensions: int = 128) -> None:
        """Initialize embedding service."""
        self.dimensions = dimensions
        self.scaler = StandardScaler()

    def _extract_features(self, parameters: dict[str, Any]) -> list[float]:
        """Extract numerical features from pattern parameters."""
        features = []

        # Extract common noise parameters
        feature_keys = [
            "scale",
            "octaves",
            "persistence",
            "lacunarity",
            "frequency",
            "amplitude",
            "speed",
            "complexity",
            "detail",
            "roughness",
            "threshold",
            "contrast",
            "brightness",
            "saturation",
            "hue_shift",
            "zoom",
            "offset_x",
            "offset_y",
        ]

        for key in feature_keys:
            value = parameters.get(key, 0.0)
            if isinstance(value, (int, float)):
                features.append(float(value))
            else:
                features.append(0.0)

        # Add color information (if present)
        colors = parameters.get("colors", [])
        if isinstance(colors, list):
            # Take up to 3 colors, extract RGB
            for i in range(3):
                if i < len(colors):
                    color = colors[i]
                    if isinstance(color, str) and color.startswith("#"):
                        # Parse hex color
                        try:
                            r = int(color[1:3], 16) / 255.0
                            g = int(color[3:5], 16) / 255.0
                            b = int(color[5:7], 16) / 255.0
                            features.extend([r, g, b])
                        except ValueError:
                            features.extend([0.0, 0.0, 0.0])
                    else:
                        features.extend([0.0, 0.0, 0.0])
                else:
                    features.extend([0.0, 0.0, 0.0])

        # Add boolean/categorical features as one-hot
        blend_modes = ["normal", "multiply", "screen", "overlay", "add"]
        blend_mode = parameters.get("blend_mode", "normal")
        for mode in blend_modes:
            features.append(1.0 if blend_mode == mode else 0.0)

        # Add hash-based features for exhibit type
        exhibit_type = parameters.get("exhibit_type", "")
        if exhibit_type:
            # Create deterministic features from exhibit type
            hash_val = int(hashlib.md5(exhibit_type.encode()).hexdigest(), 16)
            for i in range(5):
                features.append(((hash_val >> (i * 8)) & 0xFF) / 255.0)

        return features

    def generate_embedding(
        self, parameters: dict[str, Any], exhibit_type: str | None = None
    ) -> list[float]:
        """Generate embedding vector from pattern parameters."""
        # Add exhibit type to parameters if provided
        if exhibit_type:
            parameters = {**parameters, "exhibit_type": exhibit_type}

        # Extract features
        features = self._extract_features(parameters)

        # Pad or truncate to desired dimensions
        if len(features) < self.dimensions:
            # Pad with deterministic values based on JSON hash
            param_hash = hashlib.sha256(
                json.dumps(parameters, sort_keys=True).encode()
            ).digest()
            padding_needed = self.dimensions - len(features)
            for i in range(padding_needed):
                features.append(param_hash[i % len(param_hash)] / 255.0)
        elif len(features) > self.dimensions:
            # Use PCA-like reduction (simplified)
            arr = np.array(features)
            # Group and average to reduce dimensions
            chunk_size = len(features) // self.dimensions
            features = [
                float(arr[i * chunk_size : (i + 1) * chunk_size].mean())
                for i in range(self.dimensions)
            ]

        # Normalize to unit vector
        embedding = np.array(features)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.tolist()

    def compute_similarity(
        self, embedding1: list[float], embedding2: list[float]
    ) -> float:
        """Compute cosine similarity between two embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))


# Global embedding service instance
embedding_service = EmbeddingService(dimensions=settings.embedding_dimensions)
