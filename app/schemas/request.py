from re import S
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional, List

class MetricsAnalysisRequest(BaseModel):
    application_id: int
    
    blackbox_probe_name: str 
    container_name: str

    lookback_window: str = Field("5m" , pattern=r"^[0-9]+[smhd]$")

    selection_mode: str = "test_round"
    test_round_id: Optional[int] = None
    manual_start: Optional[datetime] = None
    manual_end: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_times(self) -> 'MetricsAnalysisRequest':
        """ validate input schema time range logic"""

        if self.selection_mode =="test_round" and not self.test_round_id:
            raise ValueError("Must provide test_round_id for 'test_round' selection_mode")
        if self.selection_mode =="manual" and (not self.manual_start or not self.manual_end):
            raise ValueError("Must provide manual_start and manual_end for 'manual' selection_mode")
        return self

class ApplicationLookup(BaseModel):
    id :int 
    name : str
    
    class Config:
        from_attributes = True

class TestRoundLookup(BaseModel):
    id: int 
    script_id: int
    script_name: str
    status : str
    start_time: datetime         
    end_time: Optional[datetime]

    class Config:
        from_attributes = True