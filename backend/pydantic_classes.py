from datetime import datetime, date, time
from typing import List, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, field_validator

from abc import ABC, abstractmethod

############################################
# Enumerations are defined here
############################################

class EvaluationStatus(Enum):
    Processing = "Processing"
    Pending = "Pending"
    Archived = "Archived"
    Custom = "Custom"
    Done = "Done"

class DatasetType(Enum):
    Validation = "Validation"
    Test = "Test"
    Training = "Training"

class ProjectStatus(Enum):
    Ready = "Ready"
    Created = "Created"
    Closed = "Closed"
    Pending = "Pending"
    Archived = "Archived"

class LicensingType(Enum):
    Open_source = "Open_source"
    Proprietary = "Proprietary"

############################################
# Classes are defined here
############################################
class LegalRequirementCreate(BaseModel):
    principle: str
    standard: str
    legal_ref: str
    project_1: int  # N:1 Relationship (mandatory)

class ToolCreate(BaseModel):
    licensing: LicensingType
    name: str
    source: str
    version: str
    observation_1: Optional[List[int]] = None  # 1:N Relationship

class DatashapeCreate(BaseModel):
    accepted_target_values: str
    dataset_1: Optional[List[int]] = None  # 1:N Relationship
    f_features: Optional[List[int]] = None  # 1:N Relationship
    f_date: Optional[List[int]] = None  # 1:N Relationship

class ProjectCreate(BaseModel):
    name: str
    status: ProjectStatus
    legal_requirements: Optional[List[int]] = None  # 1:N Relationship
    involves: Optional[List[int]] = None  # 1:N Relationship
    eval: Optional[List[int]] = None  # 1:N Relationship

class EvaluationCreate(BaseModel):
    status: EvaluationStatus
    observations: Optional[List[int]] = None  # 1:N Relationship
    ref: List[int]  # N:M Relationship
    config: int  # N:1 Relationship (mandatory)
    evaluates: List[int]  # N:M Relationship
    project: int  # N:1 Relationship (mandatory)

class MeasureCreate(BaseModel):
    unit: str
    error: str
    uncertainty: float
    value: float
    observation: int  # N:1 Relationship (mandatory)
    metric: int  # N:1 Relationship (mandatory)
    measurand: int  # N:1 Relationship (mandatory)

class AssessmentElementCreate(ABC, BaseModel):
    description: str
    name: str

class ConfigurationCreate(AssessmentElementCreate):
    eval: Optional[List[int]] = None  # 1:N Relationship
    params: Optional[List[int]] = None  # 1:N Relationship

class ObservationCreate(AssessmentElementCreate):
    whenObserved: datetime
    observer: str
    tool: int  # N:1 Relationship (mandatory)
    eval: int  # N:1 Relationship (mandatory)
    dataset: int  # N:1 Relationship (mandatory)
    measures: Optional[List[int]] = None  # 1:N Relationship

class ElementCreate(AssessmentElementCreate):
    evalu: List[int]  # N:M Relationship
    measure: Optional[List[int]] = None  # 1:N Relationship
    eval: List[int]  # N:M Relationship
    project: Optional[int] = None  # N:1 Relationship (optional)

class ModelCreate(ElementCreate):
    source: str
    pid: str
    data: str
    licensing: LicensingType
    dataset: int  # N:1 Relationship (mandatory)

class FeatureCreate(ElementCreate):
    min_value: float
    feature_type: str
    max_value: float
    features: int  # N:1 Relationship (mandatory)
    date: int  # N:1 Relationship (mandatory)

class DatasetCreate(ElementCreate):
    version: str
    dataset_type: DatasetType
    licensing: LicensingType
    source: str
    observation_2: Optional[List[int]] = None  # 1:N Relationship
    datashape: int  # N:1 Relationship (mandatory)
    models: Optional[List[int]] = None  # 1:N Relationship

class ConfParamCreate(AssessmentElementCreate):
    value: str
    param_type: str
    conf: int  # N:1 Relationship (mandatory)

class MetricCreate(AssessmentElementCreate):
    category: List[int]  # N:M Relationship
    measures: Optional[List[int]] = None  # 1:N Relationship
    derivedBy: List[int]  # N:M Relationship

class DerivedCreate(MetricCreate):
    expression: str
    baseMetric: List[int]  # N:M Relationship

class DirectCreate(MetricCreate):
    pass

class MetricCategoryCreate(AssessmentElementCreate):
    metrics: List[int]  # N:M Relationship

