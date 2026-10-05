# Run through scripts/build-plugin.sh (workspace paths with spaces supported).
include $(DEVKITARM)/3ds_rules
THREEGXTOOL ?= ../.deps/3gxtool-current/3gxtool
CTRPFLIB ?= /work/.deps/ctrpluginframework-0.8.0/Library
CXX := $(DEVKITARM)/bin/arm-none-eabi-g++
ARCH := -march=armv6k -mtune=mpcore -mfloat-abi=hard -mtp=soft
CPPFLAGS := -isystem $(CTRPFLIB)/include -isystem $(CTRULIB)/include -Iinclude -D__3DS__
CXXFLAGS := $(ARCH) -Os -g3 -Wall -Wextra -Werror -std=gnu++20 -fno-exceptions -fno-rtti -ffunction-sections -fdata-sections -fno-strict-aliasing -mword-relocations
LDFLAGS := $(ARCH) -T3gx.ld -Wl,--gc-sections,--section-start,.text=0x07000100 -L$(CTRPFLIB)/lib -L$(CTRULIB)/lib
SOURCES := source/main.cpp source/core.cpp source/boot.cpp
OBJECTS := $(patsubst source/%.cpp,build/%.o,$(SOURCES))
all: default.3gx
build/%.o: source/%.cpp include/core.hpp include/boot.hpp
	@mkdir -p build
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -MMD -MP -c $< -o $@
default.elf: $(OBJECTS) $(CTRPFLIB)/lib/libctrpf.a 3gx.ld
	$(CXX) $(LDFLAGS) -Wl,-Map=default.map $(OBJECTS) -lctrpf -lctru -lm -o $@
build-minimal/%.o: source/%.cpp include/boot.hpp
	@mkdir -p build-minimal
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -DUGG_MINIMAL -MMD -MP -c $< -o $@
default-minimal.elf: build-minimal/minimal.o build-minimal/boot.o $(CTRPFLIB)/lib/libctrpf.a 3gx.ld
	$(CXX) $(LDFLAGS) -Wl,-Map=default-minimal.map build-minimal/minimal.o build-minimal/boot.o -lctrpf -lctru -lm -o $@
build-minimal-boot/%.o: source/%.cpp include/boot.hpp
	@mkdir -p build-minimal-boot
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -DUGG_MINIMAL_BOOT -MMD -MP -c $< -o $@
default-minimal-boot.elf: build-minimal-boot/minimal_boot.o build-minimal-boot/boot.o $(CTRPFLIB)/lib/libctrpf.a 3gx.ld
	$(CXX) $(LDFLAGS) -Wl,-Map=default-minimal-boot.map build-minimal-boot/minimal_boot.o build-minimal-boot/boot.o -lctrpf -lctru -lm -o $@
default.3gx: default.elf plugin.plgInfo
	$(THREEGXTOOL) -s default.elf plugin.plgInfo $@
-include $(OBJECTS:.o=.d)
-include build-minimal/minimal.d build-minimal/boot.d
-include build-minimal-boot/minimal_boot.d build-minimal-boot/boot.d
.PHONY: all
