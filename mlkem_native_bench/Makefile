# Benchmark build for mlkem-native (ML-KEM-512)
CC ?= gcc
CFLAGS := -O3 -std=c99 -Wall -I mlkem_native -DMLK_CONFIG_PARAMETER_SET=512 -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem
LDFLAGS := -lm

MLK_SOURCE=$(wildcard \
	mlkem_native/src/*.c \
	mlkem_native/src/**/*.c \
	mlkem_native/src/**/**/*.c \
	mlkem_native/src/**/**/**/*.c)
RNG_SOURCE=$(wildcard test_only_rng/*.c)
APP_SOURCE=main.c

ALL_SOURCE=$(MLK_SOURCE) $(RNG_SOURCE) $(APP_SOURCE)

BIN=bench_mlkem_native

all: $(BIN)

$(BIN): $(ALL_SOURCE)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

run: $(BIN)
	./$(BIN)

clean:
	rm -f $(BIN) results_mlkem_native.csv

.PHONY: all run clean
