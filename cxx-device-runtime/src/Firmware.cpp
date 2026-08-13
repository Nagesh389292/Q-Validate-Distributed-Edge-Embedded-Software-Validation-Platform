#include "Firmware.hpp"

namespace qvalidate {

Firmware::Firmware(std::string version, std::string buildId)
    : m_version(std::move(version)),
      m_buildId(std::move(buildId)),
      m_checksum("a82f9c1b4e3f"),
      m_isCorrupted(false) {}

void Firmware::updateFirmware(const std::string& version, const std::string& buildId, const std::string& checksum) {
    m_version = version;
    m_buildId = buildId;
    m_checksum = checksum;
    m_isCorrupted = false;
}

} // namespace qvalidate
