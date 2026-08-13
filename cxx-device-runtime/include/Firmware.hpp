#pragma once

#include <string>

namespace qvalidate {

class Firmware {
public:
    explicit Firmware(std::string version = "1.0.0", std::string buildId = "BUILD-0001");
    ~Firmware() = default;

    std::string getVersion() const { return m_version; }
    std::string getBuildId() const { return m_buildId; }
    std::string getChecksum() const { return m_checksum; }
    bool isCorrupted() const { return m_isCorrupted; }

    void updateFirmware(const std::string& version, const std::string& buildId, const std::string& checksum);
    void setCorrupted(bool corrupted) { m_isCorrupted = corrupted; }

private:
    std::string m_version;
    std::string m_buildId;
    std::string m_checksum;
    bool m_isCorrupted;
};

} // namespace qvalidate
