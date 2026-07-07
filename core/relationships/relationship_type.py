from enum import Enum


class RelationshipType(Enum):
    FRONT_BACK = "front_back"
    NEGATIVE_PRINT = "negative_print"
    ORIGINAL_RESTORED = "original_restored"
    MASTER_DERIVATIVE = "master_derivative"
