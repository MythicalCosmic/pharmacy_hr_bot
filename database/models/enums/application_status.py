import enum



class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class ApplicationStatusEnum(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"