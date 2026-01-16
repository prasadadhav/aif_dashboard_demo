from datetime import datetime, date, time
from typing import List, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, field_validator

from abc import ABC, abstractmethod

############################################
# Enumerations are defined here
############################################

class ProjectStatus(Enum):
    Archived = "Archived"
    Created = "Created"
    Closed = "Closed"
    Pending = "Pending"
    Ready = "Ready"

class LicensingType(Enum):
    Proprietary = "Proprietary"
    Open_source = "Open_source"

class DatasetType(Enum):
    Training = "Training"
    Validation = "Validation"
    Test = "Test"

class EvaluationStatus(Enum):
    Archived = "Archived"
    Processing = "Processing"
    Done = "Done"
    Custom = "Custom"
    Pending = "Pending"

############################################
# Classes are defined here
############################################
class LegalRequirementCreate(BaseModel):
    legal_ref: str
    standard: str
    principle: str
    project_1: int  # N:1 Relationship (mandatory)

class ToolCreate(BaseModel):
    version: str
    source: str
    licensing: LicensingType
    name: str
    observation_1: Optional[List[int]] = None  # 1:N Relationship

class DatashapeCreate(BaseModel):
    accepted_target_values: str
    f_features: Optional[List[int]] = None  # 1:N Relationship
    dataset_1: Optional[List[int]] = None  # 1:N Relationship
    f_date: Optional[List[int]] = None  # 1:N Relationship

class ProjectCreate(BaseModel):
    status: ProjectStatus
    name: str
    legal_requirements: Optional[List[int]] = None  # 1:N Relationship
    involves: Optional[List[int]] = None  # 1:N Relationship
    eval: Optional[List[int]] = None  # 1:N Relationship

class EvaluationCreate(BaseModel):
    status: EvaluationStatus
    observations: Optional[List[int]] = None  # 1:N Relationship
    evaluates: List[int]  # N:M Relationship
    project: int  # N:1 Relationship (mandatory)
    ref: List[int]  # N:M Relationship
    config: int  # N:1 Relationship (mandatory)

class MeasureCreate(BaseModel):
    error: str
    uncertainty: float
    value: float
    unit: str
    metric: int  # N:1 Relationship (mandatory)
    observation: int  # N:1 Relationship (mandatory)
    measurand: int  # N:1 Relationship (mandatory)

class AssessmentElementCreate(ABC, BaseModel):
    name: str
    description: str

class ObservationCreate(AssessmentElementCreate):
    whenObserved: datetime
    observer: str
    eval: int  # N:1 Relationship (mandatory)
    measures: Optional[List[int]] = None  # 1:N Relationship
    tool: int  # N:1 Relationship (mandatory)
    dataset: int  # N:1 Relationship (mandatory)

class ConfParamCreate(AssessmentElementCreate):
    param_type: str
    value: str
    conf: int  # N:1 Relationship (mandatory)

class ConfigurationCreate(AssessmentElementCreate):
    params: Optional[List[int]] = None  # 1:N Relationship
    eval: Optional[List[int]] = None  # 1:N Relationship

class ElementCreate(AssessmentElementCreate):
    evalu: List[int]  # N:M Relationship
    project: Optional[int] = None  # N:1 Relationship (optional)
    eval: List[int]  # N:M Relationship
    measure: Optional[List[int]] = None  # 1:N Relationship

class DatasetCreate(ElementCreate):
    dataset_type: DatasetType
    source: str
    version: str
    licensing: LicensingType
    models: Optional[List[int]] = None  # 1:N Relationship
    observation_2: Optional[List[int]] = None  # 1:N Relationship
    datashape: int  # N:1 Relationship (mandatory)

class ModelCreate(ElementCreate):
    data: str
    pid: str
    licensing: LicensingType
    source: str
    dataset: int  # N:1 Relationship (mandatory)

class FeatureCreate(ElementCreate):
    max_value: float
    feature_type: str
    min_value: float
    features: int  # N:1 Relationship (mandatory)
    date: int  # N:1 Relationship (mandatory)

class MetricCreate(AssessmentElementCreate):
    measures: Optional[List[int]] = None  # 1:N Relationship
    category: List[int]  # N:M Relationship
    derivedBy: List[int]  # N:M Relationship

class DerivedCreate(MetricCreate):
    expression: str
    baseMetric: List[int]  # N:M Relationship

class DirectCreate(MetricCreate):
    pass

class MetricCategoryCreate(AssessmentElementCreate):
    metrics: List[int]  # N:M Relationship

