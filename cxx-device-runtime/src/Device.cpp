#include "Device.hpp"
#include <thread>
#include <iostream>

namespace qvalidate {

Device::Device(std::string deviceId)
    : m_deviceId(std::move(deviceId)),
      m_state(State::POWERED_OFF),
      m_startTime(std::chrono::steady_clock::now()),
      m_cpu(8, 2.84),
      m_memory(8192.0),
      m_firmware("4.2.1", "BUILD-1042"),
      m_health() {}

std::string Device::getStateString() const {
    switch (m_state) {
        case State::POWERED_OFF: return "POWERED_OFF";
        case State::BOOTING: return "BOOTING";
        case State::INITIALIZING: return "INITIALIZING";
        case State::READY: return "READY";
        case State::DEGRADED: return "DEGRADED";
        case State::ERROR: return "ERROR";
        default: return "UNKNOWN";
    }
}

bool Device::powerOn(double& outBootDurationSec) {
    if (m_state != State::POWERED_OFF) {
        return false;
    }
    m_state = State::BOOTING;
    auto start = std::chrono::high_resolution_clock::now();
    
    // Simulate boot sequence stages
    std::this_thread::sleep_for(std::chrono::milliseconds(150));
    m_state = State::INITIALIZING;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    if (m_firmware.isCorrupted()) {
        m_state = State::ERROR;
        m_health.setActiveFault("CORRUPTED_FIRMWARE");
        return false;
    }

    m_state = State::READY;
    m_startTime = std::chrono::steady_clock::now();
    auto end = std::chrono::high_resolution_clock::now();
    outBootDurationSec = std::chrono::duration<double>(end - start).count();
    return true;
}

bool Device::powerOff() {
    m_state = State::POWERED_OFF;
    return true;
}

bool Device::reset(bool hardReset, double& outResetDurationSec) {
    auto start = std::chrono::high_resolution_clock::now();
    powerOff();
    bool booted = powerOn(outResetDurationSec);
    auto end = std::chrono::high_resolution_clock::now();
    outResetDurationSec = std::chrono::duration<double>(end - start).count();
    return booted;
}

bool Device::deployBuild(const std::string& buildId, const std::string& version, const std::string& payloadHash, double& outDeployDurationSec) {
    auto start = std::chrono::high_resolution_clock::now();
    std::this_thread::sleep_for(std::chrono::milliseconds(200));

    m_firmware.updateFirmware(version, buildId, payloadHash);
    
    // Auto reboot after firmware flash
    double bootDur = 0.0;
    reset(false, bootDur);

    auto end = std::chrono::high_resolution_clock::now();
    outDeployDurationSec = std::chrono::duration<double>(end - start).count();
    return m_state == State::READY;
}

bool Device::injectFault(const std::string& faultType, double intensity) {
    if (faultType == "CPU_OVERLOAD") {
        m_cpu.setOverload(true, intensity > 0.0 ? intensity : 98.5);
        m_health.setActiveFault("CPU_OVERLOAD");
        m_state = State::DEGRADED;
    } else if (faultType == "MEMORY_PRESSURE") {
        m_memory.setMemoryPressure(true, intensity > 0.0 ? intensity : 7800.0);
        m_health.setActiveFault("MEMORY_PRESSURE");
        m_state = State::DEGRADED;
    } else if (faultType == "CORRUPTED_FIRMWARE") {
        m_firmware.setCorrupted(true);
        m_state = State::ERROR;
        m_health.setActiveFault("CORRUPTED_FIRMWARE");
    } else if (faultType == "PROCESS_CRASH") {
        m_state = State::ERROR;
        m_health.setActiveFault("PROCESS_CRASH");
    } else {
        return false;
    }
    return true;
}

bool Device::clearFault() {
    m_cpu.setOverload(false);
    m_memory.setMemoryPressure(false);
    m_firmware.setCorrupted(false);
    m_health.setActiveFault("NONE");
    if (m_state == State::DEGRADED || m_state == State::ERROR) {
        m_state = State::READY;
    }
    return true;
}

void Device::tick() {
    m_cpu.updateUsage();
    m_memory.updateUsage();
    m_health.updateSensors(m_cpu.getUsagePercentage(), m_memory.getUsagePercentage());
}

} // namespace qvalidate
