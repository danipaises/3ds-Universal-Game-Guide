#include "core.hpp"
#include <algorithm>
#include <cstring>
#include <limits>
namespace ugg {
uint32_t u32(const char *p) {
    const auto *q = reinterpret_cast<const unsigned char *>(p);
    return q[0] | uint32_t(q[1]) << 8 | uint32_t(q[2]) << 16 | uint32_t(q[3]) << 24;
}
uint64_t u64(const char *p) { return u32(p) | uint64_t(u32(p + 4)) << 32; }
void put32(std::string &out, uint32_t n) {
    for (unsigned i = 0; i < 4; ++i)
        out += char(n >> (i * 8));
}
uint32_t crc32(const std::string &s) {
    uint32_t c = ~0u;
    for (unsigned char b : s) {
        c ^= b;
        for (int i = 0; i < 8; ++i)
            c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1)));
    }
    return ~c;
}
bool safeId(const std::string &s) {
    if (s.empty() || s.size() > 47 || s.front() == '-' || s.back() == '-')
        return false;
    for (char c : s)
        if (!(c >= 'a' && c <= 'z') && !(c >= '0' && c <= '9') && c != '-')
            return false;
    return true;
}
bool validUtf8(const std::string &s) {
    for (size_t i = 0; i < s.size();) {
        auto c = static_cast<unsigned char>(s[i++]);
        if (c < 0x80) {
            if (c < 32 && c != '\n' && c != '\t')
                return false;
            if (c == 127)
                return false;
            continue;
        }
        unsigned n;
        uint32_t cp, min;
        if (c >= 0xC2 && c <= 0xDF) {
            n = 1;
            cp = c & 31;
            min = 0x80;
        } else if (c >= 0xE0 && c <= 0xEF) {
            n = 2;
            cp = c & 15;
            min = 0x800;
        } else if (c >= 0xF0 && c <= 0xF4) {
            n = 3;
            cp = c & 7;
            min = 0x10000;
        } else
            return false;
        if (i + n > s.size())
            return false;
        while (n--) {
            auto b = static_cast<unsigned char>(s[i++]);
            if ((b & 0xC0) != 0x80)
                return false;
            cp = (cp << 6) | (b & 63);
        }
        if (cp < min || cp > 0x10FFFF || (cp >= 0xD800 && cp <= 0xDFFF))
            return false;
    }
    return true;
}
std::string fold(const std::string &s) {
    std::string r;
    const std::string accents = "ÀÁÂÃÄÅàáâãäåÈÉÊËèéêëÌÍÎÏìíîïÒÓÔÕÖòóôõöÙÚÛÜùúûüÇçÑñ";
    const std::string plain = "aaaaaaaaaaaaeeeeeeeeiiiiiiiioooooooooouuuuuuuuccnn";
    for (size_t i = 0; i < s.size();) {
        unsigned char c = s[i];
        if (c < 128) {
            r += char(c >= 'A' && c <= 'Z' ? c + 32 : c);
            ++i;
        } else if (i + 1 < s.size() && c == 0xC3) {
            auto pos = accents.find(s.substr(i, 2));
            if (pos != std::string::npos)
                r += plain[pos / 2];
            else
                r += s.substr(i, 2);
            i += 2;
        } else {
            r += s[i++];
        }
    }
    return r;
}
static bool field(const std::string &s, size_t off, size_t length, std::string &out) {
    size_t end = s.find('\0', off);
    if (end == std::string::npos || end >= off + length)
        return false;
    out = s.substr(off, end - off);
    return validUtf8(out) &&
           !std::any_of(out.begin(), out.end(), [](unsigned char c) { return c < 32 || c == 127; });
}
Lookup lookup(Storage &io, const std::string &path, uint64_t tid, Game &game) {
    game = {};
    std::string h;
    if (!io.read(path, 0, 8, h) || h.size() != 8 || h.compare(0, 4, "UGT1"))
        return Lookup::Corrupt;
    uint32_t n = u32(h.data() + 4);
    if (n > 4096 || io.size(path) != 8 + uint64_t(n) * TitleRecordSize)
        return Lookup::Corrupt;
    uint32_t lo = 0, hi = n;
    while (lo < hi) {
        uint32_t mid = lo + (hi - lo) / 2;
        std::string rec;
        if (!io.read(path, 8 + uint64_t(mid) * TitleRecordSize, TitleRecordSize, rec) ||
            rec.size() != TitleRecordSize)
            return Lookup::Corrupt;
        uint64_t v = u64(rec.data());
        if (v < tid)
            lo = mid + 1;
        else if (v > tid)
            hi = mid;
        else {
            if (!field(rec, 8, 64, game.id) || !safeId(game.id) || !field(rec, 72, 96, game.name))
                return Lookup::Corrupt;
            return Lookup::Found;
        }
    }
    return Lookup::Unknown;
}
bool Guide::open(const std::string &file) {
    pages.clear();
    indexFingerprint = 0;
    path = file;
    bytes = io.size(path);
    std::string h;
    if (bytes > MaxGuideSize || !io.read(path, 0, 12, h) || h.size() != 12 ||
        h.compare(0, 4, "UGG1"))
        return false;
    uint32_t n = u32(h.data() + 4), indexCrc = u32(h.data() + 8);
    if (!n || n > MaxPages || bytes < 12 + uint64_t(n) * PageRecordSize)
        return false;
    std::string index;
    if (!io.read(path, 12, n * PageRecordSize, index) || index.size() != n * PageRecordSize ||
        crc32(index) != indexCrc)
        return false;
    uint64_t previous = 12 + uint64_t(n) * PageRecordSize;
    std::vector<Page> next;
    next.reserve(n);
    for (uint32_t i = 0; i < n; ++i) {
        size_t off = i * PageRecordSize;
        Page p;
        if (!field(index, off, 48, p.id) || !safeId(p.id) || !field(index, off + 48, 96, p.title) ||
            !field(index, off + 160, 48, p.map) || (!p.map.empty() && !safeId(p.map)))
            return false;
        p.flags = u32(index.data() + off + 144);
        p.offset = u32(index.data() + off + 148);
        p.length = u32(index.data() + off + 152);
        p.checksum = u32(index.data() + off + 156);
        if (p.flags > 1 || !p.length || p.length > MaxText || p.offset != previous ||
            p.offset > bytes || p.length > bytes - p.offset)
            return false;
        if (std::any_of(next.begin(), next.end(), [&p](const Page &o) { return p.id == o.id; }))
            return false;
        previous = p.offset + p.length;
        next.push_back(p);
    }
    if (previous != bytes)
        return false;
    pages.swap(next);
    indexFingerprint = indexCrc;
    return true;
}
bool Guide::text(uint32_t page, std::string &out) {
    out.clear();
    if (page >= pages.size())
        return false;
    const auto &p = pages[page];
    if (!io.read(path, p.offset, p.length, out) || out.size() != p.length ||
        crc32(out) != p.checksum || !validUtf8(out)) {
        out.clear();
        return false;
    }
    return true;
}
bool Guide::openLanguage(const std::string &folder, const std::string &game,
                         const std::string &preferred, std::string &actual) {
    pages.clear();
    indexFingerprint = 0;
    actual.clear();
    if (!safeId(game) || (preferred != "pt-BR" && preferred != "en-US"))
        return false;
    actual = preferred;
    std::string file = folder + "/" + actual + "/" + game + ".ugg";
    if (io.size(file) == UINT64_MAX && preferred != "pt-BR") {
        actual = "pt-BR";
        file = folder + "/pt-BR/" + game + ".ugg";
    }
    return open(file);
}
bool Guide::search(const std::string &query, bool spoilers, std::vector<uint32_t> &hits) {
    hits.clear();
    if (query.size() < 2 || query.size() > 80 || !validUtf8(query) || pages.empty())
        return false;
    const std::string idx = path.substr(0, path.size() - 4) + ".ugs", term = fold(query);
    if (term.size() < 2)
        return false;
    std::string h;
    if (!io.read(idx, 0, 12, h) || h.size() != 12 || h.compare(0, 4, "UGS2"))
        return false;
    uint32_t n = u32(h.data() + 4);
    if (n > 131072 || u32(h.data() + 8) != indexFingerprint ||
        io.size(idx) != 12 + uint64_t(n) * 68)
        return false;
    uint32_t lo = 0, hi = n;
    while (lo < hi) {
        uint32_t mid = lo + (hi - lo) / 2;
        std::string rec, word;
        if (!io.read(idx, 12 + uint64_t(mid) * 68, 68, rec) || rec.size() != 68 ||
            !field(rec, 0, 64, word))
            return false;
        if (word < term)
            lo = mid + 1;
        else
            hi = mid;
    }
    for (uint32_t block = lo; block < n; block += 256) {
        uint32_t count = std::min<uint32_t>(256, n - block);
        std::string buffer;
        if (!io.read(idx, 12 + uint64_t(block) * 68, count * 68, buffer) ||
            buffer.size() != count * 68)
            return false;
        for (uint32_t i = 0; i < count; ++i) {
            size_t off = i * 68;
            std::string word;
            if (!field(buffer, off, 64, word))
                return false;
            uint32_t page = u32(buffer.data() + off + 64);
            if (page >= pages.size())
                return false;
            if (word.compare(0, term.size(), term) != 0)
                return true;
            if ((spoilers || !pages[page].flags) &&
                std::find(hits.begin(), hits.end(), page) == hits.end())
                hits.push_back(page);
            if (hits.size() >= MaxPages)
                return true;
        }
    }
    return true;
}

