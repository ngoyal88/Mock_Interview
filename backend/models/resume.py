from pydantic import BaseModel, Field
from typing import List, Optional


class PersonName(BaseModel):
    raw: str = ""
    first: str = ""
    last: str = ""


class Skill(BaseModel):
    name: str


class WorkExperience(BaseModel):
    jobTitle: str = ""
    organization: str = ""
    dates: str = ""
    jobDescription: str = ""


class EducationItem(BaseModel):
    degree: str = ""
    institution: str = ""
    dates: str = ""


class Project(BaseModel):
    name: str
    description: str = ""
    technologies: List[str] = []


class ResumeData(BaseModel):
    name: PersonName = PersonName()
    phoneNumbers: List[str] = Field(default_factory=list)
    emails: List[str] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    workExperience: List[WorkExperience] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    rawText: str = ""


class ResumeResponse(BaseModel):
    data: ResumeData
    meta: dict
    
