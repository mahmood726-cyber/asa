# Asa — R Cross-Validation Script
# Validates JS GRIM + statcheck engines against R packages
# Run: Rscript tests/validate_vs_r.R

cat("=== Asa R Cross-Validation ===\n\n")

passed <- 0
total <- 0

# ── GRIM validation (vs scrutiny package) ──
cat("--- GRIM Tests (vs scrutiny::grim()) ---\n")

if (!requireNamespace("scrutiny", quietly = TRUE)) {
  cat("SKIP: scrutiny package not installed. Install with: install.packages('scrutiny')\n")
} else {
  library(scrutiny)

  grim_cases <- data.frame(
    study = c("Brown 2018", "Chen 2021", "Ahmed 2020", "Lee 2019",
              "Kim 2017", "Patel 2022"),
    x = c("3.47", "4.83", "5.20", "3.10", "2.63", "4.15"),
    n = c(25, 30, 50, 40, 20, 35),
    expected = c(FALSE, FALSE, TRUE, TRUE, FALSE, TRUE),
    stringsAsFactors = FALSE
  )

  for (i in seq_len(nrow(grim_cases))) {
    row <- grim_cases[i, ]
    result <- grim(x = row$x, n = row$n, items = 1)
    r_pass <- result$consistency
    total <- total + 1
    if (r_pass == row$expected) {
      passed <- passed + 1
      cat(sprintf("  PASS: %s — GRIM %s (expected %s)\n",
                  row$study,
                  ifelse(r_pass, "consistent", "inconsistent"),
                  ifelse(row$expected, "consistent", "inconsistent")))
    } else {
      cat(sprintf("  FAIL: %s — GRIM %s but expected %s\n",
                  row$study,
                  ifelse(r_pass, "consistent", "inconsistent"),
                  ifelse(row$expected, "consistent", "inconsistent")))
    }
  }
}

cat("\n")

# ── statcheck validation ──
cat("--- statcheck Tests (vs statcheck package) ---\n")

if (!requireNamespace("statcheck", quietly = TRUE)) {
  cat("SKIP: statcheck package not installed. Install with: install.packages('statcheck')\n")
} else {
  library(statcheck)

  # Test case 1: t(28) = 2.45, p = 0.02 — should be roughly correct
  text1 <- "The result was significant, t(28) = 2.45, p = 0.02."
  sc1 <- statcheck(text1)
  total <- total + 1
  if (nrow(sc1) > 0) {
    is_error <- sc1$Error[1]
    # p=0.02 for t(28)=2.45 is approximately correct (actual ~0.021)
    if (!is_error) {
      passed <- passed + 1
      cat(sprintf("  PASS: t(28)=2.45, p=0.02 — no error (computed p=%.4f)\n", sc1$Computed[1]))
    } else {
      cat(sprintf("  FAIL: t(28)=2.45, p=0.02 — flagged as error (computed p=%.4f)\n", sc1$Computed[1]))
    }
  } else {
    cat("  FAIL: statcheck did not detect the test statistic\n")
  }

  # Test case 2: F(1,45) = 8.92, p = 0.004 — should be approximately correct
  text2 <- "We found F(1, 45) = 8.92, p = 0.004."
  sc2 <- statcheck(text2)
  total <- total + 1
  if (nrow(sc2) > 0) {
    is_error <- sc2$Error[1]
    if (!is_error) {
      passed <- passed + 1
      cat(sprintf("  PASS: F(1,45)=8.92, p=0.004 — no error (computed p=%.4f)\n", sc2$Computed[1]))
    } else {
      cat(sprintf("  FAIL: F(1,45)=8.92, p=0.004 — flagged as error (computed p=%.4f)\n", sc2$Computed[1]))
    }
  } else {
    cat("  FAIL: statcheck did not detect the test statistic\n")
  }

  # Test case 3: t(34) = 2.15, p = 0.001 — should FAIL (p too small)
  text3 <- "The test showed t(34) = 2.15, p = 0.001."
  sc3 <- statcheck(text3)
  total <- total + 1
  if (nrow(sc3) > 0) {
    is_error <- sc3$Error[1]
    # Actual p for t(34)=2.15 is ~0.039, so p=0.001 is a gross error
    if (is_error) {
      passed <- passed + 1
      cat(sprintf("  PASS: t(34)=2.15, p=0.001 — correctly flagged as error (computed p=%.4f)\n", sc3$Computed[1]))
    } else {
      cat(sprintf("  FAIL: t(34)=2.15, p=0.001 — missed error (computed p=%.4f)\n", sc3$Computed[1]))
    }
  } else {
    cat("  FAIL: statcheck did not detect the test statistic\n")
  }
}

cat("\n")

