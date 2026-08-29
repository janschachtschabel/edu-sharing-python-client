"""b-api (Bildungs-API) -- the LLM gateway of OpenEduHub.

    from edusharing.bapi import BildungsAPI

    async with BildungsAPI.from_env() as llm:
        print(await llm.chat("Summarise: ..."))

Without a fixed model id the least loaded ready text model is chosen. The
quirks of the model families -- which body layout, where thinking must be
switched off, where the very same flag is rejected with 400 -- live in
``policy`` and are measured against the API there.

The gateway forwards more than chat. ``embeddings``, ``moderate`` and ``images``
have methods of their own, and ``call`` reaches the rest -- ``responses``,
``audio/speech``, ``batches``. Which routes are forwarded at all was measured,
not read: see ``passthrough``, whose docstring also says why ``/v3/api-docs``
cannot answer that question.

    vectors = await llm.embeddings(["a", "b"], model="text-embedding-3-small",
                                   provider="openai")
"""

from .client import BildungsAPI
from .passthrough import GeneratedImage, Moderation
from .policy import Model, build_body, pick_model, rank_models, read_answer

__all__ = ["BildungsAPI", "Model", "pick_model", "rank_models",
           "build_body", "read_answer",
           # Die durchgereichten OpenAI-Routen
           "Moderation", "GeneratedImage"]