bool State::get(bool done, uint32_t n) const {
    if (n >= MaxPages)
        return false;
    const uint8_t *bits = done ? complete : favorites;
    return (bits[n / 8] & static_cast<uint8_t>(1u << (n % 8))) != 0;
}
void State::toggle(bool done, uint32_t n) {
    if (n >= MaxPages)
        return;
    uint8_t *bits = done ? complete : favorites;
    bits[n / 8] ^= static_cast<uint8_t>(1u << (n % 8));
}
std::string State::encode(uint32_t fingerprint) const {
    std::string out = "UGP2";
    put32(out, fingerprint);
    put32(out, last);
    put32(out, line);
    out.append(reinterpret_cast<const char *>(favorites), MaxPages / 8);
    out.append(reinterpret_cast<const char *>(complete), MaxPages / 8);
    put32(out, crc32(out));
    return out;
}
bool State::decode(const std::string &s, uint32_t fingerprint) {
    if (s.size() != StateSize || s.compare(0, 4, "UGP2") || u32(s.data() + 4) != fingerprint ||
        crc32(s.substr(0, StateSize - 4)) != u32(s.data() + StateSize - 4) ||
        u32(s.data() + 8) >= MaxPages || u32(s.data() + 12) > MaxText)
        return false;
    last = u32(s.data() + 8);
    line = u32(s.data() + 12);
    std::memcpy(favorites, s.data() + 16, MaxPages / 8);
    std::memcpy(complete, s.data() + 16 + MaxPages / 8, MaxPages / 8);
    return true;
}
static bool validHotkey(uint32_t k) {
    // Physical buttons available on Old 3DS; reject Rosalina default as a subset.
    constexpr uint32_t allowed = 0xFFF, rosalina = 512 | 128 | 4;
    constexpr uint32_t horizontal = 16 | 32, vertical = 64 | 128;
    if (k & ~allowed || (k & rosalina) == rosalina || (k & horizontal) == horizontal ||
        (k & vertical) == vertical)
        return false;
    unsigned count = 0;
    for (uint32_t n = k; n; n >>= 1)
        count += n & 1;
    return count >= 2;
}
std::string Config::encode() const {
    std::string s = "UGC2";
    put32(s, hotkey);
    put32(s, (spoilers ? 1 : 0) | (touch ? 0 : 2) | (logging ? 4 : 0) | (remember ? 0 : 8));
    s += language;
    s.resize(28, '\0');
    put32(s, crc32(s));
    return s;
}
bool Config::decode(const std::string &s) {
    std::string lang;
    if (s.size() != 32 || (s.compare(0, 4, "UGC1") && s.compare(0, 4, "UGC2")) ||
        crc32(s.substr(0, 28)) != u32(s.data() + 28) || !validHotkey(u32(s.data() + 4)) ||
        u32(s.data() + 8) > (s[3] == '1' ? 1u : 15u) || !field(s, 12, 16, lang) ||
        (lang != "pt-BR" && lang != "en-US"))
        return false;
    hotkey = u32(s.data() + 4);
    const uint32_t flags = u32(s.data() + 8);
    spoilers = flags & 1;
    touch = !(flags & 2);
    logging = flags & 4;
    remember = !(flags & 8);
    language = lang;
    return true;
}
bool migrateState(Storage &io, const std::string &path, const std::string &data,
                  uint32_t fingerprint, uint32_t pageCount, State &out) {
    std::string h, records;
    if (!pageCount || pageCount > MaxPages || !io.read(path, 0, 20, h) || h.size() != 20 ||
        h.compare(0, 4, "UGR1") || u32(h.data() + 8) != fingerprint)
        return false;
    const uint32_t count = u32(h.data() + 12);
    State old;
    if (!count || count > MaxPages || io.size(path) != 20 + uint64_t(count) * 4 ||
        !old.decode(data, u32(h.data() + 4)) || old.last >= count ||
        !io.read(path, 20, count * 4, records) || records.size() != count * 4 ||
        crc32(records) != u32(h.data() + 16))
        return false;
    State next;
    bool used[MaxPages] = {};
    for (uint32_t i = 0; i < count; ++i) {
        const uint32_t to = u32(records.data() + i * 4);
        if (to == UINT32_MAX)
            continue;
        if (to >= pageCount || used[to])
            return false;
        used[to] = true;
        if (old.get(false, i))
            next.toggle(false, to);
        if (old.get(true, i))
            next.toggle(true, to);
        if (old.last == i) {
            next.last = to;
            next.line = old.line;
        }
    }
    out = next;
    return true;
}
void BufferedLog::enable(bool value) {
    enabled = value;
    if (!enabled)
        buffer.clear();
}
void BufferedLog::add(const std::string &event) {
    if (!enabled)
        return;
    std::string line = validUtf8(event) ? event : "Invalid UTF-8 diagnostic";
    for (char &c : line)
        if (c == '\n' || c == '\t')
            c = ' ';
    while (line.size() > 500) {
        size_t n = line.size() - 1;
        while (n && (static_cast<unsigned char>(line[n]) & 0xC0) == 0x80)
            --n;
        line.resize(n);
    }
    line += '\n';
    while (buffer.size() + line.size() > 4096) {
        const auto end = buffer.find('\n');
        buffer.erase(0, end == std::string::npos ? buffer.size() : end + 1);
    }
    buffer += line;
}
bool BufferedLog::flush(Storage &io, const std::string &path) {
    return !enabled || buffer.empty() || io.write(path, buffer);
}
bool loadTile(Storage &io, const std::string &path, Tile &tile) {
    tile = {};
    std::string h;
    if (!io.read(path, 0, 16, h) || h.size() != 16 || h.compare(0, 4, "UGI1"))
        return false;
    uint32_t w = u32(h.data() + 4), height = u32(h.data() + 8), checksum = u32(h.data() + 12);
    if (!w || !height || w > 320 || height > 192 || io.size(path) != 16 + uint64_t(w) * height * 2)
        return false;
    std::string data;
    if (!io.read(path, 16, w * height * 2, data) || data.size() != w * height * 2 ||
        crc32(data) != checksum)
        return false;
    tile.width = w;
    tile.height = height;
    tile.pixels.resize(w * height);
    for (size_t i = 0; i < tile.pixels.size(); ++i)
        tile.pixels[i] = static_cast<unsigned char>(data[2 * i]) |
                         uint16_t(static_cast<unsigned char>(data[2 * i + 1])) << 8;
    return true;
}
} // namespace ugg
