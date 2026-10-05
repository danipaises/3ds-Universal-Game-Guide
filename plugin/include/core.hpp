#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace ugg {
constexpr uint32_t MaxPages = 1024, MaxText = 8192, PageRecordSize = 208, TitleRecordSize = 168;
constexpr uint64_t MaxGuideSize = 4 * 1024 * 1024;
constexpr const char *Version = "0.2.1-alpha";
struct Storage {
    virtual ~Storage() = default;
    virtual uint64_t size(const std::string &path) = 0;
    virtual bool read(const std::string &path, uint64_t offset, uint32_t count,
                      std::string &out) = 0;
    virtual bool write(const std::string &path, const std::string &data) = 0;
};
bool safeId(const std::string &s);
bool validUtf8(const std::string &s);
std::string fold(const std::string &s);
uint32_t crc32(const std::string &s);
uint32_t u32(const char *p);
uint64_t u64(const char *p);
void put32(std::string &out, uint32_t n);
struct Game {
    std::string id, name;
};
enum class Lookup { Found, Unknown, Corrupt };
Lookup lookup(Storage &io, const std::string &path, uint64_t tid, Game &game);
struct Page {
    std::string id, title, map;
    uint32_t flags = 0, offset = 0, length = 0, checksum = 0;
};
class Guide {
    Storage &io;
    std::string path;
    uint64_t bytes = 0;
    uint32_t indexFingerprint = 0;

  public:
    std::vector<Page> pages;
    Guide(Storage &store) : io(store) {}
    bool open(const std::string &file);
    bool openLanguage(const std::string &folder, const std::string &game,
                      const std::string &preferred, std::string &actual);
    uint32_t fingerprint() const { return indexFingerprint; }
    bool text(uint32_t page, std::string &out);
    bool search(const std::string &query, bool spoilers, std::vector<uint32_t> &hits);
};
constexpr uint32_t StateSize = 20 + MaxPages / 4;
struct State {
    uint32_t last = 0, line = 0;
    uint8_t favorites[MaxPages / 8] = {}, complete[MaxPages / 8] = {};
    bool get(bool done, uint32_t n) const;
    void toggle(bool done, uint32_t n);
    std::string encode(uint32_t guideFingerprint) const;
    bool decode(const std::string &data, uint32_t guideFingerprint);
};
struct Config {
    uint32_t hotkey = 13; // A + Select + Start; libctru/CTRPF key masks
    bool spoilers = false;
    bool touch = true, logging = false, remember = true;
    std::string language = "pt-BR";
    std::string encode() const;
    bool decode(const std::string &data);
};
bool migrateState(Storage &io, const std::string &path, const std::string &data,
                  uint32_t fingerprint, uint32_t pageCount, State &out);
class BufferedLog {
    bool enabled = false;
    std::string buffer;

  public:
    void enable(bool value);
    bool isEnabled() const { return enabled; }
    void add(const std::string &event);
    bool flush(Storage &io, const std::string &path);
    const std::string &text() const { return buffer; }
};
struct Tile {
    uint32_t width = 0, height = 0;
    std::vector<uint16_t> pixels;
};
bool loadTile(Storage &io, const std::string &path, Tile &tile);
} // namespace ugg
