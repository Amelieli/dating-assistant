"""
CLIP-based image matching for finding visually similar profiles.
Uses OpenAI's CLIP model for image embeddings.
"""
from typing import List, Optional, Tuple
import numpy as np
from models.profile import Profile
import logging

logger = logging.getLogger(__name__)


class CLIPMatcher:
    """
    Uses CLIP embeddings to find visually similar profiles.
    Requires photo embeddings to be pre-computed and stored in Profile.photo_embeddings
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Args:
            similarity_threshold: Min cosine similarity (0-1) to consider a match
        """
        self.similarity_threshold = similarity_threshold
        
        # We'll lazy-load the CLIP model on first use
        self.clip_model = None
        self.clip_processor = None
    
    def _ensure_clip_loaded(self):
        """Lazy load CLIP model to avoid loading if not needed."""
        if self.clip_model is None:
            try:
                import clip
                import torch
                
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.clip_model, self.clip_processor = clip.load("ViT-B/32", device=device)
                logger.info(f"CLIP loaded on device: {device}")
            except ImportError:
                raise ImportError(
                    "CLIP not installed. Install with: pip install openai-clip torch torchvision"
                )
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Embed a single image using CLIP.
        
        Args:
            image_path: Path or URL to image
            
        Returns:
            Embedding vector (512-dim for ViT-B/32) or None if error
        """
        self._ensure_clip_loaded()
        
        try:
            import clip
            from PIL import Image
            import torch
            
            # Load and preprocess image
            if image_path.startswith("http"):
                from io import BytesIO
                import requests
                response = requests.get(image_path, timeout=5)
                image = Image.open(BytesIO(response.content)).convert("RGB")
            else:
                image = Image.open(image_path).convert("RGB")
            
            # Get embedding
            with torch.no_grad():
                image_input = self.clip_processor(image).unsqueeze(0)
                embedding = self.clip_model.encode_image(image_input)
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)  # Normalize
            
            return embedding.cpu().numpy().flatten()
        except Exception as e:
            logger.error(f"Error embedding image {image_path}: {e}")
            return None
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed text using CLIP for text-to-image matching.
        Useful for searching "I like people who look like..." descriptions.
        
        Args:
            text: Description (e.g., "athletic blonde woman")
            
        Returns:
            Embedding vector
        """
        self._ensure_clip_loaded()
        
        try:
            import clip
            import torch
            
            with torch.no_grad():
                text_input = clip.tokenize([text])
                text_embedding = self.clip_model.encode_text(text_input)
                text_embedding = text_embedding / text_embedding.norm(dim=-1, keepdim=True)
            
            return text_embedding.cpu().numpy().flatten()
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        if vec1 is None or vec2 is None:
            return 0.0
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_similar_profiles(
        self,
        reference_embedding: np.ndarray,
        candidates: List[Profile],
        top_k: int = 10
    ) -> List[Tuple[Profile, float]]:
        """
        Find most similar profiles to a reference embedding.
        
        Args:
            reference_embedding: CLIP embedding to match against
            candidates: List of profiles to search through
            top_k: Return top K matches
            
        Returns:
            List of (Profile, similarity_score) tuples, sorted by similarity desc
        """
        scored_profiles = []
        
        for profile in candidates:
            if not profile.photo_embeddings:
                continue  # Skip profiles without embeddings
            
            # Take average of all photo embeddings for this profile
            valid_embeddings = [e for e in profile.photo_embeddings if e is not None]
            if not valid_embeddings:
                continue
            
            avg_embedding = np.mean(valid_embeddings, axis=0)
            similarity = self.cosine_similarity(reference_embedding, avg_embedding)
            
            if similarity >= self.similarity_threshold:
                scored_profiles.append((profile, similarity))
        
        # Sort by similarity descending
        scored_profiles.sort(key=lambda x: x[1], reverse=True)
        return scored_profiles[:top_k]
    
    def find_by_text_description(
        self,
        description: str,
        candidates: List[Profile],
        top_k: int = 10
    ) -> List[Tuple[Profile, float]]:
        """
        Find profiles matching a text description.
        Example: "Find women who look athletic and outdoorsy"
        
        Args:
            description: Text description of ideal appearance
            candidates: Profiles to search
            top_k: Return top K matches
            
        Returns:
            List of (Profile, similarity_score) tuples
        """
        text_embedding = self.embed_text(description)
        return self.find_similar_profiles(text_embedding, candidates, top_k)
    
    def batch_embed_profile_photos(self, profile: Profile) -> Profile:
        """
        Embed all photos for a profile using CLIP.
        Modifies the profile in-place.
        
        Args:
            profile: Profile to embed photos for
            
        Returns:
            Modified profile with photo_embeddings populated
        """
        embeddings = []
        
        for url in profile.photo_urls:
            embedding = self.embed_image(url)
            embeddings.append(embedding)
        
        profile.photo_embeddings = embeddings
        return profile
    
    def batch_embed_profiles(self, profiles: List[Profile]) -> List[Profile]:
        """
        Embed photos for multiple profiles.
        
        Args:
            profiles: List of profiles
            
        Returns:
            Same profiles with photo_embeddings populated
        """
        for i, profile in enumerate(profiles):
            self.batch_embed_profile_photos(profile)
            if (i + 1) % 10 == 0:
                logger.info(f"Embedded {i + 1}/{len(profiles)} profiles")
        
        return profiles
