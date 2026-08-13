#pragma once

#include <string>
#include <atomic>

namespace qvalidate {

class DeviceHealth {
public:
    explicit DeviceHealth();
    ~DeviceHealth() = default;

    double getTemperatureCelsius() const;
    double getHealthScore() const; // 0 to 100
    bool isHealthy() const;
    std::string getActiveFault() const { return m_activeFault; }

    void updateSensors(double cpuUsagePct, double memUsagePct);
    void setActiveFault(const std::string& faultName) { m_activeFault = faultName; }

private:
    std::atomic<double> m_temperatureCelsius;
    std::atomic<double> m_healthScore;
    std::string m_activeFault;
};

} // namespace qvalidate
