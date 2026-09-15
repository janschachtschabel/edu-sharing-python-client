from enum import Enum


class SignupGroupResponse200(str, Enum):
    ALREADYINLIST = "AlreadyInList"
    ALREADYMEMBER = "AlreadyMember"
    INVALIDPASSWORD = "InvalidPassword"
    OK = "Ok"

    def __str__(self) -> str:
        return str(self.value)
