import enum



class GenderEnum(enum.Enum):
    male = "male"
    female = "female"


class ApplicationStatusEnum(enum.Enum):
    draft = "draft"
    pending = "pending"
    under_review = "under_review"
    interview_scheduled = "interview_scheduled"
    accepted = "accepted"
    rejected = "rejected"
    withdrawn = "withdrawn"

class LevelEnum(str, enum.Enum):
    none = "none"
    beginner = "beginner"
    elementary = "elementary"
    intermediate = "intermediate"
    upper_intermediate = "upper_intermediate"
    advanced = "advanced"
    native = "native"