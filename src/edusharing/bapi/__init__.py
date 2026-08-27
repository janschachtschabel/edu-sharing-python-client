"""b-api (Bildungs-API) -- das LLM-Gateway von OpenEduHub.

    from edusharing.bapi import BildungsAPI

    async with BildungsAPI.from_env() as llm:
        print(await llm.chat("Fasse zusammen: ..."))

Ohne feste Modell-ID wird das am wenigsten ausgelastete bereite Textmodell
gewaehlt. Die Eigenheiten der Modellfamilien -- welcher Body-Aufbau, wo das
Denken abgeschaltet gehoert, wo dasselbe Flag mit 400 abgelehnt wird -- stecken
in ``policy`` und sind dort gegen die API gemessen.
"""

from .client import BildungsAPI
from .policy import Model, build_body, pick_model, read_answer

__all__ = ["BildungsAPI", "Model", "pick_model", "build_body", "read_answer"]
