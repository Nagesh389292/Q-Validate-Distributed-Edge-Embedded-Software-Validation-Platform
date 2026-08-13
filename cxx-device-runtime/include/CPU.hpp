#pragma once

#include <string>
#include <chrono>
#include <atomic>

namespace qvalidate {

class CPU {
public:
    explicit CPU(int numCores = 8, double baseFreqGHz = 2.84);
    ~CPU() = default;

    double getUsagePercentage() const;
    int getNumCores() const { return m_numCores; }
    double getFrequencyGHz() const { return m_baseFreqGHz; }
    
    void setOverload(bool enable, double loadTargetPct = 98.5);
    bool isOverloaded() const { return m_isOverloaded; }

    void updateUsage();

private:
    int m_numCores;
    double m_baseFreqGHz;
    std::atomic<double> m_currentUsagePct;
    std::atomic<bool> m_isOverloaded;
    double m_overloadTargetPct;
};

} // namespace qvalidate
