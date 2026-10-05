# Developer-only legal probe. Build inside the pinned devkitARM container.
ROOT := ../..
CC := $(DEVKITARM)/bin/arm-none-eabi-gcc
ARCH := -march=armv6k -mtune=mpcore -mfloat-abi=hard -mtp=soft
CFLAGS := $(ARCH) -Os -Wall -Wextra -Werror -I$(DEVKITPRO)/libctru/include
LDFLAGS := $(ARCH) -specs=3dsx.specs -L$(DEVKITPRO)/libctru/lib

all: $(ROOT)/build/emulator-fixture.3dsx
$(ROOT)/build/emulator-fixture.elf: main.c
	mkdir -p $(ROOT)/build
	$(CC) $(CFLAGS) $(LDFLAGS) $< -lctru -lm -o $@
$(ROOT)/build/emulator-fixture.3dsx: $(ROOT)/build/emulator-fixture.elf
	$(DEVKITPRO)/tools/bin/3dsxtool $< $@
.PHONY: all
