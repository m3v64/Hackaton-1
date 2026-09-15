from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.models.hackaton import Course, PlannedCourse
from api.db.session import get_db
from api.schemas.models import CourseCreate, CourseOut, PlannedCourseCreate, PlannedCourseOut

router = APIRouter(prefix="/courses")


@router.get("", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db)) -> list[Course]:
    return db.query(Course).order_by(Course.name).all()


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(body: CourseCreate, db: Session = Depends(get_db)) -> Course:
    if db.get(Course, body.name):
        raise HTTPException(status_code=409, detail="Course already exists.")
    course = Course(name=body.name)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.post("/planned", response_model=PlannedCourseOut, status_code=status.HTTP_201_CREATED)
def plan_course(body: PlannedCourseCreate, db: Session = Depends(get_db)) -> PlannedCourse:
    if not db.get(Course, body.course_name):
        raise HTTPException(status_code=404, detail="Course not found.")
    planned = PlannedCourse(
        course_name=body.course_name,
        planned_date=body.planned_date,
        assigned_at=body.assigned_at,
    )
    db.add(planned)
    db.commit()
    db.refresh(planned)
    return planned
