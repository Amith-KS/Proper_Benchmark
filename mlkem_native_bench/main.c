/*
 * Benchmark harness for mlkem-native ML-KEM
 * Loops keygen / encaps / decaps N times, records per-call timing via
 * clock_gettime(CLOCK_MONOTONIC), and reports mean/median/stddev/min/max
 * in microseconds. Also writes raw samples to a CSV for later plotting.
 */
#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "mlkem_native/mlkem_native.h"
#include "test_only_rng/notrandombytes.h"

#ifndef NUM_ITERS
#define NUM_ITERS 5000
#endif
#ifndef WARMUP_ITERS
#define WARMUP_ITERS 100
#endif

static double now_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec / 1e3;
}

static int cmp_double(const void *a, const void *b) {
    double da = *(const double *)a, db = *(const double *)b;
    return (da > db) - (da < db);
}

static void report(const char *label, double *samples, int n, FILE *csv) {
    double sum = 0.0, min = samples[0], max = samples[0];
    int i;
    double *sorted = malloc((size_t)n * sizeof(double));
    memcpy(sorted, samples, (size_t)n * sizeof(double));
    qsort(sorted, (size_t)n, sizeof(double), cmp_double);

    for (i = 0; i < n; i++) {
        sum += samples[i];
        if (samples[i] < min) min = samples[i];
        if (samples[i] > max) max = samples[i];
    }
    double mean = sum / n;

    double sq = 0.0;
    for (i = 0; i < n; i++) sq += (samples[i] - mean) * (samples[i] - mean);
    double stddev = sqrt(sq / n);

    double median = sorted[n / 2];
    double p99 = sorted[(int)(0.99 * n)];

    printf("%-10s  mean=%.3f us  median=%.3f us  stddev=%.3f  min=%.3f  max=%.3f  p99=%.3f\n",
           label, mean, median, stddev, min, max, p99);

    for (i = 0; i < n; i++) {
        fprintf(csv, "mlkem-native,%s,%d,%.4f\n", label, i, samples[i]);
    }

    free(sorted);
}

int main(void) {
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t key_a[CRYPTO_BYTES];
    uint8_t key_b[CRYPTO_BYTES];
    int i;

    double *keygen_t = malloc(NUM_ITERS * sizeof(double));
    double *enc_t     = malloc(NUM_ITERS * sizeof(double));
    double *dec_t     = malloc(NUM_ITERS * sizeof(double));

    FILE *csv = fopen("results_mlkem_native.csv", "w");
    fprintf(csv, "library,operation,iter,microseconds\n");

    randombytes_reset();

    /* Warm-up (not recorded) */
    for (i = 0; i < WARMUP_ITERS; i++) {
        crypto_kem_keypair(pk, sk);
        crypto_kem_enc(ct, key_b, pk);
        crypto_kem_dec(key_a, ct, sk);
    }

    /* Keygen */
    for (i = 0; i < NUM_ITERS; i++) {
        double t0 = now_us();
        crypto_kem_keypair(pk, sk);
        keygen_t[i] = now_us() - t0;
    }

    /* Encaps (reuse last generated pk) */
    for (i = 0; i < NUM_ITERS; i++) {
        double t0 = now_us();
        crypto_kem_enc(ct, key_b, pk);
        enc_t[i] = now_us() - t0;
    }

    /* Decaps */
    for (i = 0; i < NUM_ITERS; i++) {
        double t0 = now_us();
        crypto_kem_dec(key_a, ct, sk);
        dec_t[i] = now_us() - t0;
    }

    printf("=== mlkem-native ML-KEM-%d  (N=%d, warmup=%d) ===\n",
           MLK_CONFIG_PARAMETER_SET, NUM_ITERS, WARMUP_ITERS);
    report("keygen", keygen_t, NUM_ITERS, csv);
    report("encaps", enc_t, NUM_ITERS, csv);
    report("decaps", dec_t, NUM_ITERS, csv);

    fclose(csv);
    free(keygen_t);
    free(enc_t);
    free(dec_t);
    return 0;
}
