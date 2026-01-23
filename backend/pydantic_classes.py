from datetime import datetime, date, time
from typing import List, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, field_validator

from abc import ABC, abstractmethod

############################################
# Enumerations are defined here
############################################

class DatasetType(Enum):
    Validation = "Validation"
    Test = "Test"
    Training = "Training"

class ProjectStatus(Enum):
    Created = "Created"
    Pending = "Pending"
    Ready = "Ready"
    Closed = "Closed"
    Archived = "Archived"

class EvaluationStatus(Enum):
    Pending = "Pending"
    Archived = "Archived"
    Processing = "Processing"
    Custom = "Custom"
    Done = "Done"

class LicensingType(Enum):
    Proprietary = "Proprietary"
    Open_Source = "Open_Source"

############################################
# Classes are defined here
############################################
class CommentsCreate(BaseModel):
    Comments: str
    TimeStamp: datetime
    Name: str

class LegalRequirementCreate(BaseModel):
    principle: str
    standard: str
    legal_ref: str
    project_1: int  # N:1 Relationship (mandatory)

class ToolCreate(BaseModel):
    licensing: LicensingType
    source: str
    name: str
    version: str
    observation_1: Optional[List[int]] = None  # 1:N Relationship

class DatashapeCreate(BaseModel):
    accepted_target_values: str
    dataset_1: Optional[List[int]] = None  # 1:N Relationship
    f_date: Optional[List[int]] = None  # 1:N Relationship
    f_features: Optional[List[int]] = None  # 1:N Relationship

class ProjectCreate(BaseModel):
    name: str
    status: ProjectStatus
    involves: Optional[List[int]] = None  # 1:N Relationship
    legal_requirements: Optional[List[int]] = None  # 1:N Relationship
    eval: Optional[List[int]] = None  # 1:N Relationship

class EvaluationCreate(BaseModel):
    status: EvaluationStatus
    config: int  # N:1 Relationship (mandatory)
    ref: List[int]  # N:M Relationship
    project: int  # N:1 Relationship (mandatory)
    observations: Optional[List[int]] = None  # 1:N Relationship
    evaluates: List[int]  # N:M Relationship

class MeasureCreate(BaseModel):
    value: float
    uncertainty: float
    error: str
    unit: str
    observation: int  # N:1 Relationship (mandatory)
    measurand: int  # N:1 Relationship (mandatory)
    metric: int  # N:1 Relationship (mandatory)

class AssessmentElementCreate(ABC, BaseModel):
    description: str
    name: str

class ObservationCreate(AssessmentElementCreate):
    observer: str
    whenObserved: datetime
    eval: int  # N:1 Relationship (mandatory)
    tool: int  # N:1 Relationship (mandatory)
    measures: Optional[List[int]] = None  # 1:N Relationship
    dataset: int  # N:1 Relationship (mandatory)

class ConfParamCreate(AssessmentElementCreate):
    param_type: str
    value: str
    conf: int  # N:1 Relationship (mandatory)

class ConfigurationCreate(AssessmentElementCreate):
    eval: Optional[List[int]] = None  # 1:N Relationship
    params: Optional[List[int]] = None  # 1:N Relationship

class ElementCreate(AssessmentElementCreate):
    project: Optional[int] = None  # N:1 Relationship (optional)
    measure: Optional[List[int]] = None  # 1:N Relationship
    evalu: List[int]  # N:M Relationship
    eval: List[int]  # N:M Relationship

class DatasetCreate(ElementCreate):
    source: str
    dataset_type: DatasetType
    version: str
    licensing: LicensingType
    datashape: int  # N:1 Relationship (mandatory)
    observation_2: Optional[List[int]] = None  # 1:N Relationship
    models: Optional[List[int]] = None  # 1:N Relationship

class ModelCreate(ElementCreate):
    pid: str
    licensing: LicensingType
    source: str
    data: str
    dataset: int  # N:1 Relationship (mandatory)

class FeatureCreate(ElementCreate):
    min_value: float
    max_value: float
    feature_type: str
    date: int  # N:1 Relationship (mandatory)
    features: int  # N:1 Relationship (mandatory)

class MetricCreate(AssessmentElementCreate):
    derivedBy: List[int]  # N:M Relationship
    category: List[int]  # N:M Relationship
    measures: Optional[List[int]] = None  # 1:N Relationship

class DerivedCreate(MetricCreate):
    expression: str
    baseMetric: List[int]  # N:M Relationship

class DirectCreate(MetricCreate):
    pass

class MetricCategoryCreate(AssessmentElementCreate):
    metrics: List[int]  # N:M Relationship

