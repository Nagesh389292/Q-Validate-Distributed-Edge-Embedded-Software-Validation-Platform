#include "CPU.hpp"
#include <random>
#include <algorithm>

namespace qvalidate {

CPU::CPU(int numCores, double baseFreqGHz)
    : m_numCores(numCores),
      m_baseFreqGHz(baseFreqGHz),
      m_currentUsagePct(12.5),
      m_isOverloaded(false),
      m_overloadTargetPct(98.5) {}

double CPU::getUsagePercentage() const {
    return m_currentUsagePct.load();
}

void CPU::setOverload(bool enable, double loadTargetPct) {
    m_isOverloaded.store(enable);
    m_overloadTargetPct = loadTargetPct;
}

void CPU::updateUsage() {
    if (m_isOverloaded.load()) {
        m_currentUsagePct.store(std::min(100.0, m_overloadTargetPct));
    } else {
        static std::mt19937 gen(1337);
        std::uniform_real_distribution<double> dist(-2.5, 2.5);
        double current = m_currentUsagePct.load();
        double updated = std::clamp(current + dist(gen), 5.0, 45.0);
        m_currentUsagePct.store(updated);
    }
}

} // namespace qvalidate
