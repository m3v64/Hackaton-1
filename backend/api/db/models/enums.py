import enum

class Action(enum.Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class MembershipType(enum.Enum):
    ONETIME = "1-time per week"
    TWOTIME = "2-times per week"
    UNLIMITED = "unlimited"

class CourseType(enum.Enum):
    YOGA = "yoga"
    PILATES = "pilates"
    POLEDANCING = "pole dancing"
