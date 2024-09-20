from pydantic import BaseModel, ConfigDict


class CozeModel(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=()
    )
