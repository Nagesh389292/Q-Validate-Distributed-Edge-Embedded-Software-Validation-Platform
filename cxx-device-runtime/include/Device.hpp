#pragma once

#include "CPU.hpp"
#include "Memory.hpp"
#include "Firmware.hpp"
#include "DeviceHealth.hpp"

#include <string>
#include <chrono>
#include <memory>

namespace qvalidate {

enum class State {
    POWERED_OFF = 0,
    BOOTING = 1,
    INITIALIZING = 2,
    READY = 3,
    DEGRADED = 4,
    ERROR = 5
};

class Device {
public:
    explicit Device(std::string deviceId = "DEVICE-001");
    ~Device() = default;

    std::string getId() const { return m_deviceId; }
    State getState() const { return m_state; }
    std::string getStateString() const;

    CPU& getCPU() { return m_cpu; }
    Memory& getMemory() { return m_memory; }
    Firmware& getFirmware() { return m_firmware; }
    DeviceHealth& getHealth() { return m_health; }

    bool powerOn(double& outBootDurationSec);
    bool powerOff();
    bool reset(bool hardReset, double& outResetDurationSec);
    bool deployBuild(const std::string& buildId, const std::string& version, const std::string& payloadHash, double& outDeployDurationSec);
    
    bool injectFault(const std::string& faultType, double intensity);
    bool clearFault();

    void tick(); // Update simulation stats

private:
    std::string m_deviceId;
    State m_state;
    std::chrono::steady_clock::time_point m_startTime;
    
    CPU m_cpu;
    Memory m_memory;
    Firmware m_firmware;
    DeviceHealth m_health;
};

} // namespace qvalidate
