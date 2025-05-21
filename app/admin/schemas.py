from pydantic import BaseModel

class SUserUpdateRole(BaseModel):
    role_id: int