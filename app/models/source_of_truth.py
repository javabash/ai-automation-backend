from typing import List, Optional

from pydantic import BaseModel


class Experience(BaseModel):
    id: str
    title: str
    employer: str
    start_date: str  # "YYYY-MM"
    end_date: str  # "YYYY-MM"
    description: str
    skills: List[str]
    projects: List[str]
    outcomes: List[str]


class Project(BaseModel):
    id: str
    name: str
    summary: str
    tech_stack: List[str]
    outcomes: List[str]
    related_experience: Optional[str] = None


class Skill(BaseModel):
    name: str
    type: str  # language, framework, tool, etc.
    proficiency: str
    evidence: List[str]  # list of experience/project IDs


class Certification(BaseModel):
    name: str
    authority: str
    date: str  # "YYYY-MM" or year


class Education(BaseModel):
    degree: str
    institution: str
    date: str


class SourceOfTruth(BaseModel):
    experiences: List[Experience]
    projects: List[Project]
    skills: List[Skill]
    certifications: List[Certification]
    education: List[Education]
