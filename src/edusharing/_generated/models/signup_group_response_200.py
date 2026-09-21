from enum import StrEnum


class SignupGroupResponse200(StrEnum):
    ALREADYINLIST = "AlreadyInList"
    ALREADYMEMBER = "AlreadyMember"
    INVALIDPASSWORD = "InvalidPassword"
    OK = "Ok"

    def __str__(self) -> str:
        return str(self.value)
