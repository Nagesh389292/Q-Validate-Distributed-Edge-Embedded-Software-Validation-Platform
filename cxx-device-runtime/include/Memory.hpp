#pragma once

#include <atomic>
#include <cstddef>

namespace qvalidate {

class Memory {
public:
    explicit Memory(double totalMB = 8192.0);
    ~Memory() = default;

    double getTotalMB() const { return m_totalMB; }
    double getUsedMB() const;
    double getFreeMB() const { return m_totalMB - getUsedMB(); }
    double getUsagePercentage() const { return (getUsedMB() / m_totalMB) * 100.0; }

    bool allocate(double amountMB);
    void free(double amountMB);
    void setMemoryPressure(bool enable, double targetUsedMB = 7800.0);
    bool isUnderPressure() const { return m_isUnderPressure; }

    void updateUsage();

private:
    double m_totalMB;
    std::atomic<double> m_usedMB;
    std::atomic<bool> m_isUnderPressure;
    double m_pressureTargetMB;
};

} // namespace qvalidate
