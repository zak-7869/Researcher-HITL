import pytest
from pydantic import ValidationError
from app.schemas import ResearchRequest, ReviewRequest
from app.graph import evaluate

def test_topic_trimmed():
    assert ResearchRequest(topic="  agent evaluations  ").topic == "agent evaluations"

def test_blank_topic_rejected():
    with pytest.raises(ValidationError): ResearchRequest(topic="   ")

def test_iteration_limit():
    with pytest.raises(ValidationError): ResearchRequest(topic="valid query", max_iterations=4)

def test_evaluator_loops_when_evidence_weak():
    state = {"sources":[{"url":"https://example.com"}],"evidence":"tiny","iteration":1,"max_iterations":2}
    assert evaluate(state)["evaluation"]["decision"] == "research_again"

def test_evaluator_stops_at_budget():
    state = {"sources":[],"evidence":"","iteration":2,"max_iterations":2}
    assert evaluate(state)["evaluation"]["decision"] == "report"

def test_review_enum():
    assert ReviewRequest(decision="approve").decision == "approve"
    with pytest.raises(ValidationError): ReviewRequest(decision="shell")