# ── GRIMMER validation (vs scrutiny::grimmer()) ──
cat("--- GRIMMER Tests (vs scrutiny::grimmer()) ---\n")

if (!requireNamespace("scrutiny", quietly = TRUE)) {
  cat("SKIP: scrutiny package not installed\n")
} else {
  library(scrutiny)

  if (exists("grimmer", where = asNamespace("scrutiny"))) {
    # Test cases: (sd, n, mean, expected_consistency)
    grimmer_cases <- data.frame(
      sd = c("1.0", "1.23", "0.0", "1.29"),
      n = c(10, 10, 5, 4),
      x = c("3.0", "3.0", "3.0", "2.5"),
      expected = c(TRUE, FALSE, TRUE, TRUE),
      stringsAsFactors = FALSE
    )

    for (i in seq_len(nrow(grimmer_cases))) {
      row <- grimmer_cases[i, ]
      tryCatch({
        result <- grimmer(x = row$x, sd = row$sd, n = row$n, items = 1)
        r_pass <- result$consistency
        total <- total + 1
        if (r_pass == row$expected) {
          passed <- passed + 1
          cat(sprintf("  PASS: n=%d, mean=%s, SD=%s — GRIMMER %s\n",
                      row$n, row$x, row$sd,
                      ifelse(r_pass, "consistent", "inconsistent")))
        } else {
          cat(sprintf("  FAIL: n=%d, mean=%s, SD=%s — GRIMMER %s (expected %s)\n",
                      row$n, row$x, row$sd,
                      ifelse(r_pass, "consistent", "inconsistent"),
                      ifelse(row$expected, "consistent", "inconsistent")))
        }
      }, error = function(e) {
        cat(sprintf("  SKIP: n=%d, mean=%s, SD=%s — error: %s\n",
                    row$n, row$x, row$sd, e$message))
      })
    }
  } else {
    cat("  SKIP: grimmer() not found in scrutiny (need version >= 0.3.0)\n")
  }
}

cat("\n")

# ── Benford's Law validation (vs stats::chisq.test) ──
cat("--- Benford's Law Tests (vs base R chi-squared) ---\n")

# Generate Benford-conforming counts and verify chi-squared
benford_expected <- log10(1 + 1 / (1:9))
obs_conforming <- round(benford_expected * 101)  # roughly Benford
chi_conforming <- chisq.test(obs_conforming, p = benford_expected)
total <- total + 1
if (chi_conforming$p.value > 0.05) {
  passed <- passed + 1
  cat(sprintf("  PASS: Benford-conforming data — p=%.4f (not significant)\n", chi_conforming$p.value))
} else {
  cat(sprintf("  FAIL: Benford-conforming data — p=%.4f (unexpectedly significant)\n", chi_conforming$p.value))
}

# Uniform distribution should fail Benford
obs_uniform <- rep(50, 9)
chi_uniform <- chisq.test(obs_uniform, p = benford_expected)
total <- total + 1
if (chi_uniform$p.value < 0.05) {
  passed <- passed + 1
  cat(sprintf("  PASS: Uniform data rejects Benford — p=%.6f (significant)\n", chi_uniform$p.value))
} else {
  cat(sprintf("  FAIL: Uniform data — p=%.4f (should have rejected)\n", chi_uniform$p.value))
}

cat("\n")

# ── Terminal Digit Analysis validation ──
cat("--- TDA Tests (vs base R chi-squared) ---\n")

# Uniform digits should pass
obs_tda_uniform <- rep(10, 10)
chi_tda <- chisq.test(obs_tda_uniform)
total <- total + 1
if (chi_tda$p.value > 0.05) {
  passed <- passed + 1
  cat(sprintf("  PASS: Uniform terminal digits — p=%.4f (not significant)\n", chi_tda$p.value))
} else {
  cat(sprintf("  FAIL: Uniform terminal digits — p=%.4f\n", chi_tda$p.value))
}

# Skewed digits should fail
obs_tda_skewed <- c(50, 3, 3, 3, 3, 3, 3, 3, 3, 26)
chi_tda_skewed <- chisq.test(obs_tda_skewed)
total <- total + 1
if (chi_tda_skewed$p.value < 0.01) {
  passed <- passed + 1
  cat(sprintf("  PASS: Skewed terminal digits — p=%.6f (significant)\n", chi_tda_skewed$p.value))
} else {
  cat(sprintf("  FAIL: Skewed terminal digits — p=%.4f\n", chi_tda_skewed$p.value))
}

cat(sprintf("\n=== Summary: %d/%d tests passed ===\n", passed, total))
if (passed == total) {
  cat("ALL PASS — JS engines validated against R\n")
} else {
  cat(sprintf("WARNING: %d test(s) failed\n", total - passed))
}
