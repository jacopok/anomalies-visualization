import pytest
import numpy as np
from conversion_formulas import mean_anomaly_from_true, true_anomaly_from_eccentric, eccentric_anomaly_from_mean

@pytest.mark.parametrize('eccentricity', np.linspace(0, 0.9, num=10))
def test_circular_conversion(eccentricity):
    mean_anomaly = np.linspace(0, 2*np.pi, num=100)
    
    recomputed_mean = mean_anomaly_from_true(
        true_anomaly_from_eccentric(
            eccentric_anomaly_from_mean(
                mean_anomaly, 
                eccentricity), 
            eccentricity),
        eccentricity)
    
    assert np.allclose(mean_anomaly, recomputed_mean)