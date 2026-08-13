#include "Device.hpp"
#include <iostream>
#include <thread>
#include <chrono>

int main(int argc, char** argv) {
    std::cout << "========================================================\n";
    std::cout << "   Q-Validate — Simulated Device Runtime (C++20 Engine)  \n";
    std::cout << "========================================================\n";

    std::string deviceId = "DEVICE-001";
    if (argc > 1) {
        deviceId = argv[1];
    }

    qvalidate::Device device(deviceId);
    std::cout << "[INFO] Initializing Device: " << device.getId() << std::endl;

    double bootDuration = 0.0;
    if (device.powerOn(bootDuration)) {
        std::cout << "[SUCCESS] Device booted into STATE: " << device.getStateString()
                  << " in " << bootDuration << " seconds." << std::endl;
    } else {
        std::cerr << "[ERROR] Device failed to boot." << std::endl;
    }

    std::cout << "[INFO] Running telemetry ticker daemon..." << std::endl;
    int tickCount = 0;
    while (true) {
        tickCount++;
        device.tick();
        std::cout << "  [Tick " << tickCount << "] CPU: " << device.getCPU().getUsagePercentage() << "%"
                  << " | Memory: " << device.getMemory().getUsedMB() << " / " << device.getMemory().getTotalMB() << " MB"
                  << " | Temp: " << device.getHealth().getTemperatureCelsius() << " degC"
                  << " | State: " << device.getStateString() << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }

    return 0;
}
