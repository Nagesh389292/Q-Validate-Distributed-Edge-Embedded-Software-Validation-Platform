#include "DeviceHealth.hpp"
#include <algorithm>

namespace qvalidate {

DeviceHealth::DeviceHealth()
    : m_temperatureCelsius(42.5),
      m_healthScore(100.0),
      m_activeFault("NONE") {}

double DeviceHealth::getTemperatureCelsius() const {
    return m_temperatureCelsius.load();
}

double DeviceHealth::getHealthScore() const {
    return m_healthScore.load();
}

bool DeviceHealth::isHealthy() const {
    return m_healthScore.load() > 70.0 && m_activeFault == "NONE";
}

void DeviceHealth::updateSensors(double cpuUsagePct, double memUsagePct) {
    // Base temperature calculation based on CPU & Memory load
    double targetTemp = 35.0 + (cpuUsagePct * 0.45) + (memUsagePct * 0.15);
    m_temperatureCelsius.store(targetTemp);

    double score = 100.0;
    if (cpuUsagePct > 90.0) score -= 25.0;
    if (memUsagePct > 90.0) score -= 25.0;
    if (targetTemp > 75.0) score -= 30.0;
    if (m_activeFault != "NONE") score -= 40.0;

    m_healthScore.store(std::max(0.0, score));
}

} // namespace qvalidate
