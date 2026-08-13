#include "Memory.hpp"
#include <algorithm>
#include <random>

namespace qvalidate {

Memory::Memory(double totalMB)
    : m_totalMB(totalMB),
      m_usedMB(1024.0),
      m_isUnderPressure(false),
      m_pressureTargetMB(7800.0) {}

double Memory::getUsedMB() const {
    return m_usedMB.load();
}

bool Memory::allocate(double amountMB) {
    double current = m_usedMB.load();
    if (current + amountMB > m_totalMB) {
        return false;
    }
    m_usedMB.store(current + amountMB);
    return true;
}

void Memory::free(double amountMB) {
    double current = m_usedMB.load();
    double updated = std::max(512.0, current - amountMB);
    m_usedMB.store(updated);
}

void Memory::setMemoryPressure(bool enable, double targetUsedMB) {
    m_isUnderPressure.store(enable);
    m_pressureTargetMB = targetUsedMB;
    if (enable) {
        m_usedMB.store(std::min(m_totalMB, targetUsedMB));
    }
}

void Memory::updateUsage() {
    if (m_isUnderPressure.load()) {
        m_usedMB.store(std::min(m_totalMB, m_pressureTargetMB));
    } else {
        static std::mt19937 gen(42);
        std::uniform_real_distribution<double> dist(-5.0, 5.0);
        double current = m_usedMB.load();
        double updated = std::clamp(current + dist(gen), 512.0, m_totalMB * 0.7);
        m_usedMB.store(updated);
    }
}

} // namespace qvalidate
