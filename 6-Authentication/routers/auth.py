from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session, select
from starlette import status

from db import get_db_session
from schema import UserOutput, User

# ============ Step 1: Security Scheme Definition ============
security = HTTPBasic()
"""
HTTPBasic object functions:
1. Tells FastAPI this API requires HTTP Basic authentication
2. Automatically displays authentication requirements in OpenAPI docs
3. When used as dependency, automatically parses Authorization header
4. If no authentication info provided, automatically returns 401 status code
"""


# ============ Step 3: User Authentication Dependency ============
def get_current_user(
    # Dependency 1: HTTP Basic Auth - automatically parses Authorization header
    # Expected format: Authorization: Basic base64(username:password)
    credentials: HTTPBasicCredentials = Depends(security),

    # Dependency 2: Database session for user lookup
    session: Session = Depends(get_db_session),
) -> UserOutput:
    """
    User authentication workflow:
    1. security automatically parses HTTP Basic Auth header
    2. Extracts username and password into credentials object
    3. Uses session to query database and verify user
    4. Returns user info OR raises 401 exception

    Key points about this function:
    - This is a DEPENDENCY FUNCTION, not a route handler
    - It will be called by FastAPI BEFORE the actual route function
    - The return value becomes the injected dependency value
    - If exception is raised, route function never executes
    """

    # Query database for user by username
    # credentials.username and credentials.password are automatically populated by security
    query = select(User).where(User.username == credentials.username)
    user = session.exec(query).first()

    # Verify user exists and password is correct
    if user and user.verify_password(credentials.password):
        # CRITICAL: This return value is what gets injected into route functions
        # The UserOutput object will be passed to any route that depends on get_current_user
        return UserOutput.model_validate(user)
    else:
        # Authentication failed - raise 401 exception
        # This stops execution - route function will never be called
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},  # Tells client to use Basic auth
        )

