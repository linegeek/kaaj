from fastapi import APIRouter

from app.api.v1.lenders import router as lenders_router
from app.api.v1.applications import router as applications_router
from app.api.v1.underwriting import router as underwriting_router
from app.api.v1.reference import router as reference_router
from app.api.v1.parse_policy import router as parse_policy_router

router = APIRouter()

router.include_router(lenders_router)
router.include_router(applications_router)
router.include_router(underwriting_router)
router.include_router(reference_router)
router.include_router(parse_policy_router)
