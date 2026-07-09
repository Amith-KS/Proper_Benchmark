# Benchmark build for PQClean ML-KEM-512 (clean reference implementation)
CC ?= gcc
# -I../mlkem_native_bench allows your #include "test_only_rng/notrandombytes.h" statement to resolve
CFLAGS := -O3 -std=c99 -Wall -I. -I../mlkem_native_bench
LDFLAGS := -lm

# Grab local .c files, drop the true RNG, and link directly to the sibling folder's fake RNG source
SOURCES := $(filter-out randombytes.c, $(wildcard *.c)) ../mlkem_native_bench/test_only_rng/notrandombytes.c
BIN := bench_pqclean

all: $(BIN)

$(BIN): $(SOURCES)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

run: $(BIN)
	./$(BIN)

clean:
	rm -f $(BIN) results_pqclean.csv

.PHONY: all run clean
