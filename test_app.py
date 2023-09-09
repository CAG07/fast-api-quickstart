from fastapi.testclient import TestClient
from pymongo import MongoClient
from bson import ObjectId
import pytest
from main import app

client = TestClient(app)
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['courses']

def test_get_courses_no_params():
    response = client.get("/courses")
    assert response.status_code == 200

def test_get_courses_sort_by_alphabetical():
    response = client.get("/courses?sort_by=alphabetical")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x: x['name']) == courses
     

def test_get_courses_sort_by_date():
    response = client.get("/courses?sort_by=date")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x: x['date'], reverse=True) == courses

def test_get_courses_sort_by_rating():
    response = client.get("/courses?sort_by=rating")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x: x['rating']['total'], reverse=True) == courses

def test_get_courses_filter_by_domain():
    response = client.get("/courses?domain=mathematics")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])
    
def test_get_courses_filter_by_domain_and_sort_by_alphabetical():
    response = client.get("/courses?domain=mathematics&sort_by=alphabetical")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])
    assert sorted(courses, key=lambda x: x['name']) == courses
    
def test_get_courses_filter_by_domain_and_sort_by_date():
    response = client.get("/courses?domain=mathematics&sort_by=date")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])
    assert sorted(courses, key=lambda x: x['date'], reverse=True) == courses

def test_rate_chapter():
    course_id = "64f47e1e0aa503e60c129ae3"
    chapter_id = "1"
    rating = 1

    response = client.post(f"/courses/{course_id}/{chapter_id}?rating={rating}")

    assert response.status_code == 200

    # Check if the response body has the expected structure
    assert "name" in response.json()
    assert "rating" in response.json()
    assert "total" in response.json()["rating"]
    assert "count" in response.json()["rating"]

    assert response.json()["rating"]["total"] > 0
    assert response.json()["rating"]["count"] > 0


def test_rate_chapter_not_exists():
    response = client.post("/courses/64f47e1e0aa503e60c129ae3/990/rate", json={"rating": 1})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}
