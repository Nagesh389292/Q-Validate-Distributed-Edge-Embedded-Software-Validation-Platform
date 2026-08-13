from fastapi import APIRouter
from qvalidate.tia import TestImpactAnalysisEngine
from qvalidate.api.schemas import TIARequest, TIAResponse

router = APIRouter(prefix="/regressions", tags=["Regression & Test Impact Analysis (TIA)"])
tia_engine = TestImpactAnalysisEngine()

@router.post("/impact-analysis", response_model=TIAResponse)
def perform_test_impact_analysis(req: TIARequest):
    """
    Perform Test Impact Analysis (TIA) on modified source code files.
    Maps changed files/components to affected test cases, returning the selected targeted regression suite.
    """
    analysis = tia_engine.analyze_impact(req.changed_files)
    return analysis
