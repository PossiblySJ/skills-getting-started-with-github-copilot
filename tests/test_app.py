"""Tests for the FastAPI Mergington High School API"""


def test_get_root(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test that activities endpoint returns list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check that response is a dictionary
    assert isinstance(data, dict)
    
    # Check that Chess Club is in the activities
    assert "Chess Club" in data
    
    # Check the structure of an activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity(client):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify the student was added to participants
    activities = client.get("/activities").json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_student(client):
    """Test that duplicate signup returns error"""
    # First signup
    response1 = client.post(
        "/activities/Chess Club/signup?email=duplicate@mergington.edu"
    )
    assert response1.status_code == 200
    
    # Attempt duplicate signup
    response2 = client.post(
        "/activities/Chess Club/signup?email=duplicate@mergington.edu"
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_nonexistent_activity(client):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_from_activity(client):
    """Test unregistering a student from an activity"""
    # First signup
    client.post("/activities/Programming Class/signup?email=testunreg@mergington.edu")
    
    # Verify student is signed up
    activities = client.get("/activities").json()
    assert "testunreg@mergington.edu" in activities["Programming Class"]["participants"]
    
    # Unregister
    response = client.post(
        "/activities/Programming Class/unregister?email=testunreg@mergington.edu"
    )
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    
    # Verify student was removed
    activities = client.get("/activities").json()
    assert "testunreg@mergington.edu" not in activities["Programming Class"]["participants"]


def test_unregister_not_signed_up(client):
    """Test unregistering a student who is not signed up"""
    response = client.post(
        "/activities/Art Studio/unregister?email=notsignedup@mergington.edu"
    )
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_nonexistent_activity(client):
    """Test unregistering from non-existent activity"""
    response = client.post(
        "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_participant_count_updates(client):
    """Test that participant counts are correct after signup"""
    # Get initial state
    activities1 = client.get("/activities").json()
    initial_count = len(activities1["Tennis Club"]["participants"])
    
    # Signup
    client.post("/activities/Tennis Club/signup?email=counttest@mergington.edu")
    
    # Get updated state
    activities2 = client.get("/activities").json()
    updated_count = len(activities2["Tennis Club"]["participants"])
    
    # Verify count increased
    assert updated_count == initial_count + 1
