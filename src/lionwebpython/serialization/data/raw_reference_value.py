from dataclasses import dataclass


@dataclass
class RawReferenceValue:
    referred_id: str
    resolve_info: str
