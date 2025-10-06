from app.core.scoring_model import compute_score, WEIGHTS, CAPS
import pytest

def test_compute_score_baseline():
    """Test baseline scoring for restaurante"""
    raw = {"competition":10,"offices":120,"schools":3,"parks":2,"transit":15,"flow_kde":20,"mix":0.5}
    score, feats, expl = compute_score('restaurante', raw)
    assert 0 <= score <= 100
    assert any(f['name']=='flow_kde' for f in feats)

def test_compute_score_restaurante():
    """Test restaurante scoring with realistic values"""
    raw = {
        "competition": 12,
        "offices": 45,
        "schools": 2,
        "parks": 1,
        "transit": 8,
        "flow_kde": 25.0,
        "mix": 0.72,
        "street_centrality": 0.15,
        "dist_transit_m": 150.0
    }
    score, feats, expl = compute_score('restaurante', raw)
    
    # Basic assertions
    assert 0 <= score <= 100
    assert len(feats) > 0
    assert 'flow_kde' in expl or 'offices' in expl or 'transit' in expl
    
    # Check that flow_kde has positive contribution (major factor for restaurante)
    flow_feat = next((f for f in feats if f['name'] == 'flow_kde'), None)
    assert flow_feat is not None
    assert flow_feat['weight'] == 0.35  # Highest weight for restaurante
    assert flow_feat['contribution'] > 0

def test_compute_score_academia():
    """Test academia scoring"""
    raw = {
        "competition": 5,
        "offices": 30,
        "schools": 3,
        "parks": 4,
        "transit": 10,
        "flow_kde": 15.0,
        "mix": 0.65,
        "street_centrality": 0.20
    }
    score, feats, expl = compute_score('academia', raw)
    
    assert 0 <= score <= 100
    
    # Check that parks has significant weight for academia
    parks_feat = next((f for f in feats if f['name'] == 'parks'), None)
    assert parks_feat is not None
    assert parks_feat['weight'] == 0.25  # Major factor for academia

def test_compute_score_varejo_moda():
    """Test varejo_moda scoring"""
    raw = {
        "competition": 20,
        "offices": 80,
        "schools": 1,
        "parks": 0,
        "transit": 12,
        "flow_kde": 35.0,
        "mix": 0.80,
        "street_centrality": 0.35
    }
    score, feats, expl = compute_score('varejo_moda', raw)
    
    assert 0 <= score <= 100
    
    # Check that flow_kde is important for varejo
    flow_feat = next((f for f in feats if f['name'] == 'flow_kde'), None)
    assert flow_feat is not None
    assert flow_feat['weight'] == 0.30
    
    # Competition should have negative impact
    comp_feat = next((f for f in feats if f['name'] == 'competition'), None)
    assert comp_feat is not None
    assert comp_feat['weight'] == -0.25  # Strongest negative weight

def test_compute_score_high_competition_penalty():
    """Test that high competition reduces score"""
    base_raw = {
        "competition": 5,
        "offices": 100,
        "schools": 5,
        "parks": 3,
        "transit": 15,
        "flow_kde": 30.0,
        "mix": 0.75,
        "street_centrality": 0.25
    }
    
    high_comp_raw = base_raw.copy()
    high_comp_raw["competition"] = 45
    
    score_low_comp, _, _ = compute_score('restaurante', base_raw)
    score_high_comp, _, _ = compute_score('restaurante', high_comp_raw)
    
    # High competition should result in lower score
    assert score_high_comp < score_low_comp

def test_compute_score_perfect_location():
    """Test scoring for an ideal location"""
    perfect = {
        "competition": 0,
        "offices": 300,
        "schools": 20,
        "parks": 10,
        "transit": 40,
        "flow_kde": 50.0,
        "mix": 1.0,
        "street_centrality": 1.0
    }
    score, _, _ = compute_score('restaurante', perfect)
    
    # Should get a very high score
    assert score >= 85

def test_compute_score_poor_location():
    """Test scoring for a poor location"""
    poor = {
        "competition": 50,
        "offices": 0,
        "schools": 0,
        "parks": 0,
        "transit": 0,
        "flow_kde": 0.0,
        "mix": 0.0,
        "street_centrality": 0.0
    }
    score, _, _ = compute_score('restaurante', poor)
    
    # Should get a low score
    assert score <= 40

def test_compute_score_feature_contributions():
    """Test that feature contributions are calculated correctly"""
    raw = {
        "competition": 10,
        "offices": 50,
        "schools": 5,
        "parks": 2,
        "transit": 10,
        "flow_kde": 20.0,
        "mix": 0.6,
        "street_centrality": 0.15
    }
    score, feats, expl = compute_score('academia', raw)
    
    # Check that all contributions add up
    total_contrib = sum(f['contribution'] for f in feats if f['name'] in WEIGHTS['academia'])
    
    # Score should be based on weighted sum
    expected_score = max(0.0, min(100.0, (total_contrib + 1) * 50))
    assert abs(score - expected_score) < 0.1

def test_compute_score_explanation_format():
    """Test that explanation contains top contributors"""
    raw = {
        "competition": 10,
        "offices": 100,
        "schools": 5,
        "parks": 3,
        "transit": 15,
        "flow_kde": 30.0,
        "mix": 0.7,
        "street_centrality": 0.2
    }
    score, feats, expl = compute_score('restaurante', raw)
    
    # Explanation should mention principais fatores
    assert "Principais fatores:" in expl
    
    # Should contain at least one feature name
    feature_names = [f['name'] for f in feats]
    assert any(name in expl for name in feature_names)

def test_weights_defined_for_all_business_types():
    """Test that weights are defined for all business types"""
    business_types = ['restaurante', 'academia', 'varejo_moda']
    
    for bt in business_types:
        assert bt in WEIGHTS
        assert isinstance(WEIGHTS[bt], dict)
        assert len(WEIGHTS[bt]) > 0

def test_caps_defined():
    """Test that caps are defined for all features"""
    required_caps = ['competition', 'offices', 'schools', 'parks', 'transit', 'flow_kde', 'mix']
    
    for cap in required_caps:
        assert cap in CAPS
        assert CAPS[cap] > 0

def test_compute_score_handles_missing_features():
    """Test that scoring handles missing features gracefully"""
    incomplete_raw = {
        "competition": 10,
        "flow_kde": 20.0
    }
    
    # Should not raise an error
    score, feats, expl = compute_score('restaurante', incomplete_raw)
    assert 0 <= score <= 100

def test_compute_score_normalization():
    """Test that features are normalized correctly"""
    raw = {
        "competition": 100,  # Over cap of 50
        "offices": 500,      # Over cap of 300
        "flow_kde": 80.0,    # Over cap of 50
        "transit": 50,       # Over cap of 40
        "mix": 1.2           # Over cap of 1.0 (should be clamped)
    }
    
    score, feats, expl = compute_score('restaurante', raw)
    
    # Score should still be between 0-100
    assert 0 <= score <= 100
    
    # Check that normalized values are capped
    for feat in feats:
        if feat['name'] in CAPS:
            # contribution = normalized_value * weight
            # normalized_value should be <= 1.0
            if feat['weight'] != 0:
                norm_val = feat['contribution'] / feat['weight']
                assert -1.0 <= norm_val <= 1.0
