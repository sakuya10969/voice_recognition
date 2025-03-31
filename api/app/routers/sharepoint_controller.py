from fastapi import APIRouter

from app.handlers.sharepoint_handler import get_sites, get_directories, get_subdirectories

router = APIRouter()

router.get("/sites")(get_sites)
router.get("/directories")(get_directories)
router.get("/subdirectories")(get_subdirectories)
