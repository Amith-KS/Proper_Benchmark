# Unified Benchmark build for mlkem-native (ML-KEM-512)
CC ?= gcc
LDFLAGS := -lm

# Base flags shared by both versions (No AVX2 or Native macros here)
BASE_CFLAGS := -O3 -std=c99 -Wall -I mlkem_native \
          -DMLK_CONFIG_PARAMETER_SET=512 -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem

# Find all C files recursively using shell find
MLK_SOURCE := $(shell find mlkem_native/src -name '*.c')

# Find all Assembly files recursively (Only used for AVX2)
ASM_SOURCE := $(shell find mlkem_native/src/native/x86_64 -name '*.S') \
              $(shell find mlkem_native/src/fips202/native/x86_64 -name '*.S')

APP_SOURCE := main.c

# By default, running `make` will build both executables
all: bench_mlkem_c bench_mlkem_avx2

# 1. Build the Pure C Version
bench_mlkem_c: $(MLK_SOURCE) $(APP_SOURCE)
	$(CC) $(BASE_CFLAGS) \
	-DLIB_NAME='"mlkem-native-portable"' \
	-DOUT_FILE='"results_c.csv"' \
	$^ -o $@ $(LDFLAGS)

# 2. Build the AVX2 Version
bench_mlkem_avx2: $(MLK_SOURCE) $(ASM_SOURCE) $(APP_SOURCE)
	$(CC) $(BASE_CFLAGS) -mavx2 -mbmi2 -mpopcnt \
	-DMLK_CONFIG_USE_NATIVE_BACKEND_ARITH \
	-DMLK_CONFIG_USE_NATIVE_BACKEND_FIPS202 \
	-DLIB_NAME='"mlkem-native-avx2"' \
	-DOUT_FILE='"results_avx2.csv"' \
	$^ -o $@ $(LDFLAGS)

# Run both benchmarks sequentially
run: all
	./bench_mlkem_c
	./bench_mlkem_avx2

clean:
	rm -f bench_mlkem_c bench_mlkem_avx2 results_c.csv results_avx2.csv

.PHONY: all run clean
