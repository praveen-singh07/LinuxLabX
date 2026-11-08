from pydantic import BaseModel, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    model_config = {"str_strip_whitespace": True}

    name: str = Field(min_length=2, max_length=100)


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)
    confirm_new_password: str = Field(min_length=8, max_length=72)

    @model_validator(mode="after")
    def validate_password_confirmation(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("New password confirmation does not match")
        if self.new_password == self.current_password:
            raise ValueError("New password must be different from the current password")
        return self


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }
