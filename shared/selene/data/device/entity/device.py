from dataclasses import dataclass
from datetime import datetime

from .geography import Geography
from .text_to_speech import TextToSpeech
from .wake_word import WakeWord


@dataclass
class Device(object):
    """Representation of a Device"""
    id: str
    name: str
    platform: str
    enclosure_version: str
    core_version: str
    wake_word: WakeWord
    text_to_speech: TextToSpeech
    geography: Geography = None
    placement: str = None
    last_contact_ts: datetime = None
