from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class AIRequest:
    prompt: str
    model_name: str | None = None
    system_text: str | None = None
    images: tuple[str, ...] = ()
    metadata: dict = field(default_factory=dict)
